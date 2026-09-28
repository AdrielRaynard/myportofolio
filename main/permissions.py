"""Aturan hak akses (authorization) untuk aplikasi `main`.

Empat peran yang didukung:

    Pengunjung  : hanya membaca; aksi lain diarahkan ke halaman login.
    Pengguna    : membaca + memberi/membatalkan star.
    Editor      : hak Pengguna + mengubah data (anggota group `Editor`).
    Pemilik     : hak Editor + membuat dan menghapus data (superuser).

Pemeriksaan selalu dilakukan di sisi server. Menyembunyikan tombol di
template hanya untuk kenyamanan dan bukan pengganti decorator di bawah.
"""

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

EDITOR_GROUP_NAME = "Editor"


def is_owner(user):
    """True bila `user` adalah pemilik portofolio (superuser)."""
    return user.is_authenticated and user.is_superuser


def is_editor(user):
    """True bila `user` anggota group Editor (ditetapkan lewat Django Admin)."""
    return (
        user.is_authenticated
        and user.groups.filter(name=EDITOR_GROUP_NAME).exists()
    )


def can_edit(user):
    """True bila `user` boleh mengubah data: pemilik atau editor."""
    return is_owner(user) or is_editor(user)


def role_required(predicate):
    """Buat decorator view yang mensyaratkan login lalu `predicate(user)`.

    - Belum login  -> redirect ke `settings.LOGIN_URL` (302) dengan `?next=`.
    - Sudah login tetapi tidak berhak -> HTTP 403 (`PermissionDenied`).
    """

    def decorator(view_func):
        @login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not predicate(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


owner_required = role_required(is_owner)
"""Khusus pemilik: create dan delete."""


editor_or_owner_required = role_required(can_edit)
"""Editor atau pemilik: update."""