/**
 * Toggle star tanpa reload halaman.
 *
 * Memakai event delegation di `document` agar tetap bekerja untuk kartu yang
 * dirender ulang oleh live search. Bila fetch gagal (jaringan putus, sesi
 * habis lalu dialihkan ke login, dll.) form dikirim secara normal sehingga
 * server tetap menjadi sumber kebenaran.
 */
(() => {
    const render = (button, school, { starred, star_count: count }) => {
        button.classList.toggle("is-starred", starred);
        button.setAttribute("aria-pressed", String(starred));
        button.setAttribute(
            "aria-label",
            `${starred ? "Batalkan star untuk" : "Beri star untuk"} ${school}`
        );
        button.querySelector(".star-label").textContent = starred ? "Unstar" : "Star";
        button.querySelector(".star-count").textContent = count;
    };

    document.addEventListener("submit", async (event) => {
        const form = event.target.closest("[data-star-form]");

        if (!form) {
            return;
        }

        event.preventDefault();

        const button = form.querySelector("button");

        if (button.disabled) {
            return;
        }

        button.disabled = true;

        try {
            const response = await fetch(form.action, {
                method: "POST",
                body: new FormData(form),
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    Accept: "application/json",
                },
            });

            const isJson = (
                response.headers.get("Content-Type") || ""
            ).includes("application/json");

            if (!response.ok || !isJson) {
                throw new Error(`Star gagal: ${response.status}`);
            }

            render(
                button,
                form.dataset.school,
                await response.json(),
            );
        } catch (error) {
            form.submit();
        } finally {
            button.disabled = false;
        }
    });
})();