/**
 * Utilitas JavaScript bersama untuk semua halaman.
 *
 * Dimuat lewat base.html sehingga fungsi di sini tersedia global:
 *   - escapeHtml : wajib dipakai sebelum menyisipkan teks dari server/API
 *                  ke dalam HTML (proteksi XSS).
 *   - getCookie  : membaca token CSRF dari cookie untuk request fetch().
 */

/**
 * Mengubah teks biasa menjadi aman untuk disisipkan ke dalam HTML.
 * Semua nilai yang datang dari server atau pengguna HARUS melewati fungsi
 * ini sebelum digabungkan ke string HTML agar tidak bisa dieksekusi.
 */
function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

/**
 * Membaca nilai cookie pertama yang cocok dengan `name`.
 * Dipakai untuk mengambil token CSRF (cookie `csrftoken`) milik Django.
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + "=") {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}