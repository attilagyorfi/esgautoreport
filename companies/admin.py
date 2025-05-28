# companies/admin.py
from django.contrib import admin
from .models import CompanyProfile, TEORCode # TEORCode importálása

@admin.register(TEORCode)
class TEORCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'address_city', 'tax_number', 'updated_at')
    search_fields = ('name', 'industry__name', 'industry__code', 'tax_number', 'address_city', 'address_country')
    list_filter = ('industry', 'address_country', 'updated_at')
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'industry', 'tax_number', 'registration_number')
        }),
        ('Székhely Címe', {
            'fields': ('address_country', 'address_postal_code', 'address_city', 'address_street_and_number')
        }),
        ('Időbélyegek', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    list_select_related = ('industry',) # Optimalizálás az industry ForeignKey miatt