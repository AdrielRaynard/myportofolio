from django import forms

from django.forms import ModelForm, TextInput, Textarea, NumberInput, Select

from main.models import Education

from django.conf import settings

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