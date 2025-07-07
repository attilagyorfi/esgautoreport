# esgdata/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Questionnaire(models.Model):
    class CompanySize(models.TextChoices):
        MICRO = 'micro', _('Mikrovállalkozás')
        SMALL = 'small', _('Kisvállalkozás')
        MEDIUM = 'medium', _('Középvállalkozás')
        LARGE = 'large', _('Nagyvállalat')
    class Region(models.TextChoices):
        HU_EGT_SV = 'hu_egt_sv', _('Magyarország, EGT, Svájc')
        OECD = 'oecd', _('OECD')
        OTHER = 'other', _('Egyéb')
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Kérdőív neve"))
    company_size = models.CharField(max_length=10, choices=CompanySize.choices, verbose_name=_("Vállalatméret"))
    region = models.CharField(max_length=10, choices=Region.choices, verbose_name=_("Régió"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktív"))
    def __str__(self): return self.name
    class Meta:
        verbose_name = _("Kérdőív")
        verbose_name_plural = _("Kérdőívek")
        unique_together = ('company_size', 'region')

class EsgDataPoint(models.Model):
    class Pillar(models.TextChoices):
        ENVIRONMENTAL = 'E', _('Környezetvédelem')
        SOCIAL = 'S', _('Társadalom')
        GOVERNANCE = 'G', _('Vállalatirányítás')
    class AnswerType(models.TextChoices):
        CHOICE = 'choice', _('Választás (Igen/Nem)')
        TEXT = 'text', _('Szöveg')
        NUMBER = 'number', _('Szám')
        DATE = 'date', _('Dátum')
    question_id = models.CharField(max_length=20, unique=True, verbose_name=_("Kérdés egyedi azonosítója"))
    text = models.TextField(verbose_name=_("Kérdés szövege"))
    pillar = models.CharField(max_length=1, choices=Pillar.choices, verbose_name=_("ESG Pillér"))
    answer_type = models.CharField(max_length=10, choices=AnswerType.choices, default=AnswerType.CHOICE, verbose_name=_("Válasz típusa"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktív"))
    questionnaires = models.ManyToManyField(Questionnaire, related_name='questions', verbose_name=_("Kérdőívek"))
 
    available_options = models.ManyToManyField('ChoiceOption', blank=True, verbose_name=_("Válaszlehetőségek"))

    def __str__(self): return f"{self.question_id}"
    class Meta:
        verbose_name = _("ESG Adatpont")
        verbose_name_plural = _("ESG Adatpontok")
        ordering = ['question_id']

class ChoiceOption(models.Model):
    """
    Előre definiált válaszlehetőség (pl. 'Igen', 'Nem').
    """
    text = models.CharField(max_length=100, unique=True, verbose_name=_("Válasz szövege"))

    def __str__(self):
        return self.text

    class Meta:
        verbose_name = _("Válaszlehetőség")
        verbose_name_plural = _("Válaszlehetőségek")

# ÚJ MODELL: A konkrét jelentést tárolja
class Report(models.Model):
    company = models.ForeignKey('companies.CompanyProfile', on_delete=models.CASCADE, verbose_name=_("Vállalat"))
    report_type = models.ForeignKey(Questionnaire, on_delete=models.CASCADE, verbose_name=_("Jelentés Típusa"))
    period_year = models.IntegerField(verbose_name=_("Érintett Év"))
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_("Létrehozta"))
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = _("Jelentés")
        verbose_name_plural = _("Jelentések")
        unique_together = ('company', 'report_type', 'period_year')
    def __str__(self):
        return f"{self.company.name} - {self.period_year} ({self.report_type.name})"

class CompanyDataEntry(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='entries', verbose_name=_("Jelentés"), null=True)
    data_point = models.ForeignKey(EsgDataPoint, on_delete=models.CASCADE, verbose_name=_("Adatpont"))
    choice_option = models.ForeignKey(ChoiceOption, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Választott opció"))
    text_value = models.TextField(blank=True, null=True, verbose_name=_("Szöveges válasz"))
    numeric_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Számszerű válasz"))
    date_value = models.DateField(null=True, blank=True, verbose_name=_("Dátum válasz"))
    date_recorded = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name = _("Vállalati adatbejegyzés")
        verbose_name_plural = _("Vállalati adatbejegyzések")
        unique_together = ('report', 'data_point')