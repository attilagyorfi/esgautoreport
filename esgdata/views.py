# esgdata/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # Bejelentkezéshez kötéshez
from .forms import CompanyDataEntryForm
# from .models import CompanyDataEntry # Erre közvetlenül itt nincs szükség, ha a form menti

@login_required # Ez a dekorátor biztosítja, hogy csak bejelentkezett felhasználók érhessék el ezt a nézetet
def create_company_data_entry(request):
    if request.method == 'POST':
        # Ha az űrlapot elküldték (POST kérés)
        form = CompanyDataEntryForm(request.POST, request.FILES, user=request.user) # Átadjuk a user-t is
        if form.is_valid():
            data_entry = form.save(commit=False) # Még ne mentsük az adatbázisba
            data_entry.entered_by = request.user # Beállítjuk a rögzítő felhasználót
            data_entry.save() # Most mentjük az adatbázisba
            
            # Sikeres mentés után átirányítjuk a felhasználót valahova
            # Például a dashboard főoldalára (feltéve, hogy a dashboard app 'home' nevű URL-je létezik)
            # Használhatnánk egy sikeres üzenetet is a Django messages frameworkkel.
            return redirect('dashboard:home') 
    else:
        # Ha az oldalt először töltik be (GET kérés), egy üres űrlapot mutatunk
        form = CompanyDataEntryForm(user=request.user) # Átadjuk a user-t is az __init__-nek

    context = {
        'form': form,
        'page_title': 'Új ESG Adat Rögzítése',
    }
    return render(request, 'esgdata/companydataentry_form.html', context)