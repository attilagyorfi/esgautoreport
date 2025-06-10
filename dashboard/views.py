# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Nincs szükségünk HttpResponse-ra, ha mindig renderelünk sablont
# from django.http import HttpResponse 

# Importáljuk a szükséges modelleket
from companies.models import CompanyProfile
from esgdata.models import ESGDataPoint, CompanyDataEntry
from accounts.models import UserProfile
from .forms import CompanyAndQuestionnaireSelectForm, CompanyFilterForm  # Az új szűrő form importálása
from django.db.models import Q

def home_view(request):
    num_companies_total = CompanyProfile.objects.count()
    num_esg_data_points = ESGDataPoint.objects.count()
    num_company_data_entries = CompanyDataEntry.objects.count()

    companies_list = CompanyProfile.objects.select_related('industry').all().order_by('name')
    filter_form = CompanyFilterForm(request.GET or None)
    search_active = False

    if filter_form.is_valid():
        teor_code = filter_form.cleaned_data.get('teor_code')
        company_size_key = filter_form.cleaned_data.get('company_size_filter')
        tax_number = filter_form.cleaned_data.get('tax_number_search')

        if teor_code:
            companies_list = companies_list.filter(industry=teor_code)
            search_active = True
        if tax_number:
            companies_list = companies_list.filter(tax_number__icontains=tax_number)
            search_active = True
        if company_size_key:
            matching_user_profiles = UserProfile.objects.filter(
                primary_questionnaire_type__icontains=company_size_key
            ).values_list('company_id', flat=True).distinct()
            companies_list = companies_list.filter(pk__in=list(matching_user_profiles))
            search_active = True

        if not (teor_code or company_size_key or tax_number):
            search_active = False

    context = {
        'page_title': 'ESG AutoReport Vezérlőpult',
        'num_companies': num_companies_total,
        'num_esg_data_points': num_esg_data_points,
        'num_company_data_entries': num_company_data_entries,
    }
    return render(request, 'dashboard/home.html', context)

def about_us_view(request):
    context = {
        'page_title': 'Rólunk - ESG AutoReport',
    }
    return render(request, 'dashboard/about_us.html', context)

def contact_view(request):
    context = {
        'page_title': 'Kapcsolat - ESG AutoReport',
        # Később itt átadhatnánk egy Django formot is a kapcsolatfelvételhez
    }
    return render(request, 'dashboard/contact.html', context)

def knowledge_base_view(request):
    context = {
        'page_title': 'Tudástár - ESG Szabályozás',
    }
    return render(request, 'dashboard/knowledge_base.html', context)


def data_management_overview_view(request):
    context = {
        'page_title': 'Adatkezelés - Áttekintés'
    }
    return render(request, 'dashboard/data_management_overview.html', context)

@login_required
def company_setup_view(request):
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)

    company_profile = user_profile.company

    if request.method == 'POST':
        form = CompanyAndQuestionnaireSelectForm(request.POST, user=request.user)
        if form.is_valid():
            if not company_profile:
                company_profile = CompanyProfile()
            company_profile.name = form.cleaned_data['company_name']
            company_profile.tax_number = form.cleaned_data['tax_number']
            company_profile.registration_number = form.cleaned_data['registration_number']
            company_profile.address = form.cleaned_data['address']
            company_profile.save()

            user_profile.company = company_profile
            user_profile.primary_questionnaire_type = form.cleaned_data['questionnaire_type']
            user_profile.profile_setup_complete = True
            user_profile.save()

            messages.success(request, 'A vállalati adatok és a kérdőív típus sikeresen elmentve!')
            return redirect('dashboard:home')
        else:
            messages.error(request, 'Kérjük, javítsa a hibákat az űrlapon.')
    else:
        initial_data_for_form = {}
        if company_profile:
            initial_data_for_form['company_name'] = company_profile.name
            initial_data_for_form['tax_number'] = company_profile.tax_number
            initial_data_for_form['registration_number'] = company_profile.registration_number
            initial_data_for_form['address'] = company_profile.address
        if user_profile.primary_questionnaire_type:
            initial_data_for_form['questionnaire_type'] = user_profile.primary_questionnaire_type

        form = CompanyAndQuestionnaireSelectForm(initial=initial_data_for_form, user=request.user)

    context = {
        'form': form,
        'page_title': 'Vállalati Adatok és Kérdőív Kiválasztása'
    }
    return render(request, 'dashboard/company_setup.html', context)