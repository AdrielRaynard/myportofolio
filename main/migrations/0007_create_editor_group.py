from django.db import migrations

EDITOR_GROUP_NAME = "Editor"


def create_editor_group(apps, schema_editor):
    """Pastikan group Editor selalu ada, termasuk di database baru.

    `db.sqlite3` tidak ikut repository, sehingga tanpa migrasi ini group harus
    dibuat manual di Django Admin. Keanggotaan tetap ditetapkan lewat Admin.
    """
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name=EDITOR_GROUP_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0006_education_starred_by_related_name"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        # Reverse sengaja no-op: group mungkin sudah punya anggota.
        migrations.RunPython(
            create_editor_group,
            migrations.RunPython.noop,
        ),
    ]