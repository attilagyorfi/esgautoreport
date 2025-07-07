# esgdata/forms.py
from django import forms
from .models import Questionnaire
from companies.models import CompanyProfile
import datetime

class ReportSelectionForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all(),
        label="Vállalat",
        # JAVÍTÁS: Stílusosztály hozzáadása a widgethez
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    current_year = datetime.date.today().year
    YEAR_CHOICES = [(year, year) for year in range(current_year - 5, current_year + 1)]
    
    period_year = forms.ChoiceField(
        choices=YEAR_CHOICES,
        initial=current_year,
        label="Jelentési Év",
        # JAVÍTÁS: Stílusosztály hozzáadása a widgethez
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    report_type = forms.ModelChoiceField(
        queryset=Questionnaire.objects.filter(is_active=True),
        label="Kérdőív Típusa",
        # JAVÍTÁS: Stílusosztály hozzáadása a widgethez
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Válassza ki a vállalat méretének és régiójának megfelelő kérdőívet."
    )