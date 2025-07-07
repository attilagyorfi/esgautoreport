# esgdata/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.contrib import messages
from .models import Report, EsgDataPoint, CompanyDataEntry
from .forms import ReportSelectionForm

@login_required
def create_report_selection_view(request):
    try:
        initial_data = {'company': request.user.profile.company}
    except (AttributeError, ObjectDoesNotExist):
        return redirect('dashboard:company_setup')

    if request.method == 'POST':
        form = ReportSelectionForm(request.POST)
        if form.is_valid():
            report, created = Report.objects.get_or_create(
                company=form.cleaned_data['company'],
                period_year=form.cleaned_data['period_year'],
                report_type=form.cleaned_data['report_type'],
                defaults={'created_by': request.user}
            )
            return redirect(reverse('esgdata:fill_report', kwargs={'report_id': report.id}))
    else:
        form = ReportSelectionForm(initial=initial_data)

    return render(request, 'esgdata/create_report_selection.html', {'form': form})


@login_required
def fill_report_view(request, report_id):
    from .models import Report, EsgDataPoint, CompanyDataEntry

    # JAVÍTÁS: A get_object_or_404 helyett egy try-except blokkot használunk
    try:
        report = Report.objects.get(id=report_id, created_by=request.user)
    except Report.DoesNotExist:
        messages.error(request, "A keresett jelentés nem létezik, vagy nincs jogosultsága megtekinteni.")
        return redirect('esgdata:create_report_selection')

    all_questions = report.report_type.questions.all()
    total_questions_count = all_questions.count()

    if request.method == 'POST':
        # --- Adatok mentése ---
        for question in all_questions:
            field_name = f'question_{question.id}'
            value = request.POST.get(field_name)

            if value and value.isdigit(): # Csak akkor mentünk, ha van érték és az szám (ID)
                choice = ChoiceOption.objects.get(id=value)
                CompanyDataEntry.objects.update_or_create(
                    report=report,
                    data_point=question,
                    defaults={'choice_option': choice}
                )
            else: # Ha az érték üres, töröljük a korábbi választ
                CompanyDataEntry.objects.filter(report=report, data_point=question).delete()

        # --- Annak ellenőrzése, melyik gombot nyomták meg ---
        if 'save_only' in request.POST:
            # 1. eset: Csak mentés
            messages.success(request, 'Válaszait sikeresen mentettük!')
            return redirect(reverse('esgdata:fill_report', kwargs={'report_id': report.id}))
        
        elif 'generate_report' in request.POST:
            # 2. eset: Riport generálása
            answered_questions_count = report.entries.count()
            if answered_questions_count < total_questions_count:
                # Ha nincs minden kitöltve, hibaüzenetet küldünk
                messages.error(request, f'A riport generálásához minden kérdést meg kell válaszolnia! ({answered_questions_count}/{total_questions_count} megválaszolva)')
                return redirect(reverse('esgdata:fill_report', kwargs={'report_id': report.id}))
            else:
                # Ha minden rendben, átirányítunk a riport nézetre
                messages.success(request, 'Minden kérdés megválaszolva, a riport elkészült!')
                return redirect(reverse('reports:view_report', kwargs={'report_id': report.id}))

    # --- GET kérés kezelése (ez a rész változatlan) ---
    categorized_questions = {
        'E': {'name': 'Környezeti', 'questions': []},
        'S': {'name': 'Társadalmi', 'questions': []},
        'G': {'name': 'Irányítási', 'questions': []},
    }
    for question in all_questions.order_by('question_id'):
        if question.pillar in categorized_questions:
            categorized_questions[question.pillar]['questions'].append(question)
    
    existing_answers = {entry.data_point.id: entry for entry in report.entries.all()}
    answered_count = len(existing_answers)

    context = {
        'report': report,
        'categorized_questions': categorized_questions,
        'existing_answers': existing_answers,
        'total_questions_count': total_questions_count,
        'answered_count': answered_count,
        'all_questions_answered': answered_count == total_questions_count
    }
    return render(request, 'esgdata/fill_report_form.html', context)