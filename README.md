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