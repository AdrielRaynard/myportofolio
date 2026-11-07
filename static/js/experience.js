(function experiencePage() {
    const page = document.querySelector("#experience");
    const grid = page.querySelector("#experience-list");
    const status = page.querySelector("#experience-status");
    const search = page.querySelector("#experience-search");
    const input = search.elements.title;
    const template = page.querySelector("#experience-card");
    const categories = JSON.parse(page.querySelector("#experience-categories").textContent);
    const editor = page.querySelector("#experience-editor");
    const form = page.querySelector("#experience-form");
    const addButton = page.querySelector("#add-experience");
    const busyCards = new Set();
    let activeRead;
    let timer;
    let editing;
    let opener;
    let saving = false;

    function itemUrl(pattern, id) {
        return pattern.replace("00000000-0000-0000-0000-000000000000", encodeURIComponent(id));
    }

    async function api(url, method = "GET", payload, signal) {
        const headers = {Accept: "application/json"};
        if (method !== "GET") headers["X-CSRFToken"] = getCookie("csrftoken");
        if (payload !== undefined) headers["Content-Type"] = "application/json";
        const response = await fetch(url, {
            method, headers, signal, credentials: "same-origin",
            body: payload === undefined ? undefined : JSON.stringify(payload),
        });
        if (response.status === 204) return;
        const json = response.headers.get("Content-Type")?.includes("application/json");
        const data = json ? await response.json() : null;
        if (!response.ok) {
            const errors = Object.entries(data || {}).map(([key, value]) => {
                const message = Array.isArray(value) ? value.join(" ") : String(value);
                if (key === "detail" || key === "non_field_errors") return message;
                const label = form?.elements.namedItem(key)?.labels?.[0]?.textContent || key;
                return `${label}: ${message}`;
            });
            throw new Error(errors.join("\n") || `Permintaan gagal (HTTP ${response.status}).`);
        }
        if (!json) throw new Error("Respons server tidak dapat dibaca.");
        return data;
    }

    function makeCard(item) {
        const card = template.content.firstElementChild.cloneNode(true);
        card.dataset.id = item.id;
        card.querySelector("h2").textContent = item.title;
        card.querySelector(".experience-description").textContent = item.description;
        card.querySelector(".experience-category").textContent = categories[item.category] || item.category;
        card.querySelector(".experience-status").textContent = item.is_ongoing ? "Sedang berlangsung" : "Selesai";
        card.querySelector(".star-count").textContent = item.star_count;
        if (item.thumbnail && /^https?:\/\//i.test(item.thumbnail)) {
            const image = document.createElement("img");
            image.className = "experience-thumbnail";
            image.loading = "lazy";
            image.alt = `Gambar ${item.title}`;
            image.src = item.thumbnail;
            card.prepend(image);
        }
        const star = card.querySelector('[data-action="star"]');
        if (star) {
            star.querySelector(".star-label").textContent = item.is_starred ? "Unstar" : "Star";
            star.setAttribute("aria-pressed", String(item.is_starred));
            star.setAttribute("aria-label", `${item.is_starred ? "Batalkan" : "Beri"} star untuk ${item.title}`);
            star.classList.toggle("is-starred", item.is_starred);
        }
        for (const button of card.querySelectorAll("[data-action]")) {
            button.disabled = busyCards.has(item.id);
            button.addEventListener("click", () => cardAction(button, item));
        }
        return card;
    }

    async function loadList() {
        clearTimeout(timer);
        activeRead?.abort();
        const read = new AbortController();
        activeRead = read;
        const url = new URL(page.dataset.listUrl, location.origin);
        const title = input.value.trim();
        if (title) url.searchParams.set("title", title);
        grid.setAttribute("aria-busy", "true");
        try {
            const rows = await api(url, "GET", undefined, read.signal);
            if (read.signal.aborted) return;
            grid.replaceChildren(...rows.map(makeCard));
            status.textContent = rows.length ? "" : (title
                ? "Tidak ada pengalaman dengan judul tersebut."
                : "Belum ada pengalaman yang ditambahkan.");
            const pageUrl = new URL(location.href);
            if (title) pageUrl.searchParams.set("title", title);
            else pageUrl.searchParams.delete("title");
            history.replaceState(null, "", pageUrl);
        } catch (error) {
            if (read.signal.aborted) return;
            status.textContent = "Daftar gagal dimuat. Tekan Cari untuk mencoba lagi.";
            showToast("Gagal memuat pengalaman", error.message, "error");
        } finally {
            if (read === activeRead) grid.removeAttribute("aria-busy");
        }
    }

    function openForm(item, trigger) {
        if (saving) return;
        editing = item;
        opener = trigger;
        form.reset();
        if (item) {
            for (const key of ["title", "description", "category", "thumbnail"]) {
                form.elements[key].value = item[key] ?? "";
            }
            form.elements.is_finished.checked = !item.is_ongoing;
        }
        page.querySelector("#editor-heading").textContent = item ? "Ubah pengalaman" : "Tambah pengalaman";
        editor.hidden = false;
        form.elements.title.focus();
    }

    function closeForm() {
        editor.hidden = true;
        editing = null;
        (opener?.isConnected ? opener : input).focus();
    }

    async function save(event) {
        event.preventDefault();
        if (saving) return;
        const payload = Object.fromEntries(new FormData(form));
        payload.is_finished = form.elements.is_finished.checked;
        payload.thumbnail = payload.thumbnail || null;
        if (editing) {
            // Hanya kirim perubahan pengguna agar PATCH tidak menimpa field lain.
            for (const key of Object.keys(payload)) {
                const before = key === "is_finished" ? !editing.is_ongoing : editing[key];
                if (before === payload[key]) delete payload[key];
            }
            if (!Object.keys(payload).length) {
                closeForm();
                return;
            }
        }
        saving = true;
        const controls = Array.from(form.elements);
        controls.forEach(control => { control.disabled = true; });
        try {
            const url = editing ? itemUrl(page.dataset.detailUrl, editing.id) : page.dataset.listUrl;
            await api(url, editing ? "PATCH" : "POST", payload);
            closeForm();
            showToast("Tersimpan", "Pengalaman berhasil disimpan.", "success");
            await loadList();
        } catch (error) {
            showToast("Gagal menyimpan pengalaman", error.message, "error");
        } finally {
            saving = false;
            controls.forEach(control => { control.disabled = false; });
        }
    }

    async function cardAction(button, item) {
        const action = button.dataset.action;
        if (busyCards.has(item.id) || saving) return;
        if (action === "edit") {
            openForm(item, button);
            return;
        }
        if (action === "delete" && !window.confirm(`Hapus pengalaman “${item.title}”?`)) return;
        busyCards.add(item.id);
        button.disabled = true;
        try {
            if (action === "star") {
                await api(itemUrl(page.dataset.starUrl, item.id), "POST");
            } else {
                await api(itemUrl(page.dataset.detailUrl, item.id), "DELETE");
                if (editing?.id === item.id) closeForm();
                showToast("Terhapus", "Pengalaman berhasil dihapus.", "success");
            }
            await loadList();
        } catch (error) {
            showToast("Aksi gagal", error.message, "error");
        } finally {
            busyCards.delete(item.id);
            const current = grid.querySelector(`[data-id="${CSS.escape(item.id)}"]`);
            current?.querySelectorAll("[data-action]").forEach(control => { control.disabled = false; });
            if (document.activeElement === document.body) {
                (current?.querySelector(`[data-action="${action}"]`) || input).focus();
            }
        }
    }

    input.addEventListener("input", () => {
        clearTimeout(timer);
        activeRead?.abort();
        timer = setTimeout(loadList, 250);
    });
    search.addEventListener("submit", event => {
        event.preventDefault();
        loadList();
    });
    addButton?.addEventListener("click", () => openForm(null, addButton));
    page.querySelector("#cancel-experience")?.addEventListener("click", closeForm);
    form?.addEventListener("submit", save);
    loadList();
})();