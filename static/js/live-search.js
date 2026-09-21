(() => {
    const forms = document.querySelectorAll("[data-live-search]");

    forms.forEach((form) => {
        const input = form.querySelector('input[type="search"][name]');
        const targetSelector = form.dataset.liveSearchTarget;
        const target = targetSelector ? document.querySelector(targetSelector) : null;

        if (!input || !target) {
            return;
        }

        let debounceTimer = null;
        let controller = null;
        let requestId = 0;

        const fetchResults = async () => {
            const currentRequestId = requestId + 1;
            requestId = currentRequestId;
            const query = input.value.trim();

            if (controller) {
                controller.abort();
            }
            controller = new AbortController();

            const url = new URL(form.action, window.location.origin);
            const params = new URLSearchParams(window.location.search);

            if (query) {
                params.set(input.name, query);
            } else {
                params.delete(input.name);
            }

            url.search = params.toString();
            input.setAttribute("aria-busy", "true");
            target.setAttribute("aria-busy", "true");

            try {
                const response = await fetch(url, {
                    signal: controller.signal,
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                if (!response.ok) {
                    throw new Error(`Live search failed: ${response.status}`);
                }

                const html = await response.text();
                const documentFragment = new DOMParser().parseFromString(html, "text/html");
                const nextTarget = documentFragment.querySelector(targetSelector);

                if (!nextTarget || currentRequestId !== requestId) {
                    return;
                }

                target.replaceChildren(...nextTarget.childNodes);
                window.history.replaceState({}, "", `${url.pathname}${url.search}`);
            } catch (error) {
                if (error.name !== "AbortError") {
                    console.error(error);
                }
            } finally {
                if (currentRequestId === requestId) {
                    input.removeAttribute("aria-busy");
                    target.removeAttribute("aria-busy");
                }
            }
        };

        const scheduleSearch = () => {
            window.clearTimeout(debounceTimer);
            debounceTimer = window.setTimeout(fetchResults, 250);
        };

        input.addEventListener("input", scheduleSearch);

        form.addEventListener("submit", (event) => {
            event.preventDefault();
            window.clearTimeout(debounceTimer);
            fetchResults();
        });
    });
})();