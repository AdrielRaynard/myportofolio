from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education


class EducationSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Education
        fields = [
            "id", "nama_sekolah", "tingkat", "jurusan",
            "tahun_masuk", "tahun_lulus", "deskripsi",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    def validate_nama_sekolah(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama sekolah tidak boleh kosong.")
        return value

    def validate_deskripsi(self, value):
        return strip_tags(value)

    def validate_jurusan(self, value):
        return strip_tags(value) if value is not None else None

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())