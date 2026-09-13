from django.contrib import admin

from main.models import Education

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("nama_sekolah", "tingkat", "jurusan", "tahun_masuk", "tahun_lulus")
    list_filter = ("tingkat",)
    ordering = ("-tahun_masuk",)