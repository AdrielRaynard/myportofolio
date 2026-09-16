from django.shortcuts import render

from main.forms import EducationForm
from main.models import Experience, Education

from io import BytesIO

from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.contrib import messages
from django.core import serializers
from django.shortcuts import get_object_or_404, redirect

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
    json_response = get_education_json(request)

    education = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    education = [item.object for item in education]

    nama_sekolah_query = request.GET.get("nama_sekolah", "").strip()

    context = {
        "name": "Adriel",
        "education_list": education,
        "nama_sekolah_query": nama_sekolah_query,
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

def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pendidikan baru berhasil ditambahkan!")
        return redirect("main:show_education")

    context = {
        "name": "Adriel",
        "form": form,
    }
    return render(request, "education_form.html", context)

def get_education_json(request):
    nama_sekolah_query = request.GET.get("nama_sekolah", "").strip()
    education = Education.objects.all()

    if nama_sekolah_query:
        education = education.filter(
            nama_sekolah__icontains=nama_sekolah_query
        )

    education_json = serializers.serialize("json", education)

    return HttpResponse(
        education_json,
        content_type="application/json",
    )

def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
        return redirect("main:show_education")

    return redirect("main:show_education")