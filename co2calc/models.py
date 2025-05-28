# co2calc/models.py
from django.db import models
from companies.models import CompanyProfile
from django.contrib.auth.models import User
from decimal import Decimal
import datetime

class ActivityType(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tevékenységtípus Neve", help_text="Pl. Földgáz égetés (telephelyi), Vásárolt villamos energia")
    description = models.TextField(blank=True, null=True, verbose_name="Leírás")

    # === ÚJ MEZŐ ===
    allowed_units = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Engedélyezett Mértékegységek",
        help_text="Vesszővel elválasztott lista az engedélyezett mértékegység kulcsokból (pl. kwh,kg,m3). Hagyd üresen, ha az alapértelmezett összes egység engedélyezett."
    )
    # === ÚJ MEZŐ VÉGE ===

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítva")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "CO₂ Tevékenységtípus"
        verbose_name_plural = "CO₂ Tevékenységtípusok"
        ordering = ['name']

class EmissionFactor(models.Model):
    name = models.CharField(max_length=255, verbose_name="Faktor Neve/Leírása", help_text="Pl. Földgáz (magas fűtőértékű) - DEFRA 2023")
    activity_type = models.ForeignKey(
        ActivityType,
        on_delete=models.PROTECT,
        verbose_name="Tevékenységtípus",
        help_text="Válaszd ki a tevékenységtípust, amire ez a faktor vonatkozik.",
        null=True,
        blank=True
    )
    UNIT_LITER = 'liter'
    UNIT_KWH = 'kWh'
    UNIT_KG = 'kg'
    UNIT_TONNE = 't'
    UNIT_M3 = 'm3'
    UNIT_CHOICES_FOR_FACTOR = [
        (UNIT_LITER, 'liter'),
        (UNIT_KWH, 'kWh (kilowattóra)'),
        (UNIT_KG, 'kg (kilogramm)'),
        (UNIT_TONNE, 't (tonna)'),
        (UNIT_M3, 'm³ (köbméter)'),
    ]
    unit_of_activity = models.CharField(max_length=20, choices=UNIT_CHOICES_FOR_FACTOR, db_index=True, verbose_name="Tevékenység Egysége")
    factor_value = models.DecimalField(max_digits=15, decimal_places=8, verbose_name="Emissziós Faktor Értéke")
    FACTOR_UNIT_KG_CO2E = 'kg_co2e'
    FACTOR_UNIT_T_CO2E = 't_co2e'
    EMISSION_UNIT_CHOICES = [
        (FACTOR_UNIT_KG_CO2E, 'kg CO₂e'),
        (FACTOR_UNIT_T_CO2E, 't CO₂e'),
    ]
    emission_unit_numerator = models.CharField(max_length=10, choices=EMISSION_UNIT_CHOICES, default=FACTOR_UNIT_KG_CO2E, verbose_name="Kibocsátás Egysége (Számláló)")
    source = models.CharField(max_length=100, verbose_name="Faktor Forrása")
    year_of_factor = models.IntegerField(verbose_name="Faktor Érvényességi Éve")
    notes = models.TextField(blank=True, null=True, verbose_name="Megjegyzések")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítva")

    def get_full_factor_unit(self):
        return f"{self.get_emission_unit_numerator_display()} / {self.get_unit_of_activity_display()}"
    get_full_factor_unit.short_description = "Faktor Mértékegysége"

    def __str__(self):
        return f"{self.name} ({self.factor_value} {self.get_full_factor_unit()})"

    class Meta:
        verbose_name = "Emissziós Faktor"
        verbose_name_plural = "Emissziós Faktorok"
        ordering = ['name', '-year_of_factor']
        unique_together = (('activity_type', 'unit_of_activity', 'source', 'year_of_factor'),)

class CO2CalculationInput(models.Model):
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, verbose_name="Vállalat", related_name="co2_inputs")
    activity_type = models.ForeignKey(ActivityType, on_delete=models.PROTECT, verbose_name="Tevékenység Típusa", help_text="Válassz a listából.", null=True, blank=True)

    current_year = datetime.date.today().year
    YEAR_CHOICES = [(y, str(y)) for y in range(current_year - 10, current_year + 6)] 
    period_year = models.IntegerField(choices=YEAR_CHOICES, default=current_year, verbose_name="Jelentési Év")

    MONTH_CHOICES = [(m, str(m)) for m in range(1, 13)]
    period_month = models.IntegerField(choices=MONTH_CHOICES, verbose_name="Jelentési Hónap (1-12)", blank=False, null=False, help_text="Válaszd ki a jelentési hónapot.")

    quantity = models.DecimalField(max_digits=12, decimal_places=4, verbose_name="Mennyiség")

    UNIT_LITER = 'liter'; UNIT_KWH = 'kWh'; UNIT_KG = 'kg'; UNIT_TONNE = 't'; UNIT_M3 = 'm3'
    UNIT_CHOICES = [
        (UNIT_LITER, 'liter'),
        (UNIT_KWH, 'kWh (kilowattóra)'),
        (UNIT_KG, 'kg (kilogramm)'),
        (UNIT_TONNE, 't (tonna)'),
        (UNIT_M3, 'm³ (köbméter)'),
    ]
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, verbose_name="Mértékegység")

    # === MÓDOSÍTOTT MEZŐ ===
    emission_factor = models.ForeignKey(
        EmissionFactor,
        on_delete=models.SET_NULL,  # Ha egy EmissionFactor törlődik, itt NULL lesz, nem törli a CO2Input-ot
        null=True,
        blank=True,
        verbose_name="Kiválasztott Emissziós Faktor (felülíráshoz)",
        help_text="Válassz egy konkrét faktort a listából, vagy hagyd üresen az automatikus kereséshez."
    )
    # === MÓDOSÍTOTT MEZŐ VÉGE ===

    calculated_co2e = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True, verbose_name="Kiszámított CO₂e (t)", help_text="A kalkuláció eredménye tonna CO₂ ekvivalensben. Ezt a rendszer tölti ki.")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Módosítva")

    # A save() metódust később kell majd frissíteni, hogy ezt az új FK mezőt használja!
    def save(self, *args, **kwargs):
        numeric_factor_value = None  # A számításhoz használt numerikus faktorérték
        factor_emission_unit = None  # A felhasznált faktor kibocsátási egysége (pl. kg_co2e)

        if self.quantity is None:
            self.calculated_co2e = None
            super().save(*args, **kwargs)
            return

        if self.emission_factor:
            # Manuálisan kiválasztott EmissionFactor rekord
            selected_ef_object = self.emission_factor
            numeric_factor_value = selected_ef_object.factor_value
            factor_emission_unit = selected_ef_object.emission_unit_numerator
        else:
            # Automatikus keresés
            if self.activity_type and self.unit and self.period_year:
                suitable_factors = EmissionFactor.objects.filter(
                    activity_type=self.activity_type,
                    unit_of_activity=self.unit,
                    year_of_factor__lte=self.period_year
                ).order_by('-year_of_factor')

                if suitable_factors.exists():
                    found_factor_object = suitable_factors.first()
                    numeric_factor_value = found_factor_object.factor_value
                    factor_emission_unit = found_factor_object.emission_unit_numerator

        # Számítás elvégzése, ha van mivel
        if self.quantity is not None and numeric_factor_value is not None and factor_emission_unit is not None:
            calculated_value_raw = self.quantity * numeric_factor_value

            if factor_emission_unit == EmissionFactor.FACTOR_UNIT_KG_CO2E:
                self.calculated_co2e = calculated_value_raw / Decimal('1000.0')
            elif factor_emission_unit == EmissionFactor.FACTOR_UNIT_T_CO2E:
                self.calculated_co2e = calculated_value_raw
            else:
                self.calculated_co2e = None
        else:
            self.calculated_co2e = None

        super().save(*args, **kwargs)

    def __str__(self):
        company_name = self.company.name if self.company else "Ismeretlen vállalat"
        activity_display = self.activity_type.name if self.activity_type else "N/A Tevékenység"
        return f"{company_name} - {activity_display} ({self.period_year}{f'-{self.period_month:02d}' if self.period_month else ''})"

    class Meta:
        verbose_name = "CO₂ Kalkulátor Bemeneti Adat"
        verbose_name_plural = "CO₂ Kalkulátor Bemeneti Adatok"
        ordering = ['-period_year', '-period_month', 'company', 'activity_type']
        # unique_together-t egyelőre nem módosítjuk, de ha az activity_type FK lesz, akkor az is az FK-ra kell vonatkozzon