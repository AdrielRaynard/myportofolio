from django.urls import path

from main.views import (
    create_education,
    create_experience,
    delete_education,
    delete_experience,
    download_portfolio_pdf,
    get_education_detail_json,
    get_education_json,
    get_experience_detail_json,
    get_experience_json,
    show_education,
    show_experience,
    show_main,
    update_education,
    update_experience,
    register,
    login_user,
    logout_user,
    toggle_star,
)

app_name = "main"

urlpatterns = [ 
    # Halaman
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("education/", show_education, name="show_education"),
    path("portfolio/pdf/", download_portfolio_pdf, name="download_portfolio_pdf"),

    # Experience: form & aksi
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),

    # Education: form & aksi
    path("education/add/", create_education, name="create_education"),
    path("education/<uuid:education_id>/edit/", update_education, name="update_education"),
    path("education/<uuid:education_id>/delete/", delete_education, name="delete_education"),

    # JSON Data Delivery (/api/... = endpoint untuk klien, bukan halaman)
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("api/experience/<uuid:experience_id>/", get_experience_detail_json, name="get_experience_detail_json"),
    path("api/education/", get_education_json, name="get_education_json"),
    path("api/education/<uuid:education_id>/", get_education_detail_json, name="get_education_detail_json"),

    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),

    path(
    "educations/<uuid:education_id>/star/", toggle_star, name="toggle_star"),
]