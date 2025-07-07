# dashboard/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from companies.forms import CompanyProfileForm
from esgdata.models import Report # Ezt a modellt is importáljuk
from django.db.models import Count
from django.core.exceptions import ObjectDoesNotExist

@login_required
def home(request):
    """A főoldal nézete."""
    try:
        company_exists = request.user.profile.company is not None
    except (AttributeError, ObjectDoesNotExist):
        company_exists = False
    context = {
        'company_exists': company_exists,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def profile_view(request):
    """A felhasználói profil oldal, ahol a cégadatok és a riportok kezelhetők."""
    try:
        company_profile = request.user.profile.company
        if not company_profile:
            messages.info(request, 'Kérjük, válasszon vagy hozzon létre egy vállalatot a folytatáshoz.')
            return redirect('esgdata:company_setup')
    except (ObjectDoesNotExist, AttributeError):
        return redirect('esgdata:company_setup')

    # A céghez tartozó riportok lekérdezése
    user_reports = Report.objects.filter(company=company_profile).annotate(
        answered_count=Count('entries')
    ).order_by('-period_year')

    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, instance=company_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'A cégadatokat sikeresen frissítettük!')
            return redirect('dashboard:profile')
    else:
        form = CompanyProfileForm(instance=company_profile)

    context = {
        'form': form,
        'reports': user_reports,
    }
    return render(request, 'dashboard/profile.html', context)

# --- Az alábbi nézetek hiányoztak ---

def about_us(request):
    """A "Rólunk" oldal nézete."""
    return render(request, 'dashboard/about_us.html')

def knowledge_base(request):
    """A "Tudástár" oldal nézete."""
    return render(request, 'dashboard/knowledge_base.html')

def contact(request):
    """A "Kapcsolat" oldal nézete."""
    return render(request, 'dashboard/contact.html')

# --- Az alábbi, már nem használt nézetek törölve vagy egyszerűsítve lettek ---
# A company_setup és a data_management_overview logikája már az esgdata és a profile nézetekben van.
# Így ezek a külön nézetek már feleslegesek.