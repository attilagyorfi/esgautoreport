# notifications/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone # A due_date validációhoz lehet hasznos, de most nem implementáljuk

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Felhasználó", related_name="notifications")
    message = models.TextField(verbose_name="Üzenet")
    due_date = models.DateField(blank=True, null=True, verbose_name="Határidő")
    is_read = models.BooleanField(default=False, verbose_name="Elolvasva")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Létrehozva")
    # Később hozzáadhatunk egy 'updated_at = models.DateTimeField(auto_now=True)' mezőt is, ha szükséges

    # Opcionális mezők, amiket később hozzáadhatunk a funkcionalitás bővítéséhez:
    # link = models.URLField(blank=True, null=True, verbose_name="Hivatkozás")
    # LEVEL_INFO = 'info'
    # LEVEL_WARNING = 'warning'
    # LEVEL_ERROR = 'error'
    # LEVEL_CHOICES = [
    #     (LEVEL_INFO, 'Információ'),
    #     (LEVEL_WARNING, 'Figyelmeztetés'),
    #     (LEVEL_ERROR, 'Hiba'),
    # ]
    # level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=LEVEL_INFO, verbose_name="Szint")

    def __str__(self):
        return f"Értesítés: {self.user.username} - {self.message[:50]}{'...' if len(self.message) > 50 else ''}"

    class Meta:
        verbose_name = "Értesítés"
        verbose_name_plural = "Értesítések"
        ordering = ['-created_at'] # Legfrissebb értesítések elöl