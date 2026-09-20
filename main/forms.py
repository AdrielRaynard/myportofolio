"""Form untuk aplikasi `main`.

Isi berkas:
    - SecretCodeField / SecretCodeForm : validasi kode rahasia (lihat catatan keamanan).
    - ExperienceForm                   : Create & Update pengalaman.
    - EducationForm                    : Create & Update pendidikan.

Catatan keamanan:
    Situs ini publik, sehingga setiap aksi tulis (tambah, ubah, hapus) harus
    menyertakan kode rahasia yang sama dengan `PORTFOLIO_SECRET` pada `.env`.
"""
import hmac

from django import forms
from django.conf import settings

from django.core.exceptions import ValidationError
from django.forms import ModelForm, NumberInput, Select, Textarea, TextInput, URLInput
from django.utils import timezone

from main.models import Education, Experience


class SecretCodeField(forms.CharField):
    """Field password yang otomatis tervalidasi terhadap `settings.PORTFOLIO_SECRET`.

    Validasi ada di dalam field (bukan `clean_<nama>` pada form) sehingga otomatis
    berlaku di form mana pun yang memakainya, termasuk form konfirmasi hapus.
    Bila `PORTFOLIO_SECRET` belum diatur, SEMUA input ditolak (fail closed).
    """

    default_error_messages = {"invalid_secret": "Kode rahasia salah."}

    def __init__(self, **kwargs):
        kwargs.setdefault("label", "Kode Rahasia")
        kwargs.setdefault("strip", False)
        kwargs.setdefault("widget", forms.PasswordInput(attrs={"autocomplete": "off"}))
        super().__init__(**kwargs)

    def validate(self, value):
        super().validate(value)  # menangani "wajib diisi"

        expected = getattr(settings, "PORTFOLIO_SECRET", None)
        # compare_digest: perbandingan waktu-konstan agar tidak bocor lewat timing.
        if not expected or not hmac.compare_digest(value.encode(), expected.encode()):
            raise ValidationError(
                self.error_messages["invalid_secret"], code="invalid_secret"
            )


class SecretCodeForm(forms.Form):
    """Form minimal untuk aksi yang hanya butuh kode rahasia (mis. hapus data)."""

    secret = SecretCodeField()


class ExperienceForm(ModelForm):
    """Form tambah/ubah pengalaman.

    Field model : title (Char), description (Text), category (pilihan), thumbnail (URL).
    Field form  : is_finished (Boolean) dan secret (password).

    `started_at`/`ended_at` sengaja TIDAK ada di `Meta.fields` karena berupa
    timestamp. Status selesai diatur lewat checkbox `is_finished`, lalu
    `save()` menerjemahkannya menjadi nilai `ended_at`.
    """

    is_finished = forms.BooleanField(
        label="Pengalaman ini sudah selesai",
        required=False,
        help_text="Centang jika sudah tidak dijalani lagi. Kosongkan jika masih berlangsung.",
    )
    secret = SecretCodeField()

    class Meta:
        model = Experience
        fields = ["title", "description", "category", "thumbnail"]
        labels = {
            "title": "Judul Pengalaman",
            "description": "Deskripsi",
            "category": "Kategori",
            "thumbnail": "URL Gambar (opsional)",
        }
        widgets = {
            "title": TextInput(
                attrs={"placeholder": "Staff Operasional Open House", "maxlength": 255}
            ),
            "description": Textarea(
                attrs={"placeholder": "Ceritakan peran dan kontribusimu", "rows": 4}
            ),
            "category": Select(),
            "thumbnail": URLInput(attrs={"placeholder": "https://contoh.com/gambar.png"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Saat mengubah data lama, centang otomatis sesuai status tersimpan.
        if not self.instance._state.adding:
            self.fields["is_finished"].initial = not self.instance.is_ongoing

    def save(self, commit=True):
        experience = super().save(commit=False)

        if self.cleaned_data["is_finished"]:
            # Pertahankan tanggal selesai lama agar edit ulang tidak menggesernya.
            experience.ended_at = experience.ended_at or timezone.now()
        else:
            experience.ended_at = None

        if commit:
            experience.save()
        return experience

class EducationForm(ModelForm):
    secret = forms.CharField(
        label="Kode Rahasia",
        widget=forms.PasswordInput
)

    class Meta:
        model = Education
        fields = [
        "nama_sekolah",
        "tingkat",
        "jurusan",
        "tahun_masuk",
        "tahun_lulus",
        "deskripsi",
]


        labels = {
        "nama_sekolah": "Nama Sekolah / Universitas",
        "tingkat": "Tingkat Pendidikan",
        "jurusan": "Jurusan",
        "tahun_masuk": "Tahun Masuk",
        "tahun_lulus": "Tahun Lulus",
        "deskripsi": "Deskripsi Pendidikan",
    }

        widgets = {
        "nama_sekolah": TextInput(
            attrs={
                "placeholder": "Universitas Indonesia",
                "maxlength": 255,
            }
        ),
        "tingkat": Select(
            attrs={
                "placeholder": "Pilih tingkat pendidikan",
            }
        ),
        "jurusan": TextInput(
            attrs={
                "placeholder": "Sistem Informasi",
                "maxlength": 255,
            }
        ),
        "tahun_masuk": NumberInput(
            attrs={
                "placeholder": "2025",
                "min": 1900,
                "max": 2100,
            }
        ),
        "tahun_lulus": NumberInput(
            attrs={
                "placeholder": "2029",
                "min": 1900,
                "max": 2100,
            }
        ),
        "deskripsi": Textarea(
            attrs={
                "placeholder": "Ceritakan pengalaman pendidikanmu",
                "rows": 3,
            }
        ),
    }

def clean_secret(self):
    secret = self.cleaned_data["secret"]

    if secret != settings.PORTFOLIO_SECRET:
        raise forms.ValidationError("Kode rahasia salah.")

    return secret