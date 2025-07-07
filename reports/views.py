from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from esgdata.models import CompanyDataEntry, ChoiceOption
from companies.models import CompanyProfile
from django.core.exceptions import ObjectDoesNotExist

from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from .chart_utils import generate_pie_chart
# Importáljuk az új javaslat generáló segédfüggvényt
from .suggestion_utils import generate_suggestions

# A többi nézet és a render_pdf_view függvény változatlan marad...
def render_pdf_view(template_path, context={}):
    template = get_template(template_path)
    html = template.render(context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="esg_report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Hiba történt a PDF generálása közben.')
    return response

@login_required
def generate_html_report(request):
    context = {}
    try:
        company = request.user.profile.company
        if not company:
            raise ObjectDoesNotExist
        data_entries = CompanyDataEntry.objects.filter(company=company)
        context['company'] = company
        context['data_entries'] = data_entries
    except ObjectDoesNotExist:
        context['error'] = "Ehhez a felhasználóhoz nincs vállalat rendelve."
    except Exception as e:
        context['error'] = f"Ismeretlen hiba történt: {e}"
    return render(request, 'reports/report_template.html', context)
# ...

@login_required
def generate_pdf_report(request):
    """Nézet a vállalati ESG jelentés PDF változatának generálásához és letöltéséhez."""
    try:
        company = request.user.profile.company
        if not company:
            raise ObjectDoesNotExist

        data_entries = CompanyDataEntry.objects.filter(company=company).select_related('data_point', 'choice_option')
        
        # Kategóriák és diagram generálása (ez a rész változatlan)
        categorized_entries = {}
        for entry in data_entries:
            pillar_name = entry.data_point.get_pillar_display()
            if pillar_name not in categorized_entries:
                categorized_entries[pillar_name] = []
            categorized_entries[pillar_name].append(entry)
        chart_image = generate_pie_chart(categorized_entries)
        
        # Itt hívjuk meg a javaslatgeneráló függvényt
        suggestions = generate_suggestions(data_entries)

        context = {
            'company': company,
            'categorized_entries': categorized_entries,
            'chart_image': chart_image,
            'suggestions': suggestions, # Átadjuk a javaslatokat a sablonnak
        }
        return render_pdf_view('reports/report_pdf_template.html', context)

    except ObjectDoesNotExist:
         return HttpResponse("Hiba: Ehhez a felhasználóhoz nincs vállalat rendelve.", status=404)
    except Exception as e:
        return HttpResponse(f"Hiba a PDF generálás során: {e}", status=500)