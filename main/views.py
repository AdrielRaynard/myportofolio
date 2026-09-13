from django.shortcuts import render

from main.models import Experience, Education


def show_main(request):
    context = {
        "name": "Adriel",
        "npm": "2506587150",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Mahasiswa Sistem Informasi Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Adriel",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Adriel",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)