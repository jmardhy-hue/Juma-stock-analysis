# Juma Stock Analysis

Sistem analisa saham BEI milik **Capt Juma**, dijalankan oleh **JSA** (Claude Code).
Fokus: trading jangka pendek, 1 hari sampai 5 minggu.

## Cara pakai harian
Buka Claude Code di folder ini, lalu kirim satu saham per chat:
```
COIN, harga trkhr 292, bs buy 280 - 286, target harian 298 - 303, target seminggu 310 - 320, target sebulan 330 - 340
```
JSA menjalankan 23 tahap analisa, menampilkan progres singkat di chat, lalu membuat
**PDF A4 dua halaman** di `hasil-analisa/YYYY-MM/YYYY-MM-DD_TICKER.pdf`.

## Alur 5 bagian, 23 tahap
| Bagian | Tahap | Isi |
|---|---|---|
| A. Persiapan & data | 1–4 | Baca input, ambil data harga, simpan CSV, jalankan indikator |
| B. Teknikal | 5–11 | Tren/MA, momentum, volatilitas, volume, struktur S/R, oversold, jarak target |
| C. Berita & fundamental | 12–13 | Katalis 1–4 minggu, laporan keuangan |
| D. Validasi rencana | 14–17 | Entry, stop, R/R, entry lagi/HPP |
| E. Pola Pantul Lantai | 18–23 | 6 syarat PL (3 wajib, 3 pendukung) |

## Isi folder
| Folder / file | Isi |
|---|---|
| `CLAUDE.md` | Identitas JSA, aturan analisa, peta folder |
| `MULAI-DI-KOMPUTER-BARU.md` | Langkah setup setelah folder dipindah |
| `.claude/skills/juma-stock-analysis/` | Skill utama + 5 file referensi |
| `.claude/skills/pola-pantul-lantai/` | Skill pola PL |
| `tools/` | `indikator.py`, `pola_pantul_lantai.py`, `buat_pdf.py`, `cek_setup.py`, folder `contoh/` |
| `data/harga/` | CSV harga harian |
| `data/json/` | Bahan PDF (untuk membuat ulang PDF) |
| `hasil-analisa/` | PDF hasil, per bulan |
| `log-perubahan/` | `CHANGELOG.md`, catatan perubahan sistem |
| `dokumen/` | Blueprint BEI-APTS dan dokumen acuan pola PL |

## Pindah komputer
Salin seluruh folder ini, buka di Claude Code, lalu ketik:
`JSA, pelajari folder ini dan jalankan MULAI-DI-KOMPUTER-BARU.md`

---
Analisa bersyarat, bukan rekomendasi atau perintah beli/jual.
