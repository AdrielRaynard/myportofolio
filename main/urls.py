from django.urls import path

from main.views import (
    create_education,
    delete_education,
    download_portfolio_pdf,
    get_education_json,
    get_experience_detail_json,
    get_experience_json,
    show_education,
    show_experience,
    show_main,
)

app_name = "main"

urlpatterns = [ 
    # Halaman
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("portfolio/pdf/", download_portfolio_pdf, name="download_portfolio_pdf"),

    # Education: form dan API
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),

    # JSON Data Delivery
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("api/experience/<uuid:experience_id>/", get_experience_detail_json, name="get_experience_detail_json"),
    path("api/education/", get_education_json, name="get_education_json"),
]