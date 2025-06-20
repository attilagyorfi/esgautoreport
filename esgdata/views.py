# esgdata/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import ESGReportCreationInitialForm
from companies.models import CompanyProfile
from .models import ESGDataPoint, CompanyDataEntry
from django.contrib import messages
from django.db import transaction
from decimal import Decimal, InvalidOperation
from django.urls import reverse

@login_required
def create_report_selection_view(request):
    """
    1. lépés: Megjeleníti a kiválasztó űrlapot (Cég, Év, Jelentéstípus),
    és sikeres kiválasztás után átirányít a kitöltő oldalra.
    """
    if request.method == 'POST':
        form = ESGReportCreationInitialForm(request.POST, user=request.user)
        if form.is_valid():
            company = form.cleaned_data['company']
            year = form.cleaned_data['period_year']
            report_type_key = form.cleaned_data['report_type']
            
            # Átirányítás a kitöltő nézetre az URL-ben átadott paraméterekkel
            return redirect(reverse('esgdata:fill_report', kwargs={
                'company_id': company.pk,
                'year': int(year),
                'report_type_key': report_type_key
            }))
    else: # GET kérés
        form = ESGReportCreationInitialForm(user=request.user)

    context = {
        'form': form,
        'page_title': 'ESG Jelentés Készítése - Kiválasztás',
    }
    return render(request, 'esgdata/create_report_selection.html', context)

@login_required
def fill_report_view(request, company_id, year, report_type_key):
    """
    2. lépés: Megjeleníti a kiválasztott jelentéshez tartozó kérdéseket,
    és kezeli a válaszok mentését.
    """
    company = get_object_or_404(CompanyProfile, pk=company_id)
    report_type_display = dict(ESGReportCreationInitialForm.QUESTIONNAIRE_TYPE_CHOICES).get(report_type_key, "Ismeretlen")

    # Itt szűrjük a kérdéseket a megadott jelentéstípusra!
    # Ehhez az ESGDataPoint modellen kell egy mező, ami ezt tárolja.
    # A korábbi megbeszélés alapján ez az `applies_to_questionnaire_type`.
    all_questions = ESGDataPoint.objects.filter(
        applies_to_questionnaire_type=report_type_key
    ).order_by('pillar', 'question_number') # Csoportosítás pillér/témakör szerint

    # Kérdések szétosztása szekciókba a 'pillar' mezőjük alapján
    questions_by_pillar = {
        'datasheet': [], 'environmental': [], 'social': [], 'governance': [], 'ghg_targets': []
    }
    for q in all_questions:
        if q.pillar in questions_by_pillar:
            questions_by_pillar[q.pillar].append(q)

    # Meglévő válaszok betöltése az előtöltéshez
    existing_answers = {}
    for q_dp in all_questions:
        try:
            entry = CompanyDataEntry.objects.get(company=company, data_point=q_dp, period_year=year)
            # Itt a get_display_value egy javasolt modell metódus lenne, ami visszaadja a helyes értéket
            existing_answers[q_dp.pk] = entry.get_display_value()
        except CompanyDataEntry.DoesNotExist:
            existing_answers[q_dp.pk] = None

    if request.method == 'POST' and 'save_answers' in request.POST:
        with transaction.atomic():
            for question_dp in all_questions:
                answer_key = f'answer_q_{question_dp.pk}'
                posted_value = request.POST.get(answer_key)
                file_value = request.FILES.get(answer_key)

                defaults = {'entered_by': request.user}
                question_dp.set_value_for_entry(defaults, posted_value, file_value)

                CompanyDataEntry.objects.update_or_create(
                    company=company, data_point=question_dp, period_year=year,
                    defaults=defaults
                )

        messages.success(request, "Adatok sikeresen elmentve!")
        return redirect(reverse('esgdata:report_submission_success'))

    context = {
        'page_title': f'Jelentés Kitöltése: {report_type_display}',
        'company': company,
        'year': year,
        'report_type_key': report_type_key,
        'questions_by_pillar': questions_by_pillar,
        'existing_answers': existing_answers,
    }
    return render(request, 'esgdata/fill_report.html', context)


def report_submission_success_view(request):
    """A sikeres mentést visszaigazoló oldal nézete."""
    context = {
        'page_title': 'Sikeres Adatmentés',
        'message': 'Az ESG jelentéshez kapcsolódó adataidat sikeresen elmentettük!'
    }
    return render(request, 'esgdata/report_submission_success.html', context)