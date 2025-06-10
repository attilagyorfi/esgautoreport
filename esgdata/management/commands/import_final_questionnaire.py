# esgdata/management/commands/import_final_questionnaire.py
import openpyxl
from django.core.management.base import BaseCommand, CommandError
from esgdata.models import ESGDataPoint
from django.db import transaction

class Command(BaseCommand):
    help = 'Imports questions from a pre-structured, clean Excel file.'

    def add_arguments(self, parser):
        parser.add_argument('excel_file_path', type=str, help='The path to the cleaned questionnaire Excel file.')
        parser.add_argument('--sheet_name', type=str, default='Kerdesek', help='Name of the sheet to process.')
        parser.add_argument('--clear', action='store_true', help='Deletes all existing ESGDataPoint entries before importing.')

    def handle(self, *args, **options):
        # ... (fájl és munkalap beolvasása, ahogy a legutóbbi szkriptben) ...
        # ... (pillar_mapping és response_type_mapping definíciók, ahogy korábban) ...
        
        try:
            # ... (Törlési logika a --clear kapcsolóhoz, ha szükséges) ...

            # Fejléc alapján olvasás
            header = [cell.value for cell in sheet[1]] # Feltételezzük, hogy a fejléc az 1. sorban van
            
            for row_cells in sheet.iter_rows(min_row=2):
                row_data = {header[i]: str(cell.value).strip() if cell.value else None for i, cell in enumerate(row_cells)}

                q_identifier = row_data.get('Azonosito')
                q_text = row_data.get('KerdesSzoveg')
                pillar_char = row_data.get('Piller')

                if not q_identifier or not q_text or not pillar_char:
                    skipped_count += 1
                    continue

                # ... (pillar_key és response_data_type beállítása a row_data alapján) ...

                datapoint, created = ESGDataPoint.objects.update_or_create(
                    question_number=q_identifier,
                    defaults={
                        'question_text': q_text,
                        'pillar': pillar_key,
                        'response_data_type': response_data_type,
                        'guidance': row_data.get('Utmutato', ''),
                        'choice_option_group': row_data.get('LegorduloCsoport'),
                        'is_voluntary': True if (row_data.get('Opcionalis') or '').lower() == 'igen' else False,
                    }
                )
                # ... (created/updated számlálók növelése) ...

            # ... (Sikerüzenet kiírása) ...
        except Exception as e:
            raise CommandError(f"An error occurred: {e}")