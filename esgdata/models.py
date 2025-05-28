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
        blank=True,
        null=True,
        verbose_name="Opciócsoport Azonosító",
        help_text="Azonosító, ami összeköti ezt az opciót a releváns ESG adatponttal (pl. kérdőívben használt lista neve)."
    )
    # Kiegészítés: Érdemes lenne egy 'value' mezőt is felvenni, ha a tárolt érték más, mint a megjelenített szöveg.
    # Pl. value = models.CharField(max_length=100, blank=True, null=True)
    # Egyelőre a 'text' mezőre, vagy az opció ID-jára támaszkodunk.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.text} (Csoport: {self.group_identifier or 'N/A'})"

    class Meta:
        verbose_name = "Válaszlehetőség"
        verbose_name_plural = "Válaszlehetőségek"
        ordering = ['group_identifier', 'text']
        unique_together = ('group_identifier', 'text')
# === ÚJ MODELL VÉGE ===

class ESGDataPoint(models.Model):
    # ESG Pillér (Kategória)
    PILLAR_ENVIRONMENTAL = 'environmental'
    PILLAR_SOCIAL = 'social'
    PILLAR_GOVERNANCE = 'governance'
    PILLAR_GENERAL = 'general'  # Általános kérdésekhez
    PILLAR_CHOICES = [
        (PILLAR_ENVIRONMENTAL, 'Környezeti (E)'),
        (PILLAR_SOCIAL, 'Társadalmi (S)'),
        (PILLAR_GOVERNANCE, 'Irányítási (G)'),
        (PILLAR_GENERAL, 'Általános'),
    ]

    # Válasz Típusa (Adattípus)
    DATATYPE_TEXT = 'text'
    DATATYPE_NUMBER = 'number'
    DATATYPE_DATE = 'date'
    DATATYPE_BOOLEAN = 'boolean'
    DATATYPE_DROPDOWN = 'dropdown'
    DATATYPE_FILE = 'file'
    # DATATYPE_PERCENTAGE = 'percentage'
    # DATATYPE_CURRENCY = 'currency'

    DATATYPE_CHOICES = [
        (DATATYPE_TEXT, 'Szöveges kifejtés'),
        (DATATYPE_NUMBER, 'Szám'),
        (DATATYPE_DATE, 'Dátum'),
        (DATATYPE_BOOLEAN, 'Igen/Nem (Logikai)'),
        (DATATYPE_DROPDOWN, 'Legördülő lista (Választás)'),
        (DATATYPE_FILE, 'Fájl feltöltés'),
    ]

    question_number = models.CharField(
        max_length=30,
        db_index=True,
        verbose_name="Kérdés Sorszáma (kérdőívben)",
        help_text="Pl. Á.1.1.a, K.2.1"
    )
    question_text = models.TextField(verbose_name="Kérdés Szövege / Adatpont Leírása")

    pillar = models.CharField(
        max_length=20,
        choices=PILLAR_CHOICES,
        verbose_name="ESG Pillér"
    )

    esrs_topic_standard = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Kapcsolódó ESRS Topic Standard",
        help_text="Pl. ESRS E1, ESRS S1, ESRS G1"
    )
    esrs_datapoint_definition = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ESRS Adatpont Kód (pl. DR, AR)",
        help_text="Az ESRS által definiált adatpont azonosítója, ha van."
    )

    guidance = models.TextField(
        blank=True,
        null=True,
        verbose_name="Útmutató / Megjegyzés a kitöltéshez"
    )
    is_voluntary = models.BooleanField(default=False, verbose_name="Önkéntes Megválaszolású?")

    unit_of_measure = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Elvárt Mértékegység",
        help_text="Ha a válasz numerikus, pl. EUR, Fő, óra, kWh, tonna, m3"
    )
    response_data_type = models.CharField(
        max_length=20,
        choices=DATATYPE_CHOICES,
        default=DATATYPE_TEXT,
        verbose_name="Válasz Adattípusa"
    )

    # Kapcsolat a válaszlehetőségekhez, ha a response_data_type='dropdown'
    choice_option_group = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Válaszlehetőség Csoport Azonosító",
        help_text="A 'Válaszlehetőségek' táblában lévő csoportazonosító, ha a válasz típusa 'Legördülő'."
    )

    applies_to_questionnaire_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
        verbose_name="Releváns Kérdőív Típus(ok)",
        help_text="Pl. középváll_hu_egt_sv, nagyváll_egyeb. Vesszővel elválasztva több is lehet."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.question_number or '?'} - {self.question_text[:70]}{'...' if len(self.question_text) > 70 else ''}"

    class Meta:
        verbose_name = "ESG Adatpont (Kérdés)"
        verbose_name_plural = "ESG Adatpontok (Kérdések)"
        ordering = ['question_number', 'question_text']

class CompanyDataEntry(models.Model):
    STATUS_MISSING = 'missing'
    STATUS_FILLED = 'filled'
    STATUS_VERIFIED = 'verified'

    STATUS_CHOICES = [
        (STATUS_MISSING, 'Hiányzó'),
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
        company_name = self.company.name if self.company else "Ismeretlen vállalat"
        datapoint_name = self.data_point.name if self.data_point else "Ismeretlen adatpont"
        return f"{company_name} - {datapoint_name} ({self.period_year})"

    class Meta:
        verbose_name = "Vállalati ESG Adatbevitel"
        verbose_name_plural = "Vállalati ESG Adatbevitelek"
        ordering = ['-period_year', '-period_month', 'company', 'data_point']
        unique_together = ('company', 'data_point', 'period_year', 'period_month')