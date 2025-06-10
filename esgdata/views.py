# esgdata/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CompanyDataEntryForm, ESGReportCreationInitialForm  # Ezt hozzuk majd létre
from companies.models import CompanyProfile
from .models import ESGDataPoint, CompanyDataEntry, ChoiceOption
from django.contrib import messages
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.urls import reverse  # Siker oldalhoz

@login_required  # Ez a dekorátor biztosítja, hogy csak bejelentkezett felhasználók érhessék el ezt a nézetet
def create_company_data_entry(request):
    if request.method == 'POST':
        # Ha az űrlapot elküldték (POST kérés)
        form = CompanyDataEntryForm(request.POST, request.FILES, user=request.user)  # Átadjuk a user-t is
        if form.is_valid():
            data_entry = form.save(commit=False)  # Még ne mentsük az adatbázisba
            data_entry.entered_by = request.user  # Beállítjuk a rögzítő felhasználót
            data_entry.save()  # Most mentjük az adatbázisba

            # Sikeres mentés után átirányítjuk a felhasználót valahova
            # Például a dashboard főoldalára (feltéve, hogy a dashboard app 'home' nevű URL-je létezik)
            # Használhatnánk egy sikeres üzenetet is a Django messages frameworkkel.
            return redirect('dashboard:home')
    else:
        # Ha az oldalt először töltik be (GET kérés), egy üres űrlapot mutatunk
        form = CompanyDataEntryForm(user=request.user)  # Átadjuk a user-t is az __init__-nek

    context = {
        'form': form,
        'page_title': 'Új ESG Adat Rögzítése',
    }
    return render(request, 'esgdata/companydataentry_form.html', context)

@login_required
def create_esg_report_selection_view(request):
    if request.method == 'POST':
        form = ESGReportCreationInitialForm(request.POST, user=request.user)
        if form.is_valid():
            company = form.cleaned_data['company']
            year = form.cleaned_data['period_year']
            topic_key = form.cleaned_data['pillar']
            return redirect(reverse('esgdata:fill_questionnaire', kwargs={
                'company_id': company.pk,
                'year': int(year),
                'topic_key': topic_key
            }))
        else:
            messages.error(request, "Kérjük, javítsa a hibákat a kiválasztó űrlapon.")
    else:
        form = ESGReportCreationInitialForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'ESG Jelentés Készítése - Kiválasztás',
    }
    return render(request, 'esgdata/create_esg_report_selection.html', context)

@login_required
def fill_questionnaire_view(request, company_id, year, topic_key):
    company = get_object_or_404(CompanyProfile, pk=company_id)
    topic_display = dict(ESGDataPoint.PILLAR_CHOICES).get(topic_key, "Ismeretlen témakör")
    status_choices = CompanyDataEntry.STATUS_CHOICES

    sajat_jelento_adatok, beszallito_kitolto_adatok, beszallito_kero_adatok = [], [], []
    other_topic_questions = []
    existing_answers = {}

    questions_for_page = []

    if topic_key == ESGDataPoint.PILLAR_DATASHEET:
        all_datasheet_q = ESGDataPoint.objects.filter(
            pillar=ESGDataPoint.PILLAR_DATASHEET
        ).order_by('question_number')
        for q in all_datasheet_q:
            if q.adatlap_kontextus == ESGDataPoint.CONTEXT_SAJAT_JELENTO:
                sajat_jelento_adatok.append(q)
            elif q.adatlap_kontextus == ESGDataPoint.CONTEXT_BESZALLITO:
                if q.question_number.startswith("AD-B-KIT-"):
                    beszallito_kitolto_adatok.append(q)
                elif q.question_number.startswith("AD-B-KERO-"):
                    beszallito_kero_adatok.append(q)
        questions_for_page.extend(sajat_jelento_adatok)
        questions_for_page.extend(beszallito_kitolto_adatok)
        questions_for_page.extend(beszallito_kero_adatok)
    elif topic_key:
        other_topic_questions = ESGDataPoint.objects.filter(pillar=topic_key).order_by('question_number')
        questions_for_page.extend(other_topic_questions)

    for q_dp in questions_for_page:
        try:
            entry = CompanyDataEntry.objects.get(company=company, data_point=q_dp, period_year=year)
            if q_dp.response_data_type == ESGDataPoint.DATATYPE_TEXT:
                existing_answers[q_dp.pk] = entry.value_text
            elif q_dp.response_data_type == ESGDataPoint.DATATYPE_NUMBER:
                existing_answers[q_dp.pk] = entry.value_numeric
            elif q_dp.response_data_type == ESGDataPoint.DATATYPE_DATE:
                existing_answers[q_dp.pk] = entry.value_date
            elif q_dp.response_data_type == ESGDataPoint.DATATYPE_BOOLEAN:
                existing_answers[q_dp.pk] = entry.value_text
            elif q_dp.response_data_type == ESGDataPoint.DATATYPE_DROPDOWN:
                existing_answers[q_dp.pk] = entry.value_text
            elif q_dp.response_data_type == ESGDataPoint.DATATYPE_FILE:
                existing_answers[q_dp.pk] = entry.value_file
        except CompanyDataEntry.DoesNotExist:
            existing_answers[q_dp.pk] = None

    if request.method == 'POST':
        save_errors_found = False
        try:
            with transaction.atomic():
                for question_dp in questions_for_page:
                    answer_key = f'answer_q_{question_dp.pk}'
                    posted_value_str = request.POST.get(answer_key)
                    file_value = request.FILES.get(answer_key)

                    defaults_for_saving = {
                        'value_text': None, 'value_numeric': None, 'value_date': None,
                        'entered_by': request.user, 'status': CompanyDataEntry.STATUS_MISSING
                    }
                    if file_value:
                        defaults_for_saving['value_file'] = file_value

                    has_actual_value = False
                    if question_dp.response_data_type == ESGDataPoint.DATATYPE_BOOLEAN:
                        if posted_value_str == "True":
                            defaults_for_saving['value_text'] = "Igen"
                            has_actual_value = True
                        else:
                            defaults_for_saving['value_text'] = "Nem"
                            has_actual_value = True
                    elif file_value:
                        has_actual_value = True
                    elif posted_value_str is not None and posted_value_str.strip() != '':
                        has_actual_value = True
                        if question_dp.response_data_type == ESGDataPoint.DATATYPE_TEXT or \
                           question_dp.response_data_type == ESGDataPoint.DATATYPE_DROPDOWN:
                            defaults_for_saving['value_text'] = posted_value_str.strip()
                        elif question_dp.response_data_type == ESGDataPoint.DATATYPE_NUMBER:
                            try:
                                defaults_for_saving['value_numeric'] = Decimal(posted_value_str)
                            except (InvalidOperation, ValueError):
                                messages.error(request, f"Hibás számformátum: '{question_dp.question_text}' ({posted_value_str}).")
                                has_actual_value = False
                                save_errors_found = True
                        elif question_dp.response_data_type == ESGDataPoint.DATATYPE_DATE:
                            defaults_for_saving['value_date'] = posted_value_str

                    if has_actual_value:
                        defaults_for_saving['status'] = CompanyDataEntry.STATUS_FILLED

                    if not save_errors_found:
                        entry, created = CompanyDataEntry.objects.update_or_create(
                            company=company, data_point=question_dp, period_year=year,
                            defaults=defaults_for_saving
                        )
                        if has_actual_value:
                            if question_dp.response_data_type == ESGDataPoint.DATATYPE_TEXT:
                                existing_answers[question_dp.pk] = entry.value_text
                            elif question_dp.response_data_type == ESGDataPoint.DATATYPE_NUMBER:
                                existing_answers[question_dp.pk] = entry.value_numeric
                            elif question_dp.response_data_type == ESGDataPoint.DATATYPE_DATE:
                                existing_answers[question_dp.pk] = entry.value_date
                            elif question_dp.response_data_type == ESGDataPoint.DATATYPE_BOOLEAN:
                                existing_answers[question_dp.pk] = entry.value_text
                            elif question_dp.response_data_type == ESGDataPoint.DATATYPE_DROPDOWN:
                                existing_answers[question_dp.pk] = entry.value_text
                            elif question_dp.response_data_type == ESGDataPoint.DATATYPE_FILE and entry.value_file:
                                existing_answers[question_dp.pk] = entry.value_file

                    elif not file_value and question_dp.response_data_type == ESGDataPoint.DATATYPE_FILE and not created:
                        pass
                    else:
                        if question_dp.response_data_type != ESGDataPoint.DATATYPE_FILE:
                            try:
                                entry_to_clear = CompanyDataEntry.objects.get(company=company, data_point=question_dp, period_year=year)
                                entry_to_clear.value_text = None
                                entry_to_clear.value_numeric = None
                                entry_to_clear.value_date = None
                                entry_to_clear.status = CompanyDataEntry.STATUS_MISSING
                                entry_to_clear.save()
                                existing_answers[question_dp.pk] = None
                            except CompanyDataEntry.DoesNotExist:
                                pass

                if save_errors_found:
                    transaction.set_rollback(True)
                    messages.error(request, "A mentés során hibák történtek. Kérjük, javítsa a megjelölt adatokat és próbálja újra.")
                else:
                    messages.success(request, "Adatok sikeresen elmentve!")
                    return redirect(reverse('esgdata:report_submission_success'))

        except Exception as e:
            messages.error(request, f"Általános hiba történt a válaszok mentése közben: {e}")

    context = {
        'page_title': f'ESG Jelentés Kitöltése: {topic_display}',
        'selected_company': company,
        'selected_year': year,
        'selected_topic_key': topic_key,
        'selected_topic_display': topic_display,

        'sajat_jelento_adatok': sajat_jelento_adatok,
        'beszallito_kitolto_adatok': beszallito_kitolto_adatok,
        'beszallito_kero_adatok': beszallito_kero_adatok,
        'other_topic_questions': other_topic_questions,

        'existing_answers': existing_answers,
    }
    return render(request, 'esgdata/fill_questionnaire.html', context)

def report_submission_success_view(request):
    context = {
        'page_title': 'Sikeres Adatmentés',
        'message': 'Az ESG jelentéshez kapcsolódó adataidat sikeresen elmentettük!'
    }
    return render(request, 'esgdata/report_submission_success.html', context)

# A régi create_company_data_entry nézetet egyelőre hagyd meg, vagy kommentezd ki,
# ha az új teljesen felváltja. Ha átnevezed, az URL-eket is módosítani kell.