# reports/admin.py
from django.contrib import admin
from .models import ReportGenerationRequest

@admin.register(ReportGenerationRequest)
class ReportGenerationRequestAdmin(admin.ModelAdmin):
    list_display = ('company', 'report_type', 'period_year', 'period_quarter_or_month', 'status', 'requested_by', 'requested_at', 'updated_at')
    list_filter = ('status', 'report_type', 'period_year', 'company')
    search_fields = ('company__name', 'period_year')
    readonly_fields = ('requested_at', 'updated_at', 'generated_pdf_path', 'generated_excel_path') # A generált fájlok útvonalai kezdetben csak olvashatók
    list_select_related = ('company', 'requested_by') # Optimalizálás

    fieldsets = (
        ("Alapinformációk", {
            'fields': ('company', 'report_type', 'period_year', 'period_quarter_or_month')
        }),
        ("Kérvényezés és Státusz", {
            'fields': ('requested_by', 'requested_at', 'status')
        }),
        ("Generált Fájlok (csak olvasható)", {
            'fields': ('generated_pdf_path', 'generated_excel_path'),
            'classes': ('collapse',), # Alapból összecsukva
        }),
        ("Időbélyeg", {
            'fields': ('updated_at',),
            'classes': ('collapse',),
        }),
    )