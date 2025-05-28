# notifications/admin.py
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_short_message', 'is_read', 'due_date', 'created_at')
    list_filter = ('is_read', 'user', 'due_date', 'created_at')
    search_fields = ('user__username', 'message')
    list_select_related = ('user',) # Optimalizálás a felhasználó adatainak lekérdezéséhez
    list_editable = ('is_read',) # Lehetővé teszi az 'is_read' állapot gyors váltását a listából

    def get_short_message(self, obj):
        # Rövidített üzenet megjelenítése a listában
        return (obj.message[:75] + '...') if len(obj.message) > 75 else obj.message
    get_short_message.short_description = 'Üzenet (rövidítve)'

    fieldsets = (
        (None, {
            'fields': ('user', 'message', 'due_date')
        }),
        ("Állapot", {
            'fields': ('is_read',)
        }),
        ("Időbélyeg", {
            'fields': ('created_at',),
            'classes': ('collapse',), # Alapból összecsukva
        }),
    )