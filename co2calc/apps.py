# co2calc/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _ # Fordításhoz

class Co2CalcConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'co2calc'
    verbose_name = _('CO₂ Kalkulációk') # <<< EZ AZ ÚJ/MÓDOSÍTOTT SOR