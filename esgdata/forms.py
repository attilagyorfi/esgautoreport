# esgdata/forms.py
from django import forms
from companies.models import CompanyProfile
import datetime
from django.utils.translation import gettext_lazy as _

# A jelentéstípusok, amelyeket a felhasználó választhat.
# A kulcsok (pl. 'sztfh_mikrovall_hu_egt_ch') fognak összekapcsolódni
# az adatbázisban a kérdésekkel.
QUESTIONNAIRE_TYPE_CHOICES = [
    ('', '--------- Kérjük, válasszon jelentéstípust ---------'),
    ('sztfh_nagyvall_hu_egt_ch', _('Nagyvállalkozás - EGT és Svájc')),
    ('sztfh_nagyvall_oecd_non_hu', _('Nagyvállalkozás - OECD')),
    ('sztfh_nagyvall_other', _('Nagyvállalkozás - Egyéb')),
    ('sztfh_kozepvall_hu_egt_ch', _('Középvállalkozás - EGT és Svájc')),
    ('sztfh_kozepvall_oecd_non_hu', _('Középvállalkozás - OECD')),
    ('sztfh_kozepvall_other', _('Középvállalkozás - Egyéb')),
    ('sztfh_kisvall_hu_egt_ch', _('Kisvállalkozás - EGT és Svájc')),
    ('sztfh_kisvall_oecd_non_hu', _('Kisvállalkozás - OECD')),
    ('sztfh_kisvall_other', _('Kisvállalkozás - Egyéb')),
    ('sztfh_mikrovall_hu_egt_ch', _('Mikrovállalkozás - EGT és Svájc')),
    ('sztfh_mikrovall_oecd_non_hu', _('Mikrovállalkozás - OECD')),
    ('sztfh_mikrovall_other', _('Mikrovállalkozás - Egyéb')),
]

class ESGReportCreationInitialForm(forms.Form):
    company = forms.ModelChoiceField(
        queryset=CompanyProfile.objects.all().order_by('name'),
        label="Vállalat",
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    
    # Jelentési év legördülő menü
    current_year = datetime.date.today().year
    YEAR_CHOICES = sorted([(year, str(year)) for year in range(current_year - 5, current_year + 1)], key=lambda x: x[0], reverse=True)
    
    period_year = forms.ChoiceField(
        label="Jelentési Év",
        choices=YEAR_CHOICES,
        initial=current_year,
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )
    
    # Az új, egyesített legördülő menü a jelentéstípusokhoz
    report_type = forms.ChoiceField(
        choices=QUESTIONNAIRE_TYPE_CHOICES,
        label="Jelentés Kiválasztása",
        widget=forms.Select(attrs={'class': 'form-select mb-3'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and not self.user.is_superuser:
            if hasattr(self.user, 'profile') and self.user.profile.company:
                self.fields['company'].initial = self.user.profile.company
                self.fields['company'].queryset = CompanyProfile.objects.filter(pk=self.user.profile.company.pk)
        
        self.fields['period_year'].initial = self.current_year