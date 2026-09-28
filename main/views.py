"""View untuk aplikasi `main` (portofolio pribadi)."""

import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST, require_safe
from xhtml2pdf import pisa

from main.forms import EducationForm, ExperienceForm, SecretCodeForm
from main.models import Education, Experience
from main.permissions import editor_or_owner_required, owner_required

OWNER_NAME = "Adriel"
EDITOR_GROUP_NAME = "Editor"

# Field yang boleh keluar lewat endpoint JSON.
# `starred_by` sengaja tidak diserialisasikan agar API tidak membocorkan
# identitas/account ID pengguna yang memberi star.
EXPERIENCE_JSON_FIELDS = [
    "title",
    "description",
    "category",
    "thumbnail",
    "started_at",
    "ended_at",
]

EDUCATION_JSON_FIELDS = [
    "nama_sekolah",
    "tingkat",
    "jurusan",
    "tahun_masuk",
    "tahun_lulus",
    "deskripsi",
]


def _page_context(**extra):
    """Konteks dasar yang dibutuhkan base.html, digabung dengan data halaman."""
    return {"name": OWNER_NAME, **extra}


# ---------------------------------------------------------------------------
# Helper JSON
# ---------------------------------------------------------------------------


def _json_response(objects, fields):
    """Serialisasi object/queryset ke JSON hanya dengan field yang diizinkan."""
    return HttpResponse(
        serializers.serialize(
            "json",
            objects,
            fields=fields,
            use_natural_foreign_keys=True,
        ),
        content_type="application/json",
    )


def _json_detail_response(model, pk, fields):
    """Respons JSON untuk satu objek; 404 tetap berbentuk JSON."""
    try:
        instance = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return JsonResponse(
            {"detail": f"{model._meta.verbose_name.title()} tidak ditemukan."},
            status=404,
        )
    return _json_response([instance], fields)


def _objects_from_json(json_response):
    """Deserialisasi respons JSON kembali menjadi list model instance."""
    payload = json_response.content.decode("utf-8")
    return [item.object for item in serializers.deserialize("json", payload)]


def _attach_education_star_state(request, education_list):
    """Tambahkan jumlah star dan status star user ke object hasil deserialisasi JSON."""
    education_ids = [item.pk for item in education_list]

    if not education_ids:
        return

    star_counts = dict(
        Education.objects.filter(pk__in=education_ids)
        .annotate(star_count=Count("starred_by"))
        .values_list("pk", "star_count")
    )

    starred_ids = set()
    if request.user.is_authenticated:
        starred_ids = set(
            Education.objects.filter(
                pk__in=education_ids,
                starred_by=request.user,
            ).values_list("pk", flat=True)
        )

    for education in education_list:
        education.star_count = star_counts.get(education.pk, 0)
        education.user_has_starred = education.pk in starred_ids


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
    """View generik halaman Create/Update berbasis ModelForm."""
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
    """Hapus instance hanya jika kode rahasia pada POST benar."""
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
    last_login = request.COOKIES.get(
        "last_login",
        "Belum ada sesi login / Cookie tidak ditemukan",
    )
    context = {
        "name": OWNER_NAME,
        "npm": "2506587150",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Fakultas Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan bisnis."
        ),
        "last_login": last_login,
    }
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

    return _json_response(experiences, EXPERIENCE_JSON_FIELDS)


@require_safe
def get_experience_detail_json(request, experience_id):
    """Satu pengalaman dalam JSON berdasarkan id (UUID)."""
    return _json_detail_response(Experience, experience_id, EXPERIENCE_JSON_FIELDS)


@require_safe
def show_experience(request):
    """Halaman Experience: data diambil dari JSON lalu dideserialisasi."""
    experiences = _objects_from_json(get_experience_json(request))

    context = _page_context(
        experience_list=experiences,
        title_query=request.GET.get("title", "").strip(),
    )
    return render(request, "experience.html", context)

@owner_required
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


@editor_or_owner_required
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


@owner_required
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

    return _json_response(education, EDUCATION_JSON_FIELDS)


@require_safe
def get_education_detail_json(request, education_id):
    """Satu riwayat pendidikan dalam JSON berdasarkan id (UUID)."""
    return _json_detail_response(Education, education_id, EDUCATION_JSON_FIELDS)


@require_safe
def show_education(request):
    """Halaman Education: data diambil dari JSON lalu dideserialisasi."""
    education = _objects_from_json(get_education_json(request))
    _attach_education_star_state(request, education)

    context = _page_context(
        education_list=education,
        nama_sekolah_query=request.GET.get("nama_sekolah", "").strip(),
    )
    return render(request, "education.html", context)


@owner_required
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


@editor_or_owner_required
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


@owner_required
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


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": OWNER_NAME,
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    context = {
        "name": OWNER_NAME,
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


# ---------------------------------------------------------------------------
# Star
# ---------------------------------------------------------------------------

@login_required
@require_POST
def toggle_star(request, education_id):
    """Toggle satu star per user pada Education tertentu."""
    education = get_object_or_404(Education, pk=education_id)

    if education.starred_by.filter(pk=request.user.pk).exists():
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)

    return redirect("main:show_education")
