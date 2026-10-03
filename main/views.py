"""View untuk aplikasi `main` (portofolio pribadi).

Hak akses (Pengunjung / Pengguna / Editor / Pemilik) diterapkan di sisi server
lewat decorator di `main.permissions`; template hanya menyembunyikan tombol
sebagai kenyamanan UI. Data yang tampil di halaman Experience dan Education
diambil dari endpoint JSON yang sama dengan yang dilihat klien API.
"""

import datetime
from io import BytesIO

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_safe
from xhtml2pdf import pisa

from main.forms import EducationForm, ExperienceForm, SecretCodeForm
from main.models import Education, Experience
from main.permissions import editor_or_owner_required, is_owner, owner_required

OWNER_NAME = "Adriel"

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
    require_secret=True,
):
    """View generik halaman Create/Update berbasis ModelForm.

    `require_secret=False` dipakai untuk Editor (otorisasi sudah lewat group).
    """
    is_post = request.method == "POST"
    form = form_class(
        request.POST if is_post else None,
        instance=instance,
        require_secret=require_secret,
    )

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
    """Halaman profil; menampilkan cookie `last_login` bila ada."""
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
    """Tambah pengalaman. Khusus pemilik (403 bagi Editor/Pengguna)."""
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
    """Ubah pengalaman. Editor atau pemilik; kode rahasia hanya diminta dari pemilik."""
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
        require_secret=request.user.is_superuser,
    )


@owner_required
@require_POST
def delete_experience(request, experience_id):
    """Hapus pengalaman (POST). Khusus pemilik dan wajib kode rahasia."""
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
    """Daftar education dalam JSON yang disusun manual (JsonResponse).

    Dipakai oleh halaman Education untuk memuat data lewat AJAX (fetch) dan
    sekaligus sebagai endpoint JSON Data Delivery. Query pencarian opsional:
    `?nama_sekolah=<kata kunci>` (tidak peka huruf besar/kecil).

    Selain field model, respons memuat info star dari Tugas 4:
        - star_count : jumlah pengguna yang memberi star.
        - is_starred : apakah pengguna yang sedang login sudah memberi star.
        - starred_by_names : daftar username pemberi star (untuk tooltip).
    """
    keyword = request.GET.get("nama_sekolah", "").strip()
    educations = Education.objects.all()

    if keyword:
        educations = educations.filter(nama_sekolah__icontains=keyword)

    # Sekali query: id education yang sudah diberi star oleh user saat ini.
    starred_pks = set()
    if request.user.is_authenticated:
        starred_pks = set(
            Education.objects.filter(starred_by=request.user).values_list("pk", flat=True)
        )

    data = []
    for education in educations.prefetch_related("starred_by"):
        starred_users = education.starred_by.all()

        data.append({
            "pk": str(education.pk),
            "fields": {
                "nama_sekolah": education.nama_sekolah,
                "tingkat": education.tingkat,
                "tingkat_display": education.get_tingkat_display(),
                "jurusan": education.jurusan,
                "tahun_masuk": education.tahun_masuk,
                "tahun_lulus": education.tahun_lulus,
                "deskripsi": education.deskripsi,
                "period_display": education.period_display,
                "is_ongoing": education.is_ongoing,
                "star_count": len(starred_users),
                "is_starred": education.pk in starred_pks,
                "starred_by_names": ", ".join(user.username for user in starred_users),
            },
        })

    return JsonResponse(data, safe=False)


@require_safe
def get_education_detail_json(request, education_id):
    """Satu riwayat pendidikan dalam JSON berdasarkan id (UUID)."""
    return _json_detail_response(Education, education_id, EDUCATION_JSON_FIELDS)


@require_safe
def show_education(request):
    """Kerangka halaman Education; datanya diambil klien lewat endpoint JSON.

    `form` hanya dibutuhkan oleh modal tambah education yang dirender untuk
    pemilik (superuser); pengguna lain mengabaikannya.
    """
    return render(
        request,
        "education.html",
        _page_context(form=EducationForm()),
    )


@owner_required
def create_education(request):
    """Tambah pendidikan. Khusus pemilik (403 bagi Editor/Pengguna)."""
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
    """Ubah pendidikan. Editor atau pemilik; kode rahasia hanya diminta dari pemilik."""
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
        require_secret=request.user.is_superuser,
    )


@owner_required
@require_POST
def delete_education(request, education_id):
    """Hapus pendidikan (POST). Khusus pemilik dan wajib kode rahasia."""
    education = get_object_or_404(Education, pk=education_id)

    return _delete_with_secret(
        request,
        education,
        success_url="main:show_education",
        success_message="Riwayat pendidikan berhasil dihapus!",
    )


# ---------------------------------------------------------------------------
# Education AJAX
# ---------------------------------------------------------------------------

@require_POST
def create_education_ajax(request):
    """Endpoint AJAX untuk modal tambah education pada halaman Education.

    Hak akses peran dari Tugas 4 diperiksa DI SINI (bukan hanya menyembunyikan
    tombol di template): hanya pemilik portofolio (superuser) yang boleh
    menambah data. Input divalidasi `EducationForm` (ModelForm) yang juga
    membersihkan teks dengan `strip_tags`.

    Balasan JSON:
        201 : berhasil, memuat `pk` data baru.
        400 : validasi gagal, memuat `errors` per field.
        403 : pemanggil bukan pemilik (pengunjung, pengguna, maupun editor).
    """
    if not is_owner(request.user):
        return JsonResponse(
            {"message": "Hanya pemilik portofolio yang dapat menambahkan education."},
            status=403,
        )

    form = EducationForm(request.POST)

    if not form.is_valid():
        return JsonResponse(
            {"errors": form.errors.get_json_data()},
            status=400,
        )

    education = form.save()
    return JsonResponse(
        {
            "message": "Education berhasil ditambahkan.",
            "pk": str(education.pk),
        },
        status=201,
    )


# ---------------------------------------------------------------------------
# Portfolio PDF
# ---------------------------------------------------------------------------

def download_portfolio_pdf(request):
    """Unduh ringkasan Experience dan Education sebagai PDF (publik)."""
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
    """Registrasi akun biasa (`UserCreationForm`); akun baru berperan Pengguna."""
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


def _safe_next_url(request):
    """Ambil parameter `next` hanya bila mengarah ke situs ini (cegah open redirect)."""
    next_url = request.POST.get("next") or request.GET.get("next", "")
    is_safe = url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )
    return next_url if is_safe else ""


def login_user(request):
    """Login bawaan Django, set cookie `last_login`, lalu kembali ke `?next=` bila aman."""
    form = AuthenticationForm(request, data=request.POST or None)
    next_url = _safe_next_url(request)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect(next_url or "main:show_main")
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    context = {
        "name": OWNER_NAME,
        "form": form,
        "next": next_url,
    }
    return render(request, "login.html", context)


def logout_user(request):
    """Logout, akhiri sesi, dan hapus cookie `last_login`."""
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


# ---------------------------------------------------------------------------
# Star
# ---------------------------------------------------------------------------


def _wants_json(request):
    """True bila request berasal dari fetch() halaman (bukan submit form biasa)."""
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@login_required
@require_POST
def toggle_star(request, education_id):
    """Toggle satu star per user pada Education tertentu (login + POST + CSRF).

    - Request dari JavaScript (header `X-Requested-With`): balas JSON
      `{"starred": bool, "star_count": int}` agar halaman diperbarui tanpa reload.
    - Submit form biasa (tanpa JS): redirect kembali ke halaman Education.
    """
    education = get_object_or_404(Education, pk=education_id)

    if education.starred_by.filter(pk=request.user.pk).exists():
        education.starred_by.remove(request.user)
        starred = False
    else:
        education.starred_by.add(request.user)
        starred = True

    if _wants_json(request):
        return JsonResponse(
            {"starred": starred, "star_count": education.starred_by.count()}
        )

    return redirect("main:show_education")