# Hand Color Simon Says

> Mini game berbasis **segmentasi warna** untuk mata kuliah **Pengolahan Citra dan Video** oleh
**Catherine Patricia Sindunata** · 5024241040


## Tentang Game

Hand Color Simon Says menggabungkan permainan *Simon Says* dengan **Stroop Effect**, yaitu sebuah fenomena ketika otak kesulitan membedakan <u>arti sebuah kata</u> dengan <u>warna tinta</u> yang dipakai untuk menuliskannya.

Layar dibagi menjadi **4 zona di dalam sebuah grid 2×2**, di mana setiap zonanya berisi nama warna yang ditulis dengan warna tinta **berbeda**, misalnya tulisan **"Yellow"** yang bertinta merah. Susunan teks dan tinta **diacak setiap ronde**, jadi posisinya tidak bisa diprediksi.

Di bagian atas layar muncul salah satu dari dua jenis instruksi:

| Instruksi | Yang harus disentuh | Contoh |
|---|---|---|
| `Touch the text: 'Yellow'` | Zona dengan **tulisan** "Yellow" | tulisan *Yellow* (apa pun warna tintanya) |
| `Touch the color: 'Red'` | Zona dengan **warna tinta** merah | tulisan apa pun yang bertinta merah |

Untuk "menyentuh" zona, arahkan <u>tangan dengan sarung tangan hijau</u> ke zona tersebut dan **tahan sebentar** hingga lingkaran kuning di sekitar kursor penuh.

## Aturan Permainan

| Kejadian | Efek |
|---|---|
| ✅ Jawaban benar | Skor **+1** |
| ❌ Jawaban salah | Nyawa **−1** ❤️ |
| ⏱️ Waktu habis (5 detik per ronde) | Nyawa **−1** ❤️ |
| 🏆 Skor mencapai **10** | **You Win!** |
| 💀 Nyawa habis (3 → 0) | **Game Over** |

Setelah menang atau kalah, arahkan tangan ke mana saja dan tahan untuk bermain lagi, atau tekan `ESC` untuk kembali ke menu.

---

## Kontrol

| Input | Fungsi |
|---|---|
| ✋ Tahan tangan di tombol / zona | Memilih (dwell selection) |
| `ESC` | Kembali ke menu utama |
| `Q` | Keluar dari game |
| `D` | Tampilkan / sembunyikan jendela *pipeline* pengolahan citra |
| `C` | Buka / tutup slider kalibrasi HSV (otomatis tersimpan saat ditutup) |
| `S` | Simpan hasil kalibrasi ke `hsv_calibration.json` |



## Struktur Proyek

```
PROJECT-1-PCV/
├── main.py                
├── tracker.py             
├── game_logic.py          
├── ui.py                  
├── config.py              
├── hsv_calibration.json   
└── README.md
```

## Keperluan Games

**Kebutuhan:** Python 3.10+, webcam, dan **sarung tangan berwarna hijau** (atau benda hijau lain).

```bash
# 1. Clone repository
git clone https://github.com/Rendezvouire/PROJECT-1-PCV.git
cd PROJECT-1-PCV

# 2. Install library
pip install opencv-python numpy

# 3. Jalankan game
python main.py
```

Catatan: Jalankan `python main.py` dari **dalam folder proyek**, supaya file kalibrasi tersimpan di tempat yang benar.

## Kalibrasi Warna

Hasil deteksi sangat bergantung pada pencahayaan ruangan. Jika kursor tidak muncul atau melompat-lompat:

1. Tekan `C` untuk membuka slider **H/S/V min & max** (jendela *pipeline* ikut terbuka).
2. Geser slider sampai pada panel **Opening + Closing** hanya **tangan** yang berwarna putih.
3. Tekan `C` lagi (atau `S`) untuk menyimpan. Nilai ini otomatis dimuat saat game dijalankan kembali.

**Tips:**
- Gunakan ruangan dengan cahaya cukup dan merata.
- Hindari benda hijau lain di latar belakang kamera.
- Jika noise masih banyak, naikkan **S min** dan **V min**.

## Teknologi

- **Python** — bahasa pemrograman
- **OpenCV** — akuisisi video, segmentasi warna, morfologi, kontur, dan tampilan
- **NumPy** — operasi array & mask
