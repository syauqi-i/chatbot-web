import re
import random
from disaster_data import DISASTER_INFO, GENERAL_QUESTIONS, get_disaster_names, get_disaster_info, get_general_answer


# ─── Sistem Deteksi Krisis & Prioritas Tindakan ─────────────────

# Kata kunci yang menandakan situasi darurat / krisis aktif
CRISIS_INDICATORS = {
    "tinggi": [
        "terendam", "tenggelam", "terjebak", "terperangkap", "ambruk", "roboh",
        "runtuh", "hanyut", "terbakar", "meledak", "tertimbun", "tertimpa",
        "tergulung", "terseret", "terkubur", "luka parah", "pendarahan",
        "tidak sadarkan diri", "pingsan", "sesak napas", "patah tulang",
        "korban jiwa", "meninggal", "tewas", "hilang", "darurat",
        "tolong", "bantuan segera", "evakuasi segera", "nyawa terancam",
        "rumah roboh", "atap ambruk", "jembatan putus", "jalan terputus",
        "listrik masih menyala", "kabel listrik", "gas bocor",
        "anak terjebak", "bayi", "lansia terjebak", "hamil",
        "air naik", "air masuk rumah", "banjir bandang datang",
        "lava", "lahar", "awan panas", "tsunami datang",
    ],
    "sedang": [
        "genangan", "merendam", "menggenangi", "retak", "miring",
        "guncangan", "getaran kuat", "hujan deras", "angin kencang",
        "asap tebal", "abu vulkanik", "tanah bergerak", "longsor kecil",
        "air keruh", "bau gas", "bau belerang", "sirene",
        "peringatan", "waspada", "siaga", "awas",
        "air setinggi", "ketinggian air", "cm", "meter",
        "pohon tumbang", "atap bocor", "dinding retak",
        "mengungsi", "pengungsian", "evakuasi",
    ],
    "rendah": [
        "khawatir", "takut", "cemas", "was-was", "panik",
        "cuaca buruk", "mendung gelap", "hujan terus",
        "gempa kecil", "getaran ringan", "suara gemuruh",
        "persiapan", "antisipasi", "jaga-jaga",
        "informasi terbaru", "update", "kabar terbaru",
        "apakah aman", "apakah bahaya", "daerah rawan",
        "info terbaru", "update terbaru", "gempa ringan",
        "gempa bumi ringan", "guncangan ringan", "guncangan kecil",
        "getaran kecil", "banjir kecil",
    ],
}

# Pola situasi krisis per jenis bencana
CRISIS_SITUATIONS = {
    "banjir": {
        "patterns": [
            r"terendam\s*(banjir)?\s*(\d+)\s*(cm|meter|m)",
            r"banjir\s*(\d+)\s*(cm|meter|m)",
            r"air\s*(naik|masuk|setinggi|merendam)",
            r"rumah\s*(terendam|kebanjiran|banjir)",
            r"genangan\s*air",
            r"banjir\s*(bandang|datang|melanda)",
        ],
        "tindakan_tinggi": [
            "⚡ **Matikan listrik** (MCB/sekring utama) SEGERA — bahaya korsleting!",
            "👨‍👩‍👧‍👦 **Evakuasi semua anggota keluarga** ke tempat yang lebih tinggi",
            "📄 **Bawa dokumen penting** (KTP, KK, ijazah) dalam plastik kedap air",
            "💊 **Bawa obat-obatan** penting dan P3K",
            "📱 **Hubungi petugas darurat:** 112 (Nasional) / BNPB: 021-29887300",
            "🚫 **JANGAN berjalan di arus banjir** — air selutut bisa menyeret orang dewasa",
            "🏠 Jika tidak bisa keluar, **naik ke lantai atas atau atap** dan beri tanda minta tolong",
        ],
        "tindakan_sedang": [
            "⚡ **Siapkan untuk matikan listrik** jika air terus naik",
            "📦 **Pindahkan barang berharga** dan elektronik ke tempat tinggi",
            "📄 **Kumpulkan dokumen penting** dalam tas kedap air",
            "🎒 **Siapkan tas darurat** (makanan, air, senter, baterai, P3K)",
            "📱 **Pantau info dari BMKG/BNPB** dan tetap waspada",
            "🚗 **Pindahkan kendaraan** ke tempat yang lebih tinggi",
            "👨‍👩‍👧‍👦 **Siapkan jalur evakuasi** dan beritahu anggota keluarga",
        ],
        "tindakan_rendah": [
            "📱 **Pantau informasi cuaca** dari BMKG secara berkala",
            "🎒 **Siapkan tas siaga bencana** untuk jaga-jaga",
            "📄 **Simpan dokumen penting** di tempat aman dan tinggi",
            "🔋 **Siapkan senter dan baterai cadangan**",
            "💧 **Stok air bersih dan makanan** tahan lama",
            "📞 **Simpan nomor darurat:** 112, BNPB: 021-29887300",
        ],
    },
    "gempa_bumi": {
        "patterns": [
            r"gempa\s*(bumi)?\s*(terjadi|sekarang|barusan|baru saja)",
            r"(ada|terjadi|terasa)\s*gempa",
            r"bangunan\s*(retak|roboh|ambruk|runtuh|goyang)",
            r"guncangan\s*(kuat|hebat|dahsyat)",
            r"rumah\s*(retak|roboh|goyang|ambruk)",
        ],
        "tindakan_tinggi": [
            "🛡️ **DROP, COVER, HOLD ON** — Merunduk, lindungi kepala, pegangan!",
            "🏗️ Jika di dalam ruangan: **berlindung di bawah meja kokoh**",
            "🪟 **Jauhi jendela, cermin, lemari** dan benda yang bisa jatuh",
            "🚪 Jika di dekat pintu: **keluar ke area terbuka** yang aman",
            "🚫 **JANGAN gunakan lift** — gunakan tangga darurat",
            "📱 **Hubungi petugas darurat:** 112 / BMKG: 021-6546318",
            "⚠️ **Waspada gempa susulan** — jangan kembali ke bangunan rusak",
            "🏥 Periksa luka dan **berikan pertolongan pertama** jika ada korban",
        ],
        "tindakan_sedang": [
            "🛡️ **Identifikasi tempat berlindung** terdekat (kolong meja, bawah tangga)",
            "📦 **Amankan barang-barang berat** yang bisa jatuh",
            "🚪 **Kenali jalur evakuasi** keluar bangunan",
            "🎒 **Siapkan tas darurat** (senter, P3K, air, makanan)",
            "📱 **Pantau info BMKG** untuk update gempa susulan",
            "👨‍👩‍👧‍👦 **Komunikasikan rencana evakuasi** dengan keluarga",
        ],
        "tindakan_rendah": [
            "🏠 **Periksa struktur bangunan** — pastikan tahan gempa",
            "📦 **Pasang pengaman pada perabot** berat ke dinding",
            "🎒 **Siapkan tas siaga** bencana di tempat mudah dijangkau",
            "📱 **Simpan nomor darurat** dan info jalur evakuasi",
            "🗣️ **Latih anggota keluarga** prosedur Drop, Cover, Hold On",
        ],
    },
    "tsunami": {
        "patterns": [
            r"tsunami\s*(datang|terjadi|mendekat|sekarang)",
            r"air\s*laut\s*(surut|naik|meluap)",
            r"gelombang\s*(besar|tinggi|raksasa)",
            r"(di|dekat)\s*(pantai|pesisir).*gempa",
        ],
        "tindakan_tinggi": [
            "🏃 **LARI KE TEMPAT TINGGI SEKARANG!** Minimal 30 meter dari permukaan laut",
            "⛰️ **Evakuasi minimal 2 km dari pantai** — jangan tunggu peringatan resmi!",
            "🚫 **JANGAN gunakan kendaraan** — jalan kaki lebih cepat, hindari kemacetan",
            "🏢 Jika tidak bisa ke bukit: **naik ke lantai 3+ gedung kokoh** (evakuasi vertikal)",
            "📱 **Hubungi darurat:** 112 / BMKG: 021-6546318",
            "⚠️ **JANGAN kembali ke pantai** setelah gelombang pertama — ada gelombang berikutnya!",
            "👨‍👩‍👧‍👦 **Bawa keluarga, tinggalkan barang** — nyawa lebih penting!",
        ],
        "tindakan_sedang": [
            "📱 **Pantau peringatan BMKG** secara terus-menerus",
            "🏃 **Kenali jalur evakuasi tsunami** terdekat",
            "🎒 **Siapkan tas darurat** untuk evakuasi cepat",
            "👨‍👩‍👧‍👦 **Siapkan keluarga** untuk evakuasi kapan saja",
            "⛰️ **Identifikasi tempat tinggi** terdekat dari lokasi Anda",
        ],
        "tindakan_rendah": [
            "📱 **Pantau info BMKG** untuk peringatan dini tsunami",
            "🗺️ **Hafalkan jalur evakuasi** tsunami di daerah Anda",
            "🎒 **Siapkan tas siaga** bencana",
            "📞 **Simpan nomor darurat:** 112, BMKG: 021-6546318",
        ],
    },
    "gunung_meletus": {
        "patterns": [
            r"gunung\s*(meletus|erupsi|mau meletus)",
            r"(letusan|erupsi)\s*gunung",
            r"(abu|asap|lava|lahar|awan panas)",
            r"hujan\s*abu",
            r"status\s*(awas|siaga)",
        ],
        "tindakan_tinggi": [
            "🏃 **Evakuasi SEGERA** dari zona bahaya sesuai radius yang ditentukan!",
            "😷 **Gunakan masker/kain basah** untuk melindungi pernapasan dari abu",
            "🧥 **Pakai baju lengan panjang, celana panjang, kacamata, topi**",
            "🏔️ **Hindari lembah dan aliran sungai** — jalur lahar dan awan panas!",
            "🍽️ **Tutup sumber air dan makanan** dari abu vulkanik",
            "📱 **Hubungi darurat:** 112 / PVMBG: 022-7271723",
            "🚗 **JANGAN mengemudi saat hujan abu** — jarak pandang sangat rendah!",
        ],
        "tindakan_sedang": [
            "😷 **Siapkan masker dan kacamata pelindung**",
            "📱 **Pantau status gunung dari PVMBG** secara rutin",
            "🎒 **Siapkan tas evakuasi** (masker, air, makanan, obat, dokumen)",
            "👨‍👩‍👧‍👦 **Diskusikan rencana evakuasi** dengan keluarga",
            "🏠 **Tutup jendela dan ventilasi** rumah",
        ],
        "tindakan_rendah": [
            "📱 **Pantau status aktivitas gunung** dari PVMBG",
            "😷 **Siapkan masker** untuk jaga-jaga",
            "🎒 **Siapkan tas siaga** bencana",
            "🗺️ **Kenali zona bahaya** di sekitar gunung",
        ],
    },
    "tanah_longsor": {
        "patterns": [
            r"longsor\s*(terjadi|menerjang|datang)",
            r"tanah\s*(longsor|bergerak|bergeser|retak)",
            r"(bukit|lereng|tebing)\s*(longsor|runtuh|ambrol)",
            r"rumah\s*(tertimbun|terkena longsor)",
        ],
        "tindakan_tinggi": [
            "🏃 **Bergerak MENYAMPING** dari jalur longsor — JANGAN melawan arah longsor!",
            "⛰️ **Jauhi dasar lereng** dan aliran lembah",
            "🛡️ **Lindungi kepala** dengan tangan atau benda lain",
            "📱 **Hubungi darurat:** 112 / BNPB: 021-29887300",
            "🚗 Jika di kendaraan: **putar balik atau keluar** dan lari ke area aman",
            "⚠️ **Jauhi area longsor** — risiko longsor susulan masih tinggi!",
            "👀 **Periksa anggota keluarga** yang mungkin hilang",
        ],
        "tindakan_sedang": [
            "👀 **Perhatikan tanda-tanda** longsor (retakan tanah, pohon miring)",
            "🏠 **Jauhi lereng curam** saat hujan deras",
            "📱 **Pantau peringatan cuaca** dari BMKG",
            "🎒 **Siapkan tas darurat** untuk evakuasi cepat",
            "👨‍👩‍👧‍👦 **Siapkan jalur evakuasi** alternatif",
        ],
        "tindakan_rendah": [
            "🏠 **Periksa kondisi lereng** di sekitar rumah",
            "🌳 **Tanam pohon berakar kuat** untuk menahan tanah",
            "📱 **Pantau cuaca** saat musim hujan",
            "🎒 **Siapkan tas siaga** bencana",
        ],
    },
    "angin_topan": {
        "patterns": [
            r"(angin|badai|topan|siklon|puting beliung)\s*(kencang|datang|menerjang|sekarang)",
            r"atap\s*(terbang|robek|lepas|terbuka)",
            r"pohon\s*(tumbang|roboh|patah)",
        ],
        "tindakan_tinggi": [
            "🏠 **Tetap di dalam ruangan kokoh** — JANGAN keluar saat badai!",
            "🪟 **Jauhi jendela dan pintu kaca** — bisa pecah terhempas angin",
            "🛡️ **Berlindung di ruang interior** tanpa jendela (kamar mandi, gudang)",
            "⚡ **Matikan listrik** jika ada petir atau banjir",
            "🌳 **Jangan berteduh di bawah pohon** atau dekat reklame",
            "📱 **Hubungi darurat:** 112",
            "🚗 Jika di luar: **berlindung di parit atau cekungan** rendah, lindungi kepala",
        ],
        "tindakan_sedang": [
            "🏠 **Perkuat pintu, jendela, dan atap** rumah",
            "🌳 **Amankan benda-benda** di luar rumah yang bisa terbang",
            "🔋 **Siapkan senter, radio baterai** dan baterai cadangan",
            "💧 **Stok air bersih dan makanan** tahan lama",
            "📱 **Pantau peringatan cuaca** dari BMKG",
        ],
        "tindakan_rendah": [
            "📱 **Pantau informasi cuaca** dari BMKG",
            "🏠 **Periksa kondisi atap** dan jendela rumah",
            "🌳 **Pangkas ranting pohon** yang rapuh di sekitar rumah",
            "🎒 **Siapkan tas siaga** bencana",
        ],
    },
    "kebakaran_hutan": {
        "patterns": [
            r"(kebakaran|terbakar)\s*(hutan|lahan|rumah)",
            r"api\s*(menyebar|membesar|mendekat|tidak terkendali)",
            r"asap\s*(tebal|pekat|dimana-mana)",
        ],
        "tindakan_tinggi": [
            "🏃 **Evakuasi SEGERA** jika api mendekati pemukiman!",
            "🚫 **JANGAN mencoba memadamkan** api besar sendirian",
            "😷 **Basahi kain dan tutup hidung/mulut** dari asap",
            "🧥 **Gunakan pakaian lengan panjang** sebagai pelindung",
            "📱 **Hubungi darurat:** 112 / Damkar: 113",
            "🔥 Jika terjebak: **cari area yang sudah terbakar** (area hitam) sebagai tempat berlindung",
            "🚗 **Evakuasi berlawanan arah angin** dari api",
        ],
        "tindakan_sedang": [
            "😷 **Gunakan masker** untuk melindungi pernapasan dari asap",
            "🏠 **Tutup jendela dan ventilasi** rumah",
            "💧 **Basahi area sekitar rumah** jika memungkinkan",
            "📱 **Pantau perkembangan kebakaran** dan siap evakuasi",
            "🎒 **Siapkan tas darurat** untuk evakuasi cepat",
        ],
        "tindakan_rendah": [
            "📱 **Pantau informasi** tentang kebakaran di daerah sekitar",
            "🏠 **Bersihkan dedaunan kering** di sekitar rumah",
            "🧯 **Siapkan alat pemadam api** ringan",
            "🎒 **Siapkan tas siaga** bencana",
        ],
    },
    "kekeringan": {
        "patterns": [
            r"kekeringan\s*(parah|ekstrem|berkepanjangan)",
            r"(sumur|sumber air)\s*(kering|mengering|habis)",
            r"(krisis|kekurangan)\s*air",
            r"air\s*(habis|tidak ada|susah)",
        ],
        "tindakan_tinggi": [
            "💧 **Prioritaskan air untuk minum dan memasak** — hemat maksimal!",
            "🚰 **Jangan gunakan air bersih** untuk menyiram tanaman — gunakan air bekas cucian",
            "📱 **Laporkan krisis air** ke pemerintah setempat / BPBD",
            "🏥 **Perhatikan gejala dehidrasi** pada anak dan lansia",
            "🍶 **Simpan air bersih** di tempat tertutup dan bersih",
            "🚿 **Mandi secukupnya** — hemat setiap tetes air",
        ],
        "tindakan_sedang": [
            "💧 **Hemat penggunaan air** sehari-hari",
            "🪣 **Tampung air hujan** jika memungkinkan",
            "🚰 **Gunakan air bekas cucian** untuk menyiram tanaman",
            "📱 **Pantau informasi** dari BMKG tentang cuaca",
            "🍶 **Stok air bersih** untuk kebutuhan darurat",
        ],
        "tindakan_rendah": [
            "💧 **Mulai hemat air** dari sekarang",
            "🪣 **Siapkan penampungan air hujan**",
            "🌱 **Tanam tanaman tahan kekeringan**",
            "📱 **Pantau prakiraan cuaca** dari BMKG",
        ],
    },
}


def detect_crisis(text):
    """
    Mendeteksi apakah pesan user menunjukkan situasi krisis aktif.
    Mengembalikan dict {disaster_type, priority, actions} atau None.
    """
    cleaned = clean_text(text)
    original_lower = text.lower().strip()

    # Jika terdeteksi kata tanya edukasi umum, abaikan krisis kecuali jika ada indikator krisis tinggi
    has_edu_q = any(q in original_lower for q in ["bagaimana", "mengapa", "kenapa", "jelaskan", "sebutkan", "apa itu", "pengertian", "definisi"])
    if has_edu_q:
        has_high_indicator = False
        for indicator in CRISIS_INDICATORS["tinggi"]:
            if indicator in original_lower:
                has_high_indicator = True
                break
        if not has_high_indicator:
            return None

    # Jika terdeteksi subtopik edukasi, abaikan deteksi krisis kecuali jika ada indikator krisis tinggi
    if detect_subtopic(original_lower) is not None:
        has_high_indicator = False
        for indicator in CRISIS_INDICATORS["tinggi"]:
            if indicator in original_lower:
                has_high_indicator = True
                break
        if not has_high_indicator:
            return None

    # 1. Deteksi jenis bencana dari teks
    detected_disaster = None
    for keyword, disaster_key in DISASTER_KEYWORDS.items():
        if keyword in cleaned:
            detected_disaster = disaster_key
            break

    if not detected_disaster:
        return None

    # 2. Cek apakah cocok dengan pola situasi krisis
    crisis_info = CRISIS_SITUATIONS.get(detected_disaster)
    if not crisis_info:
        return None

    is_crisis_pattern = False
    for pattern in crisis_info["patterns"]:
        if re.search(pattern, original_lower):
            is_crisis_pattern = True
            break

    # 3. Tentukan tingkat prioritas berdasarkan kata kunci krisis
    priority = None
    priority_score = 0

    for indicator in CRISIS_INDICATORS["tinggi"]:
        if indicator in original_lower:
            priority_score += 3

    for indicator in CRISIS_INDICATORS["sedang"]:
        if indicator in original_lower:
            priority_score += 1

    for indicator in CRISIS_INDICATORS["rendah"]:
        if indicator in original_lower:
            priority_score += 0.5

    # Tentukan prioritas berdasarkan skor
    if priority_score >= 3:
        priority = "tinggi"
    elif priority_score >= 1 or is_crisis_pattern:
        priority = "sedang"
    elif priority_score > 0:
        priority = "rendah"
    else:
        return None

    # 4. Ambil tindakan sesuai prioritas
    actions = crisis_info.get(f"tindakan_{priority}", [])

    return {
        "disaster_type": detected_disaster,
        "priority": priority,
        "actions": actions,
    }


def format_crisis_response(crisis_data):
    """Memformat response krisis dengan prioritas tindakan"""
    disaster_info = get_disaster_info(crisis_data["disaster_type"])
    nama = disaster_info["nama"] if disaster_info else crisis_data["disaster_type"]
    priority = crisis_data["priority"]
    actions = crisis_data["actions"]

    # Header berdasarkan prioritas
    if priority == "tinggi":
        header = "🚨🚨 **PRIORITAS TINGGI — TINDAKAN DARURAT!**"
        priority_label = "🔴 TINGGI"
        border_note = "⚠️ **SITUASI DARURAT TERDETEKSI**"
    elif priority == "sedang":
        header = "⚠️ **PRIORITAS SEDANG — WASPADA!**"
        priority_label = "🟡 SEDANG"
        border_note = "🔔 **SITUASI PERLU PERHATIAN**"
    else:
        header = "ℹ️ **PRIORITAS RENDAH — PERSIAPAN**"
        priority_label = "🟢 RENDAH"
        border_note = "📋 **LANGKAH PERSIAPAN**"

    response = f"{border_note}\n\n"
    response += f"{header}\n"
    response += f"**Bencana:** {nama} | **Status Krisis:** {priority_label}\n\n"
    response += "**Langkah Tindakan:**\n\n"

    for i, action in enumerate(actions, 1):
        response += f"{i}. {action}\n"

    response += "\n---\n"
    response += "📞 **Nomor Darurat:** 112 (Nasional) | BNPB: 021-29887300 | BMKG: 021-6546318\n"
    response += "\n💬 _Tetap tenang dan ikuti langkah di atas. Keselamatan Anda adalah prioritas utama!_"

    return response


DISASTER_KEYWORDS = {
    "gempa": "gempa_bumi",
    "gempa bumi": "gempa_bumi",
    "seismic": "gempa_bumi",
    "banjir": "banjir",
    "banjir bandang": "banjir",
    "tsunami": "tsunami",
    "gunung": "gunung_meletus",
    "gunung meletus": "gunung_meletus",
    "letusan": "gunung_meletus",
    "vulkanik": "gunung_meletus",
    "vulkan": "gunung_meletus",
    "merapi": "gunung_meletus",
    "krakatau": "gunung_meletus",
    "angin": "angin_topan",
    "topan": "angin_topan",
    "siklon": "angin_topan",
    "badai": "angin_topan",
    "hurricane": "angin_topan",
    "tornado": "angin_topan",
    "puting beliung": "angin_topan",
    "longsor": "tanah_longsor",
    "tanah longsor": "tanah_longsor",
    "kebakaran": "kebakaran_hutan",
    "kebakaran hutan": "kebakaran_hutan",
    "hutan terbakar": "kebakaran_hutan",
    "kering": "kekeringan",
    "kekeringan": "kekeringan",
    "kemarau": "kekeringan",
}

SUBTOPIC_KEYWORDS = {
    "definisi": ["definisi", "pengertian", "apa itu", "arti", "adalah", "dimaksud", "sebutkan"],
    "penyebab": ["penyebab", "sebab", "mengapa", "kenapa", "apa yang menyebabkan", "faktor", "pemicu", "disebabkan"],
    "tanda": ["tanda", "ciri", "gejala", "pertanda", "indikasi", "tanda-tanda"],
    "mitigasi": ["mitigasi", "mencegah", "pencegahan", "cara menghadapi", "persiapan menghadapi", "cara mengantisipasi"],
    "saat_terjadi": ["saat", "ketika", "waktu terjadi", "tindakan", "yang harus dilakukan saat", "langkah", "cara menyelamatkan"],
    "setelah_terjadi": ["setelah", "sesudah", "pasca", "yang harus dilakukan setelah", "tindakan setelah"],
    "fakta": ["fakta", "menarik", "unik", "tahukah", "info unik", "rekor", "paling"],
}

SAPAAN_KEYWORDS = {
    "siapa_kamu": ["siapa kamu", "siapa kau", "nama kamu", "nama mu", "perkenalkan", "hai", "halo", "hello", "hey", "hi", "helo"],
    "apa_bisa": ["bisa apa", "apa yang kamu bisa", "kemampuan", "fungsi", "kamu bisa ngapain"],
    "daftar_bencana": ["bencana apa", "jenis bencana", "macam bencana", "daftar bencana", "apa saja"],
    "cara_membantu": ["cara membantu", "donasi", "relawan", "sukarelawan"],
    "bmkg": ["bmkg", "informasi cuaca", "peringatan dini", "badan meteorologi", "kontak darurat", "nomor darurat"],
    "terima_kasih": ["terima kasih", "makasih", "thanks", "thank"],
}


def clean_text(text):
    """Membersihkan teks dari karakter tidak perlu"""
    text = text.lower().strip()
    text = re.sub(r'[^a-z\s]', '', text)
    return text


def get_intent(text):
    """Mendeteksi intent dari pertanyaan umum"""
    cleaned = clean_text(text)
    for intent, patterns in SAPAAN_KEYWORDS.items():
        for pattern in patterns:
            if pattern in cleaned:
                return intent
    return None


def detect_disaster(text):
    """Mendeteksi bencana yang dimaksud dalam pertanyaan"""
    cleaned = clean_text(text)
    matches = []
    for keyword, disaster_key in DISASTER_KEYWORDS.items():
        if keyword in cleaned:
            matches.append(disaster_key)
    if matches:
        return list(set(matches))
    return []


def detect_subtopic(text):
    """Mendeteksi subtopik yang ditanyakan"""
    cleaned = clean_text(text)
    for subtopic, keywords in SUBTOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in cleaned:
                return subtopic
    return None


def format_disaster_response(disaster_key, subtopic=None):
    """Memformat response berdasarkan bencana dan subtopik"""
    info = get_disaster_info(disaster_key)
    if not info:
        return None

    nama = info["nama"]

    if not subtopic:
        response = f"**{nama}** ({info['nama_inggris']})\n\n"
        response += f"{info['definisi']}\n\n"
        response += f"**Penyebab:**\n"
        for p in info["penyebab"][:3]:
            response += f"- {p}\n"
        response += f"\n**Yang Harus Dilakukan Saat Terjadi:**\n"
        for s in info["saat_terjadi"][:3]:
            response += f"- {s}\n"
        response += f"\nKetik '{nama.lower()} [topik]' untuk info lebih detail.\n"
        response += f"Topik: definisi, penyebab, tanda, mitigasi, saat terjadi, setelah terjadi, fakta"
        return response

    if subtopic == "definisi":
        return f"**{nama}** — {info['definisi']}"

    if subtopic == "penyebab":
        response = f"**Penyebab {nama}:**\n"
        for i, p in enumerate(info["penyebab"], 1):
            response += f"{i}. {p}\n"
        return response

    if subtopic == "tanda":
        response = f"**Tanda-tanda {nama}:**\n"
        for i, t in enumerate(info["tanda"], 1):
            response += f"{i}. {t}\n"
        return response

    if subtopic == "mitigasi":
        response = f"**Cara Mitigasi {nama}:**\n"
        for i, m in enumerate(info["mitigasi"], 1):
            response += f"{i}. {m}\n"
        return response

    if subtopic == "saat_terjadi":
        response = f"**Yang Harus Dilakukan Saat {nama} Terjadi:**\n"
        for i, s in enumerate(info["saat_terjadi"], 1):
            response += f"{i}. {s}\n"
        return response

    if subtopic == "setelah_terjadi":
        response = f"**Yang Harus Dilakukan Setelah {nama}:**\n"
        for i, s in enumerate(info["setelah_terjadi"], 1):
            response += f"{i}. {s}\n"
        return response

    if subtopic == "fakta":
        response = f"**Fakta Menarik tentang {nama}:**\n"
        for i, f in enumerate(info["fakta"], 1):
            response += f"{i}. {f}\n"
        return response

    return None


def get_fallback_response():
    """Respons default ketika tidak ada yang cocok"""
    fallbacks = [
        "Maaf, saya belum punya informasi tentang itu. Coba tanya tentang jenis bencana alam seperti gempa bumi, tsunami, banjir, gunung meletus, atau lainnya!",
        "Saya belum bisa menjawab pertanyaan itu. Silakan tanya tentang bencana alam atau cara menghadapinya!",
        "Informasi tentang itu belum ada di database saya. Ketik 'bencana apa saja' untuk melihat topik yang tersedia!",
    ]
    return random.choice(fallbacks)


def get_response(user_input):
    """Fungsi utama untuk mendapatkan response chatbot"""
    text = user_input.strip()

    if not text:
        return "Silakan tulis pertanyaan Anda!"

    # Cek intent umum (sapaan, dll)
    intent = get_intent(text)
    if intent:
        return get_general_answer(intent)

    # Cek situasi krisis / darurat (prioritas tindakan)
    crisis = detect_crisis(text)
    if crisis:
        return format_crisis_response(crisis)

    # Deteksi bencana
    disasters = detect_disaster(text)

    if disasters:
        disaster_key = disasters[0]
        subtopic = detect_subtopic(text)
        response = format_disaster_response(disaster_key, subtopic)
        if response:
            return response

    # Jika ada beberapa bencana terdeteksi tapi tidak ada subtopic yang cocok
    if disasters:
        all_names = get_disaster_names()
        names = [all_names.get(d, d) for d in disasters]
        return f"Saya menemukan kata kunci: {', '.join(names)}. Coba tanya spesifik, misal: 'Apa penyebab {names[0].lower()}?' atau 'Cara mitigasi {names[0].lower()}'"

    # Fallback
    return get_fallback_response()
