# accounts/models.py
from django.db import models
from django.contrib.auth.models import User  # A Django beépített User modellje
from companies.models import CompanyProfile

# Kérdőív típus választási lehetőségek (egyezzenek a dashboard/forms.py-val!)
QUESTIONNAIRE_TYPE_CHOICES_FOR_PROFILE = [
    ('', 'Nincs kiválasztva'),
    ('sztfh_sajat_teljes', 'Saját Vállalat Teljes ESG Kérdőíve (SZTFH)'),
    ('sztfh_nagyvall_hu_egt_ch', 'Beszállító: Nagyvállalat (HU, EGT, CH)'),
    ('sztfh_kozepvall_hu_egt_ch', 'Beszállító: Középvállalkozás (HU, EGT, CH)'),
    # ... folytasd a dashboard/forms.py-ban definiált összes típussal ...
]

class UserProfile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_ESG_FELELOS = 'esg_felelos'
    ROLE_MUNKAVALLALO = 'munkavallalo'
    ROLE_TANACSADO = 'tanacsado'
    ROLE_PENDING_APPROVAL = 'pending'  # Új szerepkör a jóváhagyásra váróknak

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Adminisztrátor'),
        (ROLE_ESG_FELELOS, 'ESG Felelős'),
        (ROLE_MUNKAVALLALO, 'Munkavállaló'),
        (ROLE_TANACSADO, 'Tanácsadó'),
        (ROLE_PENDING_APPROVAL, 'Jóváhagyásra vár'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Felhasználó", related_name="profile")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PENDING_APPROVAL, verbose_name="Szerepkör")
    company = models.ForeignKey(CompanyProfile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vállalat", related_name="user_profiles")

    # === ÚJ MEZŐK KEZDETE ===
    primary_questionnaire_type = models.CharField(
        max_length=50,
        choices=QUESTIONNAIRE_TYPE_CHOICES_FOR_PROFILE,
        blank=True,
        null=True,
        verbose_name="Elsődleges Kérdőív Típus",
        help_text="A felhasználó által kiválasztott fő kérdőív/kontextus."
    )
    profile_setup_complete = models.BooleanField(
        default=False,
        verbose_name="Profilbeállítás Befejezve",
        help_text="Jelzi, hogy a felhasználó elvégezte-e a kezdeti cégadatok megadását."
    )
    # === ÚJ MEZŐK VÉGE ===

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítva")

    def __str__(self):
        return f"{self.user.username} Profilja ({self.get_role_display()})"

    class Meta:
        verbose_name = "Felhasználói Profil"
        verbose_name_plural = "Felhasználói Profilok"