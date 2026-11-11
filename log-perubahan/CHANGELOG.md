# Log perubahan — Juma Stock Analysis

Catat setiap perubahan skill, skrip, ambang, atau format. Entri terbaru di atas.
Format: `## YYYY-MM-DD — vX.Y — judul singkat`, lalu poin "Berubah" dan "Alasan".

---

## 2026-11-11 — v1.2 — Pengambilan data harga otomatis
**Berubah**
- Skrip baru `tools/ambil_data.py <TICKER>`: ambil ~50 bar harian dari stockanalysis.com lewat curl, simpan ke `data/harga/<TICKER>.csv`, gabung dengan CSV lama tanpa tanggal ganda.
- Skill tahap 2-3 dan `referensi/A-data.md` memakai skrip ini. Investing.com ditinggalkan.
- `CLAUDE.md` peta folder menyebut `ambil_data.py`.

**Alasan**
- Investing.com memblokir akses otomatis (403), padahal Capt Juma ingin alur berjalan sendiri sampai PDF.
- stockanalysis.com memblokir User-Agent browser palsu tetapi menerima curl biasa; WebFetch tidak dipakai karena jalurnya terpisah dari proxy.

**Tidak berubah**
- Rumus indikator, ambang pola PL, aturan analisa, dan format PDF.

## 2026-11-11 — Setup di sesi cloud (Juma Stock Analysis Mobile)
- Folder disalin dari Google Drive (Juma Stock Analysis Mobile) ke repo; ukuran tiap file dicocokkan dengan aslinya.
- Python 3.13.18, reportlab 5.0.1, font DejaVu Sans (Linux).
- Hasil cek_setup: semua lolos (indikator, pola PL, PDF 2 halaman).
- Belum disalin: data/harga (CSV), data/json, hasil-analisa (PDF), dokumen/ (Blueprint BEI-APTS, perbandingan PL).
- Tidak ada perubahan skill, skrip, atau ambang.

## 2026-11-11 — Setup di komputer baru
- Python 3.14.5, reportlab 5.1.0, font: Arial (C:\Windows\Fonts\arial.ttf).
- Hasil cek_setup: semua lolos (indikator, pola PL, PDF 2 halaman).
- Skill `juma-stock-analysis` dan `pola-pantul-lantai` terbaca.
- Internet: WebSearch jalan. WebFetch ke investing.com GAGAL (DNS `ENOTFOUND www.investing.com`).
  WebFetch ke stockanalysis.com jalan, tapi data BBRI di sana tampak tertinggal (bar terakhir 7 Sep 2026). Data harga perlu sumber lain atau CSV dari Capt Juma.
- Tidak ada perubahan skill, skrip, atau ambang.

## 2026-11-11 — v1.1 — Booking order, modal, dan nama JSA
**Berubah**
- Nama asisten sekarang **JSA** di semua file dan di PDF.
- Input harian ditambah **modal** (total dana untuk saham itu) dan, kalau sudah punya posisi, `posisi X lot @harga`.
- Entry ditulis sebagai **satu harga booking terbaik** sebelum market buka, ditambah syarat "Batal booking kalau …".
  Syarat intraday (pullback, bertahan di atas X) dicek saat analisa malam. Kalau belum terpenuhi: tidak ada booking.
- `buat_pdf.py` menghitung otomatis: jumlah lot, nilai beli, biaya beli, sisa modal, **rugi rupiah kalau stop kena**, dan lot per TP.
  Biaya beli 0,15% dan jual 0,25% (asumsi). Field JSON baru: `modal`, `kesimpulan.booking`, `kesimpulan.posisi`, `kesimpulan.stop_harga`, `take_profit[].porsi_persen`.
- **Bagian 4 pertanyaan tetap dihapus** dari PDF. Isinya sudah ada di Kesimpulan dan tabel D. Tabel C ditambah baris "Prospek hold".
- Pembagian halaman: halaman 1 = header, Kesimpulan, A, B. Halaman 2 = C, D, E, Sumber.
- Kalau PDF lama sedang dibuka, skrip menyimpan sebagai `_baru.pdf` dan memberi catatan, bukan error.

**Alasan**
- Capt Juma menganalisa saat market tutup dan entry lewat booking order, tanpa memantau market berjalan.
- Jumlah lot dan rugi dalam rupiah membuat risiko langsung terlihat.

**Tidak berubah**
- Horizon 1 hari–5 minggu, rumus indikator dan ambang pola PL, aturan exit (boleh saat market tutup atau berjalan).

## 2026-11-11 — v1.0 — Pembentukan Juma Stock Analysis
**Berubah**
- Sistem lama (folder "Analisa Saham BEI") disusun ulang menjadi **Juma Stock Analysis**. Asisten bernama **JSA**, pengguna disapa **Capt Juma**.
- Alur analisa dibakukan menjadi **5 bagian, 23 tahap**: A Persiapan & data (1–4), B Teknikal (5–11), C Berita & fundamental (12–13), D Validasi rencana (14–17), E Pola Pantul Lantai (18–23).
- Skill utama baru `juma-stock-analysis` (SKILL.md + 5 file referensi). Skill `pola-pantul-lantai` tetap terpisah.
- Hasil akhir berubah dari file .md menjadi **PDF A4 dua halaman**, margin 1,27 cm, dengan footer
  "Analyzed by Capt. Jumardi AR., SE. MMar. AFNI. MM. - Tanggal Analisa".
- Skrip baru `tools/buat_pdf.py` (JSON → PDF, huruf otomatis 8,5 → 6,5 pt supaya muat 2 halaman) dan `tools/cek_setup.py`.
- Sikap sekarang 4 label berwarna: BUY (hijau), HOLD (kuning), EXIT-STOP (merah), TAKE PROFIT (biru). Sebelumnya EXIT mencakup stop dan target tercapai.
- Tabel per bagian dengan kolom berbeda, termasuk kolom Sinyal (▲▼●), Dampak (+ − 0), dan Hasil PL (LOLOS/GAGAL).
- Struktur folder: `data/harga`, `data/json`, `hasil-analisa/YYYY-MM`, `log-perubahan`, `dokumen`, `tools`.
- Instruksi pindah komputer: `MULAI-DI-KOMPUTER-BARU.md`.
- Analisa lama (.md, 5–11 Nov 2026) diarsipkan di `hasil-analisa/arsip-sebelum-v1/`. Data CSV lama dipindah ke `data/harga/`.

**Alasan**
- Capt Juma ingin sistem yang rapi, mudah direview per bagian, hasil siap cetak, dan mudah dipindah ke komputer lain.

**Tidak berubah**
- Rumus dan ambang `indikator.py` serta `pola_pantul_lantai.py` (hanya contoh path di docstring yang disesuaikan).
- Aturan analisa (bukan penasihat berlisensi, skor bukan probabilitas, wajib stop, tanpa average down otomatis).
