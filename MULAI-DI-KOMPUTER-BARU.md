# Mulai di komputer baru — instruksi untuk JSA

## Untuk Capt Juma (cukup 3 langkah)
1. Salin seluruh folder **Juma Stock Analysis** ke komputer baru (flashdisk, Google Drive, dan sebagainya).
2. Buka Claude Code, lalu pilih folder **Juma Stock Analysis** sebagai folder kerja (bukan folder induknya).
3. Ketik:
   ```
   JSA, pelajari folder ini dan jalankan MULAI-DI-KOMPUTER-BARU.md
   ```

Sisanya dikerjakan JSA.

---

## Untuk JSA: langkah setup
Kerjakan berurutan. Tulis satu baris progres per langkah. Kalau ada langkah yang gagal, jelaskan penyebabnya kepada Capt Juma dengan bahasa sederhana sebelum lanjut.

### 1. Kenali sistemnya
Baca `CLAUDE.md`, `.claude/skills/juma-stock-analysis/SKILL.md`, dan `.claude/skills/pola-pantul-lantai/SKILL.md`.
Pastikan folder kerja saat ini adalah akar folder Juma Stock Analysis (ada `CLAUDE.md` di dalamnya).

### 2. Cek Python
Jalankan `python --version` (di Windows bisa juga `py --version`).
- Butuh **Python 3.9 atau lebih baru**.
- Kalau belum ada: minta izin Capt Juma, lalu pasang. Di Windows bisa lewat `winget install Python.Python.3.12`,
  atau minta Capt Juma mengunduh dari python.org dan mencentang **"Add python.exe to PATH"** saat instalasi.
  Setelah itu Claude Code mungkin perlu dibuka ulang supaya `python` dikenali.
- Kalau perintahnya `py` dan bukan `python`, gunakan `py` di semua langkah berikutnya dan beri tahu Capt Juma.

### 3. Pasang library
```
python -m pip install -r requirements.txt
```

### 4. Jalankan cek setup
```
python tools/cek_setup.py
```
Semua baris harus `[OK]`. Kalau ada `[GAGAL]`, perbaiki sesuai pesan di baris itu, lalu jalankan ulang.
Catatan font: di Windows dan Mac, Arial dipakai otomatis. Di Linux, pasang paket `fonts-dejavu` kalau simbol tidak tampil.

### 5. Cek skill terbaca
Pastikan skill `juma-stock-analysis` dan `pola-pantul-lantai` muncul di daftar skill yang tersedia.
Kalau belum muncul, minta Capt Juma menutup lalu membuka ulang sesi Claude Code di folder ini.

### 6. Cek akses internet untuk data
Uji WebSearch singkat (misalnya `investing.com BBRI historical data`) dan satu WebFetch ke halaman historical data Investing.com.
Kalau WebFetch diblokir, catat dan beri tahu Capt Juma bahwa data harga perlu sumber lain.

### 7. Catat di log
Tambahkan entri di `log-perubahan/CHANGELOG.md`:
```
## YYYY-MM-DD — Setup di komputer baru
- Python x.y.z, reportlab x.y, font: ...
- Hasil cek_setup: semua lolos / catatan ...
```

### 8. Laporkan ke Capt Juma
Ringkas dalam tabel: langkah, hasil, catatan. Akhiri dengan:
"Sistem siap. Kirim saham pertama dengan format: `TICKER, harga trkhr X, bs buy A - B, target harian ..., target seminggu ..., target sebulan ...`"

## Catatan penting
- **Memori Claude tidak ikut pindah.** Semua aturan kerja sudah ada di `CLAUDE.md` dan skill, jadi tidak ada yang hilang.
  Kalau ada aturan baru yang penting, tulis di `CLAUDE.md` atau skill, jangan hanya di memori.
- File di `data/harga/` dan `hasil-analisa/` ikut terbawa. Data harga lama berguna untuk uji mundur pola PL.
- Jangan mengubah ambang skrip saat setup. Perubahan ambang hanya atas permintaan Capt Juma dan wajib dicatat di CHANGELOG.
