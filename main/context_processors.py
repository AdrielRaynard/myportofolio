"""Context processor: menyediakan informasi peran ke semua template."""


from .permissions import is_editor, is_owner


def roles(request):
    """Tambahkan `is_editor` dan `user_role` ke konteks template.

    - `is_editor`: dipakai `{% if user.is_superuser or is_editor %}` pada template.
    - `user_role`: label peran untuk badge navbar ("Owner", "Editor", "User");
    string kosong untuk pengunjung yang belum login.
    """
    user = request.user
    editor = is_editor(user)

    if is_owner(user):
        label = "Owner"
    elif editor:
        label = "Editor"
    elif user.is_authenticated:
        label = "User"
    else:
        label = ""

    return {"is_editor": editor, "user_role": label}