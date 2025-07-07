# companies/forms.py
from django import forms
from .models import CompanyProfile, TEORCode

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        # Itt soroljuk fel a mezőket, amiket a felhasználó szerkeszthet
        fields = [
            'name', 'industry', 'tax_number', 'registration_number',
            'address_country', 'address_postal_code', 'address_city', 
            'address_street_and_number'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.Select(attrs={'class': 'form-select'}),
            'tax_number': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_country': forms.TextInput(attrs={'class': 'form-control'}),
            'address_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'address_city': forms.TextInput(attrs={'class': 'form-control'}),
            'address_street_and_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': "Vállalat neve",
            'industry': "Iparág (TEÁOR)",
            'tax_number': "Adószám",
            'registration_number': "Cégjegyzékszám",
            'address_country': "Ország",
            'address_postal_code': "Irányítószám",
            'address_city': "Város",
            'address_street_and_number': "Utca, házszám",
        }