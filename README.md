Nama : Adriel

NPM: 2506587150

Kelas : PBP B

rubah sedikit

### Tugas 1

## Deskripsi Proyek

Website ini merupakan halaman portofolio pribadi yang dikembangkan dari Tutorial 01.
Website dibuat menggunakan HTML5 dan CSS3 dengan fokus pada penerapan struktur HTML
yang terorganisasi, responsive design, dan styling menggunakan CSS.

Pada pengembangan tugas ini, saya mempertahankan section **About Me** yang berisi
informasi pribadi seperti nama, NPM, program studi, foto, bio, serta informasi kontak
dan media sosial.

Saya kemudian menambahkan section **Skills** yang berisi beberapa kemampuan dan
teknologi yang saya kuasai. Section Skills menggunakan **CSS Grid** untuk mengatur
layout dan dilengkapi dengan efek hover serta animasi agar tampilan website lebih
interaktif.

Sebagai fitur tambahan, saya juga mengimplementasikan **Dark Mode** menggunakan
HTML dan CSS tanpa JavaScript. Website menggunakan CSS Flexbox, CSS Grid,
media queries, dan responsive design agar tampilan dapat menyesuaikan dengan
berbagai ukuran layar, baik desktop maupun mobile.

Website pada tahap ini masih berupa static web dan belum menggunakan database
maupun arsitektur MVT. Penggunaan database dan penerapan MVT mungkin akan dilakukan
pada tahap pengembangan berikutnya.

## Informasi Mahasiswa

- **Nama:** Adriel Raynard Davis Sihotang
- **NPM:** 2506587150
- **Kelas:** PBP B

## Fitur

- About Me section
- Informasi profil pribadi
- Skills section
- Responsive layout
- CSS Grid dan Flexbox
- Hover effects
- CSS animation
- Dark Mode
- Responsive design untuk desktop dan mobile
- Social media links

## Teknologi yang Digunakan

- HTML5
- CSS3
- Django
- CSS Flexbox
- CSS Grid
- CSS Media Queries
- CSS Animation
- Responsive Web Design

## Struktur Project

Struktur utama project adalah sebagai berikut:

```text
myportofolio/
├── manage.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   └── css/
│       └── style.css
└── ...
````

File utama yang digunakan untuk tampilan website:

* `templates/index.html` digunakan untuk struktur dan konten halaman.
* `static/css/style.css` digunakan untuk seluruh styling, responsive layout,
  animation, dan Dark Mode.

## Setup dan Menjalankan Project Secara Lokal

### 1. Clone atau Download Project

Clone repository atau download project, kemudian masuk ke direktori project:

```bash
cd myportofolio
```

### 2. Membuat Virtual Environment

Buat virtual environment dengan perintah:

```bash
python -m venv env
```

Aktifkan virtual environment.

**Windows:**

```bash
env\Scripts\activate
```

### 3. Install Dependencies

Install dependencies yang diperlukan menggunakan:

```bash
pip install -r requirements.txt
```

### 4. Menjalankan Development Server

Jalankan Django development server dengan:

```bash
python manage.py runserver
```

Jika berhasil, terminal akan menampilkan alamat development server:

```text
Starting development server at http://127.0.0.1:8000/
```

Buka alamat tersebut pada browser untuk melihat website portofolio.

## Deployment

Project ini juga telah di-deploy menggunakan **Pacil Web Service (PWS)** yang
disediakan oleh fakultas.

Pacil Web Service digunakan untuk menjalankan project secara online dan menghasilkan
link yang dapat digunakan untuk mengakses website portofolio.

### Deployment Status

**Status:** Running

### Deployment URL

Masukkan link website hasil deployment PWS di bawah ini:

**Website:** [MASUKKAN LINK WEBSITE PWS DI SINI]

## Pertanyaan Reflektif

### 1. Penggunaan Elemen Semantik HTML5

Ya, saya menggunakan elemen semantik HTML5 seperti `<section>` dan `<aside>` dalam
merancang struktur halaman portofolio. Pada halaman About Me, saya menggunakan
`<section>` untuk mengelompokkan konten yang memiliki tema tertentu. Pada
pengembangan tugas ini, saya juga menggunakan `<aside>` untuk bagian Skills yang
berfungsi sebagai informasi tambahan yang masih berkaitan dengan konten utama.

Penggunaan elemen semantik membantu saya membuat struktur HTML yang lebih jelas dan
terorganisasi. Selain membuat kode lebih mudah dipahami, struktur tersebut juga
memudahkan saya dalam mengatur layout menggunakan CSS Grid dan menentukan hubungan
antara bagian About Me dan Skills.

### 2. Tantangan Responsive Layout

Tantangan utama yang saya temukan ketika membuat website responsive adalah
mempertahankan layout agar tetap rapi ketika ukuran layar berubah. Pada desktop,
bagian About Me dan Skills dapat ditampilkan berdampingan menggunakan CSS Grid.
Namun, jika ukuran layar terlalu kecil, kedua bagian tersebut menjadi terlalu sempit.

Untuk mengatasinya, saya menggunakan media queries. Pada ukuran layar yang lebih
kecil, layout diubah dari dua kolom menjadi satu kolom sehingga konten dapat
ditampilkan secara vertikal dan tetap mudah dibaca.

Saya menentukan elemen yang perlu diprioritaskan berdasarkan hierarki informasi.
Informasi utama seperti nama, foto, dan bio tetap diprioritaskan, sedangkan Skills
dapat ditempatkan setelah informasi utama pada tampilan mobile. Saya juga
menyesuaikan ukuran foto dan spacing agar tidak mengambil terlalu banyak ruang.

### 3. Batasan Static Web dan Pengembangan Selanjutnya

Karena website saat ini masih berupa static web, informasi seperti Skills, bio,
dan informasi portofolio masih ditulis secara langsung di dalam HTML. Hal ini
menjadi kurang praktis jika jumlah informasi semakin banyak karena setiap perubahan
harus dilakukan secara manual pada kode.

Pada iterasi berikutnya, saya ingin menambahkan fungsionalitas dinamis menggunakan
database. Data seperti Projects, Skills, Experience, dan Education dapat disimpan
di database sehingga informasi dapat ditambahkan atau diubah tanpa harus mengubah
HTML secara manual.

Saya juga ingin menerapkan arsitektur Django MVT. Model dapat digunakan untuk
mengelola data portofolio, View untuk mengambil dan mengatur data, sedangkan
Template digunakan untuk menampilkan data tersebut secara dinamis.

## AI Disclosure

Dalam pengerjaan tugas ini, saya menggunakan Claude AI sebagai alat bantu untuk berdiskusi
dan memperoleh masukan mengenai pengembangan website, khususnya terkait struktur
HTML5, responsive CSS, layout menggunakan Flexbox dan Grid, serta implementasi
Dark Mode.

AI digunakan sebagai bantuan dalam memahami konsep, memberikan saran perbaikan
kode, dan membantu proses debugging. Implementasi akhir tetap saya sesuaikan
dengan kebutuhan project dan saya terapkan pada kode project saya sendiri.


### Tugas 2

## Deskripsi Proyek

Proyek ini merupakan aplikasi web portofolio pribadi yang dibangun menggunakan framework Django dengan menerapkan arsitektur Model-View-Template (MVT). Aplikasi ini dirancang secara khusus untuk menampilkan daftar riwayat pendidikan (education) secara dinamis yang diambil langsung dari database.

Melalui aplikasi ini, pengguna dapat melihat berbagai informasi riwayat pendidikan, seperti nama instansi/lembaga pendidikan, tingkat pendidikan, periode tahun studi, jurusan/program studi, serta deskripsi atau pencapaian terkait yang dikelola secara terpusat melalui backend Django.

## Instruksi Setup 

Ikuti langkah-langkah berikut untuk menjalankan proyek ini di lingkungan lokal Anda:

1. Prasyarat
Pastikan Anda telah menginstal Python 3.x dan Git di komputer Anda.

2. Kloning Repositori & Masuk ke Direktori
Bash
git clone <URL_REPOSITORI_ANDA>
cd <NAMA_FOLDER_PROYEK>

3. Membuat dan Mengaktifkan Virtual Environment
Windows:
Bash
python -m venv venv
venv\Scripts\activate

macOS / Linux:
Bash
python3 -m venv venv
source venv/bin/activate

4. Menginstal Dependencies
Bash
pip install -r requirements.txt
(Catatan: Jika berkas requirements.txt belum ada, Anda dapat menginstal Django secara langsung menggunakan perintah pip install django)

5. Melakukan Migrasi Database
Bash
python manage.py makemigrations
python manage.py migrate

6. Menjalankan Server Lokal
Bash
python manage.py runserver

7. Mengakses Aplikasi
Buka browser Anda dan akses alamat berikut:
http://localhost:8000/

## Pertanyaan Reflektif

### 1. Jelaskan alur yang terjadi ketika pengguna membuka halaman portofolio baru, mulai dari permintaan yang diterima proyek hingga data ditampilkan pada browser. Dalam jawabanmu, jelaskan peran urls.py proyek, urls.py aplikasi, view, model, dan template.

Browser mengirimkan HTTP Request: Pengguna mengakses URL riwayat pendidikan (misalnya /education/), kemudian browser mengirimkan permintaan tersebut ke server Django.

Pengecekan di urls.py Proyek (Root): Server mengarahkan permintaan ke berkas konfigurasi URL utama. Berkas ini menggunakan fungsi include() untuk meneruskan rute ke aplikasi yang spesifik.

Pencocokan di urls.py Aplikasi: Django mencari pola URL yang cocok (misal 'education/') dan menemukan fungsi atau kelas View yang ditugaskan untuk menangani rute tersebut.

Pemrosesan oleh View (views.py): View bertindak sebagai pusat kendali. View menerima request tersebut dan menjalankan logika bisnis, termasuk meminta data riwayat pendidikan ke Model.

Pengambilan Data oleh Model (models.py): Jika interface membutuhkan data dinamis, View akan memanggil Model. Model kemudian mengambil data riwayat pendidikan dari database menggunakan Django ORM dan mengembalikannya ke View dalam bentuk QuerySet.

Rendering Template (.html): View menyusun data dari Model ke dalam objek context, lalu menggabungkannya dengan berkas Template. Template memproses tag DTL (Django Template Language) untuk menyisipkan data dinamis ke dalam kerangka HTML.

Pengembalian HTTP Response: View mengemas kode HTML yang sudah final menjadi HTTP Response dan mengirimkannya kembali ke browser pengguna untuk dirender menjadi halaman web visual.

### 2. Mengapa data untuk bagian portofolio baru sebaiknya disimpan pada model dan tidak ditulis langsung di dalam template? Jelaskan dampaknya terhadap kemudahan pemeliharaan dan pengembangan aplikasi.

Pusat Pengelolaan Data Terpusat: Penambahan, pembaruan, atau penghapusan data portofolio dapat dilakukan dengan mudah melalui interface Django Admin tanpa perlu mengedit berkas HTML satu per satu.

Mencegah Kerusakan Tampilan: Mengedit berkas HTML secara manual berisiko merusak struktur, CSS, atau tata letak (layout). Pemisahan data dan tampilan menjaga integritas kode interface.

Kemudahan Ekspansi (Scalability): Data di Model dapat dengan mudah diurutkan, disaring berdasarkan kategori, atau dipaginasi menggunakan fitur bawaan Django ORM. Hal ini sangat sulit atau mustahil dilakukan secara efisien jika data di-hardcode.

Penggunaan Kembali Data (Reusability): Data yang sama dapat ditampilkan di berbagai bagian situs (misalnya ringkasan di beranda dan rincian di halaman detail) tanpa harus menulis ulang kontennya.

### 3. Apa perbedaan fungsi makemigrations dan migrate pada Django? Berikan contoh perubahan model yang mengharuskanmu menjalankan kedua perintah tersebut.

Perintah: python manage.py makemigrations

Fungsi Utama: Berfungsi memindai perubahan yang saya tulis di dalam berkas models.py dan membuat skema/rencana perubahan (blueprint).

Output: Menghasilkan berkas Python baru di dalam folder migrations/ (misalnya 0002_education.py).

Status Database: Pada tahap ini, struktur tabel di dalam database fisik belum berubah sama sekali.

Perintah: python manage.py migrate

Fungsi Utama: Berfungsi membaca skrip migrasi yang telah dibuat dan menerapkannya langsung ke dalam sistem database.

Output: Mengeksekusi perintah SQL (seperti CREATE TABLE atau ALTER TABLE) ke dalam database (misalnya db.sqlite3).

Status Database: Struktur tabel pada database fisik telah resmi berubah dan siap menyimpan data.

Contoh Siklus Penggunaan:
Saat saya menambahkan kelas Education baru di models.py, saya pertama-tama menjalankan python manage.py makemigrations untuk membuat riwayat rancangannya. Setelah berkas rancangan muncul, saya menjalankan python manage.py migrate agar Django benar-benar membuatkan tabel main_education di dalam database SQL saya.

## Fitur Tambahan

Untuk memenuhi nilai skala 4 pada rubrik penilaian Fungsionalitas % Kesesuaian Topik, saya menambahkan fitur tambahan sebagai berikut:

Saya menambahkan fitur untuk mengunduh ringkasan portofolio (bagian Experience dan Education) secara langsung dalam format PDF dari website, tanpa perlu screenshot atau print manual dari browser.

Fitur ini bekerja sepenuhnya di sisi server (server-side rendering). Ketika pengguna mengklik tautan "Download PDF" pada navbar, request akan diarahkan ke view baru download_portfolio_pdf di main/views.py. View ini mengambil seluruh data Experience dan Education dari database, lalu merender data tersebut ke dalam template HTML khusus (templates/portfolio_pdf.html) yang berbeda dari template halaman biasa dan dirancang khusus agar sesuai dengan kemampuan rendering PDF. Hasil render HTML tersebut kemudian dikonversi menjadi berkas PDF menggunakan library xhtml2pdf, dan dikirim kembali sebagai HttpResponse dengan header Content-Disposition: attachment, sehingga browser langsung mengunduh file portfolio-adriel.pdf alih-alih menampilkannya di layar.

Untuk menambahkan fitur ini, langkah-langkah yang saya lakukan meliputi:

Menambahkan library xhtml2pdf ke requirements.txt dan menginstalnya melalui pip install xhtml2pdf.
Membuat view baru download_portfolio_pdf yang mengambil data dari model Experience dan Education, merendernya ke string HTML menggunakan render_to_string, lalu mengonversinya menjadi PDF melalui pisa.pisaDocument.
Membuat template baru templates/portfolio_pdf.html dengan CSS yang ditulis inline (bukan file eksternal), karena xhtml2pdf tidak dapat memuat berkas CSS dari luar template.
Mendaftarkan route baru portfolio/pdf/ dengan nama main:download_portfolio_pdf pada main/urls.py.
Menambahkan tautan "Download PDF" pada navbar di seluruh halaman (index.html, experience.html, education.html) menggunakan tag {% url %} agar konsisten dan tidak melakukan hardcoded URL.
Menambahkan unit test baru (PortfolioPdfTest) untuk memastikan endpoint dapat diakses dan mengembalikan berkas PDF yang valid, tetap berfungsi ketika data kosong, dan tautan download tersedia di seluruh halaman navbar.

Dengan fitur ini, calon perekrut atau siapa pun yang mengunjungi portofolio dapat langsung mengunduh ringkasan riwayat pendidikan dan pengalaman saya dalam satu berkas PDF, tanpa harus membuka setiap halaman satu per satu.

## AI Disclosure
Dalam pengerjaan tugas ini, saya menggunakan Claude AI sebagai alat bantu untuk berdiskusi dan memperoleh masukan mengenai pengembangan backend berbasis Django. Bantuan ini khususnya terkait pemahaman arsitektur Model-View-Template (MVT), alur request-response HTTP, manajemen migrasi database, dan logika implementasi fitur tambahan pengunduhan PDF.

AI digunakan sebagai bantuan dalam memahami konsep, memberikan saran perbaikan
kode, dan membantu proses debugging. Implementasi akhir tetap saya sesuaikan
dengan kebutuhan project dan saya terapkan pada kode project saya sendiri.
