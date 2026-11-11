# Format PDF — Juma Stock Analysis

## Spesifikasi tetap
- Kertas **A4 portrait**, margin keliling **1,27 cm**, **2 halaman** per hasil.
- Halaman 1: header, **kotak Kesimpulan berwarna** (termasuk harga booking, jumlah lot, rugi rupiah), bagian A, B.
- Halaman 2: bagian C, D (tabel perbandingan), E (PL), sumber. Bagian 4 pertanyaan sudah dihapus (v1.1).
- Footer setiap halaman:
  `Analyzed by Capt. Jumardi AR., SE. MMar. AFNI. MM. - Tanggal Analisa: <tanggal>` dan nomor halaman.
- Ukuran huruf otomatis 8,5 pt dan mengecil sampai minimal 6,5 pt supaya muat 2 halaman.
  Kalau tetap lebih dari 2 halaman, skrip keluar dengan kode 2 dan menulis `PERINGATAN`. Ringkas teksnya, lalu jalankan ulang.
- Nama file: `hasil-analisa/YYYY-MM/YYYY-MM-DD_<TICKER>.pdf`. Analisa ulang di hari yang sama akan menimpa file lama.

## Warna sikap
| Sikap | Warna |
|---|---|
| `BUY` | Hijau |
| `HOLD` | Kuning (teks gelap supaya terbaca) |
| `EXIT-STOP` | Merah |
| `TAKE PROFIT` | Biru |

Label sikap selalu ditulis sebagai teks juga, jadi tetap terbaca kalau PDF dicetak hitam-putih.

## Bahan PDF: file JSON
Simpan di `data/json/YYYY-MM-DD_<TICKER>.json`. Contoh lengkap dan valid: `tools/contoh/contoh-hasil.json`.

```json
{
  "ticker": "COIN",
  "nama_emiten": "Indokripto Koin Semesta Tbk",
  "tanggal_analisa": "2026-11-11",
  "tanggal_data": "2026-11-10",
  "harga_terakhir": "292",
  "sumber_harga": "Investing.com",
  "status_harga": "belum terkonfirmasi live",
  "input_capt_juma": "COIN, harga trkhr 292, bs buy 280-286, ...",
  "asumsi": ["Belum punya posisi", "Biaya beli 0,15% dan jual 0,25%"],
  "modal": 10000000,
  "kesimpulan": {
    "sikap": "BUY",
    "judul_sikap": "Booking sebelum market buka",
    "ringkasan": "2–3 kalimat.",
    "booking": {"harga": 284, "batal_jika": "ada berita negatif semalam atau UMA"},
    "posisi": null,
    "entry": "Alasan harga booking, 1 kalimat",
    "stop_harga": 276,
    "stop": "Close harian <276, eksekusi pre-closing hari itu atau pre-opening besok",
    "take_profit": [
      {"level": "TP1", "harga": "298", "persen": "+4,9%", "porsi_persen": 50},
      {"level": "TP2", "harga": "310", "persen": "+9,2%", "porsi_persen": 25},
      {"level": "TP3", "harga": "330", "persen": "+16,2%", "porsi": "sisa"}
    ],
    "pl": "KANDIDAT 5/6 — gagal: volume (RVOL 0,47x). Zona 279–292, jangan kejar >296, target 298–303, stop close <256",
    "pemicu_perubahan": "Jadi BUY kalau ...; jadi EXIT-STOP kalau close <276."
  },
  "bagian": [
    {
      "kode": "A",
      "judul": "Persiapan & data",
      "kolom": ["No", "Tahap", "Hasil", "Keterangan"],
      "lebar": [0.05, 0.17, 0.48, 0.30],
      "baris": [["1", "Input Capt Juma", "…", "…"]]
    }
  ],
  "sumber": [
    {"judul": "Investing.com – data historis COIN", "url": "https://..."}
  ]
}
```

### Aturan isi
- `sikap` hanya boleh: `BUY`, `HOLD`, `EXIT-STOP`, `TAKE PROFIT`.
- `bagian` berisi 5 objek dengan kode `A`, `B`, `C`, `D`, `E` sesuai urutan. Bagian C otomatis mulai di halaman 2.

### Booking, lot, dan rugi rupiah (dihitung skrip)
- `modal`: angka rupiah tanpa titik (misalnya `10000000`). Total dana untuk saham ini.
- `kesimpulan.booking`: `{"harga": <angka>, "batal_jika": "<teks>"}` untuk **satu harga booking terbaik**.
  Isi `null` kalau tidak ada booking (misalnya HOLD tanpa posisi, atau EXIT-STOP).
- `kesimpulan.posisi`: `{"lot": <angka>, "harga_rata": <angka>}` kalau Capt Juma sudah punya posisi, selain itu `null`.
- `kesimpulan.stop_harga`: angka level stop. `kesimpulan.stop` tetap berisi teks basis dan cara eksekusi.
- `take_profit[].porsi_persen`: persen dari total lot. TP terakhir boleh `"porsi": "sisa"`.
- Skrip menghitung: lot = modal ÷ (harga booking × 100 × 1,0015), dibulatkan ke bawah; nilai beli; sisa modal;
  rugi kalau stop kena = selisih harga × lembar + biaya beli 0,15% + biaya jual 0,25% (asumsi); dan lot per TP.
  Dasar lot adalah `posisi` kalau ada, selain itu hasil booking.
- `lebar` opsional (proporsi kolom, jumlahnya 1). Kalau tidak diisi, skrip membagi lebar sendiri.
- Teks boleh memakai `**tebal**`.
- Sel yang isinya persis salah satu nilai berikut diberi warna otomatis:
  - `▲` hijau, `▼` merah, `●` abu-abu (kolom Sinyal di B)
  - `+` hijau, `−` merah, `0` abu-abu (kolom Dampak di C)
  - `LOLOS` hijau, `GAGAL` merah (kolom Hasil di E)
- Teks harus ringkas: satu sel idealnya di bawah 25 kata.

### Kolom per bagian
| Bagian | Kolom |
|---|---|
| A | No · Tahap · Hasil · Keterangan |
| B | No · Tahap · Indikator · Nilai · Arti · Sinyal |
| C | No · Tahap · Item · Temuan · Dampak · Tanggal |
| D | No · Parameter · Data Capt Juma · Hasil analisa JSA · Catatan |
| E | No · Syarat PL · Jenis · Ambang · Nilai · Hasil |

Bagian E diakhiri baris ringkasan: status, zona entry, jangan kejar, target harian PL, dan stop PL
(cukup satu baris dengan `No` = `—`).
