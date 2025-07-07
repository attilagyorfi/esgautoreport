# companies/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class TEORCode(models.Model):
    code = models.CharField(max_length=10, unique=True, verbose_name=_("TEÁOR Kód"), help_text="Pl. 01.11, 62.01")
    name = models.CharField(max_length=255, verbose_name=_("TEÁOR Megnevezés"))
    # Később hozzáadhatunk hierarchiát vagy csoportosítást, ha szükséges

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = _("TEÁOR Kód")
        verbose_name_plural = _("TEÁOR Kódok")
        ordering = ['code']

class CompanyProfile(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Vállalat neve"))

    # 1. A régi 'industry' mezőt átnevezzük, és nullable-re állítjuk
    industry_old_char = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("Iparág (Régi Szöveges)")
    )

    # 2. Hozzáadjuk az új 'industry' mezőt ForeignKey-ként
    industry = models.ForeignKey(
        TEORCode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Iparág (TEÁOR)")
    )

    # Az új címmezők
    address_country = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Ország"))
    address_postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("Irányítószám"))
    address_city = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Város"))
    address_street_and_number = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Utca, házszám, emelet, ajtó stb."))

    # Meglévő/új egyéb mezők
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Adószám"))
    registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Cégjegyzékszám"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Létrehozta"))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Létrehozva"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Módosítva"))
    
    # TÖRÖLT MEZŐK: number_of_employees, reporting_period_start_date, régi 'address' TextField

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Vállalati Profil")
        verbose_name_plural = _("Vállalati Profilok")
        ordering = ['name']