from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class EsgdataConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'esgdata'
    verbose_name = _('ESG Adatkezelés')