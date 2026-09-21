"""View untuk aplikasi `main` (portofolio pribadi).

Struktur berkas:
    1. Helper bersama      : konteks halaman, respons JSON, deserialisasi JSON.
    2. Profile             : halaman utama.
    3. Experience          : halaman + JSON Data Delivery + Create/Update/Delete.
    4. Education           : halaman + JSON Data Delivery + Create/Update/Delete.
    5. Portfolio PDF       : unduh ringkasan portofolio.
"""

from io import BytesIO

from django.contrib import messages
from django.core import serializers

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_safe
from xhtml2pdf import pisa

from main.forms import EducationForm, ExperienceForm, SecretCodeForm
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

def _form_view(
    request,
    form_class,
    *,
    instance=None,
    heading,
    submit_label,
    cancel_url,
    success_url,
    success_message,
):
    """View generik halaman Create/Update berbasis ModelForm (pola POST-Redirect-GET).

    - GET            : tampilkan form (terisi data lama jika `instance` diberikan).
    - POST valid     : simpan, tampilkan flash message, redirect ke `success_url`.
    - POST tidak valid: render ulang form beserta pesan error tiap field.
    """
    is_post = request.method == "POST"
    form = form_class(request.POST if is_post else None, instance=instance)

    if is_post and form.is_valid():
        form.save()
        messages.success(request, success_message)
        return redirect(success_url)

    context = _page_context(
        form=form,
        heading=heading,
        submit_label=submit_label,
        cancel_url=cancel_url,
    )
    return render(request, "form_page.html", context)


def _delete_with_secret(request, instance, *, success_url, success_message):
    """Hapus `instance` hanya jika kode rahasia pada POST benar, lalu redirect."""
    form = SecretCodeForm(request.POST)

    if form.is_valid():
        instance.delete()
        messages.success(request, success_message)
    else:
        messages.error(request, "Kode rahasia salah. Data tidak dihapus.")

    return redirect(success_url)

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

def create_experience(request):
    return _form_view(
        request,
        ExperienceForm,
        heading="Tambah Pengalaman",
        submit_label="Tambah Pengalaman",
        cancel_url=reverse("main:show_experience"),
        success_url="main:show_experience",
        success_message="Pengalaman baru berhasil ditambahkan!",
    )


def update_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    return _form_view(
        request,
        ExperienceForm,
        instance=experience,
        heading="Ubah Pengalaman",
        submit_label="Simpan Perubahan",
        cancel_url=reverse("main:show_experience"),
        success_url="main:show_experience",
        success_message="Pengalaman berhasil diperbarui!",
    )


@require_POST
def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    return _delete_with_secret(
        request,
        experience,
        success_url="main:show_experience",
        success_message="Pengalaman berhasil dihapus!",
    )

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
def get_education_detail_json(request, education_id):
    """Satu riwayat pendidikan dalam JSON berdasarkan id (UUID)."""
    return _json_detail_response(Education, education_id)


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
    return _form_view(
        request,
        EducationForm,
        heading="Tambah Riwayat Pendidikan",
        submit_label="Tambah Pendidikan",
        cancel_url=reverse("main:show_education"),
        success_url="main:show_education",
        success_message="Pendidikan baru berhasil ditambahkan!",
    )

def update_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)
    return _form_view(
        request,
        EducationForm,
        instance=education,
        heading="Ubah Riwayat Pendidikan",
        submit_label="Simpan Perubahan",
        cancel_url=reverse("main:show_education"),
        success_url="main:show_education",
        success_message="Riwayat pendidikan berhasil diperbarui!",
    )

@require_POST
def delete_education(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    return _delete_with_secret(
        request,
        education,
        success_url="main:show_education",
        success_message="Riwayat pendidikan berhasil dihapus!",
    )

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