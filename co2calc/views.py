# co2calc/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import EmissionFactor, ActivityType # ActivityType importálása
from decimal import Decimal # Szükséges lehet, ha itt is számolnánk/konvertálnánk
from .forms import CO2CalculationInputFormSet
from .models import CO2CalculationInput
from companies.models import CompanyProfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@require_GET
def get_emission_factor_ajax(request):
    activity_type_id_str = request.GET.get('activity_type_id')
    unit = request.GET.get('unit')
    period_year_str = request.GET.get('period_year')

    if not activity_type_id_str or not unit:
        return JsonResponse({'error': 'Hiányzó paraméterek: activity_type_id és unit szükséges.'}, status=400)

    try:
        activity_type_id = int(activity_type_id_str)
        filter_kwargs = {
            'activity_type_id': activity_type_id,
            'unit_of_activity': unit,
        }
        if period_year_str:
            try:
                filter_kwargs['year_of_factor__lte'] = int(period_year_str)
            except ValueError:
                pass 
        
        suitable_factor = EmissionFactor.objects.filter(**filter_kwargs).order_by('-year_of_factor').first()

        if suitable_factor:
            data = {
                'factor_id': suitable_factor.pk,  # <<< ÚJ: A talált faktor ID-ja
                'factor_value': str(suitable_factor.factor_value),
                'emission_unit_numerator': suitable_factor.emission_unit_numerator,
                'unit_of_activity': suitable_factor.unit_of_activity,
                'factor_source': suitable_factor.source,
                'factor_year': suitable_factor.year_of_factor,
                'message': 'Faktor sikeresen lekérdezve.'
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'error': 'Nincs megfelelő emissziós faktor találat.', 'factor_id': None}, status=200)

    except ValueError:
        return JsonResponse({'error': 'Érvénytelen paraméter formátum (ID vagy év).'}, status=400)
    except Exception as e:
        print(f"Hiba az emissziós faktor lekérdezésekor (AJAX): {e}")
        return JsonResponse({'error': 'Szerveroldali hiba történt a faktor lekérdezésekor.'}, status=500)

@login_required
def manage_co2_entries_view(request):
    user_company = None
    if hasattr(request.user, 'profile') and request.user.profile.company:
        user_company = request.user.profile.company

    if request.method == 'POST':
        queryset = CO2CalculationInput.objects.filter(company=user_company) if user_company else CO2CalculationInput.objects.none()
        formset = CO2CalculationInputFormSet(request.POST, request.FILES, queryset=queryset, form_kwargs={'request': request})

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                if user_company and not instance.company:
                    instance.company = user_company
                instance.save()
            return redirect('dashboard:home')
    else:
        queryset = CO2CalculationInput.objects.filter(company=user_company) if user_company else CO2CalculationInput.objects.none()
        formset = CO2CalculationInputFormSet(queryset=queryset, form_kwargs={'request': request})

    context = {
        'formset': formset,
        'page_title': f"CO₂ Kibocsátási Adatok Rögzítése {(' - ' + user_company.name) if user_company else ''}",
        'user_company': user_company
    }
    return render(request, 'co2calc/manage_co2_entries.html', context)