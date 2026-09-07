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
