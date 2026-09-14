from django.shortcuts import render

from main.models import Experience, Education

from io import BytesIO

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa


def show_main(request):
    context = {
        "name": "Adriel",
        "npm": "2506587150",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Adriel",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Adriel",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)

def download_portfolio_pdf(request):
    context = {
        "name": "Adriel",
        "experience_list": Experience.objects.all(),
        "education_list": Education.objects.all(),
    }

    html_string = render_to_string("portfolio_pdf.html", context)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_string.encode("UTF-8")), result)

    if pdf.err:
        return HttpResponse(
            "Terjadi kesalahan saat membuat PDF.",
            status=500,
        )

    response = HttpResponse(result.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="portfolio-adriel.pdf"'
    return response