# Bagian D — Validasi rencana Capt Juma (tahap 14–17)

## Tahap 14 — Validasi entry dan harga booking
- Bandingkan rentang buy dengan support terdekat, ATR, dan posisi harga terhadap MA.
- Kalau rentang buy sudah usang (harga jauh dari rentang), sebutkan dan usulkan rentang baru.
- Capt Juma entry dengan **booking order sebelum market buka**. Tentukan **satu harga booking terbaik**:
  - Di dalam atau dekat rentang buy, sedekat mungkin ke support yang masih realistis terisi (bukan harga yang hampir pasti tidak tersentuh).
  - Di atas stop, dibulatkan ke fraksi harga BEI.
  - Tidak boleh di atas batas jangan kejar.
- Syarat yang biasanya dipantau intraday (pullback, bertahan di atas X) dicek saat analisa malam. Kalau belum terpenuhi, sikapnya HOLD dan **tidak ada booking**.
- Tulis **"Batal booking kalau …"**: hal yang bisa dicek sebelum pre-opening (berita negatif semalam, event besar, hasil MSCI, UMA).
- Kalau dibuka di bawah support, struktur rusak, **bukan diskon otomatis**. Order limit bisa terisi di harga itu, dan aturan stop langsung berlaku.
- Jumlah lot, nilai beli, dan rugi di stop **dihitung otomatis oleh `buat_pdf.py`** dari modal, harga booking, dan harga stop.
  Biaya beli 0,15% dan jual 0,25% (asumsi). JSA tidak perlu menghitung manual.

## Tahap 15 — Stop / invalidation
- Level stop diambil dari struktur: swing low, support, atau low hari volume besar.
- Tulis basisnya: **close harian** atau **intraday**.
- Tulis cara eksekusinya: **pre-closing hari itu** atau **pre-opening besok**.
- Kalau stop struktural terlalu jauh (R/R jelek), usulkan stop yang lebih rapat beserta alasannya.

## Tahap 16 — Resistance & R/R
- Sebutkan resistance yang berada di antara entry dan tiap target.
- Hitung R/R per target: (target − entry) ÷ (entry − stop), dengan biaya pulang-pergi **sekitar 0,4% (asumsi)**.
- Target yang melewati resistance kuat atau lebih dari ~0,4 ATR untuk target harian diberi catatan.

## Tahap 17 — Entry lagi / HPP
- Level beli ulang hanya dengan **syarat stabilisasi yang jelas** (misalnya ekor bawah, close di atas open, higher low).
- Harus tetap dalam **budget risiko yang sama**. Tidak pernah ada average down otomatis.
- Jawab juga: apakah HPP perlu diturunkan? (Kalau belum punya posisi, jawabannya "tidak relevan".)

## Isi tabel D di PDF (tabel perbandingan)
Kolom: `No | Parameter | Data Capt Juma | Hasil analisa JSA | Catatan`

Baris wajib, urutannya tetap:
1. Harga terakhir
2. Entry
3. Stop / batal
4. Target harian (dengan % dari harga)
5. Target 1 minggu (dengan % dari harga)
6. Target 1 bulan (dengan % dari harga)
7. Entry lagi untuk menurunkan HPP
8. Perlu menurunkan HPP?
9. Status oversold
10. Sikap (BUY / HOLD / EXIT-STOP / TAKE PROFIT)

Kalau Capt Juma tidak memberi suatu nilai, isi kolomnya dengan "—" dan jelaskan asumsinya di kolom Catatan.
Baris 2 (Entry) di kolom Hasil analisa JSA ditulis sebagai harga booking, misalnya "Booking 1.390 (71 lot)", atau "Tidak ada booking".

Bagian 4 pertanyaan tetap sudah dihapus (v1.1). Isinya tertampung di Kesimpulan (entry, stop, TP, pemicu perubahan),
tabel D baris 7–8 (entry lagi/HPP), dan baris "Prospek hold" di tabel C.
