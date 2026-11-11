---
name: pola-pantul-lantai
description: Deteksi dan rencana trading pola PANTUL LANTAI (PL) untuk saham BEI, yaitu rebound jangka pendek dari saham oversold yang dasarnya bertahan, dengan entry di pullback dan target harian dekat. Ini bagian E (tahap 18–23) dari Juma Stock Analysis. Pakai setiap kali menganalisa saham harian (Kesimpulan wajib menyebut status PL), atau saat Capt Juma menyebut "pantul lantai", "pola PL", "pola ISAT/RAJA", atau bertanya apakah saham layak untuk bounce harian.
---

# Pola PANTUL LANTAI (PL)

## Asal pola
Diambil dari dua kasus yang berhasil pada 6 Nov 2026, dibandingkan dengan satu kasus yang gagal:
- **ISAT** (sinyal 5 Nov, close 1.405): pada 6 Nov dibuka turun 1.360, lalu naik ke high 1.430. Target harian tersentuh.
- **RAJA** (sinyal 5 Nov, close 386): pada 6 Nov dibuka 368 dan low tepat di lantai 360, lalu naik ke high 396. Target tersentuh.
- **EXCL** (pembanding gagal, 5 Nov close 1.510): hari sinyalnya ditutup turun di low dengan volume besar. Lantainya jebol intraday ke 1.410. Target tidak tersentuh.

Intinya: **lantai yang sudah teruji + hari sinyal yang ditutup naik + entry di pembukaan yang turun + target yang dekat.**
Rincian evaluasinya ada di `dokumen/PL_perbandingan_ISAT-RAJA-EXCL.md`.

## Cara pakai
1. Pastikan `data/harga/<TICKER>.csv` sudah diperbarui, dengan bar terakhir = hari sinyal (close terakhir).
2. Jalankan:
   ```
   python tools/pola_pantul_lantai.py data/harga/<TICKER>.csv
   ```
   Untuk uji mundur: tambah `--tanggal YYYY-MM-DD`. Kalau ada bar sesudahnya, skrip juga menampilkan hasil hari berikutnya.
3. Tulis satu baris progres, misalnya `🪃 18–23. Pola PL — 6/6 AKTIF, zona 1.367–1.405, target 1.430–1.437, stop close <1.320`.
4. Isi bagian E di JSON PDF dan field `kesimpulan.pl` (format di bawah).

## Syarat (6 syarat, 3 wajib) = tahap 18–23
| Tahap | # | Jenis | Syarat | Ambang |
|---|---|---|---|---|
| 18 | 1 | Wajib | Konteks oversold | RSI14 < 35 dan close ≤ MA20 − 1,5 ATR |
| 19 | 2 | Wajib | Lantai bertahan | Low hari sinyal ≥ low terendah 5 hari sebelumnya − 1,5% (higher low atau double bottom) |
| 20 | 3 | Wajib | Hari sinyal naik | Close > close kemarin |
| 21 | 4 | Pendukung | Tidak ditutup di low | Close location ≥ 0,35 |
| 22 | 5 | Pendukung | Volume ikut di hari naik | RVOL ≥ 0,7x pada hari naik (bukan volume besar saat turun) |
| 23 | 6 | Pendukung | Momentum membaik | MACD hist naik, atau RSI naik kalau MACD n/a |

**Status:**
- **AKTIF**: 6/6.
- **KANDIDAT**: semua syarat wajib terpenuhi dan skor 4–5/6. Porsi kecil, atau tunggu syarat yang kurang.
- **TIDAK ADA POLA**: ada syarat wajib yang gagal, atau skor ≤3. Kembali ke analisa standar.

Skor adalah jumlah syarat yang terpenuhi, **bukan peluang naik**. Status `UNCALIBRATED`: pola ini baru diuji pada beberapa kasus.

## Rencana trading PL
| Item | Aturan |
|---|---|
| Zona entry | Close sinyal − 0,35 ATR s/d close sinyal (tidak lebih rendah dari stop). Isi saat pullback atau pembukaan turun |
| Jangan kejar | Kalau dibuka di atas close sinyal + 0,1 ATR, lewati hari itu |
| Target harian | High hari sinyal s/d close + 0,3 ATR. Harus berada di bawah atau tepat di resistance terdekat |
| Stop/batal | Close di bawah swing low terdekat (low hari sinyal dan 2 hari sebelumnya). Eksekusi di pre-closing hari itu atau pre-opening besok |
| Sisa posisi | Setelah target harian tersentuh: jual sebagian (misalnya ½), sisanya ikuti target mingguan dengan stop dinaikkan ke harga entry |
| Batal sebelum entry | Dibuka ARB atau di bawah stop. Itu tanda struktur rusak, **bukan diskon** |

R/R ke target harian memang kecil (sekitar 0,6–0,8) karena pola ini mengandalkan target dekat. Karena itu, ukuran posisi harus dihitung dari jarak stop, dan sisa posisi yang dibawa ke target mingguan menjadi sumber R/R yang lebih besar.

## Isi di PDF
**Bagian E (tabel):** kolom `No | Syarat PL | Jenis | Ambang | Nilai | Hasil`. Nomor 18–23. Kolom Hasil diisi `LOLOS` atau `GAGAL`.
Baris terakhir (No `—`): status, zona entry, jangan kejar, target harian PL, stop PL. Kalau TIDAK ADA POLA: "jangan pakai rencana PL, ikuti rencana standar".

**Field `kesimpulan.pl`:** satu kalimat padat, misalnya
`AKTIF 6/6 — zona 1.367–1.405, jangan kejar >1.410, target 1.430–1.437, stop close <1.320. Pakai rencana PL untuk target harian.`
atau `TIDAK ADA POLA 2/6 — gagal: hari sinyal turun, lantai jebol. Jangan pakai rencana PL, ikuti rencana standar.`

Kalau rencana PL berbeda dari rencana Capt Juma (misalnya target harian Capt Juma > 0,4 ATR atau di atas resistance), sebutkan perbedaannya secara jelas.

## Batasan
- Hanya berlaku untuk trading 1–5 hari. Pola ini tidak membuktikan dasar jangka panjang.
- Risiko event (MSCI, rilis laporan, UMA/suspensi) bisa membatalkan pola. Cek berita (tahap 12) sebelum memakai rencana PL.
- Fraksi harga dan batas ARB/ARA harus diverifikasi. Bulatkan level ke fraksi yang berlaku.
- Kalau ada kasus PL yang gagal, catat di "Log kasus" di bawah, sesuaikan ambangnya, lalu catat perubahan ambang di `log-perubahan/CHANGELOG.md`.

## Log kasus
| Tanggal sinyal | Saham | Skor | Hasil hari berikutnya |
|---|---|---|---|
| 2026-11-05 | ISAT | 6/6 AKTIF | Zona terisi (low 1.345), high 1.430 → target tersentuh |
| 2026-11-05 | RAJA | 6/6 AKTIF | Zona terisi (low 360), high 396 → target tersentuh |
| 2026-11-05 | EXCL | 2/6 TIDAK ADA | High 1.495, close di bawah lantai 1.500 → gagal (sesuai deteksi) |
| 2026-11-05 | AISA | 5/6 KANDIDAT (uji mundur; RVOL 0,43x gagal) | Zona 88–90 terisi (open 90), high 112 → target 92–93 tersentuh |
