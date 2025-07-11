# Generated by Django 4.2.21 on 2025-06-30 13:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Pl. Földgáz égetés (telephelyi), Vásárolt villamos energia', max_length=255, unique=True, verbose_name='Tevékenységtípus Neve')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Leírás')),
                ('allowed_units', models.CharField(blank=True, help_text='Vesszővel elválasztott lista az engedélyezett mértékegység kulcsokból (pl. kwh,kg,m3). Hagyd üresen, ha az alapértelmezett összes egység engedélyezett.', max_length=255, null=True, verbose_name='Engedélyezett Mértékegységek')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Létrehozva')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Módosítva')),
            ],
            options={
                'verbose_name': 'CO₂ Tevékenységtípus',
                'verbose_name_plural': 'CO₂ Tevékenységtípusok',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='EmissionFactor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Pl. Földgáz (magas fűtőértékű) - DEFRA 2023', max_length=255, verbose_name='Faktor Neve/Leírása')),
                ('unit_of_activity', models.CharField(choices=[('liter', 'liter'), ('kWh', 'kWh (kilowattóra)'), ('kg', 'kg (kilogramm)'), ('t', 't (tonna)'), ('m3', 'm³ (köbméter)')], db_index=True, max_length=20, verbose_name='Tevékenység Egysége')),
                ('factor_value', models.DecimalField(decimal_places=8, max_digits=15, verbose_name='Emissziós Faktor Értéke')),
                ('emission_unit_numerator', models.CharField(choices=[('kg_co2e', 'kg CO₂e'), ('t_co2e', 't CO₂e')], default='kg_co2e', max_length=10, verbose_name='Kibocsátás Egysége (Számláló)')),
                ('source', models.CharField(max_length=100, verbose_name='Faktor Forrása')),
                ('year_of_factor', models.IntegerField(verbose_name='Faktor Érvényességi Éve')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='Megjegyzések')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Létrehozva')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Módosítva')),
                ('activity_type', models.ForeignKey(blank=True, help_text='Válaszd ki a tevékenységtípust, amire ez a faktor vonatkozik.', null=True, on_delete=django.db.models.deletion.PROTECT, to='co2calc.activitytype', verbose_name='Tevékenységtípus')),
            ],
            options={
                'verbose_name': 'Emissziós Faktor',
                'verbose_name_plural': 'Emissziós Faktorok',
                'ordering': ['name', '-year_of_factor'],
                'unique_together': {('activity_type', 'unit_of_activity', 'source', 'year_of_factor')},
            },
        ),
        migrations.CreateModel(
            name='CO2CalculationInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_year', models.IntegerField(choices=[(2015, '2015'), (2016, '2016'), (2017, '2017'), (2018, '2018'), (2019, '2019'), (2020, '2020'), (2021, '2021'), (2022, '2022'), (2023, '2023'), (2024, '2024'), (2025, '2025'), (2026, '2026'), (2027, '2027'), (2028, '2028'), (2029, '2029'), (2030, '2030')], default=2025, verbose_name='Jelentési Év')),
                ('period_month', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5'), (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10'), (11, '11'), (12, '12')], help_text='Válaszd ki a jelentési hónapot.', verbose_name='Jelentési Hónap (1-12)')),
                ('quantity', models.DecimalField(decimal_places=4, max_digits=12, verbose_name='Mennyiség')),
                ('unit', models.CharField(choices=[('liter', 'liter'), ('kWh', 'kWh (kilowattóra)'), ('kg', 'kg (kilogramm)'), ('t', 't (tonna)'), ('m3', 'm³ (köbméter)')], max_length=10, verbose_name='Mértékegység')),
                ('calculated_co2e', models.DecimalField(blank=True, decimal_places=4, help_text='A kalkuláció eredménye tonna CO₂ ekvivalensben. Ezt a rendszer tölti ki.', max_digits=12, null=True, verbose_name='Kiszámított CO₂e (t)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Létrehozva')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Módosítva')),
                ('activity_type', models.ForeignKey(blank=True, help_text='Válassz a listából.', null=True, on_delete=django.db.models.deletion.PROTECT, to='co2calc.activitytype', verbose_name='Tevékenység Típusa')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='co2_inputs', to='companies.companyprofile', verbose_name='Vállalat')),
                ('emission_factor', models.ForeignKey(blank=True, help_text='Válassz egy konkrét faktort a listából, vagy hagyd üresen az automatikus kereséshez.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='co2calc.emissionfactor', verbose_name='Kiválasztott Emissziós Faktor (felülíráshoz)')),
            ],
            options={
                'verbose_name': 'CO₂ Kalkulátor Bemeneti Adat',
                'verbose_name_plural': 'CO₂ Kalkulátor Bemeneti Adatok',
                'ordering': ['-period_year', '-period_month', 'company', 'activity_type'],
            },
        ),
    ]
