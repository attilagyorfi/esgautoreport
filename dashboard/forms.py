# dashboard/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from companies.models import TEORCode
from accounts.choices import QUESTIONNAIRE_TYPE_CHOICES

COMPANY_SIZE_CHOICES = [
    ('', _('Mindegyik méret')),
    ('mikrovall', _('Mikrovállalkozás')),
    ('kisvall', _('Kisvállalkozás')),
    ('kozepvall', _('Középvállalkozás')),
    ('nagyvall', _('Nagyvállalat')),
]

class CompanyAndQuestionnaireSelectForm(forms.Form):
    company_name = forms.CharField(
        label=_("Vállalat Hivatalos Neve"), 
        max_length=255, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pl. Minta Kft.'})
    )
    tax_number = forms.CharField(
        label=_("Adószám"), 
        max_length=50, 
        required=True, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pl. 12345678-1-23'})
    )
    registration_number = forms.CharField(
        label=_("Cégjegyzékszám"),
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pl. 01-09-123456'})
    )
    address = forms.CharField(
        label=_("Székhely / Hivatalos Cím"), 
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Pl. 1234 Budapest, Minta utca 10.'}),
        required=False
    )
    questionnaire_type = forms.ChoiceField(
        label=_("Kitöltendő Kérdőív Típusa"),
        choices=QUESTIONNAIRE_TYPE_CHOICES,  # <--- ITT HASZNÁLD AZ IMPORTÁLT VÁLTOZÓT
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None) 
        super().__init__(*args, **kwargs)

        if self.user and self.user.is_authenticated and hasattr(self.user, 'profile') and self.user.profile and self.user.profile.company:
            company_profile = self.user.profile.company
            self.fields['company_name'].initial = company_profile.name
            if hasattr(company_profile, 'tax_number') and company_profile.tax_number:
                self.fields['tax_number'].initial = company_profile.tax_number
            if hasattr(company_profile, 'registration_number') and company_profile.registration_number:
                self.fields['registration_number'].initial = company_profile.registration_number
            if hasattr(company_profile, 'address') and company_profile.address:
                self.fields['address'].initial = company_profile.address

        if self.user and self.user.is_authenticated and hasattr(self.user, 'profile') and self.user.profile and self.user.profile.primary_questionnaire_type:
            self.fields['questionnaire_type'].initial = self.user.profile.primary_questionnaire_type

class CompanyFilterForm(forms.Form):
    teor_code = forms.ModelChoiceField(
        queryset=TEORCode.objects.all().order_by('name'),
        required=False,
        label=_("TEÁOR Szerint"),
        empty_label=_("Összes TEÁOR kód"),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm mb-2'})
    )
    company_size_filter = forms.ChoiceField(
        choices=COMPANY_SIZE_CHOICES,
        required=False,
        label=_("Cégméret Szerint"),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm mb-2'})
    )
    tax_number_search = forms.CharField(
        required=False,
        label=_("Adószám Keresés"),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm mb-2', 'placeholder': 'Adószám...'})
    )