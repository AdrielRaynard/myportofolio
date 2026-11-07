from django.db import transaction
from django.db.models import BooleanField, Count, Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes,
)
from rest_framework.response import Response

from main.models import Education, Experience
from main.permissions import IsPortfolioOwnerOrEditorOrReadOnly
from main.serializers import EducationSerializer, ExperienceSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_list(request):
    if request.method in ("GET", "HEAD"):
        educations = Education.objects.prefetch_related("starred_by").order_by(
            "nama_sekolah", "id"
        )
        nama_sekolah = request.query_params.get("nama_sekolah", "").strip()
        if nama_sekolah:
            educations = educations.filter(nama_sekolah__icontains=nama_sekolah)

        serializer = EducationSerializer(
            educations, many=True, context={"request": request},
        )
        return Response(serializer.data)

    serializer = EducationSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def education_detail(request, education_id):
    education = get_object_or_404(
        Education.objects.prefetch_related("starred_by"), pk=education_id,
    )

    if request.method in ("GET", "HEAD"):
        serializer = EducationSerializer(education, context={"request": request})
        return Response(serializer.data)

    if request.method == "DELETE":
        education.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = EducationSerializer(
        education,
        data=request.data,
        partial=request.method == "PATCH",
        context={"request": request},
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)

@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def education_star(request, education_id):
    education = get_object_or_404(Education, pk=education_id)

    if education.starred_by.filter(pk=request.user.pk).exists():
        education.starred_by.remove(request.user)
    else:
        education.starred_by.add(request.user)

    serializer = EducationSerializer(education, context={"request": request})
    return Response(serializer.data)


def _experience_queryset(user):
    """Hitung jumlah dan status star dalam satu kueri untuk seluruh daftar."""
    is_starred = Value(False, output_field=BooleanField())
    if user.is_authenticated:
        user_stars = Experience.starred_by.through.objects.filter(
            experience_id=OuterRef("pk"), user_id=user.pk,
        )
        is_starred = Exists(user_stars)

    return Experience.objects.annotate(
        star_count=Count("starred_by"), is_starred=is_starred,
    ).order_by("-started_at", "pk")


@api_view(["GET", "HEAD", "POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_list(request):
    experiences = _experience_queryset(request.user)
    if request.method in ("GET", "HEAD"):
        title = request.query_params.get("title", "").strip()
        if title:
            experiences = experiences.filter(title__icontains=title)
        if request.query_params.get("starred") == "true":
            if request.user.is_authenticated:
                experiences = experiences.filter(starred_by=request.user)
            else:
                experiences = experiences.none()
        return Response(ExperienceSerializer(experiences, many=True).data)

    serializer = ExperienceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    experience = serializer.save()
    result = experiences.get(pk=experience.pk)
    return Response(ExperienceSerializer(result).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "HEAD", "PUT", "PATCH", "DELETE"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsPortfolioOwnerOrEditorOrReadOnly])
def experience_detail(request, experience_id):
    experience = get_object_or_404(_experience_queryset(request.user), pk=experience_id)
    if request.method in ("GET", "HEAD"):
        return Response(ExperienceSerializer(experience).data)

    if request.method == "DELETE":
        experience.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ExperienceSerializer(
        experience, data=request.data, partial=request.method == "PATCH",
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([SessionAuthentication])
@permission_classes([IsAuthenticated])
def experience_star(request, experience_id):
    with transaction.atomic():
        experience = get_object_or_404(
            Experience.objects.select_for_update(), pk=experience_id,
        )
        if experience.starred_by.filter(pk=request.user.pk).exists():
            experience.starred_by.remove(request.user)
        else:
            experience.starred_by.add(request.user)
        result = _experience_queryset(request.user).get(pk=experience.pk)
    return Response(ExperienceSerializer(result).data)
