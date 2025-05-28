# esgdata/forms.py
from django import forms
from .models import CompanyDataEntry

class CompanyDataEntryForm(forms.ModelForm):
    class Meta:
        model = CompanyDataEntry
        fields = [
            'company', 
            'data_point', 
            'period_year', 
            'period_month',
            'value_numeric', 
            'value_text', 
            'value_date', 
            'value_file',
            'source_description',
            'status',
            # Az 'entered_by' mezőt a nézetben (view) fogjuk automatikusan beállítani
            # a bejelentkezett felhasználóra, ezért itt nem szerepeltetjük.
            # Az 'entry_date', 'created_at', 'updated_at' mezők automatikusan kezelődnek.
        ]
        widgets = {
            'period_year': forms.NumberInput(attrs={'placeholder': 'ÉÉÉÉ'}),
            'period_month': forms.NumberInput(attrs={'placeholder': 'HH (1-12)'}),
            'value_date': forms.DateInput(attrs={'type': 'date'}), # HTML5 dátumválasztó
            'source_description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'company': 'Vállalat',
            'data_point': 'ESG Adatpont',
            'period_year': 'Jelentési Év',
            'period_month': 'Jelentési Hónap (opcionális)',
            'value_numeric': 'Számszerű Érték',
            'value_text': 'Szöveges Érték',
            'value_date': 'Dátum Érték',
            'value_file': 'Fájl Érték',
            'source_description': 'Adatforrás Leírása',
            'status': 'Státusz',
        }
        help_texts = {
            'period_month': 'Havi vagy negyedéves adatokhoz (1-12). Hagyd üresen éves adathoz.',
            'value_numeric': 'Csak akkor töltsd ki, ha az adatpont típusa "Szám".',
            'value_text': 'Csak akkor töltsd ki, ha az adatpont típusa "Szöveg".',
            'value_date': 'Csak akkor töltsd ki, ha az adatpont típusa "Dátum".',
            'value_file': 'Csak akkor töltsd ki, ha az adatpont típusa "Fájl".',
        }

    def __init__(self, *args, **kwargs):
        # A 'user' argumentumot a view-ból fogjuk átadni, de itt nem használjuk fel közvetlenül a form fieldjeiben
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)
        # Dinamikusan beállíthatnánk a vállalat (company) mezőt, ha a felhasználó csak egy céghez tartozik
        # Például:
        # if self.user and not self.user.is_superuser and hasattr(self.user, 'profile') and self.user.profile.company:
        #     self.fields['company'].queryset = CompanyProfile.objects.filter(pk=self.user.profile.company.pk)
        #     self.fields['company'].initial = self.user.profile.company
        #     self.fields['company'].disabled = True # Vagy widget=forms.HiddenInput()

        # TODO: Később hozzáadhatunk validációt, ami ellenőrzi, hogy a kitöltött 'value_...' mező
        #       megfelel-e a kiválasztott 'data_point' típusának.
        # TODO: A data_point queryset-jét is szűrhetnénk pl. kötelező/nem kötelező, vagy vállalat-specifikus adatpontokra.