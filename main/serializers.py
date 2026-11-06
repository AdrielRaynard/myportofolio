from django.utils import timezone
from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Education, Experience


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


class ExperienceSerializer(serializers.ModelSerializer):
    star_count = serializers.IntegerField(read_only=True)
    is_starred = serializers.BooleanField(read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    is_finished = serializers.BooleanField(write_only=True, default=False)

    class Meta:
        model = Experience
        fields = [
            "id", "title", "description", "category", "thumbnail",
            "started_at", "ended_at", "is_ongoing", "is_finished",
            "star_count", "is_starred",
        ]
        read_only_fields = ["id", "started_at", "ended_at"]
        extra_kwargs = {
            "category": {"default": "full-time"},
            "thumbnail": {"default": None},
        }

    def validate_title(self, value):
        return self._plain_text(value)

    def validate_description(self, value):
        return self._plain_text(value)

    @staticmethod
    def _plain_text(value):
        text = strip_tags(value).strip()
        if not text:
            raise serializers.ValidationError("Masukkan teks yang tidak kosong.")
        return text

    def validate(self, attrs):
        # PATCH yang hanya mengubah teks harus mempertahankan tanggal selesai.
        if "is_finished" in attrs:
            finished = attrs.pop("is_finished")
            if finished:
                previous_end = self.instance.ended_at if self.instance else None
                attrs["ended_at"] = previous_end or timezone.now()
            else:
                attrs["ended_at"] = None
        return attrs
