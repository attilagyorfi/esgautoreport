# accounts/models.py
from django.db import models
from django.contrib.auth.models import User
from companies.models import CompanyProfile
from .choices import QUESTIONNAIRE_TYPE_CHOICES  # Feltéve, hogy a choices.py-t már létrehoztad

import uuid  # <--- EZT A SORT KELL HOZZÁADNI VAGY ELLENŐRIZNI
from django.utils import timezone
import datetime

class UserProfile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_ESG_FELELOS = 'esg_felelos'
    ROLE_MUNKAVALLALO = 'munkavallalo'
    ROLE_TANACSADO = 'tanacsado'
    ROLE_PENDING_APPROVAL = 'pending'

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
    primary_questionnaire_type = models.CharField(
        max_length=50,
        choices=QUESTIONNAIRE_TYPE_CHOICES,
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítva")

    def __str__(self):
        return f"{self.user.username} Profilja ({self.get_role_display()})"

    class Meta:
        verbose_name = "Felhasználói Profil"
        verbose_name_plural = "Felhasználói Profilok"

class InvitationToken(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_USED = 'used'
    STATUS_EXPIRED = 'expired'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Aktív'),
        (STATUS_USED, 'Felhasznált'),
        (STATUS_EXPIRED, 'Lejárt'),
    ]

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Egyedi Token")
    email = models.EmailField(blank=True, null=True, verbose_name="Meghívott E-mail Címe (opcionális)", help_text="Ha meg van adva, csak ez az e-mail cím használhatja fel.")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_ACTIVE, verbose_name="Státusz")
    expires_at = models.DateTimeField(verbose_name="Lejárati Dátum")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_invitation_tokens", verbose_name="Létrehozta (Admin)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozás Ideje")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Utolsó Módosítás")

    def is_valid(self):
        return self.status == self.STATUS_ACTIVE and self.expires_at > timezone.now()

    def __str__(self):
        return f"Meghívó token: {self.token} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Regisztrációs Meghívó Token"
        verbose_name_plural = "Regisztrációs Meghívó Tokenek"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.pk and not getattr(self, 'expires_at', None):
            self.expires_at = timezone.now() + datetime.timedelta(days=7)
        super().save(*args, **kwargs)