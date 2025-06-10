# esgdata/forms.py
from django import forms
from .models import CompanyDataEntry, ESGDataPoint
from companies.models import CompanyProfile
import datetime  # Szükséges az aktuális évhez

# 1. Régi CompanyDataEntryForm (ha a régi adatbeviteli nézet még használja)
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
        ]
        widgets = {
            'period_year': forms.NumberInput(attrs={'placeholder': 'ÉÉÉÉ'}),
            'period_month': forms.NumberInput(attrs={'placeholder': 'HH (1-12)'}),
            'value_date': forms.DateInput(attrs={'type': 'date'}),
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
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Itt lehet user-alapú szűrés vagy egyedi logika, ha szükséges

# 2. Új ESGReportCreationInitialForm (az "ESG Jelentés Készítése" oldalhoz)
class ESGReportCreationInitialForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all().order_by('name'),
        label="Vállalat",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Jelentési Év - Legördülő menü
    current_year = datetime.date.today().year
    YEAR_CHOICES = [(year, str(year)) for year in range(current_year - 10, current_year + 1)]

    period_year = forms.ChoiceField(
        label="Jelentési Év",
        choices=YEAR_CHOICES,
        initial=current_year,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    pillar = forms.ChoiceField(
        choices=ESGDataPoint.PILLAR_CHOICES,
        label="Jelentésrész Kiválasztása",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_superuser:
            if hasattr(self.user, 'profile') and self.user.profile.company:
                self.fields['company'].initial = self.user.profile.company
                self.fields['company'].queryset = CompanyProfile.objects.filter(pk=self.user.profile.company.pk)
        # Csökkenő sorrendben jelenjenek meg az évek (legfrissebb elöl)
        self.fields['period_year'].choices = sorted(self.YEAR_CHOICES, key=lambda x: x[0], reverse=True)
        self.fields['period_year'].initial = self.current_year