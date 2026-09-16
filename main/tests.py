from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Education


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Staff Operasional Open House Fasilkom UI 2025",
            description="Membantu tim operasional panitia untuk mengatur event.",
            category="kepanitiaan",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Staff Operasional Open House Fasilkom UI 2025")
        self.assertEqual(self.experience.category, "kepanitiaan")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "kepanitiaan")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")


class EducationTest(TestCase):
    def setUp(self):
        Education.objects.all().delete()
        self.education = Education.objects.create(
            nama_sekolah="Universitas Contoh Testing",
            tingkat="s2",
            jurusan="Ilmu Komputer",
            tahun_masuk=2023,
            deskripsi="Menempuh studi magister sebagai bahan testing otomatis.",
        )

    def test_education_url_is_accessible_and_uses_correct_template(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")

    def test_education_model(self):
        self.assertEqual(
            str(self.education),
            f"{self.education.get_tingkat_display()} - {self.education.nama_sekolah}",
        )
        self.assertTrue(self.education.is_ongoing)
        self.assertEqual(self.education.period_display, "2023 - Sekarang")

    def test_education_page_shows_data_when_available(self):
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, self.education.nama_sekolah)
        self.assertContains(response, self.education.jurusan)
        self.assertContains(response, self.education.deskripsi)
        self.assertContains(response, "Sedang berlangsung")
        self.assertNotContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")

    def test_education_page_shows_empty_state_when_no_data(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")

    def test_completed_education_status(self):
        self.education.tahun_lulus = 2025
        self.education.save()
        response = self.client.get(reverse("main:show_education"))

        self.assertFalse(self.education.is_ongoing)
        self.assertEqual(self.education.period_display, "2023 - 2025")
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_navbar_has_education_link_on_other_pages(self):
        education_url = reverse("main:show_education")
        main_response = self.client.get(reverse("main:show_main"))
        experience_response = self.client.get(reverse("main:show_experience"))

        self.assertContains(main_response, f'href="{education_url}"')
        self.assertContains(experience_response, f'href="{education_url}"')
        

class PortfolioPdfTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Contoh Pengalaman untuk PDF",
            description="Deskripsi pengalaman untuk keperluan testing PDF.",
            category="internship",
        )
        self.education = Education.objects.create(
            nama_sekolah="Universitas Contoh PDF",
            tingkat="S1",
            jurusan="Sistem Informasi",
            tahun_masuk=2023,
        )

    def test_download_pdf_url_is_accessible_and_returns_pdf(self):
        response = self.client.get(reverse("main:download_portfolio_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn("attachment", response["Content-Disposition"])
        self.assertIn("portfolio-adriel.pdf", response["Content-Disposition"])

    def test_download_pdf_works_when_data_is_empty(self):
        Experience.objects.all().delete()
        Education.objects.all().delete()
        response = self.client.get(reverse("main:download_portfolio_pdf"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_navbar_has_download_pdf_link(self):
        pdf_url = reverse("main:download_portfolio_pdf")
        main_response = self.client.get(reverse("main:show_main"))
        experience_response = self.client.get(reverse("main:show_experience"))
        education_response = self.client.get(reverse("main:show_education"))

        self.assertContains(main_response, f'href="{pdf_url}"')
        self.assertContains(experience_response, f'href="{pdf_url}"')
        self.assertContains(education_response, f'href="{pdf_url}"')