# esgdata/admin.py
from django.contrib import admin
from .models import Questionnaire, EsgDataPoint, CompanyDataEntry, ChoiceOption, Report

@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_size', 'region', 'is_active')
    list_filter = ('company_size', 'region', 'is_active')
    search_fields = ('name',)

@admin.register(EsgDataPoint)
class EsgDataPointAdmin(admin.ModelAdmin):
    list_display = ('question_id', 'text', 'pillar', 'answer_type', 'is_active')
    list_filter = ('pillar', 'answer_type', 'is_active', 'questionnaires')
    search_fields = ('question_id', 'text')
    filter_horizontal = ('questionnaires',)

@admin.register(ChoiceOption)
class ChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'text')
    search_fields = ('text',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('company', 'report_type', 'period_year', 'created_by', 'created_at')
    list_filter = ('company', 'period_year', 'report_type')
    search_fields = ('company__name', 'report_type__name')
    autocomplete_fields = ('company', 'report_type', 'created_by')

@admin.register(CompanyDataEntry)
class CompanyDataEntryAdmin(admin.ModelAdmin):
    # JAVÍTVA: A 'company' hivatkozásokat 'report'-ra cseréltük
    list_display = ('report', 'data_point', 'choice_option', 'text_value', 'date_recorded')
    list_filter = ('report__company', 'report__period_year', 'data_point__pillar') # Szűrés a reporton keresztül
    search_fields = ('report__company__name', 'data_point__text')
    # Az autocomplete mezőt is javítjuk
    autocomplete_fields = ('report', 'data_point', 'choice_option')