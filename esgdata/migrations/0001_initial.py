# Generated by Django 4.2.21 on 2025-06-30 13:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChoiceOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=100, unique=True, verbose_name='Válasz szövege')),
            ],
            options={
                'verbose_name': 'Válaszlehetőség',
                'verbose_name_plural': 'Válaszlehetőségek',
            },
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Kérdőív neve')),
                ('company_size', models.CharField(choices=[('micro', 'Mikrovállalkozás'), ('small', 'Kisvállalkozás'), ('medium', 'Középvállalkozás'), ('large', 'Nagyvállalat')], max_length=10, verbose_name='Vállalatméret')),
                ('region', models.CharField(choices=[('hu_egt_sv', 'Magyarország, EGT, Svájc'), ('oecd', 'OECD'), ('other', 'Egyéb')], max_length=10, verbose_name='Régió')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktív')),
            ],
            options={
                'verbose_name': 'Kérdőív',
                'verbose_name_plural': 'Kérdőívek',
                'unique_together': {('company_size', 'region')},
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period_year', models.IntegerField(verbose_name='Érintett Év')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='companies.companyprofile', verbose_name='Vállalat')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Létrehozta')),
                ('report_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='esgdata.questionnaire', verbose_name='Jelentés Típusa')),
            ],
            options={
                'verbose_name': 'Jelentés',
                'verbose_name_plural': 'Jelentések',
                'unique_together': {('company', 'report_type', 'period_year')},
            },
        ),
        migrations.CreateModel(
            name='EsgDataPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_id', models.CharField(max_length=20, unique=True, verbose_name='Kérdés egyedi azonosítója')),
                ('text', models.TextField(verbose_name='Kérdés szövege')),
                ('pillar', models.CharField(choices=[('E', 'Környezetvédelem'), ('S', 'Társadalom'), ('G', 'Vállalatirányítás')], max_length=1, verbose_name='ESG Pillér')),
                ('answer_type', models.CharField(choices=[('choice', 'Választás (Igen/Nem)'), ('text', 'Szöveg'), ('number', 'Szám'), ('date', 'Dátum')], default='choice', max_length=10, verbose_name='Válasz típusa')),
                ('is_active', models.BooleanField(default=True, verbose_name='Aktív')),
                ('questionnaires', models.ManyToManyField(related_name='questions', to='esgdata.questionnaire', verbose_name='Kérdőívek')),
            ],
            options={
                'verbose_name': 'ESG Adatpont',
                'verbose_name_plural': 'ESG Adatpontok',
                'ordering': ['question_id'],
            },
        ),
        migrations.CreateModel(
            name='CompanyDataEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_value', models.TextField(blank=True, null=True, verbose_name='Szöveges válasz')),
                ('numeric_value', models.DecimalField(blank=True, decimal_places=2, max_digits=15, null=True, verbose_name='Számszerű válasz')),
                ('date_value', models.DateField(blank=True, null=True, verbose_name='Dátum válasz')),
                ('date_recorded', models.DateTimeField(auto_now=True)),
                ('choice_option', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='esgdata.choiceoption', verbose_name='Választott opció')),
                ('data_point', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='esgdata.esgdatapoint', verbose_name='Adatpont')),
                ('report', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='esgdata.report', verbose_name='Jelentés')),
            ],
            options={
                'verbose_name': 'Vállalati adatbejegyzés',
                'verbose_name_plural': 'Vállalati adatbejegyzések',
                'unique_together': {('report', 'data_point')},
            },
        ),
    ]
