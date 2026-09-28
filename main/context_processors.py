"""Context processor: menyediakan informasi peran ke semua template."""

from main.permissions import is_editor


def roles(request):
    """Tambahkan `is_editor` agar template bisa memakai `{% if user.is_superuser or is_editor %}`."""
    return {"is_editor": is_editor(request.user)}