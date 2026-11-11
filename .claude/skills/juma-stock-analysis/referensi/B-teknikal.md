# Bagian B — Teknikal (tahap 5–11)

Semua angka diambil dari output `tools/indikator.py`. Jangan menghitung ulang secara manual.

## Tahap 5 — Tren & MA
- MA5, MA10, MA20 (dan MA50/100 kalau datanya cukup) serta % jarak harga ke tiap MA.
- Harga di bawah semua MA dan urutan MA5 < MA10 < MA20 berarti downtrend.
- Harga di atas MA5 dan MA10 tapi di bawah MA20 berarti pemulihan awal di dalam downtrend.

## Tahap 6 — Momentum
- RSI14: **<30 oversold**, **30–35 mendekati oversold**, >70 jenuh beli. Bandingkan juga dengan RSI beberapa hari sebelumnya.
- MACD: lihat histogram sekarang vs sebelumnya. Histogram naik berarti momentum membaik walau MACD line masih negatif.
- MACD `INSUFFICIENT_HISTORY` kalau data kurang dari 26 bar. Tulis "n/a", jangan ditebak.

## Tahap 7 — Volatilitas
- ATR14 dalam rupiah dan % dari close. ATR adalah satuan jarak untuk target dan stop.
- Bollinger 20: harga di bawah lower band atau %B < 0 berarti ekstrem di bawah.
- Rata-rata TR 5 hari vs ATR14: kalau jauh lebih kecil, volatilitas sedang menyempit.

## Tahap 8 — Volume / flow
- RVOL: volume hari terakhir dibanding median 20 hari. ≥1x berarti partisipasi normal ke atas, <0,7x berarti tipis.
- CMF: positif berarti akumulasi, negatif berarti distribusi.
- MFI14: <20 tekanan jual ekstrem, >80 jenuh beli.
- Cermati: naik dengan volume tipis lebih lemah daripada naik dengan volume besar.

## Tahap 9 — Struktur & support/resistance
- Bar terakhir: O/H/L/C, % perubahan, close location (0 = di low, 1 = di high).
- Swing low dan high 5 hari dan 20 hari.
- Support dan resistance dari high, low, dan close penting (gap, hari volume besar, double bottom).
- Pola ARB/ARA: cek apakah ada hari yang ditutup di batas bawah atau atas. Batas ARB/ARA dan fraksi harga ditulis sebagai asumsi yang perlu diverifikasi.

## Tahap 10 — Status oversold
- RSI14 dan statusnya.
- Oversold Composite (PROXY, skala tetap 0–100). Selalu tulis keterbatasannya: ini intensitas tekanan jual, **bukan peluang rebound**, dan belum dikalibrasi dengan persentil 252 hari.
- Drawdown dari high 20 hari, jarak ke MA20 dalam ATR, serta % jarak ke MA5/10/20 dan ke high 1 bulan.

## Tahap 11 — Jarak target
- Setiap target: % dari harga dan jarak dalam ATR.
- Target harian yang lebih dari ~0,4 ATR atau berada di atas resistance terdekat diberi catatan "ambisius".

## Isi tabel B di PDF
Kolom: `No | Tahap | Indikator | Nilai | Arti | Sinyal`
- Kolom **Sinyal** diisi salah satu dari: `▲` (positif), `▼` (negatif), `●` (netral). Warnanya otomatis hijau, merah, abu-abu.
- Satu baris per tahap. Tahap yang punya beberapa indikator boleh dipecah menjadi dua baris dengan nomor yang sama, misalnya `6` untuk RSI dan `6` untuk MACD.
- Baris tahap 9 juga mencantumkan level support dan resistance utama.
