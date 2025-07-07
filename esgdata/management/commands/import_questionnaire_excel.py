# esgdata/management/commands/import_questionnaire_excel.py
import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from esgdata.models import Questionnaire, EsgDataPoint, ChoiceOption
from django.db import transaction

class Command(BaseCommand):
    help = 'Clears and imports ESG questionnaires from Excel files using the E, S, G sheets.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("--- Starting Final ESG Questionnaire Import Process ---"))

        # 1. Adatbázis tisztítása
        self.stdout.write("--> Step 1: Clearing old questionnaire data...")
        Questionnaire.objects.all().delete()
        EsgDataPoint.objects.all().delete()
        ChoiceOption.objects.all().delete()
        self.stdout.write("...Old data cleared.")

        # Alapértelmezett válaszlehetőségek létrehozása
        choice_options = [
            ChoiceOption.objects.get_or_create(text='Igen')[0],
            ChoiceOption.objects.get_or_create(text='Nem')[0],
            ChoiceOption.objects.get_or_create(text='Részben')[0],
            ChoiceOption.objects.get_or_create(text='Nem releváns')[0]
        ]

        import_folder = os.path.join(settings.BASE_DIR, 'data_imports')

        # 2. Fájlok feldolgozása
        self.stdout.write("--> Step 2: Processing Excel files...")
        for filename in sorted(os.listdir(import_folder)):
            if not filename.endswith('_readable.xlsx') or not filename.startswith('kerdoiv_'):
                if filename.endswith('_readable.xlsx'):
                     self.stdout.write(f"\nSkipping non-hungarian file: {filename}")
                continue

            self.stdout.write(f"\nProcessing file: {filename}")
            try:
                base_name = filename.replace('_readable.xlsx', '')
                parts = base_name.split('_')
                size_map = {'mikrovall': 'micro', 'kisvall': 'small', 'kozepvall': 'medium', 'nagyvall': 'large'}
                region_map = {'hu-egt-sv': 'hu_egt_sv', 'oecd': 'oecd', 'egyeb': 'other'}
                
                company_size = size_map.get(parts[1])
                region = region_map.get('-'.join(parts[2:]))
                
                if not company_size or not region:
                    continue

                q_name = f"{Questionnaire.CompanySize(company_size).label} - {Questionnaire.Region(region).label}"
                questionnaire, _ = Questionnaire.objects.get_or_create(
                    company_size=company_size, region=region, defaults={'name': q_name}
                )
                
                sheet_map = {'E - Környezetvédelem': 'E', 'S - Társadalom': 'S', 'G - Vállalatirányítás': 'G'}
                total_linked_questions = 0
                file_path = os.path.join(import_folder, filename)

                for sheet_name, pillar_code in sheet_map.items():
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        for index, row in df.iterrows():
                            # JAVÍTÁS: A HELYES OSZLOPNEVEK HASZNÁLATA
                            question_id = row.get('Kérdés ID')
                            question_text = row.get('Kérdés szövege')
                            
                            if pd.isna(question_id) or not str(question_id).strip() or pd.isna(question_text):
                                continue

                            data_point, _ = EsgDataPoint.objects.get_or_create(
                                question_id=str(question_id).strip(),
                                defaults={
                                    'text': str(question_text).strip(),
                                    'pillar': pillar_code,
                                    'answer_type': 'choice'
                                }
                            )
                            data_point.available_options.add(*choice_options)
                            questionnaire.questions.add(data_point)
                            total_linked_questions += 1
                    
                    except ValueError:
                        continue
                
                self.stdout.write(self.style.SUCCESS(f"  - Finished file. Total linked questions: {total_linked_questions}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  - An unexpected error occurred: {e}"))

        self.stdout.write(self.style.SUCCESS("\n--- Import Process Finished Successfully! ---"))