# esgdata/admin.py
from django.contrib import admin
from .models import ESGDataPoint, CompanyDataEntry, ChoiceOption # ChoiceOption importálása

@admin.register(ChoiceOption)
class ChoiceOptionAdmin(admin.ModelAdmin):
    list_display = ('text', 'group_identifier', 'id', 'updated_at')
    search_fields = ('text', 'group_identifier')
    list_filter = ('group_identifier',)
    ordering = ('group_identifier', 'text')
    list_per_page = 25

@admin.register(ESGDataPoint)
class ESGDataPointAdmin(admin.ModelAdmin):
    list_display = ('question_number', 'get_question_text_short', 'pillar', 'response_data_type', 'applies_to_questionnaire_type', 'is_voluntary', 'updated_at')
    search_fields = ('question_number', 'question_text', 'esrs_topic_standard', 'esrs_datapoint_definition', 'guidance', 'applies_to_questionnaire_type')
    list_filter = ('pillar', 'response_data_type', 'is_voluntary', 'applies_to_questionnaire_type', 'updated_at')
    list_editable = ('is_voluntary',) 
    ordering = ('question_number',) # Rendezés a kérdés sorszáma alapján
    
    fieldsets = (
        (None, {
            'fields': ('question_number', 'question_text', 'is_voluntary', 'applies_to_questionnaire_type')
        }),
        ('Besorolás és ESRS Hivatkozások', {
            'fields': ('pillar', 'esrs_topic_standard', 'esrs_datapoint_definition')
        }),
        ('Válasz Formátuma és Útmutató', {
            'fields': ('response_data_type', 'unit_of_measure', 'choice_option_group', 'guidance')
        }),
        ('Időbélyegek (Rendszer)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    def get_question_text_short(self, obj):
        """Rövidített kérdésszöveg a list_display-hez."""
        if obj.question_text:
            return (obj.question_text[:75] + '...') if len(obj.question_text) > 75 else obj.question_text
        return "-"
    get_question_text_short.short_description = 'Kérdés Szövege (rövidítve)'

@admin.register(CompanyDataEntry)
class CompanyDataEntryAdmin(admin.ModelAdmin):
    list_display = ('company', 'get_data_point_q_number', 'get_data_point_short_text', 'period_year', 'status', 'entry_date')
    list_filter = ('status', 'period_year', 'company', 'data_point__pillar', 'data_point__applies_to_questionnaire_type')
    search_fields = ('company__name', 'data_point__question_text', 'data_point__question_number', 'source_description')
    list_select_related = ('company', 'data_point', 'entered_by')
    readonly_fields = ('entry_date', 'created_at', 'updated_at', 'entered_by')
    date_hierarchy = 'entry_date'
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('company', 'data_point', ('period_year', 'period_month'))
        }),
        ('Megadott Érték', {
            'fields': ('value_numeric', 'value_text', 'value_date', 'value_file')
        }),
        ('Metaadatok', {
            'fields': ('source_description', 'status', 'entered_by')
        }),
        ('Időbélyegek (Rendszer)', {
            'fields': ('entry_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_data_point_short_text(self, obj):
        if obj.data_point and obj.data_point.question_text:
            return (obj.data_point.question_text[:50] + '...') if len(obj.data_point.question_text) > 50 else obj.data_point.question_text
        return "-"
    get_data_point_short_text.short_description = 'ESG Adatpont (Kérdés)'

    def get_data_point_q_number(self, obj):
        if obj.data_point and obj.data_point.question_number:
            return obj.data_point.question_number
        return "-"
    get_data_point_q_number.short_description = 'Adatpont Sorszáma'