# co2calc/migrations/0002_populate_activity_types.py
from django.db import migrations

ACTIVITY_TYPES = [
    "Bevásárolt áruk és szolgáltatások",
    "Dolgozói ingázás",
    "Hulladékgazdálkodás (műveletek során keletkező)",
    "Hűtőközeg szivárgás (illékony kibocsátások)",
    "Saját vagy irányított járművek üzemanyag-felhasználása (mobil égés)",
    "Telephelyi energiafelhasználás - Egyéb fűtőanyagok (stacionárius égés)",
    "Telephelyi energiafelhasználás - Földgáz (stacionárius égés)",
    "Telephelyi energiafelhasználás - Tüzelőolaj (stacionárius égés)",
    "Üzleti utak",
    "Vásárolt gőz, hőenergia vagy hűtés",
    "Vásárolt villamos energia",
]

def populate_activity_types(apps, schema_editor):
    ActivityType = apps.get_model('co2calc', 'ActivityType')
    for name in sorted(ACTIVITY_TYPES):
        ActivityType.objects.get_or_create(name=name)

def remove_activity_types(apps, schema_editor):
    ActivityType = apps.get_model('co2calc', 'ActivityType')
    ActivityType.objects.filter(name__in=ACTIVITY_TYPES).delete()

class Migration(migrations.Migration):

    dependencies = [
        # Itt az ELŐZŐ migrációra kell hivatkozni, ami létrehozta az ActivityType modellt.
        # Ha a 'makemigrations co2calc' egy '0001_initial.py'-t hozott létre, akkor ez helyes:
        ('co2calc', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(populate_activity_types, remove_activity_types),
    ]