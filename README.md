# 🌋 Edukasi Bencana Alam Chatbot

Aplikasi chatbot edukasi bencana alam berbasis **Streamlit** yang membantu pengguna mempelajari berbagai jenis bencana alam, penyebab, tanda-tanda, mitigasi, langkah penyelamatan saat bencana, serta tindakan pasca bencana.

Aplikasi ini dirancang sebagai media pembelajaran interaktif dengan tampilan modern dan chatbot yang dapat menjawab pertanyaan seputar kebencanaan secara cepat.

---

## ✨ Fitur Utama

### 🤖 Chatbot Edukasi Bencana
Pengguna dapat bertanya mengenai berbagai bencana alam, seperti:

- Gempa Bumi
- Banjir
- Tsunami
- Gunung Meletus
- Angin Topan / Puting Beliung
- Tanah Longsor
- Kebakaran Hutan
- Kekeringan

### 📚 Materi Edukasi Lengkap
Setiap jenis bencana memiliki informasi mengenai:

- Definisi
- Penyebab
- Tanda-tanda
- Mitigasi
- Langkah saat terjadi bencana
- Langkah setelah bencana
- Fakta menarik

### 🎨 Antarmuka Modern
- Animated gradient background
- Particle animation
- Responsive layout
- User-friendly navigation

### 🧠 Intent-Based Chatbot
Chatbot mampu mengenali:

- Sapaan pengguna
- Jenis bencana yang ditanyakan
- Topik spesifik yang ingin diketahui
- Pertanyaan umum terkait kebencanaan

---

## 🛠️ Teknologi yang Digunakan

- **Python**
- **Streamlit**
- **Particles.js**
- HTML & CSS Custom Styling

---

## 📂 Struktur Proyek

```text
project_tbo/
│
├── app.py                # Aplikasi utama Streamlit
├── chatbot.py            # Logika chatbot dan pemrosesan pertanyaan
├── disaster_data.py      # Basis pengetahuan bencana alam
├── requirements.txt      # Dependency proyek
│
├── static/
│   └── particles.min.js  # Animasi partikel
│
└── particle/
    └── ...               # Library particles.js
```

---

## 🚀 Instalasi

### 1. Clone Repository

```bash
git clone https://github.com/syauqi-i/chatbot-web.git
cd chatbot-web
```

### 2. Buat Virtual Environment (Opsional)

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / macOS:

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependency

```bash
pip install -r requirements.txt
```

---

## ▶️ Menjalankan Aplikasi

```bash
streamlit run app.py
```

Setelah berhasil dijalankan, buka browser:

```text
http://localhost:8501
```

---

## 💬 Contoh Pertanyaan

Pengguna dapat mencoba pertanyaan seperti:

```text
Apa itu gempa bumi?

Apa penyebab banjir?

Bagaimana mitigasi tsunami?

Apa yang harus dilakukan saat gunung meletus?

Tanda-tanda tanah longsor apa saja?

Fakta menarik tentang kekeringan.
```

---

## 🧠 Cara Kerja Chatbot

Chatbot menggunakan pendekatan berbasis aturan (*rule-based system*):

1. Membersihkan input pengguna.
2. Mendeteksi jenis bencana yang disebutkan.
3. Mengidentifikasi subtopik yang ditanyakan:
   - Definisi
   - Penyebab
   - Tanda
   - Mitigasi
   - Saat terjadi
   - Setelah terjadi
   - Fakta
4. Mengambil jawaban dari basis pengetahuan.
5. Menampilkan respons yang sesuai.

---

## 📖 Data Bencana yang Tersedia

| Bencana | Status |
|----------|---------|
| Gempa Bumi | ✅ |
| Banjir | ✅ |
| Tsunami | ✅ |
| Gunung Meletus | ✅ |
| Angin Topan | ✅ |
| Tanah Longsor | ✅ |
| Kebakaran Hutan | ✅ |
| Kekeringan | ✅ |

---

## 🎯 Tujuan Proyek

Proyek ini dibuat untuk:

- Meningkatkan literasi kebencanaan masyarakat.
- Menjadi media pembelajaran interaktif.
- Membantu pengguna memahami mitigasi dan keselamatan saat bencana.
- Mendukung edukasi kesiapsiagaan bencana berbasis teknologi.

---

## 🔮 Pengembangan Selanjutnya

Beberapa fitur yang dapat ditambahkan:

- Integrasi API BMKG
- Prediksi intent menggunakan NLP
- Voice Assistant
- Multi-language support
- Dashboard statistik penggunaan
- Peringatan dini bencana real-time

---

## 👨‍💻 Pengembang

Dikembangkan oleh kelompok 2 sebagai proyek edukasi dan pembelajaran mengenai mitigasi bencana alam.

---

## 📜 License

Proyek ini dibuat untuk tujuan edukasi dan pembelajaran.

Silakan gunakan, modifikasi, dan kembangkan sesuai kebutuhan.
