# MyPortofolio

Portofolio pribadi berbasis Django untuk menampilkan profil, **Experience**, dan **Education** secara dinamis. Proyek ini dikembangkan secara bertahap selama Tutorial/Pertemuan PBP dengan menerapkan HTML5/CSS3, Django MVT, database, form berbasis `ModelForm`, CRUD, JSON Data Delivery, template inheritance, serta beberapa fitur tambahan.

## Informasi Mahasiswa

- **Nama:** Adriel Raynard Davis Sihotang
- **NPM:** 2506587150
- **Kelas:** PBP B
- **Program Studi:** S1 Sistem Informasi
- **Institusi:** Universitas Indonesia

---

## Deskripsi Proyek

Website ini merupakan portofolio pribadi yang berkembang dari static web menjadi aplikasi Django yang mengambil data dari database.

Pada versi awal, informasi portofolio ditulis langsung pada template HTML. Pada tahap berikutnya, data **Education** dan **Experience** disimpan sebagai model Django sehingga dapat dikelola secara dinamis. Halaman web menggunakan template inheritance dengan `base.html`, sementara data juga tersedia melalui endpoint JSON.

Untuk menjaga konsistensi dan mengurangi pengulangan kode, template halaman web yang memiliki struktur umum menggunakan `{% extends "base.html" %}`. Template `portfolio_pdf.html` menjadi pengecualian karena dirender khusus oleh `xhtml2pdf` dan membutuhkan struktur HTML serta CSS tersendiri.

---

# Progres Mingguan

## Tugas 1 — Static Portfolio

### Deskripsi

Website pada tahap ini masih berupa **static web** yang dibuat dengan HTML5 dan CSS3. Halaman utama berisi informasi profil, foto, bio, informasi kontak/media sosial, serta bagian Skills.

### Fitur

- About Me / Profile
- Skills
- Informasi nama, NPM, program studi, bio, dan foto
- Social media links
- Responsive layout
- CSS Flexbox dan CSS Grid
- Hover effects dan animation
- Dark Mode berbasis CSS
- Media queries untuk tampilan desktop dan mobile

### Pembelajaran

Tahap ini berfokus pada struktur HTML yang rapi, elemen semantik, responsive design, dan pemisahan struktur halaman dengan styling CSS.

### Pertanyaan Reflektif Tugas 1

#### 1. Penggunaan Elemen Semantik HTML5

Saya menggunakan elemen semantik HTML5 seperti `<section>` dan `<aside>` untuk mengelompokkan konten berdasarkan fungsi dan hubungan informasinya. Misalnya, bagian About Me digunakan sebagai konten utama, sedangkan Skills dapat ditempatkan sebagai informasi pendukung.

Penggunaan elemen semantik membuat struktur dokumen lebih mudah dipahami, lebih terorganisasi, dan membantu proses styling maupun pengembangan halaman di tahap selanjutnya.

#### 2. Tantangan Responsive Layout

Tantangan utama adalah menjaga layout tetap rapi ketika ukuran layar berubah. Layout yang terlihat baik pada desktop dapat menjadi terlalu sempit pada layar mobile.

Solusinya adalah menggunakan CSS Grid, Flexbox, dan media queries. Pada ukuran layar yang lebih kecil, beberapa bagian diubah menjadi satu kolom sehingga informasi utama tetap mudah dibaca. Ukuran gambar dan spacing juga disesuaikan agar tidak mengambil terlalu banyak ruang.

#### 3. Batasan Static Web dan Pengembangan Selanjutnya

Pada static web, perubahan isi portofolio harus dilakukan langsung pada source code HTML. Hal ini kurang praktis ketika jumlah data bertambah.

Pengembangan berikutnya dilakukan dengan Django agar data dapat disimpan pada database, diproses oleh view, dan ditampilkan melalui template secara dinamis.

---

## Tugas 2 — Django MVT, Database, dan Education

### Deskripsi

Pada tahap ini proyek beralih menjadi aplikasi Django dengan arsitektur **Model-View-Template (MVT)**. Data riwayat pendidikan disimpan pada model `Education` dan diambil dari database menggunakan Django ORM.

Model `Education` memiliki field dengan tipe data yang beragam, antara lain:

- `nama_sekolah` — `CharField`
- `tingkat` — `CharField` dengan pilihan (`choices`)
- `jurusan` — `CharField`
- `tahun_masuk` — `PositiveIntegerField`
- `tahun_lulus` — `PositiveIntegerField` dan dapat dikosongkan
- `deskripsi` — `TextField`

### Alur Dasar MVT

1. Browser mengirim HTTP request ke server Django.
2. `portofolio/urls.py` menerima request lalu meneruskannya ke URL aplikasi `main` melalui `include()`.
3. `main/urls.py` mencocokkan URL dengan view yang sesuai.
4. View mengambil atau mengolah data menggunakan model dan Django ORM.
5. View mengirim data melalui context ke template.
6. Template menghasilkan HTML.
7. Django mengirim HTTP response kembali ke browser.

### Pertanyaan Reflektif Tugas 2

#### 1. Alur request sampai data tampil pada browser

Ketika pengguna membuka halaman seperti `/education/`, browser mengirim request ke server Django. Root URL di `portofolio/urls.py` meneruskan request ke `main/urls.py`. Setelah pola `education/` ditemukan, Django menjalankan `show_education` di `main/views.py`.

View kemudian mengambil data melalui model `Education`. Django ORM menerjemahkan operasi tersebut menjadi query ke database dan mengembalikan hasilnya. Data dimasukkan ke dalam context, lalu template `education.html` diproses menggunakan Django Template Language. Hasil akhirnya berupa HTML yang dikirim kembali sebagai HTTP response dan ditampilkan oleh browser.

#### 2. Mengapa data disimpan dalam model?

Data yang disimpan dalam model dapat dikelola secara terpusat dan tidak perlu ditulis berulang kali di template. Perubahan data dapat dilakukan tanpa mengubah struktur HTML, sehingga pemeliharaan menjadi lebih mudah.

Model juga memungkinkan data di-query, difilter, diurutkan, dan digunakan kembali pada halaman lain. Pemisahan antara data dan presentasi membuat aplikasi lebih mudah dikembangkan dibandingkan jika semua data di-hardcode di template.

#### 3. Perbedaan `makemigrations` dan `migrate`

`python manage.py makemigrations` membaca perubahan pada model dan membuat file migrasi sebagai catatan perubahan struktur database.

`python manage.py migrate` menerapkan file migrasi tersebut ke database sehingga perubahan benar-benar dibuat atau diubah pada tabel database.

Contohnya, ketika model `Education` ditambahkan, prosesnya adalah membuat migrasi terlebih dahulu dengan `makemigrations`, kemudian menerapkannya menggunakan `migrate`.

### Fitur Tambahan Tugas 2 — Download PDF

Saya menambahkan fitur **Download PDF** untuk mengunduh ringkasan Experience dan Education.

Alurnya adalah sebagai berikut:

1. Pengguna memilih `Download PDF` pada navbar.
2. Request masuk ke view `download_portfolio_pdf`.
3. View mengambil data Experience dan Education.
4. Data dirender menggunakan `portfolio_pdf.html`.
5. HTML dikonversi menjadi PDF menggunakan `xhtml2pdf`.
6. PDF dikembalikan sebagai `HttpResponse` dengan `Content-Disposition: attachment`.

Template PDF tidak melakukan `extends` dari `base.html` karena PDF dirender oleh library `xhtml2pdf`, bukan sebagai halaman web biasa.

---

### Tugas 3

## Tujuan

Tugas 3 berfokus pada dua hal utama:

1. **Refactoring template** menggunakan template inheritance agar struktur HTML yang sama tidak ditulis berulang.
2. Penerapan mekanisme **Create, Update, Delete, dan JSON Data Delivery** untuk data portofolio.

Pada tugas ini, **Education** digunakan sebagai bagian utama untuk memenuhi kebutuhan CRUD berbasis `ModelForm`. Pada versi akhir proyek, pola yang sama juga diterapkan pada **Experience** sehingga kedua bagian dapat dikelola secara dinamis.

## Refactoring Template

`templates/base.html` menjadi root template yang berisi skeleton dokumen HTML, navbar, dark-mode toggle, pemanggilan CSS/JavaScript, flash messages, dan footer.

Template berikut menggunakan inheritance:

- `templates/index.html`
- `templates/experience.html`
- `templates/education.html`
- `templates/form_page.html`

Pola yang digunakan adalah:

```django
{% extends "base.html" %}
```

Konten spesifik setiap halaman ditempatkan pada block seperti:

```django
{% block title %}...{% endblock title %}
{% block content %}...{% endblock content %}
```

### Pengecualian

`templates/portfolio_pdf.html` sengaja tidak melakukan `extends` dari `base.html`. Template tersebut memiliki struktur khusus untuk kebutuhan rendering PDF dengan `xhtml2pdf`, sehingga tidak identik dengan halaman web biasa.

## ModelForm

Untuk data Education, saya membuat `EducationForm` pada `main/forms.py` sebagai subclass `ModelForm`.

Field model yang digunakan antara lain:

```text
nama_sekolah : CharField
 tingkat    : CharField dengan choices
jurusan      : CharField
 tahun_masuk : PositiveIntegerField
tahun_lulus  : PositiveIntegerField / nullable
deskripsi    : TextField
```

`id` tidak dimasukkan ke dalam `Meta.fields` karena dibuat otomatis oleh model. Field yang berhubungan dengan timestamp juga tidak perlu diisi pengguna.

Selain field model, form memiliki `secret` sebagai field tambahan untuk memverifikasi kode rahasia sebelum operasi tulis.

`ExperienceForm` juga menggunakan `ModelForm` dan mengelola field `title`, `description`, `category`, serta `thumbnail`. Status selesai/berjalan direpresentasikan oleh checkbox `is_finished`, lalu diterjemahkan menjadi `ended_at` ketika form disimpan.

## Create, Update, Delete

### Education

- Create: `/education/add/`
- Update: `/education/<uuid>/edit/`
- Delete: `/education/<uuid>/delete/`
- List: `/education/`

### Experience

- Create: `/experience/add/`
- Update: `/experience/<uuid>/edit/`
- Delete: `/experience/<uuid>/delete/`
- List: `/experience/`

View form menggunakan pola **POST-Redirect-GET**. Request GET menampilkan form, sedangkan POST memvalidasi data lalu menyimpannya. Jika berhasil, pengguna diarahkan kembali ke halaman daftar dan mendapatkan flash message.

## CSRF Protection

Semua form yang mengubah data memakai:

```django
{% csrf_token %}
```

Hal ini penting agar request POST dari aplikasi memiliki token CSRF yang valid dan tidak mudah dipalsukan oleh situs lain. Form delete juga menggunakan CSRF token karena operasi penghapusan merupakan perubahan state.

## JSON Data Delivery

Data portofolio tersedia dalam format JSON melalui endpoint berikut:

### Education

```text
GET /api/education/
GET /api/education/<uuid>/
```

Filter nama sekolah dapat digunakan melalui query parameter:

```text
GET /api/education/?nama_sekolah=Universitas
```

### Experience

```text
GET /api/experience/
GET /api/experience/<uuid>/
```

Filter judul dapat digunakan melalui query parameter:

```text
GET /api/experience/?title=Backend
```

View JSON menggunakan Django serializer, misalnya:

```python
serializers.serialize("json", queryset)
```

Response dikembalikan sebagai `application/json`.

## Deserialisasi pada Halaman Web

Halaman Education dan Experience tidak hanya mengambil queryset langsung untuk ditampilkan. View halaman memanggil endpoint JSON, kemudian melakukan deserialisasi kembali menjadi object model Django.

Alurnya:

```text
Database
   ↓
Django ORM / QuerySet
   ↓
Serialization
   ↓
JSON Response
   ↓
Deserialization
   ↓
Model Instances
   ↓
Template
   ↓
HTML pada Browser
```

Pada kode, proses deserialisasi dilakukan melalui `serializers.deserialize("json", ...)` lalu object hasilnya diambil dari `item.object`.

---

#### Pertanyaan Reflektif

### 1. Mengapa menggunakan `ModelForm` dan mengapa perlu `{% csrf_token %}`?

`ModelForm` digunakan karena form berhubungan langsung dengan model Django. Dengan `ModelForm`, struktur field form dapat dibuat berdasarkan field pada model tanpa harus mendefinisikan ulang seluruh field secara manual di HTML. Django juga dapat menangani validasi tipe data, validasi field, error message, dan proses penyimpanan object ke database melalui `form.save()`.

Pendekatan ini membuat kode lebih singkat, mengurangi duplikasi antara model dan form, serta menjaga agar aturan validasi yang diterapkan pada form tetap konsisten dengan struktur model. Pada proyek ini, `EducationForm` juga dapat digunakan untuk Create maupun Update dengan memberikan `instance` saat mengedit data.

`{% csrf_token %}` diperlukan pada form yang melakukan perubahan data, terutama request POST. CSRF token membantu Django membedakan request yang benar-benar berasal dari sesi pengguna pada aplikasi dengan request palsu yang dikirim oleh situs lain. Tanpa token CSRF yang valid, middleware perlindungan CSRF Django dapat menolak request tersebut.

### 2. Mengapa JSON lebih disukai daripada XML dalam banyak aplikasi web modern?

JSON biasanya lebih disukai untuk API web modern karena sintaksnya relatif ringkas dan langsung merepresentasikan struktur data seperti object, array, string, number, boolean, dan `null`. Struktur tersebut juga sangat dekat dengan struktur data yang umum digunakan pada JavaScript dan banyak bahasa pemrograman modern.

Dibandingkan XML, JSON biasanya membutuhkan lebih sedikit markup sehingga payload lebih ringan dan lebih mudah dibaca manusia. Parsing JSON juga umumnya sederhana untuk aplikasi web.

XML tetap relevan untuk kebutuhan tertentu, terutama sistem yang memerlukan atribut, namespace, schema yang kompleks, atau kompatibilitas dengan sistem lama. Jadi, penggunaan JSON bukan berarti XML selalu lebih buruk; JSON lebih cocok untuk pola pertukaran data yang umum digunakan pada banyak aplikasi web modern.

### 3. Apa alur view ketika mengembalikan data dalam bentuk JSON dan mengapa perlu serialization?

Ketika pengguna mengakses endpoint, misalnya `/api/education/`, request pertama-tama masuk ke `portofolio/urls.py`, kemudian diteruskan ke `main/urls.py`. URL tersebut dipetakan ke `get_education_json`.

View mengambil data `Education` menggunakan Django ORM. Setelah itu, queryset diserialisasi menggunakan Django serializer:

```python
serializers.serialize("json", education)
```

Hasil serialization berupa string JSON yang memuat informasi model, primary key, dan field-field data. String tersebut kemudian dikembalikan melalui `HttpResponse` dengan content type `application/json`.

Pada halaman `/education/`, view `show_education` menggunakan response JSON tersebut, membaca isinya, lalu melakukan deserialisasi dengan `serializers.deserialize("json", ...)`. Object hasil deserialisasi diberikan ke template sehingga data yang ditampilkan melalui halaman web berasal dari jalur JSON yang sama.

Serialization diperlukan karena object model Django dan QuerySet bukan format data yang bisa dikirim begitu saja sebagai JSON. Serialization mengubah object tersebut menjadi representasi data yang dapat ditransmisikan sebagai teks JSON dan dipahami oleh client atau proses lain.

---

# Struktur Project

Struktur penting proyek saat ini:

```text
myportofolio/
├── manage.py
├── README.md
├── requirements.txt
├── .env
├── main/
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── portofolio/
│   ├── settings.py
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── experience.html
│   ├── education.html
│   ├── form_page.html
│   ├── portfolio_pdf.html
│   └── components/
│       ├── delete_modal.html
│       └── messages.html
└── static/
    ├── css/
    │   └── style.css
    ├── js/
    │   └── live-search.js
    └── img/
        └── fotoAdriel.png
```

### Tanggung Jawab File Utama

| File | Fungsi |
|---|---|
| `main/models.py` | Mendefinisikan model `Experience` dan `Education` |
| `main/forms.py` | Mendefinisikan `ModelForm` dan validasi kode rahasia |
| `main/views.py` | Menangani halaman, CRUD, JSON delivery, deserialisasi, dan PDF |
| `main/urls.py` | Menghubungkan URL dengan view aplikasi `main` |
| `portofolio/urls.py` | Root URL project dan `include()` ke aplikasi `main` |
| `templates/base.html` | Root template untuk halaman web biasa |
| `templates/form_page.html` | Template reusable untuk Create dan Update |
| `templates/components/delete_modal.html` | Modal konfirmasi delete yang reusable |
| `templates/portfolio_pdf.html` | Template khusus untuk rendering PDF |
| `main/tests.py` | Pengujian view, form, JSON, CRUD, template inheritance, dan PDF |

---

# Teknologi yang Digunakan

- Python
- Django
- SQLite untuk development/local database
- HTML5
- CSS3
- Django Template Language (DTL)
- Django ORM
- Django ModelForm
- JSON serialization/deserialization
- JavaScript untuk live search
- `xhtml2pdf` untuk export PDF
- Gunicorn / WhiteNoise untuk kebutuhan deployment
- PostgreSQL dependency untuk deployment/production environment

---

# Setup dan Menjalankan Project Secara Lokal

## 1. Masuk ke direktori project

```bash
cd myportofolio
```

## 2. Buat virtual environment

### Windows

```bash
python -m venv env
env\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv env
source env/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Siapkan environment variable

Buat file `.env` di root project. Jangan memasukkan secret asli ke repository publik.

Contoh:

```env
PORTFOLIO_SECRET=ganti_dengan_kode_rahasia_sendiri
```

`PORTFOLIO_SECRET` digunakan untuk melindungi operasi Create, Update, dan Delete pada data portofolio.

## 5. Jalankan migrasi database

```bash
python manage.py makemigrations
python manage.py migrate
```

Jika repository sudah memiliki migration files dan tidak ada perubahan model, `makemigrations` biasanya tidak menghasilkan migrasi baru; `migrate` tetap digunakan untuk memastikan database mengikuti migration history.

## 6. Jalankan test

```bash
python manage.py test
```

Test suite mencakup, antara lain:

- halaman utama dan halaman Experience/Education
- template inheritance
- keberadaan satu skeleton HTML
- JSON endpoint dan filter
- serialization/deserialization
- Create/Update/Delete
- validasi form
- CSRF-protected POST flow
- flash message
- PDF response dan link download

## 7. Jalankan development server

```bash
python manage.py runserver
```

Kemudian buka:

```text
http://localhost:8000/
```

---

# Verifikasi Fitur Tugas 3

Sebelum submission, lakukan checklist berikut pada local server:

### Template

- [ ] `/` dapat dibuka
- [ ] `/experience/` dapat dibuka
- [ ] `/education/` dapat dibuka
- [ ] Halaman form Create/Update menggunakan `base.html`
- [ ] Navbar dan Dark Mode tetap muncul konsisten
- [ ] `portfolio_pdf.html` tetap standalone

### Education CRUD

- [ ] Klik **Tambah Pendidikan**
- [ ] Isi form dan kode rahasia yang benar
- [ ] Pastikan data muncul pada halaman Education
- [ ] Ubah data menggunakan tombol Ubah
- [ ] Hapus data melalui tombol Hapus
- [ ] Coba kode rahasia salah dan pastikan data tidak terhapus

### Experience CRUD

- [ ] Tambah Experience
- [ ] Ubah Experience
- [ ] Hapus Experience
- [ ] Uji status ongoing/finished

### JSON

- [ ] Buka `/api/education/`
- [ ] Buka `/api/experience/`
- [ ] Uji endpoint detail menggunakan UUID
- [ ] Uji filter query parameter
- [ ] Pastikan response memiliki `Content-Type: application/json`
- [ ] Pastikan halaman HTML tetap menampilkan data melalui proses deserialisasi JSON

---

# Catatan Implementasi dan Keputusan Desain

## 1. Reusable Form Template

`form_page.html` dibuat sebagai template reusable untuk Create dan Update. View hanya mengirim context seperti `form`, `heading`, `submit_label`, dan `cancel_url`, sehingga tidak diperlukan file HTML form terpisah untuk setiap operasi.

## 2. Reusable Delete Component

`components/delete_modal.html` digunakan oleh Experience dan Education. Komponen menerima parameter seperti `item_id`, `item_label`, `delete_url`, dan `noun` sehingga dapat dipakai untuk beberapa jenis data.

## 3. Secret Code untuk Operasi Tulis

Karena situs portofolio dapat diakses publik, operasi tulis diberi proteksi tambahan menggunakan `PORTFOLIO_SECRET`. Kode rahasia tidak ditulis langsung pada template dan diambil dari environment variable.

Form menggunakan `SecretCodeField`, sedangkan delete menggunakan `SecretCodeForm`. Perbandingan secret menggunakan `hmac.compare_digest` dan konfigurasi dibuat fail closed ketika secret tidak tersedia.

Fitur ini merupakan pengamanan tambahan untuk proyek pembelajaran dan bukan pengganti sistem autentikasi/otorisasi pengguna yang lengkap.

## 4. POST-Redirect-GET

Setelah POST yang berhasil, view melakukan redirect ke halaman daftar. Pola ini mencegah resubmission ketika pengguna melakukan refresh pada browser dan sekaligus membuat hasil aksi lebih mudah dipahami.

---

Fitur Ekstra: Live Search

Selain fitur wajib pada Tugas 3, proyek ini memiliki fitur tambahan berupa Live Search pada halaman Experience dan Education. Fitur ini memungkinkan pengguna mencari data secara langsung berdasarkan kata kunci tanpa harus melakukan reload halaman secara penuh.

Cara Kerja

Pada halaman Experience, pengguna dapat mencari pengalaman berdasarkan judul melalui parameter title, sedangkan pada halaman **Education, pencarian dilakukan berdasarkan nama sekolah melalui parameter nama_sekolah`.

Ketika pengguna mengetik pada kolom pencarian, JavaScript pada static/js/live-search.js akan menangkap event input. Pencarian tidak langsung dikirim untuk setiap karakter, tetapi menggunakan teknik debouncing selama 250 ms. Hal ini mengurangi jumlah request yang dikirim ke server ketika pengguna masih mengetik.

Setelah jeda tersebut selesai, JavaScript mengirim request GET menggunakan fetch() ke URL halaman dengan query parameter yang sesuai. Server Django kemudian memproses query tersebut menggunakan filter icontains, sehingga pencarian tidak harus sama persis dengan teks yang tersimpan di database.

Sebagai contoh:

/experience/?title=organisasi

atau:

/education/?nama_sekolah=universitas

View Django kemudian mengambil data yang sesuai dan merender halaman berdasarkan hasil pencarian. JavaScript membaca kembali HTML tersebut, mengambil bagian grid hasil pencarian, kemudian mengganti isi grid pada halaman yang sedang dibuka. Dengan demikian, daftar hasil dapat diperbarui tanpa melakukan full page reload.

## Fitur Ekstra: Live Search

Selain fitur wajib pada Tugas 3, proyek ini memiliki fitur tambahan berupa **Live Search** pada halaman **Experience** dan **Education**. Fitur ini memungkinkan pengguna mencari data secara langsung berdasarkan kata kunci tanpa harus melakukan reload halaman secara penuh.

### Cara Kerja

Pada halaman **Experience**, pengguna dapat mencari pengalaman berdasarkan judul melalui parameter `title`, sedangkan pada halaman **Education`, pencarian dilakukan berdasarkan nama sekolah melalui parameter `nama_sekolah`.

Ketika pengguna mengetik pada kolom pencarian, JavaScript pada `static/js/live-search.js` akan menangkap event `input`. Pencarian tidak langsung dikirim untuk setiap karakter, tetapi menggunakan teknik **debouncing selama 250 ms**. Hal ini mengurangi jumlah request yang dikirim ke server ketika pengguna masih mengetik.

Setelah jeda tersebut selesai, JavaScript mengirim request `GET` menggunakan `fetch()` ke URL halaman dengan query parameter yang sesuai. Server Django kemudian memproses query tersebut menggunakan filter `icontains`, sehingga pencarian tidak harus sama persis dengan teks yang tersimpan di database.

Sebagai contoh:

```text
/experience/?title=organisasi
```

atau:

```text
/education/?nama_sekolah=universitas
```

View Django kemudian mengambil data yang sesuai dan merender halaman berdasarkan hasil pencarian. JavaScript membaca kembali HTML tersebut, mengambil bagian grid hasil pencarian, kemudian mengganti isi grid pada halaman yang sedang dibuka. Dengan demikian, daftar hasil dapat diperbarui tanpa melakukan full page reload.

### Optimasi dan Penanganan Request

Implementasi Live Search memiliki beberapa mekanisme tambahan:

* **Debouncing 250 ms** untuk mengurangi request yang terlalu sering ketika pengguna mengetik.
* **`AbortController`** untuk membatalkan request sebelumnya apabila pengguna sudah mengetik kata kunci baru.
* **Request ID** untuk memastikan response dari request lama tidak menimpa hasil pencarian yang lebih baru.
* **`history.replaceState()`** untuk memperbarui query parameter pada URL tanpa melakukan reload halaman.
* Atribut **`aria-busy`** digunakan ketika request sedang diproses agar status loading dapat dikenali oleh teknologi bantu.

### Mengapa Fitur Ini Ditambahkan?

Fitur Live Search ditambahkan untuk meningkatkan **usability** portofolio. Pengguna tidak perlu menekan tombol atau memuat ulang seluruh halaman setiap kali ingin mencari data. Fitur ini juga menunjukkan penggunaan JavaScript dan komunikasi asynchronous antara browser dengan server Django dalam proyek.

Fitur ini bersifat **tambahan (extra feature)** dan tidak menggantikan requirement utama Tugas 3 seperti Create, Update, Delete, ModelForm, dan JSON Data Delivery.

# AI Disclosure

## Tools yang Digunakan

Dalam pengerjaan proyek selama semester, saya menggunakan AI sebagai alat bantu belajar, brainstorming, debugging, review, dan penyusunan dokumentasi , bukan sebagai pengganti proses memahami dan memverifikasi kode.

Tool yang saya gunakan:

- Claude AI — terutama untuk berdiskusi mengenai struktur HTML/CSS dan pengembangan Django pada tahap awal.
- ChatGPT — digunakan untuk debugging, menjelaskan error, mengecek implementasi Django dan membandingkan kode sebelum/sesudah.

## Strategi Prompting

Saya biasanya memberikan konteks terlebih dahulu, kemudian meminta AI melakukan tugas yang spesifik. Contoh strategi yang digunakan:

1. Context-first — menyertakan potongan kode, traceback/error, struktur file, atau instruksi tugas.
2. Constraint-aware — meminta solusi tetap sesuai materi yang sedang dipelajari dan tidak menambahkan teknologi yang belum diperlukan.
3. Step-by-step debugging** — meminta AI menjelaskan sumber error, file yang terlibat, dan perubahan minimal yang diperlukan.
4. Verification — meminta checklist atau test case agar hasil implementasi dapat diperiksa kembali secara manual.
5. Refinement — setelah solusi awal diberikan, kode disesuaikan kembali dengan struktur proyek, style, dan kebutuhan tugas.

## Bagian yang Dibantu AI

AI membantu saya terutama pada:

- review dan perbaikan struktur HTML/CSS pada Tugas 1
- pemahaman alur Django MVT pada Tugas 2
- debugging routing dan URL namespacing Django
- penjelasan konsep `ModelForm`, CSRF, migration, serialization, dan deserialization
- saran refactoring template menjadi `base.html` + `{% extends %}`
- ide struktur CRUD dan reusable form template
- review test case dan edge case
- penyusunan dokumentasi dan pertanyaan reflektif pada Tugas 3

Kode final tetap saya tinjau, sesuaikan, dan jalankan sendiri agar kompatibel dengan project saya.

## Contoh Log Prompting

| Tahap | Kebutuhan | Ringkasan Prompt | Hasil yang Dipakai |
|---|---|---|---|
| Tugas 1 | HTML/CSS | Meminta review struktur semantic HTML, responsive layout, CSS Grid/Flexbox, dan Dark Mode | Saran struktur dan styling |
| Tugas 2 | Django MVT | Meminta penjelasan request-response serta hubungan `urls.py`, view, model, dan template | Pemahaman konsep + dokumentasi |
| Debugging | URL namespace | Menyertakan traceback `NoReverseMatch` dan meminta diagnosis sumber namespace | Koreksi routing/reverse URL |
| Tugas 3 | Refactoring | Meminta cara mengubah halaman yang memiliki skeleton sama menjadi `{% extends "base.html" %}` | Struktur `base.html` dan child templates |
| Tugas 3 | CRUD/JSON | Menyertakan requirement tugas dan kode sebelum/sesudah untuk direview | Review implementasi CRUD, JSON, dan deserialisasi |
| Tugas 3 | README | Meminta penyusunan README yang memenuhi rubrik, termasuk refleksi dan AI disclosure | Dokumentasi mingguan dan refleksi |

## Keterbatasan AI dan Perbaikan Manual

AI sangat membantu untuk menghasilkan kemungkinan solusi dengan cepat, tetapi saran AI tidak selalu langsung cocok dengan project. Beberapa keterbatasan yang saya temui adalah:

- AI dapat menyarankan kode yang tidak sesuai dengan nama route, struktur folder, atau versi Django yang digunakan.
- AI dapat memberikan solusi yang terlalu kompleks dibandingkan kebutuhan tugas.
- Penjelasan AI dapat terlihat masuk akal tetapi tetap perlu diverifikasi terhadap kode aktual, traceback, dokumentasi, dan hasil runtime.
- Contoh kode dari AI tidak otomatis menjamin bahwa seluruh halaman memiliki context, URL namespace, atau dependency yang benar.

Karena itu, saya melakukan perbaikan manual dengan mengecek file yang benar-benar digunakan project, mencocokkan nama URL namespace seperti `main:...`, menyesuaikan reusable template dengan CSS yang sudah ada, dan mempertahankan `portfolio_pdf.html` sebagai template standalone karena kebutuhan rendering PDF berbeda dari halaman browser. Salah satu masalah yang saya temui adalah error `NoReverseMatch` karena namespace `main` belum terdaftar dengan benar; saya telusuri konfigurasi root/app URL dan pemanggilan `{% url %}` sampai referensinya konsisten.

Saya juga menambahkan dan meninjau test untuk memastikan fitur tidak hanya terlihat benar secara visual, tetapi juga bekerja secara fungsional, termasuk pengujian JSON endpoint, CRUD, form validation, template inheritance, flash message, dan PDF.

# Tugas 4 — Autentikasi, Otorisasi, dan Star

## Tujuan

Menerapkan pola autentikasi dan otorisasi dari Tutorial 04 pada portofolio hasil Tugas 3:

1. **Halaman daftar dan JSON tetap publik.**
2. **Perubahan data dan pemberian star mengikuti hak akses.**
3. Ada peran baru, **Editor**, yang boleh mengubah data tanpa memiliki seluruh hak pemilik.

---

## Matriks Hak Akses

| Aksi                                              | Pengunjung        | Pengguna | Editor | Pemilik (superuser) |
| ------------------------------------------------- | ----------------- | -------- | ------ | ------------------- |
| Melihat Profile, Experience, Education, JSON, PDF | Ya                | Ya       | Ya     | Ya                  |
| Memberi / membatalkan star                        | Redirect ke login | Ya       | Ya     | Ya                  |
| Mengubah (update) data                            | Redirect ke login | 403      | Ya     | Ya                  |
| Membuat (create) data                             | Redirect ke login | 403      | 403    | Ya                  |
| Menghapus (delete) data                           | Redirect ke login | 403      | 403    | Ya                  |

> **Hierarki peran:** Peran Editor mewarisi hak Pengguna, dan Pemilik mewarisi hak Editor.

---

# 1. Autentikasi

### Register

**`/register/`** memakai `UserCreationForm`.

Akun baru otomatis berperan **Pengguna**.

### Login

**`/login/`** memakai `AuthenticationForm` bawaan Django dan `login()`, lalu mengisi cookie `last_login`.

Parameter **`?next=`** didukung sehingga pengguna kembali ke halaman tujuan setelah login.

Nilai `next` divalidasi dengan `url_has_allowed_host_and_scheme` agar tidak menjadi **open redirect**.

### Logout

**`/logout/`** mengakhiri sesi dan menghapus cookie `last_login`.

### Profile dan Navbar

Halaman Profile menampilkan nilai cookie `last_login` sebagai **"Sesi Terakhir Login"**.

Navbar menampilkan username dan **badge peran** (Owner / Editor / User) untuk akun yang login.

---

# 2. Otorisasi (Server-Side)

Logika peran ada di **`main/permissions.py`**.

### Komponen Otorisasi

**`is_owner(user)`**

`True` bila user terautentikasi dan `is_superuser`.

**`is_editor(user)`**

`True` bila user anggota group `Editor`:

```python
user.groups.filter(name="Editor").exists()
```

**`can_edit(user)`**

```python
is_owner or is_editor
```

**`role_required(predicate)`**

Pembuat decorator:

* `@login_required` lebih dulu
* lalu `predicate`
* belum login menghasilkan **redirect 302 ke login**
* sudah login tapi tidak berhak menghasilkan **HTTP 403** (`PermissionDenied`)

**`owner_required`**

Dipakai untuk `create_*` dan `delete_*`.

**`editor_or_owner_required`**

Dipakai untuk `update_*`.

### Pemasangan Decorator pada View

**`create_education`, `create_experience`**

```python
@owner_required
```

**`update_education`, `update_experience`**

```python
@editor_or_owner_required
```

**`delete_education`, `delete_experience`**

```python
@owner_required
@require_POST
```

**`toggle_star`**

```python
@login_required
@require_POST
```

> **Penting:** Pemeriksaan ada di view (server), bukan hanya di template, sehingga akses langsung lewat URL tetap ditolak.

---

# 3. Peran Editor lewat Django `Group`

Group **`Editor`** dibuat otomatis oleh data migration:

```text
main/migrations/0007_create_editor_group.py
```

Jadi group tersebut tersedia di database baru tanpa langkah manual.

### Menambahkan User sebagai Editor

Keanggotaan ditetapkan lewat **Django Admin**:

```text
/admin/ → Users → pilih user → Groups → Editor
```

### Context Processor

Template membaca peran lewat context processor:

```text
main.context_processors.roles
```

Context processor ini mengirim `is_editor` dan `user_role` ke semua template.

Kondisi yang dipakai:

```django
{% if user.is_superuser or is_editor %}
```

### Editor dan Kode Rahasia

Karena hak Editor diverifikasi lewat group, Editor **tidak** perlu mengetahui kode rahasia pemilik saat mengubah data:

```text
require_secret=False
```

pada `OptionalSecretMixin`.

---

# 4. Kontrol Aksi pada Template

Tombol disembunyikan bagi pengguna yang tidak berhak.

### Tambah Pendidikan / Tambah Pengalaman

**Tampil untuk:** Pemilik (`user.is_superuser`)

### Ubah

**Tampil untuk:** Pemilik dan Editor (`user.is_superuser or is_editor`)

### Hapus

**Tampil untuk:** Pemilik

Termasuk **modal konfirmasi**.

### Tombol Star

**Tampil untuk:** Pengguna yang login

Pengunjung melihat:

> **Login untuk Star**

---

# 5. Fitur Star (`ManyToManyField`)

Model `Education` memiliki:

```python
starred_by = ManyToManyField(
    User,
    related_name="starred_education",
    blank=True
)
```

### Migrasi

**Migrasi `0005`**

Menambahkan field.

**Migrasi `0006`**

Mengganti `related_name` awal:

```text
starred_projects
```

yang mengikuti istilah di tutorial menjadi:

```text
starred_education
```

agar sesuai dengan model.

### View `toggle_star`

Endpoint:

```text
POST /educations/<uuid>/star/
```

Nama route:

```text
main:toggle_star
```

### Perilaku Toggle

Bila user sudah ada di `starred_by`, star dibatalkan.

Bila belum, star diberikan.

Relasi M2M menjamin **maksimal satu star per user**.

### Respons JavaScript

Permintaan dari JavaScript dengan header:

```text
X-Requested-With
```

dibalas JSON:

```json
{
    "starred": bool,
    "star_count": int
}
```

Sehingga tombol diperbarui **tanpa reload**.

### Fallback Tanpa JavaScript

Submit form biasa tanpa JavaScript dibalas redirect ke halaman Education.

Bila `fetch()` gagal,:

```text
static/js/star-toggle.js
```

mengirim form secara normal sebagai fallback.

### Komponen Tombol Star

File:

```text
templates/components/education_star.html
```

memuat:

```html
<form method="post">
```

dengan:

```django
{% csrf_token %}
```

Komponen ini menampilkan:

* **jumlah total star**
* **status star user**
* `Star` / `Unstar`
* `aria-pressed`

### Perhitungan Star

Jumlah star dan status user dihitung di view melalui:

```text
_attach_education_star_state
```

dengan:

```python
Count("starred_by")
```

sehingga tidak ada query per kartu.

---

# 6. Integritas API dan Keamanan Data

Endpoint JSON Tugas 3 tetap berfungsi dan tetap **publik**.

Method yang digunakan hanya:

```text
GET
HEAD
```

### Whitelist Field JSON

Serializer memakai **whitelist field**:

```text
EDUCATION_JSON_FIELDS
EXPERIENCE_JSON_FIELDS
```

Tanpa whitelist, serializer Django akan ikut menyertakan field M2M:

```text
starred_by
```

berupa daftar ID akun.

Dengan whitelist, **tidak ada identitas atau ID pengguna yang bocor lewat API**.

### Endpoint Detail

Endpoint detail yang tidak ditemukan mengembalikan **JSON 404**, bukan halaman HTML.

### Keamanan Operasi Tulis

Aksi tulis memakai:

```text
POST
```

dengan CSRF token.

`PORTFOLIO_SECRET` dibaca dari `.env`, dibandingkan dengan:

```python
hmac.compare_digest
```

dan **fail closed** bila belum diatur.

---

# Daftar Endpoint

### Public

**`/`**

* Method: `GET`
* Akses: Publik
* Keterangan: Profile dan cookie `last_login`

**`/experience/`**

**`/education/`**

* Method: `GET`
* Akses: Publik
* Keterangan: Daftar (data dari JSON, dideserialisasi)

**`/api/experience/`**

**`/api/education/`**

* Method: `GET`
* Akses: Publik
* Keterangan: JSON daftar
* Filter: `?title=` / `?nama_sekolah=`

**`/api/experience/<uuid>/`**

**`/api/education/<uuid>/`**

* Method: `GET`
* Akses: Publik
* Keterangan: JSON detail

**`/portfolio/pdf/`**

* Method: `GET`
* Akses: Publik
* Keterangan: Unduh PDF

**`/register/`**

**`/login/`**

**`/logout/`**

* Method: `GET/POST`
* Akses: Publik
* Keterangan: Autentikasi

### Login Required

**`/educations/<uuid>/star/`**

* Method: `POST`
* Akses: Login
* Keterangan: Toggle star

### Editor dan Pemilik

**`/education/<uuid>/edit/`**

**`/experience/<uuid>/edit/`**

* Method: `GET/POST`
* Akses: Editor, Pemilik
* Keterangan: Update

### Pemilik

**`/education/add/`**

**`/experience/add/`**

* Method: `GET/POST`
* Akses: Pemilik
* Keterangan: Create

**`/education/<uuid>/delete/`**

**`/experience/<uuid>/delete/`**

* Method: `POST`
* Akses: Pemilik
* Keterangan: Delete

### Staff

**`/admin/`**

* Method: `GET/POST`
* Akses: Staff
* Keterangan: Django Admin (kelola group Editor)

---

# Pemetaan ke Checklist Tugas

### Peran Editor lewat `Group` atau `Permission`

**Implementasi:** Group `Editor` (migrasi `0007`), keanggotaan lewat Django Admin.

### Pembatasan hak akses di server (redirect login / 403)

**Implementasi:** `main/permissions.py`, dipasang sebagai decorator di `main/views.py`.

### Sembunyikan tombol create/update/delete

**Implementasi:** Kondisi `user.is_superuser` / `is_editor` di template.

### `ManyToManyField` ke `User` + migrasi

**Implementasi:** `Education.starred_by`, migrasi `0005` dan `0006`.

### View `toggle_star`

**Implementasi:** `toggle_star` + `components/education_star.html`

Menggunakan:

```django
POST + {% csrf_token %}
```

serta jumlah dan status star.

### Endpoint JSON aman

**Implementasi:** Whitelist field, `starred_by` tidak diserialisasi.

### Berjalan dengan `python manage.py runserver`

**Implementasi:** Lihat bagian **Setup dan Menjalankan Project**.

---

# Struktur Project

```text
myportofolio/

├── manage.py
├── README.md
├── requirements.txt
├── test_e2e.py                     # uji end-to-end Selenium (opsional)
├── .env                            # tidak masuk repository
│
├── main/
│   ├── models.py                   # Experience, Education (+ starred_by)
│   ├── forms.py                    # ModelForm, SecretCodeField, OptionalSecretMixin
│   ├── views.py                    # halaman, CRUD, JSON, PDF, auth, toggle_star
│   ├── permissions.py              # peran + decorator otorisasi
│   ├── context_processors.py       # is_editor, user_role untuk template
│   ├── urls.py
│   ├── admin.py
│   ├── tests.py                    # 122 metode test
│   └── migrations/                 # 0005-0007: star, related_name, group Editor
│
├── portofolio/
│   ├── settings.py
│   └── urls.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── experience.html
│   ├── education.html
│   ├── form_page.html
│   ├── login.html
│   ├── register.html
│   ├── portfolio_pdf.html
│   └── components/
│       ├── delete_modal.html
│       ├── education_star.html
│       └── messages.html
│
└── static/
    ├── css/style.css
    ├── js/live-search.js
    ├── js/star-toggle.js
    └── img/fotoAdriel.png
```

---

# Teknologi yang Digunakan

* **Python dan Django 6.0** (`django<6.1`)
* **SQLite** (lokal) dan **PostgreSQL** (produksi, lewat `PRODUCTION=True`)
* **Django Auth** (`User`, `Group`, session), Django ORM, `ModelForm`, serializers
* **HTML5, CSS3, Django Template Language**
* **JavaScript** (live search dan toggle star)
* **`xhtml2pdf`** untuk ekspor PDF
* **`python-dotenv`** untuk environment variable
* **`whitenoise`** dan **`gunicorn`** untuk deployment
* **Selenium** (hanya untuk `test_e2e.py`, tidak ada di `requirements.txt`)

---

# Setup dan Menjalankan Project

## Prasyarat

**Python 3.12 atau lebih baru**

Dikembangkan dengan Python 3.13.

Selain itu diperlukan:

```text
git
```

## 1. Clone dan masuk ke direktori project

```bash
git clone <url-repository>

cd myportofolio
```

## 2. Buat dan aktifkan virtual environment

### Windows

```bash
python -m venv env

env\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv env

source env/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Siapkan file `.env`

Buat file `.env` di root project, sejajar dengan `manage.py`.

File ini ada di `.gitignore`, jadi **jangan di-commit**.

```env
PORTFOLIO_SECRET=isi_dengan_kode_rahasia_sendiri
```

`PORTFOLIO_SECRET` dipakai untuk melindungi operasi tulis milik **Pemilik**:

```text
create
update
delete
```

Bila tidak diisi, server tetap berjalan, tetapi operasi tulis Pemilik ditolak (**fail closed**).

Peran Editor tidak memakai kode ini.

### Variabel Tambahan (Opsional)

```env
# Hanya untuk test_e2e.py
E2E_USER_PASSWORD=...
E2E_ADMIN_PASSWORD=...

# Hanya untuk produksi (PostgreSQL)
PRODUCTION=True
DB_NAME=...
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=...
```

## 5. Terapkan migrasi database

```bash
python manage.py migrate
```

Perintah ini:

* membuat tabel
* membuat relasi star
* mengisi data pendidikan awal
* **membuat group `Editor` secara otomatis**

Berkas `db.sqlite3` tidak ikut repository, jadi langkah ini **wajib pada clone baru**.

Bila mengubah model sendiri, jalankan:

```bash
python manage.py makemigrations
```

sebelum:

```bash
python manage.py migrate
```

## 6. Buat akun Pemilik (superuser)

```bash
python manage.py createsuperuser
```

## 7. Jalankan server

```bash
python manage.py runserver
```

Buka:

```text
http://localhost:8000/
```

Panel admin ada di:

```text
http://localhost:8000/admin/
```

## 8. Buat akun untuk setiap peran

### Pemilik

Akun dari langkah 6.

### Pengguna

Daftar lewat:

```text
/register/
```

### Editor

1. Daftar lewat `/register/`.
2. Login ke `/admin/` sebagai Pemilik.
3. Buka **Users**.
4. Pilih akun tersebut.
5. Buka **Groups**.
6. Tambahkan `Editor`.
7. **Save**.

## 9. Jalankan test

```bash
python manage.py test
```

Test suite (**122 metode**) mencakup:

* halaman dan template inheritance
* JSON dan filter
* serialisasi/deserialisasi
* CRUD dan validasi form
* kode rahasia
* redirect login dan 403 untuk tiap peran
* visibilitas tombol per peran
* toggle star
* satu star per user
* JSON tanpa `starred_by`
* respons AJAX
* redirect `?next=` yang aman
* group Editor dari migrasi
* badge peran

## 10. (Opsional) Uji end-to-end

Install Selenium:

```bash
pip install selenium
```

Jalankan:

```bash
python test_e2e.py
```

atau:

```bash
python test_e2e.py --headless
```

Server harus sedang berjalan dan Chrome terpasang.

Skrip memeriksa:

* CSRF token
* login
* cookie `last_login`
* cookie `sessionid`
* 403 untuk pengguna biasa
* akses superuser
* penghapusan cookie saat logout

---

# Verifikasi Fitur Tugas 4

Checklist manual dengan server lokal berjalan.

## Pengunjung (belum login)

* [ ] `/`, `/experience/`, `/education/`, `/api/education/`, `/api/experience/` dapat dibuka
* [ ] Tidak ada tombol Tambah, Ubah, atau Hapus
* [ ] Tombol star berbunyi **"Login untuk Star"** dan mengarah ke `/login/?next=/education/`
* [ ] Membuka `/education/add/` atau `/education/<uuid>/edit/` langsung diarahkan ke `/login/?next=...`
* [ ] Setelah login, pengguna kembali ke halaman tujuan

## Pengguna biasa

* [ ] Navbar menampilkan username dan badge **User**
* [ ] Star dapat diberikan lalu dibatalkan; jumlah star bertambah dan berkurang tanpa reload
* [ ] Tidak ada tombol Tambah, Ubah, atau Hapus
* [ ] `/education/add/` dan `/education/<uuid>/edit/` menghasilkan **403 Forbidden**

## Editor

* [ ] Badge **Editor**
* [ ] Tombol **Ubah** tampil
* [ ] Tombol Tambah dan Hapus tidak tampil
* [ ] Form ubah dapat disimpan **tanpa** kode rahasia
* [ ] `/education/add/` menghasilkan **403**
* [ ] POST ke URL delete menghasilkan **403**

## Pemilik

* [ ] Badge **Owner**
* [ ] Tombol Tambah, Ubah, dan Hapus tampil
* [ ] Create, update, dan delete berhasil dengan kode rahasia yang benar
* [ ] Create, update, dan delete gagal bila kode rahasia salah
* [ ] Owner tetap dapat memberi star

## JSON dan Keamanan

* [ ] Beri star dengan satu akun, lalu buka `/api/education/`: tidak ada field `starred_by` maupun username
* [ ] Filter `?nama_sekolah=` dan detail per UUID tetap bekerja
* [ ] UUID yang tidak ada menghasilkan JSON 404
* [ ] Logout menghapus cookie `last_login`

---

# Catatan Desain dan Keamanan

## 1. Pemeriksaan di server, tampilan di template

Menyembunyikan tombol hanya kenyamanan UI.

Sumber kebenarannya adalah decorator di `permissions.py`, sehingga URL yang diketik langsung tetap ditolak.

## 2. Dua kode status berbeda dengan sengaja

Pengunjung diarahkan ke login (**302**) karena masalahnya belum terautentikasi.

Pengguna yang sudah login tetapi tidak berhak menerima **403** karena login ulang tidak akan membantu.

## 3. Group untuk Editor

Menggunakan `Group` memudahkan pemilik menambah atau mencabut Editor lewat Admin tanpa mengubah kode.

Migrasi data memastikan group selalu ada.

## 4. Kode rahasia tetap ada untuk Pemilik

Kode rahasia dari Tugas 3 dipertahankan sebagai lapisan tambahan untuk aksi tulis Pemilik.

Editor cukup diverifikasi lewat group.

## 5. Whitelist field JSON

Field yang boleh keluar dari API disebut eksplisit, sehingga penambahan field baru pada model tidak otomatis ikut terekspos.

## 6. Star toggle dengan progressive enhancement

Form POST biasa selalu berfungsi.

JavaScript hanya menambah pembaruan tanpa reload.

## 7. Batasan yang diketahui

Logout memakai `GET` seperti pada tutorial.

`DEBUG = True` dan `SECRET_KEY` bawaan di `settings.py` hanya cocok untuk pengembangan dan perlu diganti untuk produksi.

---

### Fitur Tambahan Tugas 4

#### 1. Toggle Star Tanpa Reload (AJAX + Fallback)

Tombol star di halaman Education memperbarui jumlah dan status star tanpa memuat ulang halaman.

Cara kerja:
1. Tombol star adalah form `POST` biasa dengan `{% csrf_token %}`, sehingga tetap berfungsi tanpa JavaScript.
2. `static/js/star-toggle.js` mencegat event `submit` lalu mengirim `fetch()` ke `toggle_star` dengan header `X-Requested-With: XMLHttpRequest`.
3. View `toggle_star` mendeteksi header tersebut dan membalas JSON `{"starred": bool, "star_count": int}`. Tanpa header itu, view melakukan redirect seperti biasa.
4. JavaScript memperbarui kelas `is-starred`, label Star/Unstar, `aria-pressed`, dan jumlah star.
5. Jika `fetch` gagal (jaringan putus atau sesi habis), form dikirim secara normal sehingga server tetap menjadi sumber kebenaran.
6. Event delegation di `document` membuat tombol tetap berfungsi pada kartu yang dirender ulang oleh Live Search.

#### 2. Badge Peran di Navbar

Navbar menampilkan badge **Owner**, **Editor**, atau **User** di samping username.

Cara kerja:
1. `main/context_processors.py` menghitung peran dari `main/permissions.py`: superuser menjadi Owner, anggota grup `Editor` menjadi Editor, dan pengguna login lainnya menjadi User.
2. Label dikirim ke semua template sebagai `user_role`, bersama boolean `is_editor`.
3. `base.html` menampilkan badge dan memakai kelas CSS `role-badge--<peran>` untuk warna berbeda.

#### 3. Editor Tanpa Kode Rahasia dan Login Kembali ke Halaman Tujuan

- Editor mengubah data tanpa kode rahasia milik pemilik. `OptionalSecretMixin` menghapus field `secret` dari form saat view memanggil `require_secret=False`. Pemilik tetap wajib mengisinya.
- Setelah login, pengguna dikembalikan ke halaman asal lewat `?next=`. Nilai `next` divalidasi dengan `url_has_allowed_host_and_scheme` agar tidak terjadi open redirect.

# AI Disclosure

Bagian ini menjelaskan penggunaan AI dalam pengerjaan **kode, test, dan fitur** proyek.

Saya dibantu AI pada seluruh bagian pengerjaan Tugas 4, sehingga rinciannya saya tuliskan per komponen.

Isi `README.md` ini tidak termasuk dalam cakupan disclosure.

## Tools

### Claude (Anthropic)

Pemakaian:

* Diskusi rancangan
* Penjelasan konsep Django
* Penyusunan kode dan test
* Review kode

### ChatGPT (OpenAI)

Pemakaian:

* Debugging error
* Pemeriksaan implementasi
* Pembandingan kode sebelum dan sesudah

---

# Strategi Prompting

## 1. Context-first

Setiap prompt memuat konteks:

* teks tugas dan checklist
* potongan kode terkait
* struktur file
* traceback

## 2. Constraint-aware

Checklist tugas dijadikan batasan eksplisit, misalnya:

> "403 untuk aksi tidak berhak, redirect login untuk pengunjung"

dan AI diminta tidak menambah teknologi di luar materi.

## 3. Perubahan minimal

Untuk bug, AI diminta menunjuk file dan baris penyebab lalu mengusulkan perubahan sekecil mungkin.

## 4. Verifikasi

AI diminta membuat test dan skenario manual untuk tiap hak akses agar hasilnya bisa saya periksa sendiri.

## 5. Iterasi dan penyesuaian

Keluaran AI dibandingkan dengan kode proyek:

* nama route
* namespace `main:`
* CSS yang ada

Kemudian diperbaiki, lalu di-commit bertahap.

---

# Bagian yang Dibantu AI

## `main/permissions.py`

Komponen:

```text
role_required
owner_required
editor_or_owner_required
```

**Bantuan AI:** Usulan struktur decorator: `login_required` dibungkus pemeriksaan peran dengan `PermissionDenied`.

**Yang saya lakukan:** Memetakan empat peran ke decorator tiap view, memastikan pengunjung mendapat 302 dan pengguna tidak berhak mendapat 403.

## Group Editor dan migrasi `0007`

**Bantuan AI:** Penjelasan `Group` vs `Permission` dan ide data migration agar group tersedia di database baru.

**Yang saya lakukan:** Menjalankan migrasi di database bersih, menguji penetapan Editor lewat Django Admin.

## `context_processors.roles` dan badge peran

**Bantuan AI:** Ide mengirim `is_editor` dan `user_role` ke semua template.

**Yang saya lakukan:** Menyesuaikan kondisi template dan gaya badge dengan CSS proyek.

## `Education.starred_by`, migrasi `0005`-`0006`

**Bantuan AI:** Contoh `ManyToManyField` ke `User` dan penjelasan `related_name`.

**Yang saya lakukan:** Mengganti `related_name` menjadi `starred_education`, membuat dan menjalankan migrasi.

## View `toggle_star` dan `education_star.html`

**Bantuan AI:** Kerangka view toggle (POST, `login_required`, `add`/`remove`) dan komponen tombol.

**Yang saya lakukan:** Menambahkan perhitungan jumlah star dengan `Count`, status per user, dan tautan login untuk pengunjung.

## `static/js/star-toggle.js`

**Bantuan AI:** Pola `fetch()` dengan event delegation dan fallback ke submit form.

**Yang saya lakukan:** Menguji bersama live search dan memastikan tombol tetap bekerja tanpa JavaScript.

## Whitelist field JSON

**Bantuan AI:** Peringatan bahwa serializer akan menyertakan `starred_by`.

**Yang saya lakukan:** Menerapkan `fields=` pada semua endpoint dan menambah test yang memeriksa username tidak muncul.

## Redirect `?next=` pada login

**Bantuan AI:** Saran validasi `url_has_allowed_host_and_scheme`.

**Yang saya lakukan:** Menguji `next` internal, eksternal, dan tanpa `next`.

## Editor tanpa kode rahasia (`OptionalSecretMixin`)

**Bantuan AI:** Ide membuat field `secret` opsional per pemakaian form.

**Yang saya lakukan:** Menyesuaikan pemanggilan form di view dan menguji bahwa Pemilik tetap wajib kode.

## Test (`main/tests.py`, 122 metode) dan `test_e2e.py`

**Bantuan AI:** Draf test untuk peran, star, JSON, migrasi, serta skrip Selenium.

**Yang saya lakukan:** Menyesuaikan test dengan hak akses baru, menghapus false positive, menjalankan seluruh suite.

Keputusan akhir, penyesuaian ke struktur proyek, dan penjalanan kode dilakukan oleh saya.

Riwayat commit (branch `polish/tugas-04`) memperlihatkan proses perbaikan tersebut, misalnya:

* mengganti `related_name`
* mengembalikan `permissions.py` yang sempat terhapus
* menghapus kode duplikat di `settings.py`
* menyesuaikan test yang memberi hasil positif palsu

---

# Contoh Log Prompting

## Otorisasi

**Kebutuhan:** Pembatasan per peran

**Ringkasan prompt:** Menyertakan tabel empat peran dan `views.py`, meminta pembatasan server-side dengan redirect login dan 403.

**Hasil yang dipakai:** Decorator peran di `permissions.py`.

## Peran Editor

**Kebutuhan:** Group

**Ringkasan prompt:** Menanyakan perbedaan `Group` dan `Permission` serta cara memastikan group ada di database baru.

**Hasil yang dipakai:** Group `Editor` lewat data migration.

## Star

**Kebutuhan:** Relasi M2M

**Ringkasan prompt:** Meminta contoh `ManyToManyField` ke `User` dan view toggle satu star per user.

**Hasil yang dipakai:** Field `starred_by` dan view `toggle_star`.

## Keamanan API

**Kebutuhan:** Kebocoran data

**Ringkasan prompt:** Menanyakan apakah serializer menampilkan relasi M2M dan cara membatasinya.

**Hasil yang dipakai:** Whitelist `fields` dan test kebocoran.

## Star tanpa reload

**Kebutuhan:** Interaktivitas

**Ringkasan prompt:** Meminta `fetch()` yang tetap bekerja tanpa JavaScript dan setelah live search.

**Hasil yang dipakai:** `star-toggle.js` dan respons JSON pada `toggle_star`.

## Login

**Kebutuhan:** Redirect aman

**Ringkasan prompt:** Meminta pengembalian ke halaman tujuan tanpa membuka open redirect.

**Hasil yang dipakai:** `_safe_next_url` dan test `next`.

## Pengujian

**Kebutuhan:** Cakupan test

**Ringkasan prompt:** Menyertakan checklist tugas, meminta test per peran dan edge case.

**Hasil yang dipakai:** `AuthorizationAndStarTest` dan kelas test terkait.

---

# Keterbatasan AI dan Perbaikan Manual

### Struktur Proyek

Saran AI tidak selalu cocok dengan struktur proyek.

Contohnya `related_name` awal yang mengikuti istilah tutorial:

```text
starred_projects
```

tidak sesuai karena relasinya berada di model `Education`, sehingga saya ganti melalui migrasi `0006`.

### Serializer

Serializer bawaan akan menyertakan relasi M2M.

Tanpa pemeriksaan, `starred_by` akan tampil di API publik, jadi saya menambahkan whitelist field dan test khusus.

### Test

Test yang dibuat sebelum ada login gagal setelah hak akses diterapkan dan sebagian memberi hasil positif palsu.

Misalnya mencocokkan angka `pk` yang kebetulan muncul di dalam UUID.

Saya menyesuaikan test dengan peran baru dan memeriksa username, bukan `pk`.

### Konsistensi Project

Kode dari AI tidak menjamin konsistensi:

* nama route
* namespace `main:`
* CSS

Saya memeriksa hal tersebut dan menjalankan:

```bash
python manage.py test
```

serta pengujian manual per peran sebelum commit.

## Tugas 5 — AJAX: fetch, Debouncing, Modal, Toast, dan Perlindungan XSS

### Tujuan

Menerapkan seluruh pola AJAX dari Tutorial 05 secara end-to-end pada bagian **Education**
(bukan Projects), dengan hak akses dari Tugas 4 tetap berlaku: pengunjung dapat membaca
data, sedangkan penambahan data hanya dapat dilakukan oleh pemilik (superuser).

### Pemetaan ke Checklist Tugas

| Checklist | Implementasi | Lokasi |
|---|---|---|
| Daftar hanya merender kerangka | `show_education` tidak mengirim queryset; template hanya berisi state container + konfigurasi JSON | `show_education`, `education.html` |
| Data diambil lewat `fetch()` | Klien memanggil `GET /api/education/` lalu merender kartu | `static/js/education.js` |
| Respons JSON disusun manual | `JsonResponse` berisi field model + `star_count` dan `is_starred` pengguna login | `get_education_json` |
| Loading / empty / error | `#loading`, `#empty` (pesan spesifik saat sedang mencari), `#error` + tombol "Coba Lagi" | `education.html`, `education.js` |
| Pencarian AJAX + debouncing | Event `input` → debounce 300 ms → request dengan filter `nama_sekolah__icontains`; request lama dibatalkan `AbortController` | `education.js`, `get_education_json` |
| Form tambah di dalam modal | Modal Popover API; submit dicegat lalu dikirim `fetch POST` | `education_form_modal.html`, `education.js` |
| View POST dengan `ModelForm` + status HTTP | `create_education_ajax`: **201** berhasil, **400** validasi gagal (`errors` per field), **403** tanpa hak | `main/views.py` |
| Hak akses diperiksa di view | `is_owner(request.user)` dari `main.permissions` — bukan hanya menyembunyikan tombol | `create_education_ajax` |
| Token CSRF pada POST | Header `X-CSRFToken` (dari cookie) untuk request modal; `csrfmiddlewaretoken` pada form star/hapus yang dirender klien | `education.js`, `base.html` |
| Daftar ter-update tanpa reload | Setelah 201, `fetchEducations()` dipanggil ulang dengan kata kunci aktif | `addEducation` |
| Toast sukses / gagal | `showToast` untuk sukses, pesan validasi berlabel field, dan kegagalan jaringan | `addEducation`, `static/js/toast.js` |
| Escaping sisi klien | `escapeHtml()` dipakai pada **setiap** nilai teks sebelum masuk `innerHTML`; toast menulis via `textContent` | `static/js/utils.js`, `education.js` |
| Pembersihan sisi server | `strip_tags` pada `clean_<field>` `EducationForm`; input yang hanya berisi tag ditolak | `main/forms.py` |
| Berjalan untuk semua peran | `python manage.py runserver` + 136 test hijau; diuji manual untuk pengunjung, pengguna, editor, pemilik | `main/tests.py` |

### Alur Kerja AJAX

```text
Menampilkan daftar:
  Browser (kerangka education.html)
    → fetch() GET /api/education/ (JSON manual + info star)
    → education.js: buildEducationCard() (setiap teks di-escape)
    → grid terisi tanpa reload

Menambah data:
  Modal (popover) → submit dicegat
    → fetch POST /education/add-ajax/ (X-CSRFToken + FormData)
    → server: cek is_owner → EducationForm (strip_tags + validasi)
    → 201: reset form, tutup modal, toast sukses, muat ulang daftar
    → 400: toast berisi pesan validasi per field
    → 403: toast "hanya pemilik portofolio"
```

### Fitur Tambahan — Shortcut Keyboard

- **`/`** memfokuskan kolom pencarian dari mana pun (diabaikan saat mengetik di field lain, saat modal terbuka, atau saat tombol modifier ditekan).
- **`Esc`** membersihkan filter bila fokus berada di kolom pencarian.
- Modal tambah/hapus tidak ditangani manual karena Popover API (`popover="auto"`) sudah menutup diri lewat *light dismiss* bawaan browser.

### Perubahan File Utama

| File | Perubahan |
|---|---|
| `static/js/utils.js` (baru) | `escapeHtml()` dan `getCookie()` bersama untuk semua halaman |
| `static/js/education.js` (baru) | Seluruh logika klien halaman Education (fetch, debounce, render, modal, toast, shortcut) |
| `templates/education.html` | Kerangka halaman + elemen state + konfigurasi JSON (`education-config`) |
| `templates/base.html` | Memuat `utils.js`, block `scripts`, menghapus footer duplikat |
| `main/views.py` | `show_education` jadi kerangka; `get_education_json` menyusun `JsonResponse` manual (agregasi `Count`, tanpa identitas pemberi star); `create_education_ajax` memeriksa `is_owner` |
| `main/forms.py` | Perbaikan `clean_jurusan`: jurusan kosong disimpan `NULL`, bukan teks `"None"` |
| `main/migrations/0008_fix_none_jurusan.py` (baru) | Data migration: membetulkan baris lama yang jurusannya `"None"` |
| `main/tests.py` | Test AJAX skeleton, status 201/400/403, sanitasi XSS, kebocoran username, kontrak skrip, shortcut |

### Setup Tambahan

Cuma perlu:

```bash
python manage.py migrate   # menerapkan 0008_fix_none_jurusan (perbaikan data lama)
```

### Verifikasi Fitur Tugas 5

**Semua peran**

* [ ] `/education/` memuat data tanpa reload; loading → grid
* [ ] Pencarian terkirim hanya setelah berhenti mengetik (~300 ms)
* [ ] Kata kunci tanpa hasil menampilkan pesan pencarian spesifik

**Pengunjung** — tidak ada tombol tambah; star berupa tautan "Login untuk Star"

**Pengguna/Editor** — bisa star tanpa reload; POST ke `/education/add-ajax/` → **403**

**Pemilik** — modal tambah muncul; 201 → toast sukses + daftar ter-update; input tidak valid → 400 → toast berlabel field; kode rahasia salah → toast error

**XSS** — menambah data `<img src="x" onerror="alert('XSS!')">` ditolak server; versi campuran teks disimpan bersih dan tampil sebagai teks biasa, tanpa alert

**Keamanan** — `/api/education/` tidak memuat username maupun field `starred_by_names`

### Pertanyaan Reflektif

#### 1. Apa itu debouncing dan mengapa penting pada pencarian AJAX?

**Debouncing** adalah teknik menunda eksekusi sebuah fungsi sampai pengguna *berhenti* melakukan aksi tertentu (misalnya berhenti mengetik) selama jeda waktu yang ditentukan. Setiap event baru yang masuk mereset timer; fungsi hanya dijalankan bila tidak ada event lagi selama jeda tersebut.

Di `static/js/education.js`, setiap event `input` pada kolom pencarian memanggil `clearTimeout(searchDebounceTimer)` lalu menjadwalkan ulang `setTimeout(..., SEARCH_DEBOUNCE_DELAY)` dengan delay **300 ms**. Request pencarian hanya terkirim ketika pengguna berhenti mengetik selama 300 ms.

Teknik ini penting pada pencarian AJAX karena:

- **Menghemat request.** Tanpa debouncing, mengetik "universitas" (11 karakter) mengirim 11 request, dan 10 di antaranya sia-sia karena kata kuncinya sudah usang sebelum responsnya dipakai.
- **Mengurangi beban server dan jaringan** tanpa mengorbankan kesan real-time — jeda 300 ms tidak dirasakan manusia, tetapi sudah menggabungkan seluruh ketikan menjadi satu request.
- **Mengurangi race condition.** Respons untuk kata kunci lama bisa tiba belakangan dan menimpa hasil yang lebih baru. Karena itu debouncing dikombinasikan dengan `AbortController`: request sebelumnya *dibatalkan* ketika kata kunci berubah, sehingga hasil yang tampil dijamin milik kata kunci terakhir.

#### 2. Apa fungsi `await` pada `fetch()` dan apa yang terjadi tanpa `await`?

`fetch()` adalah operasi **asynchronous**: ia langsung mengembalikan sebuah `Promise` yang akan selesai (resolve) ketika respons HTTP tiba, sementara baris kode berikutnya secara default sudah dieksekusi lebih dulu. `await` menunda eksekusi fungsi `async` yang memuatnya sampai Promise tersebut selesai, lalu "membuka" nilainya sehingga bisa dipakai seperti operasi biasa:

```javascript
const response = await fetch(url);        // menunggu respons HTTP tiba
if (!response.ok) throw new Error(...);   // aman: response sudah objek Response
const data = await response.json();       // menunggu body selesai di-parse
```

Jika `await` dihilangkan (dan tidak ada penanganan lain), variabel `response` **bukan** objek `Response`, melainkan `Promise` yang belum selesai. Akibatnya:

- `response.ok` bernilai `undefined`, sehingga guard `if (!response.ok) throw ...` selalu terpicu — halaman selalu berpindah ke *error state* meskipun server sukses membalas.
- `response.json()` melempar `TypeError: response.json is not a function`, karena objek `Promise` tidak punya method `json()`.
- Alur program menjadi tidak deterministik: kode yang seharusnya menunggu data justru berjalan lebih dulu dengan data yang belum tersedia, sehingga daftar bisa dirender kosong atau *loading state* tidak pernah selesai.

"Tanpa `await`" tidak otomatis berarti salah: alternatif yang valid adalah merantai `fetch(url).then(...)` — secara semantik sama-sama menangani Promise, hanya gaya penulisannya berbeda. Yang berbahaya adalah **membaca hasil fetch sebelum Promise-nya selesai**. Kelebihan `await` adalah kodenya terbaca seperti sinkron dan langsung bisa dibungkus `try/catch`, yang dipakai untuk menampilkan *error state* ketika jaringan gagal.

#### 3. Apa itu serangan XSS dan mengapa data lewat AJAX/JavaScript lebih rentan?

**Cross-Site Scripting (XSS)** adalah serangan ketika penyerang menyisipkan kode HTML/JavaScript berbahaya ke dalam halaman yang dilihat orang lain, umumnya lewat data yang dikirim pengguna. Contoh pada aplikasi ini: nama sekolah berisi payload `<img src="x" onerror="alert('XSS!')">`. Bila payload dirender kembali tanpa dibersihkan, browser mengeksekusinya sebagai bagian halaman — bisa mencuri cookie (termasuk `sessionid`), melakukan aksi atas nama korban, atau mengubah tampilan halaman. Berdasarkan jalurnya, XSS dibagi menjadi *stored* (payload tersimpan di database), *reflected* (ikut dalam request), dan *DOM-based* (terjadi saat JavaScript memanipulasi DOM).

Data yang ditampilkan lewat AJAX/JavaScript lebih rentan karena:

- **Template Django punya proteksi bawaan, JavaScript tidak.** Django Template Language otomatis meng-escape setiap variabel — `{{ education.nama_sekolah }}` mengubah `<` menjadi `&lt;` dst., sehingga payload hanya tampil sebagai teks. Saat merender lewat JavaScript, tidak ada mekanisme otomatis seperti itu.
- **Jalur klasik DOM-based XSS: `innerHTML` + template literal.** Kesalahan umum adalah menulis `card.innerHTML = \`<h2>${education.nama_sekolah}</h2>\``. Browser mem-parsing string tersebut *sebagai HTML*, sehingga tag berbahaya ikut dibuat dan dieksekusi. Di halaman AJAX, hampir semua data melewati jalur ini.
- **Data JSON sering dianggap "terpercaya".** Padahal isi JSON tetap merupakan input pengguna yang tersimpan di database (stored XSS) — berasal dari server bukan berarti aman disisipkan mentah-mentah ke DOM.

Karena itu proteksi diterapkan berlapis (*defence in depth*):

1. **Sisi server** — `strip_tags` pada `clean_<field>` di `EducationForm`: tag HTML dibuang sebelum data masuk database, dan input yang hanya berisi tag ditolak. Diuji oleh `test_xss_payload_is_sanitized_server_side`.
2. **Sisi klien** — fungsi `escapeHtml()` di `static/js/utils.js` meng-escape `& < > " '` dan dipakai pada **setiap** nilai teks sebelum digabungkan ke template literal di `buildEducationCard`; payload tampil sebagai teks biasa dan `alert` tidak pernah muncul. Toast juga aman karena `showToast` menulis pesan lewat `textContent`, bukan `innerHTML`.

## AI Disclosure Tugas 5

### Tools yang Digunakan

- **ZCode (GLM)** — debugging error dan anomali perilaku, penulisan draf test regresi, dan penyusunan dokumentasi README bagian ini.

### Strategi Prompting

1. **Context-first** — prompt selalu menyertakan traceback/pesan test yang gagal, potongan kode terkait, dan konteks implementasi, bukan cuma deskripsi gejala.
2. **Constraint-aware** — AI diminta menahan diri pada materi Tutorial 05 dan struktur proyek yang sudah ada (namespace `main:`, komponen template, CSS) tanpa menambah teknologi baru.
3. **Verification-driven** — setiap diagnosis diikuti permintaan test regresi dan skenario uji manual per peran agar klaim bisa saya periksa sendiri sebelum dipakai.
4. **Iterasi** — saran pertama tidak selalu dipakai mentah; hasilnya dibandingkan dengan perilaku aktual di browser dan hasil `python manage.py test`, lalu dikoreksi.

### Bagian yang Dibantu AI

| Bagian | Bantuan AI | Yang saya lakukan |
|---|---|---|
| Debugging jurusan kosong tersimpan `"None"` | Menjelaskan akar masalah `strip_tags(None)` pada field `null=True` dan pola perbaikannya | Membuat test regresi merah→hijau, menjalankan migration, memverifikasi di Admin |
| Debugging queryset `annotate()` mengabaikan `Meta.ordering` | Mendiagnosis kenapa urutan JSON berubah setelah refactoring agregasi (query GROUP BY membuang default ordering) | Membaca ulang SQL hasil query, menambah `order_by` eksplisit, memastikan 136 test hijau |
| Review keamanan respons star | Menjelaskan vektor kebocoran username pemberi star pada respons JSON publik dan alternatif agregasi `Count` | Menulis skenario uji anonim dengan star yang sudah ada, menghapus field dari konsumsi UI |
| Penulisan test regresi | Draf test AJAX skeleton, status 201/400/403, sanitasi XSS, kebocoran username, dan kontrak skrip klien | Menyesuaikan nama/pola test dengan konvensi `tests.py`, membuang false positive, menjalankan seluruh suite |
| Debugging shortcut `/` mati saat toast tampil | Menjelaskan selector `:popover-open` ikut mencocokkan toast `popover="manual"` | Mempersempit selector, menguji interaksi modal/toast di browser |
| Dokumentasi README Tugas 5 | Kerangka dokumentasi, jawaban pertanyaan reflektif, dan log prompting | Meninjau, menyesuaikan dengan implementasi aktual, dan memastikan setiap klaim sesuai kode |

### Contoh Log Prompting

| Tahap | Kebutuhan | Ringkasan Prompt | Hasil yang Dipakai |
|---|---|---|---|
| Debugging | Jurusan `"None"` | Menyertakan `clean_jurusan` + definisi model, meminta penjelasan kenapa kosong jadi teks `"None"` | Diagnosa `strip_tags(None)` + pola guard + data migration |
| Debugging | Urutan JSON kacau | Menyertakan test yang gagal (`data[0]` salah) dan SQL queryset, meminta diagnosis | Temuan `Meta.ordering` diabaikan pada query agregasi |
| Keamanan | Kebocoran username | Menyertakan `get_education_json`, meminta analisis data apa saja yang ter ekspos ke anonim | Daftar field berisiko + alternatif perhitungan star tanpa memuat `User` |
| Pengujian | Cakupan regresi | Menyertakan checklist tugas, meminta draf test per checklist dan edge case | Draf test yang kemudian saya sesuaikan dan jalankan |
| Dokumentasi | README mingguan | Meminta struktur bagian Tugas 5 + jawaban reflektif sesuai format README yang sudah ada | Dokumentasi bagian ini |

### Keterbatasan AI dan Perbaikan Manual

- **Diagnosis AI tidak selalu tepat sasaran.** Beberapa saran perbaikan awal tidak memperhitungkan perilaku Django yang halus (mis. query agregasi yang mengabaikan `Meta.ordering`), sehingga tetap harus diverifikasi dengan SQL dan test sebelum diterima.
- **Test hasil draf AI bisa memberi hasil positif palsu.** Test kebocoran username versi awal lolos hanya karena database uji kosong; saya perbaiki dengan menambahkan star *sebelum* memeriksa respons anonim.
- **Semua klaim diverifikasi sendiri** — `python manage.py test` (136 test), `node --check` untuk berkas JS, dan pengujian manual per peran di `runserver` sebelum perubahan dianggap selesai. Keputusan akhir, penyesuaian ke struktur proyek, dan penjalanan kode dilakukan oleh saya.