# dashboard/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _ # Fordításhoz

# Ezeknek a kulcsoknak és értékeknek konzisztensnek kell lenniük azzal,
# amit az UserProfile modell 'primary_questionnaire_type' mezőjének choices-ában,
# és az ESGDataPoint modell 'applies_to_questionnaire_type' mezőjében használni fogunk.
# Érdemes lehet ezeket egy központi helyre (pl. egy choices.py fájlba) kiszervezni később.
QUESTIONNAIRE_TYPE_CHOICES = [
    ('', '--------- Kérjük, válasszon kérdőív típust! ---------'),
    ('sztfh_sajat_teljes', 'Saját Vállalat Teljes ESG Kérdőíve (SZTFH alapján)'),
    # A 12 szállítói kategória az SZTFH rendelet 4. § (10) alapján:
    ('sztfh_nagyvall_hu_egt_ch', 'Beszállító: Nagyvállalat (HU, EGT, CH)'),
    ('sztfh_kozepvall_hu_egt_ch', 'Beszállító: Középvállalkozás (HU, EGT, CH)'),
    ('sztfh_kisvall_hu_egt_ch', 'Beszállító: Kisvállalkozás (HU, EGT, CH)'),
    ('sztfh_mikrovall_hu_egt_ch', 'Beszállító: Mikrovállalkozás (HU, EGT, CH)'),
    ('sztfh_nagyvall_oecd_non_hu', 'Beszállító: Nagyvállalat (OECD, nem HU/EGT/CH)'),
    ('sztfh_kozepvall_oecd_non_hu', 'Beszállító: Középvállalkozás (OECD, nem HU/EGT/CH)'),
    ('sztfh_kisvall_oecd_non_hu', 'Beszállító: Kisvállalkozás (OECD, nem HU/EGT/CH)'),
    ('sztfh_mikrovall_oecd_non_hu', 'Beszállító: Mikrovállalkozás (OECD, nem HU/EGT/CH)'),
    ('sztfh_nagyvall_other', 'Beszállító: Nagyvállalat (Egyéb ország)'),
    ('sztfh_kozepvall_other', 'Beszállító: Középvállalkozás (Egyéb ország)'),
    ('sztfh_kisvall_other', 'Beszállító: Kisvállalkozás (Egyéb ország)'),
    ('sztfh_mikrovall_other', 'Beszállító: Mikrovállalkozás (Egyéb ország)'),
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
        required=False, # Ez legyen opcionális, ha nem minden esetben van
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Pl. 01-09-123456'})
    )
    address = forms.CharField(
        label=_("Székhely / Hivatalos Cím"), 
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Pl. 1234 Budapest, Minta utca 10.'}),
        required=False # Ez is legyen opcionális
    )
    questionnaire_type = forms.ChoiceField(
        label=_("Kitöltendő Kérdőív Típusa"), 
        choices=QUESTIONNAIRE_TYPE_CHOICES, 
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        # A 'user' argumentumot a nézetből (view) fogjuk átadni,
        # hogy elő tudjuk tölteni az űrlapot a felhasználó meglévő cégadataival, ha vannak.
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