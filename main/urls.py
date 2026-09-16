from django.urls import path

from main.views import (
    show_main,
    show_experience,
    show_education,
    download_portfolio_pdf,
    create_education,
    get_education_json,
    delete_education,
)

app_name = "main"

urlpatterns = [ 
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("portfolio/pdf/", download_portfolio_pdf, name="download_portfolio_pdf"),
    path("education/add/", create_education, name="create_education"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),
]