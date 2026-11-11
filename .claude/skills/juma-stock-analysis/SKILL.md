---
name: juma-stock-analysis
description: Alur analisa saham BEI harian Juma Stock Analysis (JSA) untuk trading 1 hari sampai 5 minggu, dari data harga sampai PDF A4 dua halaman. Pakai setiap kali Capt Juma mengirim ticker beserta harga, rentang buy, dan target (misalnya "COIN, harga trkhr 256, bs buy 254-258, target harian ..."), atau minta analisa ulang, cek saham, atau buat ulang PDF hasil analisa.
---

# Juma Stock Analysis — alur 5 bagian, 23 tahap

Semua path di bawah relatif terhadap akar folder **Juma Stock Analysis**.
Setiap tahap ditulis sebagai **satu baris progres** di chat: emoji, nomor, nama tahap, lalu hasilnya. Contoh:

```
🔎 2. Data harga — Investing.com, 23 bar, close 10 Nov = 292 ✅
📈 5. Tren & MA — MA5/10/20 = 280/289/362 → harga di atas MA5–10, masih −19% dari MA20
```

Bagian yang ringkas boleh digabung menjadi satu baris (misalnya tahap 18–23 menjadi satu baris PL).

## Bagian A — Persiapan & data (tahap 1–4)
Baca `referensi/A-data.md`.
| No | Tahap | Inti |
|---|---|---|
| 1 | Baca input | Ticker, harga, rentang buy, target harian, mingguan, bulanan. Yang kurang dicatat sebagai asumsi |
| 2 | Ambil data harga | `python tools/ambil_data.py <TICKER>` (stockanalysis.com, langsung jadi CSV). Cadangan: CSV yang dikirim Capt Juma |
| 3 | Cek CSV | `data/harga/<TICKER>.csv` dibuat skrip. Bandingkan close terakhir dengan harga dari Capt Juma, tulis selisihnya |
| 4 | Jalankan indikator | `python tools/indikator.py data/harga/<TICKER>.csv --harga <harga> --target <t1,t2,...>` |

## Bagian B — Teknikal (tahap 5–11)
Baca `referensi/B-teknikal.md`.
| No | Tahap | Inti |
|---|---|---|
| 5 | Tren & MA | MA5/10/20 dan % jarak harga |
| 6 | Momentum | RSI14, MACD |
| 7 | Volatilitas | ATR14, Bollinger, %B |
| 8 | Volume / flow | RVOL, CMF, MFI |
| 9 | Struktur & S/R | Bar terakhir, swing 5 dan 20 hari, support/resistance, tanda ARB/ARA |
| 10 | Status oversold | RSI, Oversold Composite (proxy), drawdown, jarak MA20 dalam ATR |
| 11 | Jarak target | % dan ATR ke tiap target |

## Bagian C — Berita & fundamental (tahap 12–13)
Baca `referensi/C-berita-fundamental.md`.
| No | Tahap | Inti |
|---|---|---|
| 12 | Berita & katalis | 1–4 minggu terakhir, aksi korporasi, UMA/suspensi/papan pemantauan khusus, sektor, event |
| 13 | Fundamental singkat | Laporan terakhir, QoQ/YoY, market cap, valuasi kasar, utang |

## Bagian D — Validasi rencana (tahap 14–17)
Baca `referensi/D-validasi.md`.
| No | Tahap | Inti |
|---|---|---|
| 14 | Validasi entry | Rentang buy vs support, ATR, aturan jangan kejar |
| 15 | Stop / invalidation | Level, basis (close/intraday), cara eksekusi |
| 16 | Resistance & R/R | Resistance yang menghadang, R/R dengan biaya 0,4% (asumsi) |
| 17 | Entry lagi / HPP | Level beli ulang hanya dengan syarat stabilisasi, budget risiko sama |

## Bagian E — Pola Pantul Lantai (tahap 18–23)
Ikuti skill `pola-pantul-lantai` dan jalankan `python tools/pola_pantul_lantai.py data/harga/<TICKER>.csv`.
Tahap 18–23 adalah syarat PL 1–6 (3 wajib, 3 pendukung).

## Output: PDF A4 dua halaman
Baca `referensi/format-pdf.md`, lalu:
1. Tulis `data/json/YYYY-MM-DD_<TICKER>.json` (tanggal = tanggal analisa). Contoh lengkapnya ada di `tools/contoh/contoh-hasil.json`. Isi juga `answer` (2 pertanyaan tetap, jawaban YA atau TIDAK, lihat `referensi/format-pdf.md`).
2. Jalankan `python tools/buat_pdf.py data/json/YYYY-MM-DD_<TICKER>.json`.
   PDF tersimpan di `hasil-analisa/YYYY-MM/YYYY-MM-DD_<TICKER>.pdf`.
3. Kalau skrip memberi `PERINGATAN: lebih dari 2 halaman` (exit code 2), ringkas teks di JSON (bukan menghapus baris wajib), lalu jalankan ulang.
4. Kirim PDF ke Capt Juma dengan tool kirim file. **Jangan menjelaskan hasil di chat** (tanpa ringkasan): cukup baris progres tahap dan file PDF-nya.

Entry selalu ditulis sebagai **satu harga booking terbaik** sebelum market buka (lihat `CLAUDE.md`, bagian "Cara entry dan exit").
Jumlah lot dan rugi rupiah dihitung otomatis oleh `buat_pdf.py` dari `modal`, `kesimpulan.booking.harga`, dan `kesimpulan.stop_harga`.

Tidak ada file .md hasil. JSON di `data/json/` adalah bahan kerja untuk membuat ulang PDF.

## Aturan sikap (wajib ada di Kesimpulan)
`BUY` (hijau) · `HOLD` (kuning) · `EXIT-STOP` (merah) · `TAKE PROFIT` (biru). Arti lengkapnya ada di `CLAUDE.md`.
Sikap adalah analisa bersyarat, bukan perintah. Selalu tulis apa yang akan mengubah sikap tersebut.
