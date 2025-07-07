# accounts/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = _('Felhasználói Fiókok és Profilok')

    def ready(self):
        # Ezzel a sorral importáljuk és aktiváljuk a signale-ket
        import accounts.signals