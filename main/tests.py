import json
from unittest import mock

from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import Group, User
from django.contrib.messages import constants as message_levels
from django.contrib.messages.storage.base import Message
from django.core import serializers
from django.http import HttpResponse, response
from django.template.loader import render_to_string
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
from main.forms import EducationForm, ExperienceForm, SecretCodeField, SecretCodeForm
from main.models import Experience, Education
from main.permissions import can_edit, is_editor, is_owner
from pathlib import Path
from django.conf import settings



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

    def test_experience_page_has_no_stray_markdown_fences(self):
        """Regresi: sisa ``` hasil salin markdown pernah ikut tampil di kartu."""
        response = self.client.get(reverse("main:show_experience"))
        self.assertNotContains(response, "```")

        empty = self.client.get(reverse("main:show_experience"), {"title": "tidak-ada"})
        self.assertNotContains(empty, "```")

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

    def test_education_page_renders_ajax_skeleton_without_server_side_data(self):
        """Halaman hanya kerangka; data harus datang dari endpoint JSON (AJAX)."""
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        self.assertContains(response, 'id="loading"')
        self.assertContains(response, 'id="error"')
        self.assertContains(response, 'id="empty"')
        self.assertContains(response, 'id="grid"')
        # Bukti halaman benar-benar AJAX: data tidak ikut dirender server.
        self.assertNotContains(response, self.education.nama_sekolah)
        self.assertNotContains(response, self.education.deskripsi)

    def test_education_data_is_served_by_json_endpoint(self):
        response = self.client.get(reverse("main:get_education_json"))
        data = json.loads(response.content)

        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["pk"], str(self.education.pk))
        self.assertEqual(
            data[0]["fields"]["nama_sekolah"], "Universitas Contoh Testing"
        )
        self.assertTrue(data[0]["fields"]["is_ongoing"])
        self.assertEqual(data[0]["fields"]["period_display"], "2023 - Sekarang")
        self.assertEqual(data[0]["fields"]["star_count"], 0)
        self.assertFalse(data[0]["fields"]["is_starred"])

    def test_education_page_shows_empty_state_when_no_data(self):
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada riwayat pendidikan yang ditambahkan.")

    def test_completed_education_status_in_json(self):
        self.education.tahun_lulus = 2025
        self.education.save()

        data = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )

        self.assertFalse(data[0]["fields"]["is_ongoing"])
        self.assertEqual(data[0]["fields"]["period_display"], "2023 - 2025")

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

    def setUp(self):
        # Halaman create hanya boleh dibuka pemilik portofolio (superuser).
       owner = User.objects.create_superuser(username="base-owner", password="password")
       self.client.force_login(owner)

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
        owner = User.objects.create_superuser(username="flash-owner", password="password")
        self.client.force_login(owner)
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
        self.assertContains(response, "data-live-search")
        self.assertContains(response, 'data-live-search-target=".experience-grid"')

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
        self.smak = Education.objects.create(
            nama_sekolah="SMAK Contoh", tingkat="sma", tahun_masuk=2022
        )

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

    def test_list_json_includes_star_state_of_logged_in_user(self):
        user = User.objects.create_user(username="json-star", password="password")
        self.ui.starred_by.add(user)
        self.client.force_login(user)

        data = json.loads(self.client.get(reverse("main:get_education_json")).content)
        fields_by_pk = {item["pk"]: item["fields"] for item in data}

        self.assertEqual(fields_by_pk[str(self.ui.pk)]["star_count"], 1)
        self.assertTrue(fields_by_pk[str(self.ui.pk)]["is_starred"])
        self.assertEqual(fields_by_pk[str(self.smak.pk)]["star_count"], 0)
        self.assertFalse(fields_by_pk[str(self.smak.pk)]["is_starred"])

    def test_list_json_does_not_expose_star_giver_usernames(self):
        """Regresi: respons publik tidak boleh memuat identitas pemberi star.

        Star sengaja ditambahkan dulu sebelum request anonim, agar lolos/tidak
        nya test tidak sekadar karena database uji masih kosong.
        """
        giver = User.objects.create_user(username="stargiver-rahasia", password="password")
        self.ui.starred_by.add(giver)

        response = self.client.get(reverse("main:get_education_json"))
        content = response.content.decode()

        self.assertNotIn("stargiver-rahasia", content)
        self.assertNotIn("starred_by_names", content)

    def test_education_page_loads_data_via_ajax_script(self):
        """Kerangka halaman memuat konfigurasi JSON + skrip education.js."""
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "js/education.js")
        self.assertContains(response, 'id="education-config"')
        self.assertContains(response, reverse("main:get_education_json"))
        self.assertContains(response, 'id="csrf-token-holder"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_education_script_registers_keyboard_shortcuts(self):
        """Shortcut "/" fokus pencarian dan Esc membersihkan filter harus terpasang."""
        js_source = (
            Path(settings.BASE_DIR) / "static" / "js" / "education.js"
        ).read_text(encoding="utf-8")

        self.assertIn('"keydown"', js_source)
        self.assertIn('event.key === "/"', js_source)
        self.assertIn('"Escape"', js_source)
        self.assertIn("fetchEducations(\"\")", js_source)
        # "/" tidak boleh mati selama toast (popover="manual") tampil, dan
        # tidak boleh menembak saat modal popover="auto" terbuka/modifier ditekan.
        self.assertIn('[popover="auto"]:popover-open', js_source)
        self.assertIn("event.ctrlKey", js_source)
        self.assertIn("event.metaKey", js_source)
        self.assertIn("event.altKey", js_source)


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
        self.owner = User.objects.create_superuser(
            username="crud-owner", password="password"
        )
        self.client.force_login(self.owner)
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

@override_settings(PORTFOLIO_SECRET=SECRET)
class EducationFormTest(TestCase):
    def valid_data(self, **overrides):
        data = {
            "nama_sekolah": "Universitas Indonesia",
            "tingkat": "S1",
            "jurusan": "Sistem Informasi",
            "tahun_masuk": 2025,
            "tahun_lulus": 2029,
            "deskripsi": "",
            "secret": SECRET,
        }
        data.update(overrides)
        return data

    def test_wrong_secret_is_rejected(self):
        """Regresi: clean_secret dulu berada di luar class sehingga tidak pernah dipanggil."""
        form = EducationForm(self.valid_data(secret="asal-isi"))

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.as_data()["secret"][0].code, "invalid_secret")

    def test_missing_secret_is_rejected(self):
        form = EducationForm(self.valid_data(secret=""))

        self.assertFalse(form.is_valid())
        self.assertIn("secret", form.errors)

    def test_correct_secret_saves_education(self):
        form = EducationForm(self.valid_data())

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().nama_sekolah, "Universitas Indonesia")

    def test_graduation_year_is_optional_for_ongoing_education(self):
        form = EducationForm(self.valid_data(tahun_lulus=""))

        self.assertTrue(form.is_valid(), form.errors)
        self.assertTrue(form.save().is_ongoing)

    def test_empty_jurusan_is_saved_as_null_not_the_string_none(self):
        """Regresi: jurusan kosong tidak boleh tersimpan sebagai teks "None"."""
        form = EducationForm(self.valid_data(jurusan=""))

        self.assertTrue(form.is_valid(), form.errors)
        education = form.save()

        self.assertIsNone(education.jurusan)

    def test_graduation_year_cannot_precede_entry_year(self):
        form = EducationForm(self.valid_data(tahun_masuk=2025, tahun_lulus=2020))

        self.assertFalse(form.is_valid())
        self.assertIn("tahun_lulus", form.errors)


@override_settings(PORTFOLIO_SECRET=SECRET)
class EducationCrudViewTest(TestCase):
    def setUp(self):
        Education.objects.all().delete()
        self.owner = User.objects.create_superuser(
            username="education-owner", password="password"
        )
        self.client.force_login(self.owner)
        self.education = Education.objects.create(
            nama_sekolah="SMAK Contoh", tingkat="sma", tahun_masuk=2022, tahun_lulus=2025
        )

    def payload(self, **overrides):
        data = {
            "nama_sekolah": "Universitas Indonesia",
            "tingkat": "S1",
            "jurusan": "Sistem Informasi",
            "tahun_masuk": 2025,
            "tahun_lulus": "",
            "deskripsi": "Sedang kuliah.",
            "secret": SECRET,
        }
        data.update(overrides)
        return data

    # --- Create ---
    def test_create_page_uses_generic_form_template(self):
        response = self.client.get(reverse("main:create_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "form_page.html")
        self.assertContains(response, "Tambah Riwayat Pendidikan")

    def test_create_with_correct_secret_saves(self):
        response = self.client.post(
            reverse("main:create_education"), self.payload(), follow=True
        )

        self.assertRedirects(response, reverse("main:show_education"))
        self.assertTrue(
            Education.objects.filter(nama_sekolah="Universitas Indonesia").exists()
        )
        self.assertContains(response, "Pendidikan baru berhasil ditambahkan!")

    def test_create_with_wrong_secret_saves_nothing(self):
        response = self.client.post(
            reverse("main:create_education"), self.payload(secret="salah")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kode rahasia salah.")
        self.assertEqual(Education.objects.count(), 1)

    # --- Update ---
    def test_update_page_is_prefilled(self):
        response = self.client.get(
            reverse("main:update_education", args=[self.education.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ubah Riwayat Pendidikan")
        self.assertContains(response, 'value="SMAK Contoh"')
        self.assertContains(response, 'value="2022"')
        self.assertContains(response, '<option value="sma" selected>')

    def test_update_changes_same_record_without_creating_new_one(self):
        response = self.client.post(
            reverse("main:update_education", args=[self.education.pk]),
            self.payload(
                nama_sekolah="SMAK Baru", tingkat="sma", tahun_masuk=2021
            ),
            follow=True,
        )

        self.assertRedirects(response, reverse("main:show_education"))
        self.education.refresh_from_db()
        self.assertEqual(self.education.nama_sekolah, "SMAK Baru")
        self.assertEqual(self.education.tahun_masuk, 2021)
        self.assertEqual(Education.objects.count(), 1)
        self.assertContains(
            response, "Riwayat pendidikan berhasil diperbarui!"
        )

    def test_update_with_wrong_secret_leaves_record_unchanged(self):
        self.client.post(
            reverse("main:update_education", args=[self.education.pk]),
            self.payload(nama_sekolah="Diretas", secret="salah"),
        )

        self.education.refresh_from_db()
        self.assertEqual(self.education.nama_sekolah, "SMAK Contoh")

    def test_update_unknown_id_returns_404(self):
        response = self.client.get(
            reverse(
                "main:update_education",
                args=["00000000-0000-0000-0000-000000000000"],
            )
        )

        self.assertEqual(response.status_code, 404)

    # --- Delete ---
    def test_delete_with_correct_secret_removes_record(self):
        response = self.client.post(
            reverse("main:delete_education", args=[self.education.pk]),
            {"secret": SECRET},
            follow=True,
        )

        self.assertRedirects(response, reverse("main:show_education"))
        self.assertFalse(
            Education.objects.filter(pk=self.education.pk).exists()
        )
        self.assertContains(
            response, "Riwayat pendidikan berhasil dihapus!"
        )

    def test_delete_without_valid_secret_keeps_record(self):
        for payload in ({"secret": "salah"}, {}):
            with self.subTest(payload=payload):
                response = self.client.post(
                    reverse(
                        "main:delete_education",
                        args=[self.education.pk],
                    ),
                    payload,
                    follow=True,
                )

                self.assertTrue(
                    Education.objects.filter(pk=self.education.pk).exists()
                )
                self.assertContains(
                    response,
                    "Kode rahasia salah. Data tidak dihapus.",
                )

    def test_delete_rejects_get_requests(self):
        response = self.client.get(
            reverse("main:delete_education", args=[self.education.pk])
        )

        self.assertEqual(response.status_code, 405)
        self.assertTrue(
            Education.objects.filter(pk=self.education.pk).exists()
        )

    # --- JSON detail ---
    def test_detail_json_returns_single_education(self):
        response = self.client.get(
            reverse(
                "main:get_education_detail_json",
                args=[self.education.pk],
            )
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        self.assertEqual(
            data[0]["fields"]["nama_sekolah"],
            "SMAK Contoh",
        )

    def test_detail_json_returns_json_404_for_unknown_id(self):
        response = self.client.get(
            reverse(
                "main:get_education_detail_json",
                args=["00000000-0000-0000-0000-000000000000"],
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "tidak ditemukan",
            json.loads(response.content)["detail"],
        )

    # --- Antarmuka halaman Education ---
    def test_education_page_exposes_ajax_endpoints_and_secret_modal_for_owner(self):
        """Regresi: modal hapus Education dulu dibuat tetapi tidak pernah di-include."""
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, reverse("main:create_education_ajax"))
        self.assertContains(response, reverse("main:get_education_json"))
        self.assertContains(response, 'popover="auto"')
        self.assertContains(response, 'name="secret"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_created_education_is_immediately_available_in_json(self):
        self.client.post(
            reverse("main:create_education"),
            self.payload(),
        )

        data = json.loads(
            self.client.get(
                reverse("main:get_education_json")
            ).content
        )
        self.assertIn(
            "Universitas Indonesia",
            [i["fields"]["nama_sekolah"] for i in data],
        )

class AuthorizationAndStarTest(TestCase):
    """Test inti Tugas 5 tanpa menduplikasi seluruh test CRUD yang sudah ada."""

    def setUp(self):
        Experience.objects.all().delete()
        Education.objects.all().delete()

        self.regular = User.objects.create_user(
            username="regular-user", password="password"
        )
        self.editor = User.objects.create_user(
            username="editor-user", password="password"
        )
        editor_group, _ = Group.objects.get_or_create(name="Editor")
        self.editor.groups.add(editor_group)
        self.owner = User.objects.create_superuser(
            username="portfolio-owner", password="password"
        )

        self.experience = Experience.objects.create(
            title="Experience Test",
            description="Untuk pengujian authorization.",
            category="research",
        )
        self.education = Education.objects.create(
            nama_sekolah="Education Test",
            tingkat="S1",
            jurusan="Sistem Informasi",
            tahun_masuk=2025,
        )

    def test_visitor_must_login_for_protected_actions(self):
        actions = [
            ("get", "main:create_experience", []),
            ("get", "main:create_education", []),
            ("get", "main:update_experience", [self.experience.pk]),
            ("get", "main:update_education", [self.education.pk]),
            ("post", "main:delete_experience", [self.experience.pk]),
            ("post", "main:delete_education", [self.education.pk]),
        ]

        for method, url_name, args in actions:
            with self.subTest(url_name=url_name, method=method):
                response = getattr(self.client, method)(
                    reverse(url_name, args=args),
                    data={},
                )
                self.assertEqual(response.status_code, 302)
                self.assertIn("/login/", response["Location"])

    def test_regular_user_cannot_create_update_or_delete(self):
        self.client.force_login(self.regular)

        actions = [
            ("get", "main:create_experience", []),
            ("get", "main:create_education", []),
            ("get", "main:update_experience", [self.experience.pk]),
            ("get", "main:update_education", [self.education.pk]),
            ("post", "main:delete_experience", [self.experience.pk]),
            ("post", "main:delete_education", [self.education.pk]),
        ]

        for method, url_name, args in actions:
            with self.subTest(url_name=url_name, method=method):
                response = getattr(self.client, method)(
                    reverse(url_name, args=args),
                    data={},
                )
                self.assertEqual(response.status_code, 403)

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_login(self.editor)

        for url_name, args in (
            ("main:update_experience", [self.experience.pk]),
            ("main:update_education", [self.education.pk]),
        ):
            response = self.client.get(reverse(url_name, args=args))
            self.assertEqual(response.status_code, 200)

        for url_name, args, method in (
            ("main:create_experience", [], "get"),
            ("main:create_education", [], "get"),
            ("main:delete_experience", [self.experience.pk], "post"),
            ("main:delete_education", [self.education.pk], "post"),
        ):
            response = getattr(self.client, method)(
                reverse(url_name, args=args),
                data={},
            )
            self.assertEqual(response.status_code, 403)

    def test_role_based_controls_are_hidden_or_shown(self):
        experience_url = reverse("main:show_experience")
        create_url = reverse("main:create_experience")
        update_url = reverse("main:update_experience", args=[self.experience.pk])
        delete_url = reverse("main:delete_experience", args=[self.experience.pk])

        self.client.force_login(self.regular)
        response = self.client.get(experience_url)
        self.assertNotContains(response, create_url)
        self.assertNotContains(response, update_url)
        self.assertNotContains(response, delete_url)

        self.client.force_login(self.editor)
        response = self.client.get(experience_url)
        self.assertContains(response, update_url)
        self.assertNotContains(response, create_url)
        self.assertNotContains(response, delete_url)

        self.client.force_login(self.owner)
        response = self.client.get(experience_url)
        self.assertContains(response, create_url)
        self.assertContains(response, update_url)
        self.assertContains(response, delete_url)

    def test_star_can_be_added_and_removed_by_one_user(self):
        self.client.force_login(self.regular)

        response = self.client.post(
            reverse("main:toggle_star", args=[self.education.pk]),
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertTrue(
            self.education.starred_by.filter(pk=self.regular.pk).exists()
        )

        data = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )
        self.assertTrue(data[0]["fields"]["is_starred"])
        self.assertEqual(data[0]["fields"]["star_count"], 1)

        response = self.client.post(
            reverse("main:toggle_star", args=[self.education.pk]),
            follow=True,
        )
        self.assertRedirects(response, reverse("main:show_education"))
        self.assertFalse(
            self.education.starred_by.filter(pk=self.regular.pk).exists()
        )

        data = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )
        self.assertFalse(data[0]["fields"]["is_starred"])
        self.assertEqual(data[0]["fields"]["star_count"], 0)

    def test_star_endpoint_accepts_post_only(self):
        self.client.force_login(self.regular)

        response = self.client.get(
            reverse("main:toggle_star", args=[self.education.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_json_does_not_expose_star_users(self):
        self.education.starred_by.add(self.regular)

        response = self.client.get(
            reverse("main:get_education_detail_json", args=[self.education.pk])
        )
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("starred_by", data[0]["fields"])
        # Cek username (bukan pk): angka pk mudah "kebetulan" muncul di dalam UUID.
        self.assertNotIn(self.regular.username, response.content.decode())

class AuthPagesTest(TestCase):
    """Halaman login/register memakai base.html dengan tepat satu <title>."""

    def test_login_and_register_have_single_title(self):
        for url_name, label in (("main:login", "Login"), ("main:register", "Register")):
            with self.subTest(page=url_name):
                html = self.client.get(reverse(url_name)).content.decode()

                self.assertEqual(html.count("<title>"), 1)
                self.assertIn(f"<title>{label} - Adriel</title>", html)

class PermissionHelpersTest(TestCase):
    """Helper peran di main/permissions.py dan context processor `roles`."""

    def setUp(self):
        self.regular = User.objects.create_user(
            username="helper-regular",
            password="password",
        )
        self.editor = User.objects.create_user(
            username="helper-editor",
            password="password",
        )
        group, _ = Group.objects.get_or_create(name="Editor")
        self.editor.groups.add(group)
        self.owner = User.objects.create_superuser(
            username="helper-owner",
            password="password",
        )

    def test_role_predicates(self):
        from django.contrib.auth.models import AnonymousUser

        cases = [
            # user,               owner, editor, can_edit
            (AnonymousUser(),     False, False, False),
            (self.regular,        False, False, False),
            (self.editor,         False, True,  True),
            (self.owner,          True,  False, True),
        ]

        for user, owner, editor, edit in cases:
            with self.subTest(user=str(user)):
                self.assertEqual(is_owner(user), owner)
                self.assertEqual(is_editor(user), editor)
                self.assertEqual(can_edit(user), edit)

    def test_context_processor_exposes_is_editor(self):
        self.client.force_login(self.editor)
        self.assertTrue(
            self.client.get(
                reverse("main:show_education")
            ).context["is_editor"]
        )

        self.client.force_login(self.regular)
        self.assertFalse(
            self.client.get(
                reverse("main:show_education")
            ).context["is_editor"]
        )

class LoginRedirectTest(TestCase):
    """Login mengembalikan pengguna ke halaman tujuan (`?next=`) dengan aman."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="next-user",
            password="password",
        )

    def login(self, next_url=None, query=""):
        data = {
            "username": "next-user",
            "password": "password",
        }

        if next_url is not None:
            data["next"] = next_url

        return self.client.post(reverse("main:login") + query, data)

    def test_login_form_carries_next_as_hidden_field(self):
        response = self.client.get(
            reverse("main:login"),
            {"next": "/education/"},
        )

        self.assertContains(
            response,
            '<input type="hidden" name="next" value="/education/">',
        )

    def test_protected_page_redirects_back_after_login(self):
        Education.objects.all().delete()

        response = self.client.get(reverse("main:create_education"))
        self.assertEqual(
            response["Location"],
            "/login/?next=/education/add/",
        )

        response = self.login(next_url="/education/")
        self.assertRedirects(
            response,
            "/education/",
            fetch_redirect_response=False,
        )
        self.assertIn("sessionid", response.cookies)
        self.assertIn("last_login", response.cookies)

    def test_next_from_query_string_is_used_when_form_field_missing(self):
        response = self.login(query="?next=/experience/")

        self.assertRedirects(
            response,
            "/experience/",
            fetch_redirect_response=False,
        )

    def test_external_next_is_ignored(self):
        for evil in (
            "https://evil.example/",
            "//evil.example/",
            "javascript:alert(1)",
        ):
            with self.subTest(next=evil):
                response = self.login(next_url=evil)

                self.assertRedirects(
                    response,
                    reverse("main:show_main"),
                    fetch_redirect_response=False,
                )

    def test_login_without_next_goes_to_home(self):
        response = self.login()

        self.assertRedirects(
            response,
            reverse("main:show_main"),
            fetch_redirect_response=False,
        )

class StarRelationTest(TestCase):
    """Relasi ManyToMany Education <-> User untuk fitur star."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="star-user",
            password="password",
        )
        self.other = User.objects.create_user(
            username="star-other",
            password="password",
        )
        self.education = Education.objects.create(
            nama_sekolah="Universitas Star",
            tingkat="S1",
            tahun_masuk=2025,
        )

    def test_reverse_accessor_lists_starred_education_for_user(self):
        self.education.starred_by.add(self.user)

        self.assertEqual(
            list(self.user.starred_education.all()),
            [self.education],
        )
        self.assertEqual(
            self.other.starred_education.count(),
            0,
        )

    def test_same_user_cannot_star_twice(self):
        self.education.starred_by.add(self.user)
        self.education.starred_by.add(self.user)

        self.assertEqual(
            self.education.starred_by.count(),
            1,
        )

class EditorGroupMigrationTest(TestCase):
    def test_editor_group_exists_after_migrate(self):
        self.assertTrue(
            Group.objects.filter(name="Editor").exists()
        )

    def test_user_added_to_group_becomes_editor(self):
        user = User.objects.create_user(
            username="new-editor",
            password="password",
        )
        self.assertFalse(is_editor(user))

        user.groups.add(
            Group.objects.get(name="Editor")
        )

        self.assertTrue(is_editor(user))

@override_settings(PORTFOLIO_SECRET=SECRET)
class EditorUpdateWithoutSecretTest(TestCase):
    """Editor mengubah data tanpa kode rahasia; pemilik tetap wajib memakainya."""

    def setUp(self):
        Education.objects.all().delete()
        Experience.objects.all().delete()

        self.editor = User.objects.create_user(
            username="secret-editor",
            password="password",
        )
        self.editor.groups.add(Group.objects.get(name="Editor"))

        self.owner = User.objects.create_superuser(
            username="secret-owner",
            password="password",
        )

        self.education = Education.objects.create(
            nama_sekolah="Lama",
            tingkat="S1",
            tahun_masuk=2020,
        )
        self.experience = Experience.objects.create(
            title="Lama",
            description="d",
            category="research",
        )

    def education_payload(self, **overrides):
        data = {
            "nama_sekolah": "Baru",
            "tingkat": "S1",
            "tahun_masuk": 2020,
        }
        data.update(overrides)
        return data

    def experience_payload(self, **overrides):
        data = {
            "title": "Baru",
            "description": "d",
            "category": "research",
        }
        data.update(overrides)
        return data

    def test_editor_form_has_no_secret_field(self):
        self.client.force_login(self.editor)

        for url in (
            reverse("main:update_education", args=[self.education.pk]),
            reverse("main:update_experience", args=[self.experience.pk]),
        ):
            with self.subTest(url=url):
                self.assertNotContains(
                    self.client.get(url),
                    'name="secret"',
                )

    def test_editor_can_update_education_and_experience_without_secret(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("main:update_education", args=[self.education.pk]),
            self.education_payload(),
        )
        self.assertRedirects(
            response,
            reverse("main:show_education"),
        )

        response = self.client.post(
            reverse("main:update_experience", args=[self.experience.pk]),
            self.experience_payload(),
        )
        self.assertRedirects(
            response,
            reverse("main:show_experience"),
        )

        self.education.refresh_from_db()
        self.experience.refresh_from_db()

        self.assertEqual(
            self.education.nama_sekolah,
            "Baru",
        )
        self.assertEqual(
            self.experience.title,
            "Baru",
        )

    def test_owner_still_needs_secret_to_update(self):
        self.client.force_login(self.owner)

        url = reverse(
            "main:update_education",
            args=[self.education.pk],
        )

        self.assertContains(
            self.client.get(url),
            'name="secret"',
        )

        self.client.post(
            url,
            self.education_payload(),
        )
        self.education.refresh_from_db()

        self.assertEqual(
            self.education.nama_sekolah,
            "Lama",
        )

        self.client.post(
            url,
            self.education_payload(secret=SECRET),
        )
        self.education.refresh_from_db()

        self.assertEqual(
            self.education.nama_sekolah,
            "Baru",
        )

    def test_owner_still_needs_secret_to_create(self):
        self.client.force_login(self.owner)

        self.assertContains(
            self.client.get(reverse("main:create_education")),
            'name="secret"',
        )

class StarToggleAjaxTest(TestCase):
    """toggle_star membalas JSON untuk fetch() dan redirect untuk form biasa."""

    AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}

    def setUp(self):
        Education.objects.all().delete()

        self.user = User.objects.create_user(
            username="ajax-user",
            password="password",
        )
        self.other = User.objects.create_user(
            username="ajax-other",
            password="password",
        )
        self.education = Education.objects.create(
            nama_sekolah="Universitas Ajax",
            tingkat="S1",
            tahun_masuk=2025,
        )
        self.url = reverse(
            "main:toggle_star",
            args=[self.education.pk],
        )

    def test_ajax_toggle_returns_state_and_total_count(self):
        self.education.starred_by.add(self.other)
        self.client.force_login(self.user)

        first = self.client.post(self.url, **self.AJAX)
        second = self.client.post(self.url, **self.AJAX)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(
            first["Content-Type"],
            "application/json",
        )
        self.assertEqual(
            first.json(),
            {"starred": True, "star_count": 2},
        )
        self.assertEqual(
            second.json(),
            {"starred": False, "star_count": 1},
        )
        self.assertFalse(
            self.education.starred_by.filter(
                pk=self.user.pk
            ).exists()
        )

    def test_plain_form_post_still_redirects(self):
        self.client.force_login(self.user)

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            reverse("main:show_education"),
        )

    def test_ajax_from_visitor_is_redirected_to_login_not_counted(self):
        response = self.client.post(
            self.url,
            **self.AJAX,
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/login/",
            response["Location"],
        )
        self.assertEqual(
            self.education.starred_by.count(),
            0,
        )

    def test_ajax_unknown_education_returns_404(self):
        self.client.force_login(self.user)

        url = reverse(
            "main:toggle_star",
            args=["00000000-0000-0000-0000-000000000000"],
        )

        self.assertEqual(
            self.client.post(url, **self.AJAX).status_code,
            404,
        )

    def test_client_script_renders_star_markup_for_script_and_accessibility(self):
        """Kontrak markup kartu buatan education.js: form star yang dipakai star-toggle.js."""
        js_source = (
            Path(settings.BASE_DIR) / "static" / "js" / "education.js"
        ).read_text(encoding="utf-8")

        self.assertIn("data-star-form", js_source)
        self.assertIn('class="star-label"', js_source)
        self.assertIn("csrfmiddlewaretoken", js_source)
        self.assertIn("aria-pressed", js_source)

        response = self.client.get(reverse("main:show_education"))
        self.assertContains(response, "js/star-toggle.js")
        self.assertContains(response, 'id="csrf-token-holder"')
        self.assertContains(response, "csrfmiddlewaretoken")

    def test_visitor_gets_login_link_config_but_no_star_form(self):
        self.education.starred_by.add(self.other)

        response = self.client.get(reverse("main:show_education"))

        self.assertNotContains(response, "data-star-form")
        self.assertContains(response, "/login/?next=/education/")

        data = json.loads(
            self.client.get(reverse("main:get_education_json")).content
        )
        self.assertEqual(data[0]["fields"]["star_count"], 1)
        self.assertFalse(data[0]["fields"]["is_starred"])

class RoleBadgeTest(TestCase):
    """Navbar menampilkan peran akun yang sedang login."""

    def setUp(self):
        self.regular = User.objects.create_user(
            username="badge-regular",
            password="password",
        )
        self.editor = User.objects.create_user(
            username="badge-editor",
            password="password",
        )
        self.editor.groups.add(
            Group.objects.get(name="Editor")
        )
        self.owner = User.objects.create_superuser(
            username="badge-owner",
            password="password",
        )

    def badge_for(self, user):
        if user:
            self.client.force_login(user)

        return self.client.get(
            reverse("main:show_main")
        )

    def test_badge_shows_role_for_each_account_type(self):
        for user, role in (
            (self.regular, "User"),
            (self.editor, "Editor"),
            (self.owner, "Owner"),
        ):
            with self.subTest(role=role):
                response = self.badge_for(user)

                self.assertEqual(
                    response.context["user_role"],
                    role,
                )
                self.assertContains(
                    response,
                    f"role-badge--{role.lower()}",
                )

    def test_superuser_who_is_also_in_editor_group_is_shown_as_owner(self):
        self.owner.groups.add(
            Group.objects.get(name="Editor")
        )

        self.assertEqual(
            self.badge_for(self.owner).context["user_role"],
            "Owner",
        )

    def test_visitor_has_no_badge(self):
        response = self.client.get(
            reverse("main:show_main")
        )

        self.assertEqual(
            response.context["user_role"],
            "",
        )
        self.assertNotContains(
            response,
            "role-badge",
        )

@override_settings(PORTFOLIO_SECRET=SECRET)
class CreateEducationAjaxTest(TestCase):
    """Endpoint AJAX tambah education: 201 berhasil, 400 validasi, 403 tanpa hak."""

    def setUp(self):
        Education.objects.all().delete()

        self.regular = User.objects.create_user(
            username="ajax-regular", password="password"
        )
        self.editor = User.objects.create_user(
            username="ajax-editor", password="password"
        )
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.owner = User.objects.create_superuser(
            username="ajax-owner", password="password"
        )
        self.url = reverse("main:create_education_ajax")

    def payload(self, **overrides):
        data = {
            "nama_sekolah": "Universitas Ajax",
            "tingkat": "S1",
            "jurusan": "Sistem Informasi",
            "tahun_masuk": 2025,
            "tahun_lulus": "",
            "deskripsi": "Kuliah.",
            "secret": SECRET,
        }
        data.update(overrides)
        return data

    def test_owner_can_add_education_via_ajax(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["Content-Type"], "application/json")
        result = response.json()
        self.assertIn("berhasil", result["message"])
        self.assertTrue(
            Education.objects.filter(pk=result["pk"]).exists()
        )

    def test_invalid_payload_returns_400_with_field_errors(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.url, self.payload(nama_sekolah=""))

        self.assertEqual(response.status_code, 400)
        self.assertIn("nama_sekolah", response.json()["errors"])
        self.assertEqual(Education.objects.count(), 0)

    def test_wrong_secret_returns_400_and_saves_nothing(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.url, self.payload(secret="salah"))

        self.assertEqual(response.status_code, 400)
        self.assertIn("secret", response.json()["errors"])
        self.assertEqual(Education.objects.count(), 0)

    def test_editor_is_forbidden(self):
        self.client.force_login(self.editor)

        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_regular_user_is_forbidden(self):
        self.client.force_login(self.regular)

        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_visitor_is_forbidden(self):
        response = self.client.post(self.url, self.payload())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Education.objects.count(), 0)

    def test_get_method_is_rejected(self):
        self.client.force_login(self.owner)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 405)

    def test_xss_payload_is_sanitized_server_side(self):
        """strip_tags pada clean_<field> harus membuang tag HTML sebelum simpan."""
        self.client.force_login(self.owner)

        response = self.client.post(
            self.url,
            self.payload(
                nama_sekolah='<img src="x" onerror="alert(\'XSS!\')">Sekolah Aman',
                deskripsi="<script>alert(1)</script>Deskripsi aman",
            ),
        )

        self.assertEqual(response.status_code, 201)
        education = Education.objects.get()
        self.assertEqual(education.nama_sekolah, "Sekolah Aman")
        self.assertNotIn("<", education.nama_sekolah)
        self.assertNotIn("<", education.deskripsi)
        self.assertNotIn("onerror", education.nama_sekolah)