from django.db import models

import uuid
from django.db import models

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class RiwayatPendidikan(models.Model):
    LEVEL_CHOICES = [
        ('smp', 'SMP'),
        ('sma', 'SMA/SMK'),
        ('s1', 'S1 (Sarjana)'),
        ('s2', 'S2 (Magister)'),
        ('s3', 'S3 (Doktor)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nama_sekolah = models.CharField(max_length=255)
    tingkat = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='s1')
    jurusan = models.CharField(max_length=255, blank=True, null=True)
    tahun_masuk = models.PositiveIntegerField()
    tahun_lulus = models.PositiveIntegerField(blank=True, null=True)
    deskripsi = models.TextField(blank=True)

    class Meta:
        ordering = ['-tahun_masuk']

    def __str__(self):
        return f"{self.get_tingkat_display()} - {self.nama_sekolah}"

    @property
    def is_ongoing(self):
        return self.tahun_lulus is None

    @property
    def period_display(self):
        if self.is_ongoing:
            return f"{self.tahun_masuk} - Sekarang"
        return f"{self.tahun_masuk} - {self.tahun_lulus}"
