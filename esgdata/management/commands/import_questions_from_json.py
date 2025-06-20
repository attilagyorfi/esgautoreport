# esgdata/management/commands/import_questions_from_json.py
import json
from django.core.management.base import BaseCommand, CommandError
from esgdata.models import ESGDataPoint, CompanyDataEntry
from django.db import transaction

class Command(BaseCommand):
    help = 'Imports questions from a structured JSON file for a specific report type.'

    def add_arguments(self, parser):
        parser.add_argument('json_file_path', type=str, help='The path to the structured JSON file.')
        parser.add_argument(
            '--report-type-key',
            type=str,
            required=True,
            help="The key of the report type these questions belong to (e.g., 'sztfh_mikrovall_hu_egt_ch')."
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Deletes ALL existing questions and answers for this specific report type before importing.',
        )

    def handle(self, *args, **options):
        json_file_path = options['json_file_path']
        report_type_key = options['report_type_key']
        
        pillar_mapping = {
            'A': 'datasheet',
            'E': 'environmental', 
            'S': 'social', 
            'G': 'governance',
            'U': 'ghg_targets',
        }

        try:
            with transaction.atomic():
                if options['clear']:
                    self.stdout.write(self.style.WARNING(f"Deleting data for report type '{report_type_key}'..."))
                    
                    points_to_delete = ESGDataPoint.objects.filter(applies_to_questionnaire_type=report_type_key)
                    
                    entries_to_delete = CompanyDataEntry.objects.filter(data_point__in=points_to_delete)
                    deleted_entries_count, _ = entries_to_delete.delete()
                    self.stdout.write(self.style.SUCCESS(f'--> Deleted {deleted_entries_count} related CompanyDataEntry objects.'))

                    deleted_points_count, _ = points_to_delete.delete()
                    self.stdout.write(self.style.SUCCESS(f'--> Successfully deleted {deleted_points_count} ESGDataPoint objects.'))

                self.stdout.write(self.style.SUCCESS(f"Importing questions from '{json_file_path}' for report type '{report_type_key}'..."))
                
                with open(json_file_path, mode='r', encoding='utf-8') as file:
                    questions_data = json.load(file)

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for item in questions_data:
                    q_identifier = item.get('Azonosito')
                    q_text = item.get('KerdesSzoveg')
                    pillar_char = item.get('Piller')

                    # Szigorú ellenőrzés: Azonosító, Kérdés és Pillér is kötelező!
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
                            'applies_to_questionnaire_type': report_type_key, # A legfontosabb: a kérdés összekötése a jelentéstípussal
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