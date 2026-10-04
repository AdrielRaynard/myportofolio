/**
 * Logika klien halaman Education (pemuatan data end-to-end lewat AJAX).
 *
 *   1. Memuat daftar education dari endpoint JSON (`main:get_education_json`)
 *      memakai fetch(), lengkap dengan kondisi loading / kosong / error.
 *   2. Pencarian berdasarkan nama pendidikan dengan debouncing 300 ms,
 *      sehingga request hanya dikirim setelah pengguna berhenti mengetik.
 *   3. Mengirim form tambah education di dalam modal lewat fetch POST
 *      (token CSRF via header `X-CSRFToken`), lalu memperbarui daftar tanpa
 *      reload dan menampilkan toast untuk sukses maupun kegagalan validasi.
 *   4. Proteksi XSS: setiap nilai teks dari server di-escape dengan
 *      escapeHtml() (static/js/utils.js) sebelum disisipkan ke HTML, dan
 *      server sendiri sudah membersihkan input dengan strip_tags.
 *
 * Elemen khusus peran (modal tambah, tombol hapus) hanya ada untuk pemilik,
 * jadi keberadaannya selalu diperiksa sebelum event listener dipasang.
 */
(() => {
    "use strict";

    // ------------------------------------------------------------- Konfigurasi

    const configElement = document.getElementById("education-config");
    if (!configElement) {
        return; // Halaman ini bukan Education; tidak ada yang perlu dilakukan.
    }

    const CONFIG = JSON.parse(configElement.textContent);
    const UUID_PLACEHOLDER = "00000000-0000-0000-0000-000000000000";
    const SEARCH_DEBOUNCE_DELAY = 300;

    /** Ganti UUID placeholder pada URL template Django dengan id asli. */
    const urlFor = (template, id) =>
        template.replace(UUID_PLACEHOLDER, encodeURIComponent(id));

    // ------------------------------------------------------------------- DOM

    const elements = {
        loading: document.getElementById("loading"),
        error: document.getElementById("error"),
        empty: document.getElementById("empty"),
        emptyMessage: document.getElementById("empty-message"),
        grid: document.getElementById("grid"),
        searchForm: document.getElementById("education-search-form"),
        searchInput: document.getElementById("search-input"),
        retryButton: document.getElementById("retry-button"),
        addForm: document.getElementById("education-form"),
        addModal: document.getElementById("add-education-modal"),
        csrfHolder: document.getElementById("csrf-token-holder"),
    };

    let searchDebounceTimer = null;
    let listAbortController = null;

    // ------------------------------------------------------------- Utilitas

    /** Token CSRF dari {% csrf_token %} yang dirender di dalam csrf-token-holder. */
    function getCsrfToken() {
        const input = elements.csrfHolder
            && elements.csrfHolder.querySelector('input[name="csrfmiddlewaretoken"]');
        return input ? input.value : "";
    }

    // ------------------------------------------------------------- Rendering

    /**
     * Kontrol star: form POST (dijadikan fetch oleh star-toggle.js) untuk
     * pengguna login, atau tautan login dengan `?next=` untuk pengunjung.
     */
    function buildStarControl(education, id) {
        const countHtml = `<span class="star-count">${escapeHtml(education.star_count)}</span>`;

        if (!CONFIG.isAuthenticated) {
            return `
                <a href="${escapeHtml(CONFIG.loginUrl)}"
                   class="button button-star"
                   aria-label="Login untuk memberi star pada ${escapeHtml(education.nama_sekolah)}">
                    <span aria-hidden="true">★</span>
                    Login untuk Star
                    ${countHtml}
                </a>
            `;
        }

        const starLabel = education.is_starred ? "Unstar" : "Star";
        const starTitle = education.star_count > 0
            ? `Dibintangi oleh ${escapeHtml(education.starred_by_names)}`
            : "Jadilah yang pertama memberi star";

        return `
            <form method="post"
                  action="${escapeHtml(urlFor(CONFIG.starUrlTemplate, id))}"
                  class="star-form"
                  data-star-form
                  data-school="${escapeHtml(education.nama_sekolah)}">
                <input type="hidden"
                       name="csrfmiddlewaretoken"
                       value="${escapeHtml(getCsrfToken())}">

                <button type="submit"
                        class="button button-star${education.is_starred ? " is-starred" : ""}"
                        aria-pressed="${education.is_starred ? "true" : "false"}"
                        title="${starTitle}">
                    <span aria-hidden="true">★</span>
                    <span class="star-label">${starLabel}</span>
                    ${countHtml}
                </button>
            </form>
        `;
    }

    /** Tombol + modal konfirmasi hapus (Popover API), khusus pemilik. */
    function buildDeleteControl(education, id) {
        if (!CONFIG.isOwner) {
            return "";
        }

        const modalId = `delete-${id}`;
        const schoolName = escapeHtml(education.nama_sekolah);
        const deleteUrl = escapeHtml(urlFor(CONFIG.deleteUrlTemplate, id));

        return `
            <button type="button"
                    class="button button-danger"
                    popovertarget="${modalId}"
                    aria-label="Hapus ${schoolName}"
                    title="Hapus riwayat pendidikan">
                Hapus
            </button>

            <div id="${modalId}"
                 class="delete-modal"
                 popover="auto"
                 role="dialog"
                 aria-modal="true"
                 aria-labelledby="delete-title-${id}">

                <button type="button"
                        class="delete-modal__backdrop"
                        popovertarget="${modalId}"
                        popovertargetaction="hide"
                        aria-label="Tutup konfirmasi hapus"></button>

                <div class="delete-modal__content">
                    <button type="button"
                            class="delete-modal__close"
                            popovertarget="${modalId}"
                            popovertargetaction="hide"
                            aria-label="Tutup konfirmasi hapus">×</button>

                    <h2 id="delete-title-${id}">Hapus Riwayat Pendidikan?</h2>

                    <p>
                        Apakah kamu yakin ingin menghapus
                        <strong>${schoolName}</strong>?
                        Tindakan ini tidak bisa dibatalkan.
                    </p>

                    <form method="post" action="${deleteUrl}">
                        <input type="hidden"
                               name="csrfmiddlewaretoken"
                               value="${escapeHtml(getCsrfToken())}">

                        <div class="form-group">
                            <label for="delete-secret-${id}">Kode Rahasia</label>
                            <input type="password"
                                   name="secret"
                                   id="delete-secret-${id}"
                                   autocomplete="off"
                                   required>
                        </div>

                        <div class="delete-modal__actions">
                            <button type="button"
                                    class="button button-secondary"
                                    popovertarget="${modalId}"
                                    popovertargetaction="hide">
                                Batal
                            </button>

                            <button type="submit" class="button button-danger">
                                Ya, Hapus
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        `;
    }

    /** Satu kartu education dari satu item respons JSON. */
    function buildEducationCard(item) {
        const education = item.fields;
        const id = item.pk;

        const card = document.createElement("article");
        card.className = "education-card";
        card.innerHTML = `
            <h2>${escapeHtml(education.nama_sekolah)}</h2>

            <span class="education-tingkat">
                ${escapeHtml(education.tingkat_display)}
            </span>

            ${education.jurusan
                ? `<p class="education-jurusan">${escapeHtml(education.jurusan)}</p>`
                : ""
            }

            <p class="education-period">
                ${escapeHtml(education.period_display)}
            </p>

            ${education.deskripsi
                ? `<p class="education-deskripsi">${escapeHtml(education.deskripsi)}</p>`
                : ""
            }

            <p class="education-status">
                ${education.is_ongoing ? "Sedang berlangsung" : "Selesai"}
            </p>

            <div class="card-actions">
                ${buildStarControl(education, id)}
                ${buildDeleteControl(education, id)}
            </div>
        `;

        return card;
    }

    /** Tampilkan tepat satu dari empat kondisi halaman (loading/error/empty/grid). */
    function displayPageSection({ showLoading = false, showError = false, showEmpty = false, showGrid = false }) {
        elements.loading.classList.toggle("hide", !showLoading);
        elements.error.classList.toggle("hide", !showError);
        elements.empty.classList.toggle("hide", !showEmpty);
        elements.grid.classList.toggle("hide", !showGrid);
    }

    // ---------------------------------------------------------------- Data

    /**
     * Ambil daftar education dari endpoint JSON lalu render ke grid.
     * Request pencarian lama dibatalkan lewat AbortController agar hasil
     * yang tampil selalu milik kata kunci terakhir.
     */
    async function fetchEducations(searchQuery = "") {
        if (listAbortController) {
            listAbortController.abort();
        }
        listAbortController = new AbortController();

        try {
            displayPageSection({ showLoading: true });

            const url = searchQuery
                ? `${CONFIG.listUrl}?nama_sekolah=${encodeURIComponent(searchQuery)}`
                : CONFIG.listUrl;

            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: listAbortController.signal,
            });

            if (!response.ok) {
                throw new Error(`Gagal memuat data (status ${response.status}).`);
            }

            const educationData = await response.json();

            if (educationData.length === 0) {
                elements.emptyMessage.textContent = searchQuery
                    ? `Tidak ada pendidikan yang cocok dengan pencarian "${searchQuery}".`
                    : "Belum ada riwayat pendidikan yang ditambahkan.";
                displayPageSection({ showEmpty: true });
            } else {
                elements.grid.replaceChildren(
                    ...educationData.map(buildEducationCard),
                );
                displayPageSection({ showGrid: true });
            }
        } catch (error) {
            if (error.name === "AbortError") {
                return; // Dibatalkan fetch yang lebih baru; abaikan.
            }
            console.error("Gagal memuat education:", error);
            displayPageSection({ showError: true });
        }
    }

    // ------------------------------------------------------------- Pencarian

    function scheduleSearch() {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => {
            fetchEducations(elements.searchInput.value.trim());
        }, SEARCH_DEBOUNCE_DELAY);
    }

    elements.searchInput.addEventListener("input", scheduleSearch);

    elements.searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(searchDebounceTimer);
        fetchEducations(elements.searchInput.value.trim());
    });

    if (elements.retryButton) {
        elements.retryButton.addEventListener("click", () => {
            fetchEducations(elements.searchInput.value.trim());
        });
    }

    // ------------------------------------------------------- Tambah (modal)

    function closeAddModal() {
        if (elements.addModal && elements.addModal.matches(":popover-open")) {
            elements.addModal.hidePopover();
        }
    }

    async function addEducation(event) {
        event.preventDefault();

        const submitButton = elements.addForm.querySelector('button[type="submit"]');
        submitButton.disabled = true;

        try {
            const response = await fetch(CONFIG.createUrl, {
                method: "POST",
                headers: { "X-CSRFToken": getCookie("csrftoken") },
                body: new FormData(elements.addForm),
            });

            const result = await response.json().catch(() => ({}));

            if (response.ok) {
                elements.addForm.reset();
                closeAddModal();
                showToast("Berhasil", "Education baru berhasil ditambahkan!", "success");
                fetchEducations(elements.searchInput.value.trim());
            } else if (result.errors) {
                // Gabungkan semua pesan validasi per field dari server (400).
                const errorMessages = Object.values(result.errors)
                    .flat()
                    .map((error) => error.message);
                showToast("Gagal menambahkan education", errorMessages.join(" "), "error");
            } else {
                // Kegagalan non-validasi (mis. 403 tanpa hak akses).
                showToast(
                    "Gagal menambahkan education",
                    result.message || `Terjadi kesalahan (status ${response.status}).`,
                    "error",
                );
            }
        } catch (error) {
            console.error("Gagal menambahkan education:", error);
            showToast(
                "Gagal menambahkan education",
                "Tidak dapat terhubung ke server. Silakan coba lagi.",
                "error",
            );
        } finally {
            submitButton.disabled = false;
        }
    }

    // Modal hanya dirender untuk pemilik; jangan pasang listener bila tidak ada.
    if (elements.addForm) {
        elements.addForm.addEventListener("submit", addEducation);
    }

    // ------------------------------------------------------------- Mulai

    fetchEducations(elements.searchInput.value.trim());
})();