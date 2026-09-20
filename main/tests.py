import json
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from django.contrib.messages import constants as message_levels
from django.contrib.messages.storage.base import Message
from django.core import serializers
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from main.forms import ExperienceForm, SecretCodeField, SecretCodeForm
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
        self.assertContains(response, "Kepanitiaan")
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


class BaseTemplateInheritanceTest(TestCase):
    """Semua halaman HTML yang strukturnya identik harus memakai base.html."""

    PAGE_URL_NAMES = [
        "main:show_main",
        "main:show_experience",
        "main:show_education",
        "main:create_education",
    ]

    def test_every_page_extends_base_template(self):
        for url_name in self.PAGE_URL_NAMES:
            with self.subTest(page=url_name):
                response = self.client.get(reverse(url_name))

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "base.html")

    def test_every_page_has_exactly_one_document_skeleton(self):
        """Tidak boleh ada skeleton HTML ganda (sisa copy-paste sebelum refactor)."""
        for url_name in self.PAGE_URL_NAMES:
            with self.subTest(page=url_name):
                html = self.client.get(reverse(url_name)).content.decode()

                self.assertEqual(html.count("<html"), 1)
                self.assertEqual(html.count("<title>"), 1)
                self.assertEqual(html.count('class="site-header"'), 1)
                self.assertEqual(html.count('class="site-footer"'), 1)

    def test_theme_toggle_checkbox_precedes_site_wrapper_on_every_page(self):
        """CSS checkbox hack: checkbox harus ada dan berada SEBELUM .site-wrapper."""
        for url_name in self.PAGE_URL_NAMES:
            with self.subTest(page=url_name):
                html = self.client.get(reverse(url_name)).content.decode()

                self.assertEqual(html.count('id="theme-toggle"'), 1)
                self.assertEqual(html.count('class="site-wrapper"'), 1)
                self.assertLess(
                    html.index('id="theme-toggle"'),
                    html.index('class="site-wrapper"'),
                )

    def test_pdf_template_is_intentionally_standalone(self):
        """Template PDF punya struktur berbeda, jadi tidak boleh membawa navbar/tema web."""
        html = render_to_string("portfolio_pdf.html", {"name": "Adriel"})

        self.assertNotIn("theme-toggle", html)
        self.assertNotIn("site-header", html)


class FlashMessageTest(TestCase):
    def test_messages_component_renders_level_class(self):
        html = render_to_string(
            "components/messages.html",
            {"messages": [Message(message_levels.SUCCESS, "Data tersimpan!")]},
        )

        self.assertIn("Data tersimpan!", html)
        self.assertIn("message--success", html)

    def test_messages_component_renders_nothing_without_messages(self):
        html = render_to_string("components/messages.html", {"messages": []})

        self.assertNotIn("message", html)

    @override_settings(PORTFOLIO_SECRET="rahasia-test")
    def test_success_message_is_displayed_after_redirect(self):
        response = self.client.post(
            reverse("main:create_education"),
            {
                "nama_sekolah": "Sekolah Uji Flash",
                "tingkat": "S1",
                "tahun_masuk": 2020,
                "secret": "rahasia-test",
            },
            follow=True,
        )

        self.assertContains(response, "Pendidikan baru berhasil ditambahkan!")
        self.assertContains(response, "message--success")

class ExperienceJsonTest(TestCase):
    """JSON Data Delivery untuk Experience + halaman yang mengonsumsinya."""

    def setUp(self):
        Experience.objects.all().delete()
        self.older = Experience.objects.create(
            title="Asisten Dosen Dasar-Dasar Pemrograman",
            description="Membimbing mahasiswa baru belajar Python.",
            category="volunteer",
        )
        self.newer = Experience.objects.create(
            title="Magang Backend Developer",
            description="Membangun REST API dengan Django.",
            category="internship",
            thumbnail="https://example.com/magang.png",
        )

    def get_json(self, url_name, *args, **params):
        response = self.client.get(reverse(url_name, args=args), params)
        return response, json.loads(response.content)

    def test_list_endpoint_returns_json_with_serialized_fields(self):
        response, data = self.get_json("main:get_experience_json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertEqual(item["model"], "main.experience")
            self.assertEqual(
                set(item["fields"]),
                {"title", "description", "category", "thumbnail", "started_at", "ended_at"},
            )

    def test_list_is_ordered_newest_first(self):
        _, data = self.get_json("main:get_experience_json")

        self.assertEqual([item["pk"] for item in data], [str(self.newer.pk), str(self.older.pk)])

    def test_list_can_be_filtered_by_title_case_insensitively(self):
        _, data = self.get_json("main:get_experience_json", title="  backend ")

        self.assertEqual([item["pk"] for item in data], [str(self.newer.pk)])

    def test_filter_without_match_returns_empty_list(self):
        _, data = self.get_json("main:get_experience_json", title="tidak-ada")

        self.assertEqual(data, [])

    def test_detail_endpoint_returns_single_experience(self):
        response, data = self.get_json("main:get_experience_detail_json", self.newer.pk)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["fields"]["title"], "Magang Backend Developer")

    def test_detail_endpoint_returns_json_404_for_unknown_id(self):
        response, data = self.get_json(
            "main:get_experience_detail_json", "00000000-0000-0000-0000-000000000000"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("tidak ditemukan", data["detail"])

    def test_json_endpoints_are_read_only(self):
        response = self.client.post(reverse("main:get_experience_json"))

        self.assertEqual(response.status_code, 405)

    def test_page_context_holds_deserialized_model_instances(self):
        response = self.client.get(reverse("main:show_experience"))

        experiences = response.context["experience_list"]
        self.assertEqual(len(experiences), 2)
        self.assertTrue(all(isinstance(item, Experience) for item in experiences))
        self.assertEqual(experiences[0].pk, self.newer.pk)

    def test_page_renders_data_delivered_by_the_json_endpoint(self):
        """Bukti halaman memakai JSON: data yang hanya ada di JSON tetap tampil."""
        only_in_json = Experience(
            title="Hanya Ada Di Respons JSON", description="Tidak disimpan ke DB.", category="research"
        )
        fake_response = HttpResponse(
            serializers.serialize("json", [only_in_json]), content_type="application/json"
        )

        with mock.patch("main.views.get_experience_json", return_value=fake_response):
            response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Hanya Ada Di Respons JSON")
        self.assertNotContains(response, self.newer.title)

    def test_page_search_filters_and_shows_query(self):
        response = self.client.get(reverse("main:show_experience"), {"title": "Asisten"})

        self.assertContains(response, self.older.title)
        self.assertNotContains(response, self.newer.title)
        self.assertContains(response, 'value="Asisten"')

    def test_page_search_without_match_shows_specific_empty_state(self):
        response = self.client.get(reverse("main:show_experience"), {"title": "xyz"})

        self.assertContains(response, "Tidak ada pengalaman dengan judul tersebut.")

    def test_page_shows_thumbnail_only_when_available(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, 'src="https://example.com/magang.png"')
        self.assertEqual(response.content.decode().count("experience-thumbnail"), 1)

    def test_page_only_accepts_safe_methods(self):
        response = self.client.post(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 405)

    def test_categories_used_by_existing_data_are_valid_choices(self):
        """`kepanitiaan` & `organisasi` dipakai data nyata dan harus ada di choices."""
        valid = {value for value, _ in Experience.EXPERIENCE_CHOICES}

        self.assertTrue({"kepanitiaan", "organisasi"} <= valid)


class EducationJsonTest(TestCase):
    def setUp(self):
        Education.objects.all().delete()
        self.ui = Education.objects.create(
            nama_sekolah="Universitas Indonesia", tingkat="S1", tahun_masuk=2025
        )
        Education.objects.create(nama_sekolah="SMAK Contoh", tingkat="sma", tahun_masuk=2022)

    def test_education_json_lists_all_and_filters_by_school_name(self):
        all_data = json.loads(self.client.get(reverse("main:get_education_json")).content)
        filtered = json.loads(
            self.client.get(reverse("main:get_education_json"), {"nama_sekolah": "indonesia"}).content
        )

        self.assertEqual(len(all_data), 2)
        self.assertEqual([item["pk"] for item in filtered], [str(self.ui.pk)])

    def test_education_json_is_read_only(self):
        response = self.client.post(reverse("main:get_education_json"))
                
        self.assertEqual(response.status_code, 405)


SECRET = "rahasia-test"


@override_settings(PORTFOLIO_SECRET=SECRET)
class SecretCodeFieldTest(TestCase):
    def test_correct_secret_is_accepted(self):
        self.assertEqual(SecretCodeField().clean(SECRET), SECRET)

    def test_wrong_secret_is_rejected(self):
        with self.assertRaises(ValidationError) as ctx:
            SecretCodeField().clean("salah")

        self.assertEqual(ctx.exception.code, "invalid_secret")

    def test_empty_secret_is_rejected_as_required(self):
        with self.assertRaises(ValidationError) as ctx:
            SecretCodeField().clean("")

        self.assertEqual(ctx.exception.code, "required")

    def test_secret_is_compared_exactly_without_stripping(self):
        with self.assertRaises(ValidationError):
            SecretCodeField().clean(f" {SECRET} ")

    @override_settings(PORTFOLIO_SECRET=None)
    def test_fails_closed_when_secret_is_not_configured(self):
        """Tanpa PORTFOLIO_SECRET di .env, tidak boleh ada input yang lolos."""
        for candidate in ("apa-saja", "None", "x"):
            with self.subTest(candidate=candidate):
                with self.assertRaises(ValidationError):
                    SecretCodeField().clean(candidate)

    def test_secret_form_validates_via_the_field(self):
        self.assertTrue(SecretCodeForm({"secret": SECRET}).is_valid())
        self.assertFalse(SecretCodeForm({"secret": "salah"}).is_valid())

    def test_secret_widget_never_renders_the_submitted_value(self):
        html = str(SecretCodeForm({"secret": "salah"})["secret"])

        self.assertIn('type="password"', html)
        self.assertNotIn("salah", html)


@override_settings(PORTFOLIO_SECRET=SECRET)
class ExperienceFormTest(TestCase):
    def valid_data(self, **overrides):
        data = {
            "title": "Asisten Dosen",
            "description": "Membimbing mahasiswa baru.",
            "category": "volunteer",
            "thumbnail": "",
            "secret": SECRET,
        }
        data.update(overrides)
        return data

    def test_model_fields_exclude_id_and_timestamps(self):
        self.assertEqual(
            ExperienceForm.Meta.fields, ["title", "description", "category", "thumbnail"]
        )
        for excluded in ("id", "started_at", "ended_at"):
            self.assertNotIn(excluded, ExperienceForm().fields)

    def test_form_uses_varied_field_types(self):
        types = {name: type(f).__name__ for name, f in ExperienceForm().fields.items()}

        self.assertEqual(types["title"], "CharField")
        self.assertEqual(types["description"], "CharField")  # TextField -> Textarea
        self.assertEqual(types["category"], "TypedChoiceField")
        self.assertEqual(types["thumbnail"], "URLField")
        self.assertEqual(types["is_finished"], "BooleanField")

    def test_valid_data_creates_ongoing_experience(self):
        form = ExperienceForm(self.valid_data())

        self.assertTrue(form.is_valid(), form.errors)
        experience = form.save()
        self.assertTrue(experience.is_ongoing)
        self.assertIsNone(experience.thumbnail)

    def test_is_finished_sets_ended_at(self):
        form = ExperienceForm(self.valid_data(is_finished="on"))

        self.assertTrue(form.is_valid(), form.errors)
        experience = form.save()
        self.assertFalse(experience.is_ongoing)
        self.assertIsNotNone(experience.ended_at)

    def test_editing_finished_experience_keeps_original_end_date(self):
        ended = timezone.now() - timezone.timedelta(days=30)
        experience = Experience.objects.create(
            title="Lama", description="d", category="research", ended_at=ended
        )

        form = ExperienceForm(self.valid_data(is_finished="on"), instance=experience)
        form.is_valid()
        form.save()

        experience.refresh_from_db()
        self.assertEqual(experience.ended_at, ended)

    def test_unchecking_is_finished_reopens_the_experience(self):
        experience = Experience.objects.create(
            title="Lama", description="d", category="research", ended_at=timezone.now()
        )

        form = ExperienceForm(self.valid_data(), instance=experience)
        form.is_valid()
        form.save()

        experience.refresh_from_db()
        self.assertTrue(experience.is_ongoing)

    def test_edit_form_prechecks_is_finished_from_saved_state(self):
        finished = Experience.objects.create(
            title="A", description="d", category="research", ended_at=timezone.now()
        )
        ongoing = Experience.objects.create(title="B", description="d", category="research")

        self.assertTrue(ExperienceForm(instance=finished).fields["is_finished"].initial)
        self.assertFalse(ExperienceForm(instance=ongoing).fields["is_finished"].initial)
        self.assertIsNone(ExperienceForm().fields["is_finished"].initial)

    def test_invalid_input_is_rejected_per_field(self):
        cases = {
            "title": ("", "required"),
            "description": ("", "required"),
            "category": ("bukan-kategori", "invalid_choice"),
            "thumbnail": ("bukan url", "invalid"),
            "secret": ("salah", "invalid_secret"),
        }
        for field, (value, code) in cases.items():
            with self.subTest(field=field):
                form = ExperienceForm(self.valid_data(**{field: value}))

                self.assertFalse(form.is_valid())
                self.assertEqual(form.errors.as_data()[field][0].code, code)


@override_settings(PORTFOLIO_SECRET=SECRET)
class ExperienceCrudViewTest(TestCase):
    def setUp(self):
        Experience.objects.all().delete()
        self.experience = Experience.objects.create(
            title="Staff Operasional",
            description="Membantu tim operasional.",
            category="kepanitiaan",
        )

    def payload(self, **overrides):
        data = {
            "title": "Magang Backend",
            "description": "Membangun REST API.",
            "category": "internship",
            "thumbnail": "https://example.com/a.png",
            "secret": SECRET,
        }
        data.update(overrides)
        return data

    # --- Create ---
    def test_create_page_renders_generic_form_with_all_fields(self):
        response = self.client.get(reverse("main:create_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form_page.html")
        for name in ("title", "description", "category", "thumbnail", "is_finished", "secret"):
            self.assertContains(response, f'name="{name}"')
        self.assertContains(response, 'type="password"')

    def test_create_saves_redirects_and_shows_flash_message(self):
        response = self.client.post(
            reverse("main:create_experience"), self.payload(), follow=True
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Magang Backend").exists())
        self.assertContains(response, "Pengalaman baru berhasil ditambahkan!")

    def test_create_with_wrong_secret_saves_nothing_and_shows_error(self):
        response = self.client.post(
            reverse("main:create_experience"), self.payload(secret="salah")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kode rahasia salah.")
        self.assertEqual(Experience.objects.count(), 1)

    def test_create_with_invalid_data_keeps_typed_values(self):
        response = self.client.post(
            reverse("main:create_experience"), self.payload(description="")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "form-error")
        self.assertContains(response, 'value="Magang Backend"')
        self.assertEqual(Experience.objects.count(), 1)

    def test_created_data_is_immediately_available_in_json(self):
        self.client.post(reverse("main:create_experience"), self.payload())

        data = json.loads(self.client.get(reverse("main:get_experience_json")).content)
        self.assertIn("Magang Backend", [item["fields"]["title"] for item in data])

    # --- Update ---
    def test_update_page_is_prefilled_with_existing_data(self):
        response = self.client.get(
            reverse("main:update_experience", args=[self.experience.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Staff Operasional"')
        self.assertContains(response, "Membantu tim operasional.")
        # kategori data lama (di luar choices awal) harus terpilih, bukan jatuh ke default
        self.assertContains(response, '<option value="kepanitiaan" selected>')

    def test_update_changes_same_record_without_creating_new_one(self):
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.pk]),
            self.payload(title="Judul Baru", category="organisasi"),
            follow=True,
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Judul Baru")
        self.assertEqual(self.experience.category, "organisasi")
        self.assertEqual(Experience.objects.count(), 1)
        self.assertContains(response, "Pengalaman berhasil diperbarui!")

    def test_update_with_wrong_secret_leaves_record_unchanged(self):
        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.pk]),
            self.payload(title="Diretas", secret="salah"),
        )

        self.assertEqual(response.status_code, 200)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Staff Operasional")

    def test_update_unknown_id_returns_404(self):
        response = self.client.get(
            reverse("main:update_experience", args=["00000000-0000-0000-0000-000000000000"])
        )

        self.assertEqual(response.status_code, 404)

    # --- Delete ---
    def test_delete_with_correct_secret_removes_record(self):
        response = self.client.post(
            reverse("main:delete_experience", args=[self.experience.pk]),
            {"secret": SECRET},
            follow=True,
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())
        self.assertContains(response, "Pengalaman berhasil dihapus!")

    def test_delete_with_wrong_or_missing_secret_keeps_record(self):
        for payload in ({"secret": "salah"}, {}):
            with self.subTest(payload=payload):
                response = self.client.post(
                    reverse("main:delete_experience", args=[self.experience.pk]),
                    payload,
                    follow=True,
                )

                self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())
                self.assertContains(response, "Kode rahasia salah. Data tidak dihapus.")
                self.assertContains(response, "message--error")

    def test_delete_rejects_get_requests(self):
        response = self.client.get(reverse("main:delete_experience", args=[self.experience.pk]))

        self.assertEqual(response.status_code, 405)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_delete_unknown_id_returns_404(self):
        response = self.client.post(
            reverse("main:delete_experience", args=["00000000-0000-0000-0000-000000000000"]),
            {"secret": SECRET},
        )

        self.assertEqual(response.status_code, 404)

    # --- Antarmuka halaman Experience ---
    def test_experience_page_links_to_add_edit_and_delete(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, reverse("main:create_experience"))
        self.assertContains(response, reverse("main:update_experience", args=[self.experience.pk]))
        self.assertContains(response, reverse("main:delete_experience", args=[self.experience.pk]))

    def test_delete_modal_asks_for_secret_and_carries_csrf(self):
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, 'popover="auto"')
        self.assertContains(response, 'name="secret"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_no_stray_diff_markers_are_rendered(self):
        """Regresi: karakter '+' sisa salinan patch pernah ikut tampil di halaman."""
        response = self.client.get(reverse("main:show_experience"))

        stray = [
            line.strip()
            for line in response.content.decode().splitlines()
            if line.lstrip().startswith("+ ") or line.strip() == "+"
        ]

        self.assertEqual(stray, [])