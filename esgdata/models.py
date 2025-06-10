# esgdata/models.py
from django.db import models
from django.contrib.auth.models import User  # Szükséges a CompanyDataEntry.entered_by mezőhöz
from companies.models import CompanyProfile # Szükséges a CompanyDataEntry.company mezőhöz

# === ÚJ MODELL KEZDETE ===
class ChoiceOption(models.Model):
    text = models.CharField(max_length=500, verbose_name="Opció Szövege")
    group_identifier = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Opciócsoport Azonosító (SZTFH)",
        help_text="Azonosító a 'Legördülő lista' Excelből, ami összeköti ezt az opciócsoportot a releváns ESG adatponttal."
    )
    # order = models.IntegerField(default=0, verbose_name="Sorrend") # Ha a sorrend fontos, ezt aktiváld

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text} (Csoport: {self.group_identifier})"

    class Meta:
        verbose_name = "Válaszlehetőség (Kérdőívhez)"
        verbose_name_plural = "Válaszlehetőségek (Kérdőívhez)"
        ordering = ['group_identifier', 'text']  # vagy ['group_identifier', 'order'] ha sorrend is van
        unique_together = ('group_identifier', 'text')
# === ÚJ MODELL VÉGE ===

class ESGDataPoint(models.Model):
    # ESG Pillér (Kategória)
    PILLAR_ENVIRONMENTAL = 'environmental'
    PILLAR_SOCIAL = 'social'
    PILLAR_GOVERNANCE = 'governance'
    PILLAR_GENERAL = 'general'  # Általános kérdésekhez (megmaradhat, vagy az Adatlap kiválthatja)
    PILLAR_DATASHEET = 'datasheet'  # ÚJ: Adatlap
    PILLAR_GHG_TARGETS = 'ghg_targets'  # ÚJ: ÜHG Célok

    PILLAR_CHOICES = [
        (PILLAR_ENVIRONMENTAL, 'Környezeti (E)'),
        (PILLAR_SOCIAL, 'Társadalmi (S)'),
        (PILLAR_GOVERNANCE, 'Irányítási (G)'),
        (PILLAR_DATASHEET, 'Általános Vállalati Adatlap'),  # ÚJ
        (PILLAR_GHG_TARGETS, 'ÜHG Emissziós Célok'),        # ÚJ
        (PILLAR_GENERAL, 'Egyéb Általános Adatok'),         # Esetleg átnevezve, ha az Adatlap nem fedi le teljesen
    ]

    # Válasz Típusa (Adattípus)
    DATATYPE_TEXT = 'text_long'
    DATATYPE_SHORT_TEXT = 'text_short'
    DATATYPE_NUMBER = 'number'
    DATATYPE_DATE = 'date'
    DATATYPE_BOOLEAN = 'boolean'
    DATATYPE_DROPDOWN = 'dropdown'
    DATATYPE_FILE = 'file'
    DATATYPE_YEAR = 'year'
    DATATYPE_PERCENTAGE = 'percentage'
    DATATYPE_CURRENCY_EUR = 'currency_eur'
    DATATYPE_CURRENCY_HUF = 'currency_huf'

    DATATYPE_CHOICES = [
        (DATATYPE_TEXT, 'Hosszú szöveges válasz'),
        (DATATYPE_SHORT_TEXT, 'Rövid szöveges válasz'),
        (DATATYPE_NUMBER, 'Szám'),
        (DATATYPE_YEAR, 'Évszám'),
        (DATATYPE_PERCENTAGE, 'Százalék'),
        (DATATYPE_CURRENCY_EUR, 'Pénznem (EUR)'),
        (DATATYPE_CURRENCY_HUF, 'Pénznem (HUF)'),
        (DATATYPE_DATE, 'Dátum'),
        (DATATYPE_BOOLEAN, 'Igen/Nem'),
        (DATATYPE_DROPDOWN, 'Legördülő lista'),
        (DATATYPE_FILE, 'Fájl feltöltés'),
    ]

    questionnaire_version = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name="Kérdőív Verzió Azonosító",
        help_text="Azonosító, melyik SZTFH kérdőívből származik, pl. 'kozepvall_hu_egt_ch_v1'"
    )
    question_number = models.CharField(
        max_length=30,
        db_index=True,
        verbose_name="Kérdés Sorszáma"
    )
    question_text = models.TextField(verbose_name="Kérdés Szövege")
    pillar = models.CharField(
        max_length=20,  # Lehet, hogy ezt növelni kell, ha hosszabb kulcsokat használunk (pl. 'environmental')
        choices=PILLAR_CHOICES,
        verbose_name="Jelentésrész Kiválasztása"  # Átnevezzük a verbose_name-t
    )

    esrs_topic_standard = models.CharField(max_length=100, blank=True, null=True, verbose_name="ESRS Topic Standard")
    esrs_datapoint_definition = models.CharField(max_length=100, blank=True, null=True, verbose_name="ESRS Adatpont Definíció")

    guidance = models.TextField(blank=True, null=True, verbose_name="Útmutató/Megjegyzés")
    is_voluntary = models.BooleanField(default=False, verbose_name="Önkéntes")

    unit_of_measure = models.CharField(max_length=100, blank=True, null=True, verbose_name="Elvárt Mértékegység")
    response_data_type = models.CharField(
        max_length=30,
        choices=DATATYPE_CHOICES,
        default=DATATYPE_TEXT,
        verbose_name="Válasz Adattípusa"
    )

    choice_option_group = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Legördülő Lista Csoportkulcsa",
        help_text="Azonosító a 'Legördülő lista' Excelből, ha a válasz típusa 'Legördülő'."
    )

    applies_to_questionnaire_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Kérdőív Típus"
    )

    CONTEXT_SAJAT_JELENTO = 'sajat'
    CONTEXT_BESZALLITO = 'beszallito'
    CONTEXT_ALTALANOS = 'altalanos'  # Ha nem specifikus
    CONTEXT_CHOICES = [
        (CONTEXT_ALTALANOS, 'Általános (nem specifikus)'),
        (CONTEXT_SAJAT_JELENTO, 'Saját Jelentő Adatlapja'),
        (CONTEXT_BESZALLITO, 'Beszállítói Adatlap'),
    ]
    adatlap_kontextus = models.CharField(
        max_length=20,
        choices=CONTEXT_CHOICES,
        default=CONTEXT_ALTALANOS,
        verbose_name="Adatlap Kontextusa",
        blank=True, null=True  # Lehet null, ha nem adatlap típusú kérdés
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    placeholder_text = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Placeholder szöveg az input mezőhöz"
    )

    def __str__(self):
        return f"{self.questionnaire_version} - {self.question_number} - {self.question_text[:70]}{'...' if len(self.question_text) > 70 else ''}"

    class Meta:
        verbose_name = "ESG Kérdés (Adatpont)"
        verbose_name_plural = "ESG Kérdések (Adatpontok)"
        ordering = ['questionnaire_version', 'question_number']
        unique_together = ('questionnaire_version', 'question_number')

    def get_choice_options(self):
        if self.response_data_type == self.DATATYPE_DROPDOWN and self.choice_option_group:
            return ChoiceOption.objects.filter(group_identifier=self.choice_option_group).order_by('text')
        return ChoiceOption.objects.none()

class CompanyDataEntry(models.Model):
    STATUS_MISSING = 'missing'
    STATUS_FILLED = 'filled'
    STATUS_VERIFIED = 'verified'
    STATUS_IN_PROGRESS = 'in_progress'  # <<< ÚJ STÁTUSZ

    STATUS_CHOICES = [
        (STATUS_MISSING, 'Hiányzó'),
        (STATUS_IN_PROGRESS, 'Folyamatban'),  # <<< ÚJ OPCIÓ
        (STATUS_FILLED, 'Kitöltött'),
        (STATUS_VERIFIED, 'Ellenőrzött'),
    ]

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, verbose_name="Vállalat", related_name="data_entries")
    data_point = models.ForeignKey(ESGDataPoint, on_delete=models.PROTECT, verbose_name="ESG Adatpont", related_name="entries")
    
    period_year = models.IntegerField(verbose_name="Év")
    period_month = models.IntegerField(blank=True, null=True, verbose_name="Hónap (opcionális)", help_text="Havi vagy negyedéves adatokhoz (1-12)")
    
    value_numeric = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, verbose_name="Számszerű érték")
    value_text = models.TextField(blank=True, null=True, verbose_name="Szöveges érték")
    value_date = models.DateField(blank=True, null=True, verbose_name="Dátum érték")
    value_file = models.FileField(upload_to='esg_data_files/%Y/%m/', blank=True, null=True, verbose_name="Fájl érték") 
    
    source_description = models.TextField(blank=True, null=True, verbose_name="Adatforrás leírása")
    entered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Rögzítette")
    entry_date = models.DateTimeField(auto_now_add=True, verbose_name="Rögzítés dátuma")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_MISSING, verbose_name="Státusz")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva (rendszer)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítva (rendszer)")

    def __str__(self):
        company_name = self.company.name if self.company else "Ismeretlen cég"
        # Módosítsd 'self.data_point.name'-ről 'self.data_point.question_text'-re
        datapoint_name = self.data_point.question_text if self.data_point else "Ismeretlen adatpont"
        return f"Adatbevitel: {company_name} - {datapoint_name[:50]}..." # Levágjuk, hogy ne legyen túl hosszú

    class Meta:
        verbose_name = "Vállalati ESG Adatbevitel"
        verbose_name_plural = "Vállalati ESG Adatbevitelek"
        ordering = ['-period_year', '-period_month', 'company', 'data_point']
        unique_together = ('company', 'data_point', 'period_year', 'period_month')