# co2calc/forms.py
from django import forms
from .models import CO2CalculationInput, EmissionFactor  # EmissionFactor importálása

# === ÚJ EGYEDI WIDGET KEZDETE ===
class EmissionFactorSelectWidget(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        
        # Biztosítjuk, hogy option['attrs'] létezzen és szótár legyen
        if 'attrs' not in option or option['attrs'] is None:  # Biztosítjuk, hogy létezzen
            option['attrs'] = {}

        if value:  # Csak akkor, ha van valós érték (nem az üres "----" opció)
            option['attrs']['data-test-value'] = f"OptionValue-{value}"  # Teszt attribútum hozzáadása
            try:
                ef = EmissionFactor.objects.get(pk=value)
                option['attrs']['data-factor-value'] = str(ef.factor_value)
                option['attrs']['data-emission-unit'] = ef.emission_unit_numerator
                option['attrs']['data-debug-info'] = "EF_found"
            except EmissionFactor.DoesNotExist:
                option['attrs']['data-debug-info'] = "EF_DoesNotExist"
            except Exception as e:
                print(f"HIBA A WIDGETBEN (create_option for value {value}): {type(e).__name__} - {e}")
                option['attrs']['data-debug-info'] = f"EF_Error_{type(e).__name__}"
        else:
            option['attrs']['data-test-value'] = "OptionValue-Empty"  # Az üres opcióhoz is
            option['attrs']['data-debug-info'] = "EF_Value_Is_None_Or_Empty"
            
        return option
# === ÚJ EGYEDI WIDGET VÉGE ===

class CO2CalculationInputForm(forms.ModelForm):
    class Meta:
        model = CO2CalculationInput
        fields = [
            # A 'company'-t a nézetben fogjuk beállítani, ha a felhasználó egy céghez van kötve,
            # vagy ha az egész oldal egy adott céghez tartozó adatbevitel.
            # Egyelőre hagyjuk benne, de később finomíthatjuk.
            'company', 
            'activity_type', 
            'period_year', 
            'period_month',
            'quantity', 
            'unit', 
            'emission_factor', 
            # 'calculated_co2e' - ezt a rendszer számolja, nem direkt beviteli mező
        ]
        widgets = {
            # A choices mezők (activity_type, period_year, period_month, unit)
            # automatikusan legördülőként jelennek meg.
            'emission_factor': EmissionFactorSelectWidget,  # <<< AZ ÚJ WIDGET HASZNÁLATA
        }
        labels = {
            'company': 'Vállalat',
            'activity_type': 'Tevékenység Típusa',
            'period_year': 'Jelentési Év',
            'period_month': 'Jelentési Hónap',
            'quantity': 'Mennyiség',
            'unit': 'Mértékegység',
            'emission_factor': 'Kiválasztott Emissziós Faktor (felülíráshoz)',
        }
        help_texts = {
            'emission_factor': 'Válassz egy konkrét faktort a listából, vagy hagyd üresen az automatikus szerveroldali kereséshez.',
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None) # A request objektum tárolása, ha a view átadja
        super().__init__(*args, **kwargs)
        # Itt lehetne logikát hozzáadni a 'company' mező előtöltéséhez a bejelentkezett felhasználó alapján,
        # ha a request elérhető és tartalmazza a usert.
        # Pl. if self.request and self.request.user.is_authenticated and hasattr(self.request.user, 'profile'):
        #         if self.request.user.profile.company:
        #             self.fields['company'].initial = self.request.user.profile.company
        #             self.fields['company'].disabled = True # Akár le is tilthatjuk a módosítást

from django.forms import modelformset_factory

CO2CalculationInputFormSet = modelformset_factory(
    CO2CalculationInput,  # A modell, amit használunk
    form=CO2CalculationInputForm,  # Az imént definiált egyedi formunk
    extra=1,  # Hány üres űrlapot jelenítsen meg alapból
    can_delete=False,  # Egyelőre nem engedélyezzük a meglévő adatok törlését ezen a felületen
    # fields = [...] # Itt is megadhatnánk a mezőket, ha nem használnánk egyedi form-ot
    # exclude = [...]
)