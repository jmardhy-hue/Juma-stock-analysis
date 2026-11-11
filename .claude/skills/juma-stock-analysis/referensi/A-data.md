# Bagian A — Persiapan & data (tahap 1–4)

## Tahap 1 — Baca input
Ambil dari pesan Capt Juma: ticker, harga terakhir, rentang buy, target harian, target 1 minggu, target 1 bulan, dan **modal** (total dana untuk saham itu).
Yang sering tidak ada dan harus dicatat sebagai **asumsi**:
- Sudah punya posisi atau belum (default: belum punya posisi). Kalau sudah, formatnya misalnya `posisi 70 lot @1360`.
- Harga rata-rata (HPP) kalau sudah punya posisi.
- Stop yang dipakai Capt Juma.
- Modal, kalau tidak disebut. Tanpa modal, Kesimpulan tetap ditulis tapi tanpa jumlah lot dan rugi rupiah.
- Asal harga (close kemarin, pra-pembukaan, atau live).

Jangan berhenti untuk bertanya. Catat asumsinya, lalu lanjut.

## Tahap 2 — Ambil data harga
- Cara utama (otomatis): `python tools/ambil_data.py <TICKER>`. Skrip mengambil ~50 bar dari stockanalysis.com lewat curl, menggabungkan dengan CSV lama, dan langsung menyimpan `data/harga/<TICKER>.csv`.
- Investing.com tidak dipakai lagi: memblokir akses otomatis (403).
- Butuh **minimal 26 bar** supaya MACD terhitung, dan **minimal 21 bar** untuk pola PL. Kalau halaman hanya memberi sedikit bar, gabungkan dengan CSV lama di `data/harga/`.
- Kalau Investing.com gagal, coba sumber lain dan sebutkan sumbernya di PDF.

## Tahap 3 — Simpan CSV
- File: `data/harga/<TICKER>.csv`
- Header wajib: `date,open,high,low,close,volume`
- Tanggal format `YYYY-MM-DD`. Volume dalam **lembar** (bukan lot, bukan juta).
- Kalau file sudah ada, perbarui dengan bar baru tanpa membuat tanggal ganda.
- Bandingkan close terakhir dengan harga dari Capt Juma. Kalau berbeda, tulis keduanya di tabel A. Jangan memilih satu angka diam-diam.
- Kalau harga dari Capt Juma adalah harga pra-pembukaan atau belum dicek live, tandai **"belum terkonfirmasi live"**.

## Tahap 4 — Jalankan indikator
```
python tools/indikator.py data/harga/<TICKER>.csv --harga <harga> --target <t1,t2,...>
```
Masukkan semua batas bawah dan atas target ke `--target`. Output skrip adalah sumber angka untuk bagian B.

## Isi tabel A di PDF
Kolom: `No | Tahap | Hasil | Keterangan`
| No | Tahap | Contoh Hasil | Contoh Keterangan |
|---|---|---|---|
| 1 | Input Capt Juma | Harga 292, buy 280–286, target harian 298–303 | Asumsi: belum punya posisi |
| 2 | Data harga | 26 bar, 6 Okt – 10 Nov 2026 | Investing.com |
| 3 | Kecocokan harga | Close 10 Nov = 292, sama dengan input | Belum terkonfirmasi live |
| 4 | Indikator | indikator.py berhasil | MACD tersedia (≥26 bar) |
