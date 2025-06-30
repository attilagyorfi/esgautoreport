from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import ReportGenerationRequest
from esgdata.models import CompanyDataEntry
from companies.models import CompanyProfile

# A login_required dekorátort érdemes használni, hogy csak bejelentkezett felhasználók érhessék el
from django.contrib.auth.decorators import login_required

@login_required
def generate_report_view(request, request_id):
    """
    Ez a nézet legenerál egy PDF jelentést egy ReportGenerationRequest alapján.
    """
    # 1. Kérjük le a riport generálási kérelmet
    report_request = get_object_or_404(ReportGenerationRequest, pk=request_id, company__user_profiles__user=request.user)

    # 2. Gyűjtsük össze a releváns adatokat
    company = report_request.company
    reporting_period = report_request.reporting_period
    
    # Itt az összes, az adott céghez és periódushoz tartozó adatpontot gyűjtjük le.
    # Ezt később lehet finomítani a riport típus (questionnaire_type) alapján.
    data_entries = CompanyDataEntry.objects.filter(
        company=company,
        reporting_period=reporting_period
    ).order_by('data_point__pillar', 'data_point__datapoint_id')

    # 3. Rendereljük a HTML sablont a kontextussal
    context = {
        'company': company,
        'reporting_period': reporting_period,
        'data_entries': data_entries,
        'generation_date': report_request.created_at,
    }
    html_string = render_to_string('reports/report_template.html', context)

    # 4. WeasyPrint segítségével konvertáljuk a HTML-t PDF-fé
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    # 5. Adjuk vissza a PDF-et HTTP válaszként
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="esg_report_{company.name}_{reporting_period}.pdf"'
    
    return response