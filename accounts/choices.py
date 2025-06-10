# ESGAutoReport/accounts/choices.py
from django.utils.translation import gettext_lazy as _

QUESTIONNAIRE_TYPE_CHOICES = [
    ('', '--------- Kérjük, válasszon kérdőív típust! ---------'),
    ('sztfh_sajat_teljes', _('Saját Vállalat Teljes ESG Kérdőíve (SZTFH alapján)')),
    # A 12 szállítói kategória az SZTFH rendelet 4. § (10) alapján:
    ('sztfh_nagyvall_hu_egt_ch', _('Beszállító: Nagyvállalat (HU, EGT, CH)')),
    ('sztfh_kozepvall_hu_egt_ch', _('Beszállító: Középvállalkozás (HU, EGT, CH)')),
    ('sztfh_kisvall_hu_egt_ch', _('Beszállító: Kisvállalkozás (HU, EGT, CH)')),
    ('sztfh_mikrovall_hu_egt_ch', _('Beszállító: Mikrovállalkozás (HU, EGT, CH)')),
    ('sztfh_nagyvall_oecd_non_hu', _('Beszállító: Nagyvállalat (OECD, nem HU/EGT/CH)')),
    ('sztfh_kozepvall_oecd_non_hu', _('Beszállító: Középvállalkozás (OECD, nem HU/EGT/CH)')),
    ('sztfh_kisvall_oecd_non_hu', _('Beszállító: Kisvállalkozás (OECD, nem HU/EGT/CH)')),
    ('sztfh_mikrovall_oecd_non_hu', _('Beszállító: Mikrovállalkozás (OECD, nem HU/EGT/CH)')),
    ('sztfh_nagyvall_other', _('Beszállító: Nagyvállalat (Egyéb ország)')),
    ('sztfh_kozepvall_other', _('Beszállító: Középvállalkozás (Egyéb ország)')),
    ('sztfh_kisvall_other', _('Beszállító: Kisvállalkozás (Egyéb ország)')),
    ('sztfh_mikrovall_other', _('Beszállító: Mikrovállalkozás (Egyéb ország)')),
]