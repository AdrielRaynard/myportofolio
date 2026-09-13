from django.db import migrations


RIWAYATPENDIDIKAN_SEED_DATA = [
    {
        "nama_sekolah": "SMPK PENABUR Bintaro Jaya",
        "tingkat": "smp",
        "jurusan": None,
        "tahun_masuk": 2019,
        "tahun_lulus": 2022,
        "deskripsi": "Menyelesaikan pendidikan jenjang menengah pertama.",
    },
    {
        "nama_sekolah": "SMAK PENABUR Bintaro Jaya",
        "tingkat": "sma",
        "jurusan": "Matematika dan Ilmu Pengetahuan Alam (MIPA)",
        "tahun_masuk": 2022,
        "tahun_lulus": 2025,
        "deskripsi": "Menyelesaikan pendidikan jenjang menengah atas dengan fokus pada matematika dan ilmu pengetahuan alam.",
    },
    {
        "nama_sekolah": "Fakultas Ilmu Komputer, Universitas Indonesia",
        "tingkat": "S1",
        "jurusan": "Sistem Informasi",
        "tahun_masuk": 2025,
        "tahun_lulus": 2029,
        "deskripsi": "Sedang menempuh studi S1 Sistem Informasi di Fakultas Ilmu Komputer Universitas Indonesia.",
    },
]


def seed_riwayat_pendidikan(apps, schema_editor):
    RiwayatPendidikan = apps.get_model("main", "RiwayatPendidikan")
    for entry in RIWAYATPENDIDIKAN_SEED_DATA:
        RiwayatPendidikan.objects.create(**entry)


def remove_seeded_riwayat_pendidikan(apps, schema_editor):
    RiwayatPendidikan = apps.get_model("main", "RiwayatPendidikan")
    names = [entry["nama_sekolah"] for entry in RIWAYATPENDIDIKAN_SEED_DATA]
    RiwayatPendidikan.objects.filter(nama_sekolah__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_riwayatpendidikan'),
    ]

    operations = [
        migrations.RunPython(seed_riwayat_pendidikan, remove_seeded_riwayat_pendidikan),
    ]