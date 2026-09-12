import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RiwayatPendidikan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nama_sekolah', models.CharField(max_length=255)),
                ('tingkat', models.CharField(choices=[('smp', 'SMP'), ('sma', 'SMA/SMK'), ('s1', 'S1 (Sarjana)'), ('s2', 'S2 (Magister)'), ('s3', 'S3 (Doktor)')], default='s1', max_length=10)),
                ('jurusan', models.CharField(blank=True, max_length=255, null=True)),
                ('tahun_masuk', models.PositiveIntegerField()),
                ('tahun_lulus', models.PositiveIntegerField(blank=True, null=True)),
                ('deskripsi', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['-tahun_masuk'],
            },
        ),
    ]