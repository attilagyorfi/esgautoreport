# esgdata/management/commands/import_questions_from_json.py
import json
from django.core.management.base import BaseCommand, CommandError
from esgdata.models import ESGDataPoint, CompanyDataEntry # CompanyDataEntry importálása a törléshez
from django.db import transaction

class Command(BaseCommand):
    help = 'Imports questions from a structured JSON file into the ESGDataPoint model.'

    def add_arguments(self, parser):
        # A kötelező argumentum a JSON fájl elérési útja
        parser.add_argument('json_file_path', type=str, help='The path to the structured JSON file.')
        
        # JAVÍTÁS: Hozzáadjuk a hiányzó --clear argumentum definícióját
        parser.add_argument(
            '--clear',
            action='store_true', # Ez egy kapcsolóvá teszi, nem vár értéket maga után
            help='Deletes all existing CompanyDataEntry and ESGDataPoint entries before importing.',
        )

    def handle(self, *args, **options):
        json_file_path = options['json_file_path']
        
        # Pillar és Response Type megfeleltetések
        pillar_mapping = {
            'E': 'environmental', 
            'S': 'social', 
            'G': 'governance',
            # Kiegészítés az Adatlaphoz és ÜHG-hoz, ha a JSON-ban is E/S/G-ként vannak
            # Ha más a jelölésük, ide kell felvenni. Tegyük fel, hogy 'A' az Adatlap és 'U' az ÜHG
            'A': 'datasheet',
            'U': 'ghg_targets',
        }
        response_type_mapping = {
            'legördülő': ESGDataPoint.DATATYPE_DROPDOWN,
            'igen/nem': ESGDataPoint.DATATYPE_BOOLEAN,
            'szám': ESGDataPoint.DATATYPE_NUMBER,
            'szöveg': ESGDataPoint.DATATYPE_TEXT,
            'dátum': ESGDataPoint.DATATYPE_DATE,
            'fájl': ESGDataPoint.DATATYPE_FILE,
        }

        try:
            with transaction.atomic():
                if options['clear']:
                    self.stdout.write(self.style.WARNING('Deleting all existing CompanyDataEntry objects...'))
                    deleted_entries, _ = CompanyDataEntry.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_entries} CompanyDataEntry objects.'))
                    
                    self.stdout.write(self.style.WARNING('Deleting all existing ESGDataPoint objects...'))
                    deleted_points, _ = ESGDataPoint.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS(f'Successfully deleted {deleted_points} ESGDataPoint objects.'))

                self.stdout.write(self.style.SUCCESS(f"Importing questions from '{json_file_path}'..."))
                
                with open(json_file_path, mode='r', encoding='utf-8') as file:
                    questions_data = json.load(file)

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for item in questions_data:
                    q_identifier = item.get('Azonosito')
                    q_text = item.get('KerdesSzoveg')
                    pillar_char = item.get('Piller')

                    if not q_identifier or not q_text or not pillar_char:
                        skipped_count += 1
                        continue
                    
                    pillar_key = pillar_mapping.get(pillar_char.upper())
                    if not pillar_key:
                        self.stdout.write(self.style.WARNING(f"Skipping '{q_identifier}': Invalid pillar character '{pillar_char}'."))
                        skipped_count += 1
                        continue

                    resp_type_str = (item.get('ValaszTipus') or 'szöveg').lower()
                    response_data_type = response_type_mapping.get(resp_type_str, ESGDataPoint.DATATYPE_TEXT)

                    datapoint, created = ESGDataPoint.objects.update_or_create(
                        question_number=q_identifier,
                        defaults={
                            'question_text': q_text,
                            'pillar': pillar_key,
                            'response_data_type': response_data_type,
                            'guidance': item.get('Utmutato', ''),
                            'choice_option_group': item.get('LegorduloCsoport') if response_data_type == ESGDataPoint.DATATYPE_DROPDOWN else None,
                            'is_voluntary': True if (item.get('Opcionalis') or '').lower() == 'igen' else False,
                        }
                    )
                    if created: created_count += 1
                    else: updated_count += 1

                self.stdout.write(self.style.SUCCESS(f"\nImport finished!"))
                self.stdout.write(f"  Created: {created_count}")
                self.stdout.write(f"  Updated: {updated_count}")
                self.stdout.write(f"  Skipped (missing data): {skipped_count}")

        except FileNotFoundError:
            raise CommandError(f"File not found at: {json_file_path}")
        except json.JSONDecodeError:
            raise CommandError(f"Error decoding JSON from the file: {json_file_path}")
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")