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
from .forms import CompanyAndQuestionnaireSelectForm

def home_view(request):
    # Adatok lekérdezése az adatbázisból
    num_companies = CompanyProfile.objects.count()
    num_esg_data_points = ESGDataPoint.objects.count()
    num_company_data_entries = CompanyDataEntry.objects.count()

    context = {
        'page_title': 'ESG AutoReport Főoldal',
        'welcome_message': 'Üdvözöllek az ESG AutoReport rendszerben!',
        'num_companies': num_companies,
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