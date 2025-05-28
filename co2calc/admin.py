# co2calc/admin.py
from django.contrib import admin
from .models import CO2CalculationInput, EmissionFactor, ActivityType  # <<< ActivityType importálása

@admin.register(CO2CalculationInput)
class CO2CalculationInputAdmin(admin.ModelAdmin):
    list_display = ('company', 'activity_type', 'quantity', 'unit', 'period_year', 'period_month', 'calculated_co2e', 'updated_at')
    list_filter = ('period_year', 'company', 'activity_type')
    search_fields = ('company__name', 'activity_type', 'unit')
    list_select_related = ('company',)
    readonly_fields = ('calculated_co2e', 'created_at', 'updated_at')

    fieldsets = (
        ("Alapinformációk", {
            'fields': ('company', 'activity_type', ('period_year', 'period_month'))
        }),
        ("Mennyiségi Adatok", {
            'fields': ('quantity', 'unit', 'emission_factor')
        }),
        ("Eredmény (rendszer tölti, dinamikusan frissül)", {
            'fields': ('calculated_co2e',)
        }),
        ("Időbélyegek", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    class Media:
        js = ('co2calc/js/co2_calculator.js',)

@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_type', 'unit_of_activity', 'factor_value', 'get_full_factor_unit', 'source', 'year_of_factor', 'updated_at')  # 'activity_identifier' -> 'activity_type'
    list_filter = ('source', 'year_of_factor', 'unit_of_activity', 'emission_unit_numerator', 'activity_type')
    search_fields = ('name', 'activity_type__name', 'source', 'notes')
    ordering = ('name', '-year_of_factor')
    fieldsets = (
        (None, {
            'fields': ('name', 'activity_type', 'unit_of_activity')
        }),
        ("Faktor Értéke és Egysége", {
            'fields': ('factor_value', 'emission_unit_numerator')
        }),
        ("Forrás és Érvényesség", {
            'fields': ('source', 'year_of_factor')
        }),
        ("Megjegyzések", {
            'fields': ('notes',)
        }),
        ("Időbélyegek", {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('activity_type',)

@admin.register(ActivityType)
class ActivityTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'updated_at')
    search_fields = ('name', 'description')
    ordering = ('name',)