import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Education, Experience


class EducationAPITest(APITestCase):
    def setUp(self):
        Education.objects.all().delete()  # Isolasi dari data awal migrasi di database tes.
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.education = Education.objects.create(
            nama_sekolah="Sekolah Contoh", deskripsi="Deskripsi sekolah", tahun_masuk=2023,
        )
        self.list_url = reverse("api:education-list")
        self.detail_url = reverse("api:education-detail", args=[self.education.id])
        self.star_url = reverse("api:education-star", args=[self.education.id])
        self.payload = {
            "nama_sekolah": "Sekolah Baru", "deskripsi": "Deskripsi baru", "tahun_masuk": 2024,
            "tingkat": "S1", "jurusan": "Informatika", "tahun_lulus": None,
        }

    def test_public_list_and_detail(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.education.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)
        for url in (self.list_url, self.detail_url):
            self.assertEqual(self.client.options(url).status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.nama_sekolah, "Sekolah Contoh")
        self.assertEqual(Education.objects.count(), 1)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"nama_sekolah": "CONTOH"})
        self.assertEqual(len(response.data), 1)
        response = self.client.get(self.list_url, {"nama_sekolah": "not-found"})
        self.assertEqual(response.data, [])

    def test_missing_education(self):
        url = reverse("api:education-detail", args=[uuid.uuid4()])
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
            self.assertEqual(self.client.patch(self.detail_url, {"nama_sekolah": "Changed"}, format="json").status_code, 403)
            self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.assertEqual(Education.objects.count(), 1)
        self.education.refresh_from_db()
        self.assertEqual(self.education.nama_sekolah, "Sekolah Contoh")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Education.objects.filter(pk=response.data["id"]).exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)
        for changes, field in [
            ({"nama_sekolah": "   "}, "nama_sekolah"),
            ({"nama_sekolah": '<img src="x" onerror="alert(1)">'}, "nama_sekolah"),
            ({"tingkat": "bukan-jenjang"}, "tingkat"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)
        self.assertEqual(Education.objects.count(), 1)

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.detail_url, {"nama_sekolah": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.nama_sekolah, "Changed")
        self.assertEqual(self.education.deskripsi, "Deskripsi sekolah")
        response = self.client.put(self.detail_url, {"nama_sekolah": "Incomplete"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Education.objects.filter(pk=self.education.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)
        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "starred_by_names": "forged", "starred_by": [self.visitor.id],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["starred_by_names"], "")

    def test_staff_without_editor_group_cannot_update(self):
        self.visitor.is_staff = True
        self.visitor.save()
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"nama_sekolah": "Changed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_editor_can_update_but_cannot_create_or_delete(self):
        self.visitor.groups.add(Group.objects.get(name="Editor"))
        self.client.force_authenticate(user=self.visitor)
        response = self.client.patch(self.detail_url, {"deskripsi": "Revisi"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.education.refresh_from_db()
        self.assertEqual(self.education.deskripsi, "Revisi")
        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(self.list_url, self.payload, format="json").status_code, 403)
        self.assertEqual(self.client.delete(self.detail_url).status_code, 403)
        self.education.refresh_from_db()
        self.assertEqual(self.education.nama_sekolah, self.payload["nama_sekolah"])
        self.assertEqual(Education.objects.count(), 1)

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Education.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        client.login(username="owner", password="test-password")
        # The Browsable API form renders a real CSRF token into the response.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value
        response = client.post(
            self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ExperienceAPITest(APITestCase):
    """Kontrak REST API Experience untuk pengunjung, pengguna, Editor, dan pemilik."""

    def setUp(self):
        Experience.objects.all().delete()
        editor_group, _ = Group.objects.get_or_create(name="Editor")

        self.owner = User.objects.create_superuser(
            username="experience-owner",
            password="test-password",
            email="owner@example.com",
        )
        self.member = User.objects.create_user(
            username="experience-member",
            password="test-password",
        )
        self.editor = User.objects.create_user(
            username="experience-editor",
            password="test-password",
        )
        self.editor.groups.add(editor_group)
        self.experience = Experience.objects.create(
            title="Asisten Riset",
            description="Membantu pengolahan data penelitian.",
            category="research",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Magang Backend",
            "description": "Membangun layanan Django.",
            "category": "internship",
            "thumbnail": "https://example.com/magang.png",
        }

    def test_public_can_read_list_detail_and_search(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.experience.id))
        self.assertFalse(response.data[0]["is_starred"])
        self.assertEqual(response.data[0]["star_count"], 0)
        self.assertNotIn("starred_by", response.data[0])

        detail = self.client.get(self.detail_url)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.data["title"], self.experience.title)

        search = self.client.get(self.list_url, {"title": "RISET"})
        self.assertEqual([item["id"] for item in search.data], [str(self.experience.id)])
        self.assertEqual(
            self.client.get(
                reverse("api:experience-detail", args=[uuid.uuid4()])
            ).status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_guest_and_member_cannot_create_update_or_delete(self):
        for user in (None, self.member):
            with self.subTest(user=user):
                self.client.force_authenticate(user=user)
                self.assertEqual(
                    self.client.post(self.list_url, self.payload, format="json").status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    self.client.patch(
                        self.detail_url,
                        {"title": "Tidak Boleh Diubah"},
                        format="json",
                    ).status_code,
                    status.HTTP_403_FORBIDDEN,
                )
                self.assertEqual(
                    self.client.delete(self.detail_url).status_code,
                    status.HTTP_403_FORBIDDEN,
                )

        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Riset")

    def test_editor_can_put_and_patch_but_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        patched = self.client.patch(
            self.detail_url,
            {"description": "Revisi <em>Editor</em>."},
            format="json",
        )
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.description, "Revisi Editor.")

        replaced = self.client.put(
            self.detail_url,
            {**self.payload, "title": "Diperbarui Editor"},
            format="json",
        )
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.assertEqual(
            self.client.post(self.list_url, self.payload, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(self.detail_url).status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertEqual(Experience.objects.count(), 1)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Diperbarui Editor")

    def test_owner_can_create_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        created = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        created_id = created.data["id"]
        self.assertTrue(Experience.objects.filter(pk=created_id).exists())

        deleted = self.client.delete(
            reverse("api:experience-detail", args=[created_id])
        )
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Experience.objects.filter(pk=created_id).exists())

    def test_validation_strips_tags_and_rejects_invalid_input(self):
        self.client.force_authenticate(user=self.owner)
        original_count = Experience.objects.count()

        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "   "}, "description"),
            ({"category": "tidak-valid"}, "category"),
            ({"thumbnail": "bukan-url"}, "thumbnail"),
        ]:
            with self.subTest(changes=changes):
                response = self.client.post(
                    self.list_url,
                    {**self.payload, **changes},
                    format="json",
                )
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
                self.assertIn(field, response.data)

        created = self.client.post(
            self.list_url,
            {
                **self.payload,
                "title": "<strong>Pengalaman Aman</strong>",
                "description": "<p>Deskripsi Aman</p>",
                "is_finished": True,
            },
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["title"], "Pengalaman Aman")
        self.assertEqual(created.data["description"], "Deskripsi Aman")
        self.assertFalse(created.data["is_ongoing"])
        self.assertIsNotNone(created.data["ended_at"])
        self.assertEqual(Experience.objects.count(), original_count + 1)

    def test_patch_without_is_finished_preserves_finished_date(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        original_end = self.experience.ended_at
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            self.detail_url,
            {"title": "Judul Diperbarui"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.ended_at, original_end)

    def test_star_requires_login_is_scoped_to_request_user_and_toggles(self):
        rejected = self.client.post(self.star_url)
        self.assertEqual(rejected.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.experience.starred_by.count(), 0)

        self.client.force_authenticate(user=self.member)
        starred = self.client.post(self.star_url)
        self.assertTrue(starred.data["is_starred"])
        self.assertEqual(starred.data["star_count"], 1)

        self.client.force_authenticate(user=self.owner)
        other_user_view = self.client.get(self.detail_url)
        self.assertFalse(other_user_view.data["is_starred"])
        self.assertEqual(other_user_view.data["star_count"], 1)
        self.assertNotIn("experience-member", str(other_user_view.data))

        self.client.force_authenticate(user=self.member)
        unstarred = self.client.post(self.star_url)
        self.assertFalse(unstarred.data["is_starred"])
        self.assertEqual(unstarred.data["star_count"], 0)
        self.assertEqual(self.experience.starred_by.count(), 0)

    def test_computed_fields_cannot_be_forged(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.post(
            self.list_url,
            {
                **self.payload,
                "star_count": 99,
                "is_starred": True,
                "is_ongoing": False,
                "ended_at": "2030-01-01T00:00:00Z",
                "starred_by": [self.member.id],
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertTrue(response.data["is_ongoing"])
        self.assertIsNone(response.data["ended_at"])

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="experience-owner", password="test-password")
        )

        response = client.post(self.list_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

    def test_session_write_with_csrf_from_experience_page_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(
            client.login(username="experience-owner", password="test-password")
        )
        page = client.get(reverse("main:show_experience"))
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value

        response = client.post(
            self.list_url,
            self.payload,
            format="json",
            HTTP_X_CSRFTOKEN=token,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_list_rejects_delete_method(self):
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
