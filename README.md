# LeafDetect

Deteksi Penyakit Daun Bawang berbasis **Django + MobileNetV2**, dengan aplikasi
**Flutter** yang memakai kamera HP. Catatan ini dibuat agar alur kerja tidak
hilang arah: apa yang dijalankan, alamat apa yang dibuka, dan apa yang dilakukan
kalau ada masalah.

## Ringkasan cepat

| Kebutuhan | Alamat / perintah |
| --- | --- |
| Server (VS Code) | `F5` → pilih **“LeafDetect: Django 8001 (buka browser otomatis)”** |
| Server (terminal) | `python manage.py runserver 0.0.0.0:8001` |
| Buka di **laptop** | <http://127.0.0.1:8001> |
| Buka di **HP** | `http://<IP-Wi-Fi-laptop>:8001` (sekarang `http://192.168.0.103:8001`) |
| Hubungkan aplikasi HP | Scan QR di bagian **“Buka LeafDetect di HP”** |
| Hentikan server | `Ctrl+C` (terminal) atau `Shift+F5` (F5) |

QR Code di proyek ini adalah QR untuk **menghubungkan HP ke server**, bukan
QRIS/pembayaran.

## 1. Persyaratan

- **Python 3.12** — jangan 3.15, karena TensorFlow belum tersedia di sana.
- **Flutter** sudah terpasang (`flutter --version`).
- HP Android + APK LeafDetect.
- Laptop dan HP di **jaringan Wi-Fi yang sama**.

## 2. Struktur proyek

```text
LeafDetect/
├── backend/models/           # daunai_mobilenetv2.keras + class_names.json
├── detector/                 # views.py: halaman web, /health, /detect
├── leafdetect_project/       # settings.py, urls.py
├── mobile/                   # aplikasi Flutter
│   └── lib/
│       ├── helpers/          # api_client, server_info, image_utils, frame_converter
│       ├── model/            # detection_result, disease_info, history_item
│       ├── service/          # health, detection, history
│       ├── ui/               # connect, beranda, deteksi, riwayat, tentang
│       └── widget/           # sidebar (drawer), result_card
├── static/                   # style.css, script.js
├── templates/index.html      # halaman web + QR Code
├── .vscode/launch.json       # konfigurasi F5 (tidak ikut git)
└── requirements.txt
```

## 3. Menjalankan server dari VS Code

1. `File → Open Folder…` → pilih `C:\Users\Lenovo\LeafDetect`.
2. `Ctrl+Shift+P` → **Python: Select Interpreter** →
   `C:\Users\Lenovo\LeafDetect\.venv\Scripts\python.exe` (Python 3.12.6).
3. `Ctrl+Shift+D` → pilih konfigurasi:
   - **“LeafDetect: Django 8001 (buka browser otomatis)”** → log di tab
     *Debug Console*, browser terbuka sendiri.
   - **“LeafDetect: Django 8001 (log di terminal)”** → log di terminal, tanpa
     auto-buka.
4. Tekan `F5`.

Atau lewat terminal (`Ctrl+~`), tanpa perlu memilih konfigurasi:

```powershell
python manage.py runserver 0.0.0.0:8001
```

### Tanda server sudah siap

```
Model MobileNetV2 berhasil dimuat.
Kelas: ['bercak ungu', 'embun bulu', 'hawar daun', 'moler', 'sehat']
Starting development server at http://0.0.0.0:8001/
```

Selama baris terakhir belum muncul, server belum siap. Peringatan TensorFlow
(`oneDNN custom operations are on`, `GPU support is not available`) dan
peringatan kuning Django tentang *development server* adalah **normal**.

### Catatan F5

- Konfigurasi memakai `--noreload`: setelah mengubah kode Python, tekan tombol
  **restart** (↻) di toolbar debug.
- Hentikan dengan `Shift+F5` atau tombol ⏹, bukan `Ctrl+C`.
- `.vscode/` masuk `.gitignore`, jadi `launch.json` tidak ikut ter-push. Kalau
  clone di komputer lain, buat ulang konfigurasinya.

## 4. Alamat yang dibuka (sering bikin bingung)

| Dibuka di | Alamat | Keterangan |
| --- | --- | --- |
| Laptop | `http://127.0.0.1:8001` | `127.0.0.1` = *localhost*, selalu menunjuk komputer sendiri |
| Laptop | `http://localhost:8001` | sama saja dengan di atas |
| HP | `http://192.168.0.103:8001` | IP LAN laptop, hanya berlaku di jaringan yang sama |

`0.0.0.0` yang dicetak Django **bukan alamat untuk browser**. Artinya "dengarkan
di semua interface": `127.0.0.1` (laptop) dan IP LAN (HP).

### Cara mengetahui IP LAN

1. **Paling mudah:** buka `http://127.0.0.1:8001` → bagian **“Buka LeafDetect di
   HP”** menampilkan alamatnya, dan QR Code berisi alamat yang sama.
2. **Terminal:** `ipconfig` → **Wireless LAN adapter Wi-Fi** → `IPv4 Address`.
3. **PowerShell:**

   ```powershell
   (Get-NetIPAddress -AddressFamily IPv4 |
       Where-Object InterfaceAlias -eq 'Wi-Fi').IPAddress
   ```

IP bisa berubah saat pindah jaringan. Kalau berubah: muat ulang halaman web (QR
dibuat ulang otomatis), lalu di aplikasi pakai **Ganti Server**.

### Mengganti port

Port mengikuti argumen `runserver`. Contoh ke `9000`:

```powershell
python manage.py runserver 0.0.0.0:9000
```

Alamat laptop jadi `http://127.0.0.1:9000`, dan alamat di halaman web/QR
menyesuaikan otomatis (`request.get_port()`). Tambahkan aturan firewall untuk
port baru bila HP tidak bisa terhubung.

## 5. Menghubungkan aplikasi HP ke server

1. Pastikan server jalan dan HP bisa membuka `http://<IP-LAN>:8001` di browser.
2. Buka aplikasi LeafDetect → izinkan akses kamera.
3. Arahkan kamera ke QR Code pada halaman web.
4. Aplikasi memeriksa `/health`, lalu menyimpan alamat server.
5. Kalau QR susah terbaca: masukkan alamat manual, contoh
   `http://192.168.0.103:8001`, lalu **Hubungkan**.
6. Untuk mengganti server: menu ☰ → **Ganti Server**.

## 6. Menjalankan aplikasi Flutter

```powershell
cd mobile
flutter pub get
flutter devices
flutter run
```

Membuat APK debug:

```powershell
flutter build apk --debug
```

Hasil: `mobile/build/app/outputs/flutter-apk/app-debug.apk` (±168 MB).
Salin ke HP, aktifkan **Install unknown apps**, lalu install.

Perintah pemeriksaan:

```powershell
cd mobile
flutter analyze
flutter test
```

## 7. Alur pemakaian harian

**Menyiapkan:**
1. Buka folder proyek di VS Code.
2. `F5` → konfigurasi Django 8001.
3. Tunggu `Starting development server at http://0.0.0.0:8001/`.
4. Buka `http://127.0.0.1:8001` di laptop, cek bagian **Buka LeafDetect di HP**.

**Menguji di HP:**
5. Buka aplikasi → Beranda harus **“Server terhubung”** dan menampilkan 5 kelas.
6. Menu ☰ → **Deteksi**. Ada dua cara memakai kamera:
   - **Deteksi otomatis** (aktif secara bawaan): arahkan kamera ke daun, hasil
     di layar diperbarui kira-kira setiap 1,5 detik. Hasil ini **tidak**
     disimpan ke riwayat, sama seperti mode live di website.
   - **Ambil Foto**: membekukan gambar, menampilkan hasil lengkap (semua skor
     kelas + saran), dan **menyimpan** ke riwayat.
   - **Galeri**: memilih foto yang sudah ada di HP, lalu dianalisis seperti
     Ambil Foto.
7. Hasil manual muncul sebagai kartu: penyakit, confidence, skor semua kelas,
   saran. Hasil otomatis muncul ringkas di bawah kamera.
8. Menu ☰ → **Riwayat** → hasil manual tersimpan (maksimal 12 item).
9. Kalau deteksi otomatis berhenti sendiri, biasanya koneksi ke server terputus:
   cek Beranda, lalu nyalakan lagi sakelar **Deteksi otomatis**.

**Selesai:**
10. `Shift+F5` (atau `Ctrl+C`) untuk menghentikan server.

## 8. API

| Method | Endpoint | Keterangan |
| --- | --- | --- |
| GET | `/health` | Status server, nama model, daftar kelas |
| POST | `/detect` | Terima gambar `multipart/form-data`, field `file` |

Contoh:

```powershell
curl.exe -X POST -F "file=@gambar-daun.jpg" http://127.0.0.1:8001/detect
```

Contoh respons `/detect`:

```json
{
  "status": "success",
  "model": "MobileNetV2",
  "disease": "sehat",
  "confidence": 0.9956,
  "confidence_percent": 99.56,
  "image_size": { "width": 1536, "height": 1024 },
  "predictions": {
    "bercak ungu": 0.0003,
    "embun bulu": 0.0036,
    "hawar daun": 0.0005,
    "moler": 0.0,
    "sehat": 0.9956
  }
}
```

Kode error: `400` file tidak ada / bukan gambar, `413` lebih dari 10 MB,
`503` model belum termuat.

## 9. Model

- MobileNetV2, input **224 × 224**, 5 kelas: `bercak ungu`, `embun bulu`,
  `hawar daun`, `moler`, `sehat`.
- File: `backend/models/daunai_mobilenetv2.keras` dan
  `backend/models/class_names.json`.
- Batas unggah 10 MB. Model dimuat sekali saat server start (beberapa detik).

## 10. Troubleshooting

| Gejala | Penyebab & solusi |
| --- | --- |
| `ModuleNotFoundError: No module named 'django'` | Interpreter salah (Python 3.15). Pilih `.venv` di langkah 3. |
| `That port is already in use` | Server lain masih jalan. `Get-NetTCPConnection -LocalPort 8001 \| % { Stop-Process -Id $_.OwningProcess -Force }` |
| `Activate.ps1 cannot be loaded` | Jangan aktivasi venv; panggil `.\.venv\Scripts\python.exe` langsung. |
| HP tidak bisa membuka alamat LAN | Server harus `0.0.0.0`, HP satu Wi-Fi, dan firewall mengizinkan. PowerShell **as Administrator**: `New-NetFirewallRule -DisplayName "LeafDetect 8001" -Direction Inbound -LocalPort 8001 -Protocol TCP -Action Allow` |
| QR menampilkan `127.0.0.1` | Komputer tanpa rute internet untuk deteksi IP. Set `$env:LEAFDETECT_PUBLIC_URL = "http://192.168.0.103:8001/"` sebelum runserver. |
| Aplikasi HP: “Tidak dapat terhubung” | Alamat lama/port lama masih tersimpan → **Ganti Server** → scan QR baru. |
| Log `GET /v1/models 404` tiap 30 detik | Aplikasi OpenCode memprobe port 8000 (format OpenAI). Bukan bagian LeafDetect, tidak berbahaya. Muncul hanya jika server di port 8000. |
| `18 unapplied migration(s)` | Tidak dipakai LeafDetect. Abaikan, atau `python manage.py migrate`. |
| Peringatan kuning *development server* | Normal, bawaan Django. Hanya relevan untuk produksi. |
| Kamera browser HP tidak muncul | Browser memblokir kamera di `http://` IP LAN. Gunakan aplikasi Flutter (kamera native). |

## 11. Git (commit & push)

Identitas Git harus diatur sekali:

```powershell
git config --global user.name "Nymexxx"
git config --global user.email "panduariffalah12@gmail.com"
```

Di VS Code (panel **Source Control**):

1. Arahkan mouse ke **Changes** → klik **+** (Stage All Changes).
2. Tulis pesan, contoh `Tambah aplikasi Flutter LeafDetect dan QR koneksi server`.
3. Klik **✓ Commit** (`Ctrl+Enter`).
4. Klik **Sync Changes** (⟳) untuk push ke GitHub.

Yang otomatis diabaikan: `mobile/build/` (termasuk APK), `.venv/`,
`mobile/android/local.properties`, `.vscode/`, `db.sqlite3`, dataset.

## 12. Dokumen teknis (Word & PDF)

Untuk proposal, PPT, atau menyerahkan konteks ke AI/tim lain:

| File | Isi |
| --- | --- |
| `docs/LeafDetect-Dokumentasi-Teknis.docx` | 41 halaman: arsitektur, backend, model, Flutter, alur, pengujian, batasan, lampiran, prompt AI |
| `docs/LeafDetect-Dokumentasi-Teknis.pdf` | Versi baca cepat dari dokumen yang sama |
| `docs/generate_technical_doc.py` | Skrip pembuat dokumen (bisa diedit lalu dijalankan ulang) |

Membuat ulang setelah kode berubah:

```powershell
.\.venv\Scripts\python.exe -m pip install -r docs\requirements-docs.txt
.\.venv\Scripts\python.exe docs\generate_technical_doc.py
```

Setelah file `.docx` dibuka, klik kanan pada **Daftar Isi** → **Update Field**
bila nomor halaman belum muncul.

## 13. Batasan

- `runserver` hanya untuk pengembangan, bukan produksi publik.
- Kamera HP dan scan QR sudah berfungsi di perangkat fisik; tidak bisa diuji di
  laptop tanpa kamera.
- Deteksi otomatis memakai *image streaming* kamera. Kalau perangkat tidak
  mendukung, sakelar otomatis mati sendiri dan aplikasi menyarankan **Ambil
  Foto**.
- Fitur mengikuti kemampuan LeafDetect yang ada: deteksi gambar, hasil prediksi,
  riwayat lokal. Tidak ada login, CRUD, atau pembayaran.
- Hasil AI adalah prediksi, bukan diagnosis pasti. Periksa tanaman secara
  langsung.

