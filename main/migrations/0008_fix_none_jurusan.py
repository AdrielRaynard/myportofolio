"""Perbaikan data: jurusan yang tersimpan sebagai teks "None" menjadi NULL.

Regresi: clean_jurusan lama memanggil strip_tags(None) untuk input kosong
pada field nullable, sehingga jurusan kosong tersimpan sebagai teks "None".
"""

from django.db import migrations


def fix_none_jurusan(apps, schema_editor):
    """Ubah baris dengan jurusan tepat bernilai teks "None" menjadi NULL."""
    education = apps.get_model("main", "Education")
    education.objects.filter(jurusan="None").update(jurusan=None)


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0007_create_editor_group"),
    ]

    operations = [
        migrations.RunPython(fix_none_jurusan, migrations.RunPython.noop),
    ]