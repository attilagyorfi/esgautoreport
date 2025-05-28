# reports/models.py
from django.db import models
from django.contrib.auth.models import User
from companies.models import CompanyProfile

class ReportGenerationRequest(models.Model):
    REPORT_TYPE_ANNUAL = 'annual'
    REPORT_TYPE_QUARTERLY = 'quarterly'
    REPORT_TYPE_MONTHLY = 'monthly'

    REPORT_TYPE_CHOICES = [
        (REPORT_TYPE_ANNUAL, 'Éves'),
        (REPORT_TYPE_QUARTERLY, 'Negyedéves'),
        (REPORT_TYPE_MONTHLY, 'Havi'),
    ]

    STATUS_REQUESTED = 'requested'
    STATUS_PROCESSING = 'processing'
    STATUS_COMPLETED = 'completed'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = [
        (STATUS_REQUESTED, 'Kérvényezve'),
        (STATUS_PROCESSING, 'Folyamatban'),
        (STATUS_COMPLETED, 'Elkészült'),
        (STATUS_ERROR, 'Hiba'),
    ]

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, verbose_name="Vállalat", related_name="report_requests")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE_CHOICES, verbose_name="Jelentés Típusa")
    period_year = models.IntegerField(verbose_name="Jelentési Év")
    period_quarter_or_month = models.IntegerField(blank=True, null=True, verbose_name="Jelentési Negyedév/Hónap", help_text="Negyedéves (1-4) vagy havi (1-12) jelentés esetén")

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kérvényezte", related_name="report_requests_made")
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Kérvényezés Ideje")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED, verbose_name="Státusz")

    # A fájlnevekhez az upload_to egyedi mappákat generálhatna a kérés ID-ja alapján,
    # de egyelőre egyszerűbb, közös mappát használunk.
    generated_pdf_path = models.FileField(upload_to='generated_reports/pdf/%Y/%m/', blank=True, null=True, verbose_name="Generált PDF elérési útja")
    generated_excel_path = models.FileField(upload_to='generated_reports/excel/%Y/%m/', blank=True, null=True, verbose_name="Generált Excel elérési útja")

    # created_at és updated_at mezőket is hozzáadhatnánk, ha szükséges a kérés életciklusának pontosabb követéséhez
    # created_at = models.DateTimeField(auto_now_add=True) # Ez megegyezne a requested_at-tel
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Utolsó Módosítás")


    def __str__(self):
        return f"Jelentéskérés: {self.company.name} - {self.period_year} ({self.get_report_type_display()}) - Státusz: {self.get_status_display()}"

    class Meta:
        verbose_name = "Jelentésgenerálási Kérés"
        verbose_name_plural = "Jelentésgenerálási Kérések"
        ordering = ['-requested_at']