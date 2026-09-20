"""View untuk aplikasi `main` (portofolio pribadi).

Struktur berkas:
    1. Helper bersama      : konteks halaman, respons JSON, deserialisasi JSON.
    2. Profile             : halaman utama.
    3. Experience          : halaman + JSON Data Delivery.
    4. Education           : halaman + JSON + Create + Delete.
    5. Portfolio PDF       : unduh ringkasan portofolio.
"""

from io import BytesIO

from django.contrib import messages
from django.core import serializers

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_safe
from xhtml2pdf import pisa

from main.forms import EducationForm
from main.models import Education, Experience

OWNER_NAME = "Adriel"


# ---------------------------------------------------------------------------
# Helper bersama
# ---------------------------------------------------------------------------

def _page_context(**extra):
    """Konteks dasar yang dibutuhkan base.html, digabung dengan data halaman."""
    return {"name": OWNER_NAME, **extra}


def _json_response(objects):
    """Serialisasi model instance / queryset menjadi respons `application/json`."""
    return HttpResponse(
        serializers.serialize("json", objects),
        content_type="application/json",
    )


def _json_detail_response(model, pk):
    """Respons JSON untuk satu objek; 404 dalam bentuk JSON (bukan halaman HTML)."""
    try:
        instance = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return JsonResponse(
            {"detail": f"{model._meta.verbose_name.title()} tidak ditemukan."},
            status=404,
        )
    return _json_response([instance])


def _objects_from_json(json_response):
    """Deserialisasi respons JSON kembali menjadi list model instance.

    Halaman HTML memakai ini agar mengonsumsi data persis seperti klien API
    (JSON -> objek Python), bukan langsung dari database.
    """
    payload = json_response.content.decode("utf-8")
    return [item.object for item in serializers.deserialize("json", payload)]


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

def show_main(request):
    context = _page_context(
        npm="2506587150",
        study_program="S1 Sistem Informasi",
        bio=(
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    )

    return render(request, "index.html", context)

# ---------------------------------------------------------------------------
# Experience
# ---------------------------------------------------------------------------

@require_safe
def get_experience_json(request):
    """Daftar pengalaman dalam JSON. Filter opsional: `?title=<kata kunci>`."""
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()

    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    return _json_response(experiences)


@require_safe
def get_experience_detail_json(request, experience_id):
    """Satu pengalaman dalam JSON berdasarkan id (UUID)."""
    return _json_detail_response(Experience, experience_id)


@require_safe

def show_experience(request):
    """Halaman Experience: data diambil dari JSON lalu dideserialisasi."""
    experiences = _objects_from_json(get_experience_json(request))

    context = _page_context(
        experience_list=experiences,
        title_query=request.GET.get("title", "").strip(),
    )
    return render(request, "experience.html", context)

# ---------------------------------------------------------------------------
# Education
# ---------------------------------------------------------------------------

@require_safe
def get_education_json(request):
    """Daftar pendidikan dalam JSON. Filter opsional: `?nama_sekolah=<kata kunci>`."""
    nama_sekolah_query = request.GET.get("nama_sekolah", "").strip()
    education = Education.objects.all()

    if nama_sekolah_query:
        education = education.filter(nama_sekolah__icontains=nama_sekolah_query)

    return _json_response(education)

@require_safe
def show_education(request):
    """Halaman Education: data diambil dari JSON lalu dideserialisasi."""
    education = _objects_from_json(get_education_json(request))

    context = _page_context(
        education_list=education,
        nama_sekolah_query=request.GET.get("nama_sekolah", "").strip(),
    )
    return render(request, "education.html", context)

def create_education(request):
    form = EducationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pendidikan baru berhasil ditambahkan!")
        return redirect("main:show_education")

    return render(request, "education_form.html", _page_context(form=form))

def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if request.method == "POST":
        education.delete()
        messages.success(request, "Riwayat pendidikan berhasil dihapus!")
        return redirect("main:show_education")

# ---------------------------------------------------------------------------
# Portfolio PDF
# ---------------------------------------------------------------------------

def download_portfolio_pdf(request):
    context = _page_context(
        experience_list=Experience.objects.all(),
        education_list=Education.objects.all(),
    )

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