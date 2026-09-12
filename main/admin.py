from django.contrib import admin

from main.models import RiwayatPendidikan

@admin.register(RiwayatPendidikan)
class RiwayatPendidikanAdmin(admin.ModelAdmin):
    list_display = ("nama_sekolah", "tingkat", "jurusan", "tahun_masuk", "tahun_lulus")
    list_filter = ("tingkat",)
    ordering = ("-tahun_masuk",)