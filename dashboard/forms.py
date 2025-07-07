# dashboard/forms.py
from django import forms
from companies.models import CompanyProfile

class CompanySelectionForm(forms.Form):
    """
    Űrlap, amely lehetővé teszi a felhasználó számára, hogy kiválassza
    vagy létrehozzon egy vállalatot és hozzárendelje a profiljához.
    """
    company = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all(),
        label="Válasszon egy meglévő vállalatot",
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    new_company_name = forms.CharField(
        label="Vagy adjon meg egy új vállalatnevet",
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pl. Minta Kft.'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get("company")
        new_company_name = cleaned_data.get("new_company_name")

        if not company and not new_company_name:
            raise forms.ValidationError("Kérjük, válasszon egy meglévő vállalatot, vagy adjon meg egy újat!")

        if company and new_company_name:
            raise forms.ValidationError("Kérjük, csak az egyik opciót válassza: vagy egy meglévőt, vagy egy újat!")

        return cleaned_data

    def save(self):
        company = self.cleaned_data.get("company")
        new_company_name = self.cleaned_data.get("new_company_name")

        if new_company_name:
            # Létrehozzuk az új vállalatot a 'created_by' mezővel
            company = CompanyProfile.objects.create(name=new_company_name, created_by=self.user)

        # Hozzárendeljük a vállalatot a felhasználó profiljához
        user_profile = self.user.profile
        user_profile.company = company
        user_profile.save()