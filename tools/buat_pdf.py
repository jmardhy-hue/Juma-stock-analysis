"""Buat PDF hasil analisa Juma Stock Analysis (A4, margin 1,27 cm, 2 halaman).

Pemakaian:
    python tools/buat_pdf.py data/json/2026-11-11_KOTA.json --eksternal   (PDF eksternal 1 halaman, *_eksternal.pdf)
    python tools/buat_pdf.py data/json/2026-11-11_COIN.json
    python tools/buat_pdf.py tools/contoh/contoh-hasil.json --keluar uji.pdf

Tanpa --keluar, PDF disimpan di hasil-analisa/YYYY-MM/YYYY-MM-DD_<TICKER>.pdf
(YYYY-MM-DD = tanggal_analisa di JSON). File lama dengan nama sama akan ditimpa.

Kode keluar: 0 = berhasil 2 halaman, 2 = lebih dari 2 halaman (ringkas teks lalu ulangi), 1 = error.
Format JSON: lihat .claude/skills/juma-stock-analysis/referensi/format-pdf.md
"""
import io
import json
import os
import re
import sys

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (CondPageBreak, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                    Spacer, Table, TableStyle)
except ImportError:
    print("ERROR: library reportlab belum terpasang. Jalankan: python -m pip install -r requirements.txt")
    sys.exit(1)

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TANDA_TANGAN = "Analyzed by Capt. Jumardi AR., SE. MMar. AFNI. MM."
MARGIN = 1.27 * cm
TINGGI_FOOTER = 0.75 * cm
MAKS_HALAMAN = 2
# Mode PDF eksternal (1 halaman, untuk dibagikan): nama diganti, hanya Kesimpulan, ANSWER, C, dan E bila muat.
EKSTERNAL = False
DENGAN_E = True
MERK = "Juma Stock Analysis"
GANTI_EKSTERNAL = [("Juma Stock Analysis", "J Stock Analysis"), ("JUMA STOCK ANALYSIS", "J STOCK ANALYSIS"),
                   ("Capt. Jumardi AR., SE. MMar. AFNI. MM.", "CJ"), ("Capt Juma", "CJ")]
KETERANGAN_EKSTERNAL = ("Halaman ini adalah halaman hasil saja. Halaman analisa lengkap terdiri dari 2 halaman "
                        "dan tersimpan hanya untuk konsumsi internal.")
UKURAN_MIN_E_EKSTERNAL = 7.0  # kalau bagian E baru muat di bawah ukuran ini, bagian E dibuang
UKURAN_AWAL, UKURAN_MIN, LANGKAH = 8.5, 6.5, 0.25

BULAN = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
         "Agustus", "September", "Oktober", "November", "Desember"]

# Warna sikap: (warna utama, latar muda, warna teks di atas warna utama)
SIKAP = {
    "BUY": ("#1E7B34", "#E7F4EA", "#FFFFFF"),
    "HOLD": ("#E3B505", "#FFF7D6", "#2B2400"),
    "EXIT-STOP": ("#B3261E", "#FCE8E6", "#FFFFFF"),
    "TAKE PROFIT": ("#0B57A4", "#E3EEFB", "#FFFFFF"),
}
NAVY = colors.HexColor("#14213D")
GARIS = colors.HexColor("#C9CED6")
ABU_MUDA = colors.HexColor("#F2F4F7")
MAGENTA = colors.HexColor("#B5179E")
WARNA_SEL = {
    "▲": "#1E7B34", "+": "#1E7B34", "LOLOS": "#1E7B34",
    "▼": "#B3261E", "−": "#B3261E", "-": "#B3261E", "GAGAL": "#B3261E",
    "●": "#6B7280", "0": "#6B7280",
}
# Pengganti karakter kalau font tidak punya glyph-nya
PENGGANTI = {"−": "-", "≥": ">=", "≤": "<=", "→": "->", "←": "<-", "▲": "^", "▼": "v",
             "●": "o", "✓": "v", "✗": "x", "…": "...", "≈": "~", "½": "1/2", "–": "-", "—": "-"}

FONT = {"biasa": "Helvetica", "tebal": "Helvetica-Bold", "glyph": None}


def siapkan_font():
    """Pakai Arial (Windows) atau DejaVu/Liberation (Linux/Mac) supaya simbol seperti − ≥ ▲ tampil."""
    calon = [
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
    ]
    for biasa, tebal in calon:
        if os.path.exists(biasa) and os.path.exists(tebal):
            f = TTFont("JSA", biasa)
            pdfmetrics.registerFont(f)
            pdfmetrics.registerFont(TTFont("JSA-Bold", tebal))
            pdfmetrics.registerFontFamily("JSA", normal="JSA", bold="JSA-Bold", italic="JSA", boldItalic="JSA-Bold")
            FONT.update(biasa="JSA", tebal="JSA-Bold", glyph=set(f.face.charToGlyph.keys()))
            return biasa
    return "Helvetica (bawaan; beberapa simbol diganti teks biasa)"


def aman(teks):
    """Ganti karakter yang tidak ada di font, escape XML, dan ubah **x** jadi tebal."""
    teks = "" if teks is None else str(teks)
    if EKSTERNAL:
        for lama, baru in GANTI_EKSTERNAL:
            teks = teks.replace(lama, baru)
    glyph = FONT["glyph"]
    hasil = []
    for ch in teks:
        ada = ord(ch) < 128 or (glyph is not None and ord(ch) in glyph) or (glyph is None and ord(ch) < 256)
        hasil.append(ch if ada else PENGGANTI.get(ch, "?"))
    teks = "".join(hasil).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", teks).replace("\n", "<br/>")


def tanggal_id(iso):
    try:
        y, m, d = (int(x) for x in str(iso)[:10].split("-"))
        return f"{d} {BULAN[m - 1]} {y}"
    except (ValueError, IndexError):
        return str(iso)


def gaya(ukuran):
    dasar = dict(fontName=FONT["biasa"], fontSize=ukuran, leading=ukuran * 1.22, alignment=TA_LEFT)
    return {
        "sel": ParagraphStyle("sel", **dasar),
        "kepala": ParagraphStyle("kepala", **{**dasar, "fontName": FONT["tebal"], "textColor": colors.white}),
        "judul": ParagraphStyle("judul", **{**dasar, "fontName": FONT["tebal"], "fontSize": ukuran + 2.5,
                                            "leading": (ukuran + 2.5) * 1.2, "textColor": NAVY, "keepWithNext": 1,
                                            "spaceBefore": ukuran * 0.9, "spaceAfter": ukuran * 0.35}),
        "kecil": ParagraphStyle("kecil", **{**dasar, "fontSize": ukuran - 0.8, "leading": (ukuran - 0.8) * 1.2,
                                            "textColor": colors.HexColor("#4B5563")}),
        "teks": ParagraphStyle("teks", **{**dasar, "spaceAfter": ukuran * 0.3}),
    }


def lebar_kolom(kolom, lebar, total):
    if lebar and len(lebar) == len(kolom):
        s = sum(lebar)
        return [total * w / s for w in lebar]
    sempit = {"no": 0.05, "sinyal": 0.07, "dampak": 0.09, "hasil": 0.08, "jenis": 0.09, "tanggal": 0.10}
    tetap = {i: sempit[k.lower()] for i, k in enumerate(kolom) if k.lower() in sempit}
    sisa = (1 - sum(tetap.values())) / max(1, len(kolom) - len(tetap))
    return [total * tetap.get(i, sisa) for i in range(len(kolom))]


def tabel_bagian(bag, g, lebar_total):
    kolom = bag["kolom"]
    data = [[Paragraph(aman(k), g["kepala"]) for k in kolom]]
    gaya_tambahan = []
    for r, baris in enumerate(bag.get("baris", []), start=1):
        baris = list(baris) + [""] * (len(kolom) - len(baris))
        sel = []
        for c, isi in enumerate(baris[:len(kolom)]):
            isi_s = str(isi).strip()
            if isi_s in WARNA_SEL:
                sel.append(Paragraph(f'<font color="{WARNA_SEL[isi_s]}"><b>{aman(isi_s)}</b></font>', g["sel"]))
            else:
                sel.append(Paragraph(aman(isi), g["sel"]))
        if str(baris[0]).strip() in ("—", "-", "–"):
            gaya_tambahan.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#E8ECF3")))
        data.append(sel)
    t = Table(data, colWidths=lebar_kolom(kolom, bag.get("lebar"), lebar_total), repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, GARIS),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ABU_MUDA]),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ] + gaya_tambahan))
    return t


def header(d, g, lebar):
    kiri = Paragraph(
        f'<font size="{g["sel"].fontSize - 0.5}" color="#C9D3E6">{MERK.upper()} · disusun oleh JSA</font><br/>'
        f'<font size="{g["sel"].fontSize + 7}"><b>{aman(d["ticker"])}</b></font>'
        f'<font size="{g["sel"].fontSize + 1.5}">  {aman(d.get("nama_emiten", ""))}</font>',
        ParagraphStyle("hk", parent=g["sel"], textColor=colors.white, leading=g["sel"].fontSize + 9))
    kanan = Paragraph(
        f'Harga terakhir <b>{aman(d.get("harga_terakhir", ""))}</b><br/>'
        f'Data: {aman(tanggal_id(d.get("tanggal_data", "")))} · {aman(d.get("sumber_harga", ""))}<br/>'
        f'{aman(d.get("status_harga", ""))} · <b>UNCALIBRATED</b>',
        ParagraphStyle("hn", parent=g["sel"], textColor=colors.white, alignment=2))
    t = Table([[kiri, kanan]], colWidths=[lebar * 0.58, lebar * 0.42])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                           ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    return [t]


BIAYA_BELI, BIAYA_JUAL = 0.0015, 0.0025   # asumsi, total ~0,4% pulang-pergi
LEMBAR_PER_LOT = 100


def angka(x):
    """1390 -> '1.390', 284.5 -> '284,5'."""
    x = float(x)
    if x == int(x):
        return f"{int(x):,}".replace(",", ".")
    return f"{x:,.1f}".replace(",", "#").replace(".", ",").replace("#", ".")


def rupiah(x):
    return "Rp" + f"{round(x):,}".replace(",", ".")


def persen(x):
    return f"{x * 100:.1f}%".replace(".", ",")


def hitung_modal(modal, k):
    """Hitung lot, nilai, sisa modal, rugi di stop, dan lot per TP. None kalau datanya tidak cukup."""
    try:
        stop = float(k["stop_harga"]) if k.get("stop_harga") not in (None, "") else None
        if k.get("posisi"):
            lot = int(k["posisi"]["lot"])
            harga = float(k["posisi"]["harga_rata"])
            jenis = "posisi"
            nilai = lot * LEMBAR_PER_LOT * harga
            biaya_beli, sisa = nilai * BIAYA_BELI, None
            dasar = float(modal) if modal else nilai + biaya_beli
        elif k.get("booking") and modal:
            harga = float(k["booking"]["harga"])
            modal = float(modal)
            lot = int(modal // (harga * LEMBAR_PER_LOT * (1 + BIAYA_BELI)))
            jenis = "booking"
            nilai = lot * LEMBAR_PER_LOT * harga
            biaya_beli = nilai * BIAYA_BELI
            sisa, dasar = modal - nilai - biaya_beli, modal
        else:
            return None
    except (KeyError, TypeError, ValueError):
        return None
    lembar = lot * LEMBAR_PER_LOT
    rugi = None if stop is None else lembar * (harga - stop) + biaya_beli + lembar * stop * BIAYA_JUAL
    lot_tp, terpakai = [], 0
    tp = k.get("take_profit", [])
    for i, x in enumerate(tp):
        if x.get("porsi_persen") is not None:
            n = int(lot * float(x["porsi_persen"]) / 100)
        elif i == len(tp) - 1 and str(x.get("porsi", "")).lower().startswith("sisa"):
            n = lot - terpakai
        else:
            lot_tp.append(None)
            continue
        terpakai += n
        lot_tp.append(n)
    return {"jenis": jenis, "harga": harga, "lot": lot, "nilai": nilai, "biaya_beli": biaya_beli,
            "sisa": sisa, "dasar": dasar, "rugi_stop": rugi, "lot_tp": lot_tp}


def kotak_kesimpulan(k, modal, g, lebar):
    sikap = str(k.get("sikap", "")).upper().strip()
    utama, latar, teks_utama = SIKAP.get(sikap, ("#6B7280", "#F2F4F7", "#FFFFFF"))
    utama_c, latar_c = colors.HexColor(utama), colors.HexColor(latar)
    s = g["sel"]
    besar = ParagraphStyle("sk", parent=s, fontName=FONT["tebal"], fontSize=s.fontSize + 4,
                           leading=(s.fontSize + 4) * 1.2, textColor=colors.HexColor(teks_utama))
    label = ParagraphStyle("lb", parent=s, fontName=FONT["tebal"])
    judul = f'KESIMPULAN · SIKAP: {aman(sikap)}'
    if k.get("judul_sikap"):
        judul += f' — {aman(k["judul_sikap"])}'

    m = hitung_modal(modal, k)
    tp = k.get("take_profit", [])
    tp_baris = []
    for x, lot_tp in zip(tp, m["lot_tp"] if m else [None] * len(tp)):
        teks = f'<b>{aman(x.get("level", ""))}</b> {aman(x.get("harga", ""))} ({aman(x.get("persen", ""))})'
        if lot_tp is not None:
            teks += f' · <b>{lot_tp} lot</b>'
        elif x.get("porsi"):
            teks += f' · {aman(x["porsi"])}'
        tp_baris.append(teks)
    tp_teks = "<br/>".join(tp_baris) or "—"

    if m and m["jenis"] == "booking":
        entry_teks = (f'<b>Booking {angka(m["harga"])} · {m["lot"]} lot</b> = {rupiah(m["nilai"])}<br/>'
                      f'Biaya beli ~{rupiah(m["biaya_beli"])} · sisa modal {rupiah(m["sisa"])}')
    elif m and m["jenis"] == "posisi":
        entry_teks = f'<b>Posisi {m["lot"]} lot @{angka(m["harga"])}</b> = {rupiah(m["nilai"])}'
    elif k.get("booking") is None and not k.get("posisi"):
        entry_teks = "<b>Tidak ada booking</b>"
    else:
        entry_teks = "<b>Lot belum dihitung</b> (modal atau harga tidak ada)"
    if k.get("entry"):
        entry_teks += "<br/>" + aman(k["entry"])
    if (k.get("booking") or {}).get("batal_jika"):
        entry_teks += "<br/><b>Batal booking kalau:</b> " + aman(k["booking"]["batal_jika"])

    stop_teks = aman(k.get("stop", "—"))
    if m and m.get("rugi_stop") is not None:
        r = m["rugi_stop"]
        if r >= 0:
            stop_teks += f'<br/><b>Rugi kalau stop kena ≈ {rupiah(r)}</b> ({persen(r / m["dasar"])} modal)'
        else:
            stop_teks += f'<br/><b>Stop di atas harga beli: tetap untung ≈ {rupiah(-r)}</b>'

    lk = lebar - 2
    baris = [
        [Paragraph(judul, besar), "", ""],
        [Paragraph(aman(k.get("ringkasan", "")), s), "", ""],
        [Paragraph("<b>Entry</b><br/>" + entry_teks, s),
         Paragraph("<b>Exit rugi (stop)</b><br/>" + stop_teks, s),
         Paragraph("<b>Exit untung</b><br/>" + tp_teks, s)],
        [Paragraph("<b>Pola Pantul Lantai (PL):</b> " + aman(k.get("pl", "—")), s), "", ""],
        [Paragraph("<b>Yang mengubah sikap:</b> " + aman(k.get("pemicu_perubahan", "—")), label), "", ""],
    ]
    t = Table(baris, colWidths=[lk * 0.34, lk * 0.33, lk * 0.33])
    t.setStyle(TableStyle([
        ("SPAN", (0, 0), (-1, 0)), ("SPAN", (0, 1), (-1, 1)), ("SPAN", (0, 3), (-1, 3)), ("SPAN", (0, 4), (-1, 4)),
        ("BACKGROUND", (0, 0), (-1, 0), utama_c),
        ("BACKGROUND", (0, 1), (-1, -1), latar_c),
        ("BOX", (0, 0), (-1, -1), 1.4, utama_c),
        ("LINEBELOW", (0, 1), (-1, 3), 0.4, utama_c),
        ("LINEAFTER", (0, 2), (1, 2), 0.4, utama_c),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 5), ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
    ]))
    return t


def bagian_answer(d, g, lebar):
    """Section ANSWER: judul magenta, jawaban YA di-highlight hijau dan TIDAK merah."""
    jawab = d.get("answer") or []
    if not jawab:
        return []
    s = g["sel"]
    rata = ParagraphStyle("ans_rata", parent=s, fontName=FONT["tebal"], alignment=TA_CENTER, textColor=colors.white)
    judul = Paragraph("ANSWER", ParagraphStyle("ans_judul", parent=g["judul"], textColor=MAGENTA))
    data = [[Paragraph(k, g["kepala"]) for k in ("No", "Pertanyaan", "Jawaban", "Penjelasan")]]
    gaya = []
    for r, a in enumerate(jawab, start=1):
        ya = str(a.get("jawaban", "")).strip().upper()
        data.append([Paragraph(str(r), s),
                     Paragraph("<b>%s</b>" % aman(a.get("pertanyaan", "")), s),
                     Paragraph(aman(ya), rata),
                     Paragraph(aman(a.get("penjelasan", "")), s)])
        warna = "#1E7B34" if ya == "YA" else "#B3261E" if ya == "TIDAK" else "#6B7280"
        gaya.append(("BACKGROUND", (2, r), (2, r), colors.HexColor(warna)))
    t = Table(data, colWidths=[lebar * 0.05, lebar * 0.27, lebar * 0.10, lebar * 0.58], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, GARIS),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ABU_MUDA]),
        ("VALIGN", (2, 1), (2, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ] + gaya))
    return [KeepTogether([judul, t])]


def susun(d, ukuran, lebar):
    g = gaya(ukuran)
    isi = header(d, g, lebar)
    isi += [Spacer(1, ukuran * 0.8), kotak_kesimpulan(d.get("kesimpulan", {}), d.get("modal"), g, lebar)]
    isi += bagian_answer(d, g, lebar)
    nama_bagian = {"A": "Persiapan & data", "B": "Teknikal", "C": "Berita & fundamental",
                   "D": "Validasi rencana Capt Juma", "E": "Pola Pantul Lantai (PL)"}
    for bag in d.get("bagian", []):
        kode = str(bag.get("kode", "")).upper()
        if EKSTERNAL and kode not in (("C", "E") if DENGAN_E else ("C",)):
            continue
        judul = Paragraph(f'{aman(kode)}. {aman(bag.get("judul") or nama_bagian.get(kode, ""))}', g["judul"])
        isi += [CondPageBreak(ukuran * 5.5), judul, tabel_bagian(bag, g, lebar)]
    if d.get("sumber") and not EKSTERNAL:
        isi.append(Paragraph("Sumber", g["judul"]))
        daftar = []
        for i, s in enumerate(d["sumber"], start=1):
            url = str(s.get("url", ""))
            teks = aman(s.get("judul", url))
            if url:
                url_aman = url.replace("&", "&amp;").replace('"', "%22")
                teks = f'<link href="{url_aman}" color="#0B57A4">{teks}</link>'
            daftar.append(f"{i}. {teks}")
        isi.append(Paragraph("<br/>".join(daftar), g["kecil"]))
    isi.append(Spacer(1, ukuran * 0.6))
    isi.append(Paragraph(
        "<b>Catatan:</b> Analisa bersyarat, bukan rekomendasi atau perintah beli/jual. JSA bukan penasihat berlisensi. "
        "Skor dan Oversold Composite bukan probabilitas. Status UNCALIBRATED. Fraksi harga dan batas ARB/ARA perlu "
        "diverifikasi. Biaya pulang-pergi ~0,4% adalah asumsi.", g["kecil"]))
    if EKSTERNAL:
        isi.append(Spacer(1, 3))
        isi.append(Paragraph("<b>Keterangan:</b> " + KETERANGAN_EKSTERNAL, g["kecil"]))
    return isi


def render(d, ukuran, total_halaman, tujuan):
    tgl = tanggal_id(d.get("tanggal_analisa", ""))

    def footer(canvas, doc):
        canvas.saveState()
        lebar_hal, _ = A4
        y = MARGIN
        canvas.setStrokeColor(GARIS)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN, y + TINGGI_FOOTER - 3, lebar_hal - MARGIN, y + TINGGI_FOOTER - 3)
        canvas.setFont(FONT["tebal"], 7.5)
        canvas.setFillColor(NAVY)
        canvas.drawString(MARGIN, y + 9, f"{TANDA_TANGAN} - Tanggal Analisa: {tgl}")
        canvas.setFont(FONT["biasa"], 6.5)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(MARGIN, y + 1, f"{MERK} · {d.get('ticker', '')} · analisa bersyarat, bukan rekomendasi")
        canvas.drawRightString(lebar_hal - MARGIN, y + 9,
                               f"Halaman {doc.page}" + (f" / {total_halaman}" if total_halaman else ""))
        canvas.restoreState()

    doc = SimpleDocTemplate(tujuan, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
                            bottomMargin=MARGIN + TINGGI_FOOTER + 4,
                            title=f"{MERK} - {d.get('ticker', '')} - {d.get('tanggal_analisa', '')}",
                            author=TANDA_TANGAN, subject="Analisa saham BEI", creator="JSA")
    hitung = {"n": 0}

    def tiap_halaman(canvas, doc):
        hitung["n"] = doc.page
        footer(canvas, doc)
    doc.build(susun(d, ukuran, doc.width), onFirstPage=tiap_halaman, onLaterPages=tiap_halaman)
    return hitung["n"]


def periksa(d):
    pesan = []
    for f in ("ticker", "tanggal_analisa", "tanggal_data", "harga_terakhir", "kesimpulan", "bagian"):
        if f not in d:
            pesan.append(f"field '{f}' tidak ada")
    sikap = str(d.get("kesimpulan", {}).get("sikap", "")).upper().strip()
    if sikap not in SIKAP:
        pesan.append(f"sikap '{sikap}' tidak dikenal (pakai: {', '.join(SIKAP)})")
    kode = [str(b.get("kode", "")).upper() for b in d.get("bagian", [])]
    if kode != list("ABCDE"):
        pesan.append(f"urutan bagian {kode}, seharusnya A, B, C, D, E")
    k = d.get("kesimpulan", {})
    if not d.get("modal"):
        pesan.append("modal tidak diisi: lot dan rugi rupiah tidak dihitung")
    if k.get("booking"):
        try:
            if k.get("stop_harga") is not None and float(k["booking"]["harga"]) <= float(k["stop_harga"]):
                pesan.append("harga booking tidak di atas stop_harga")
        except (KeyError, TypeError, ValueError):
            pesan.append("booking.harga atau stop_harga bukan angka")
    if (k.get("booking") or k.get("posisi")) and k.get("stop_harga") is None:
        pesan.append("stop_harga kosong: rugi rupiah tidak dihitung")
    for b in d.get("bagian", []):
        if str(b.get("kode", "")).upper() == "D" and len(b.get("baris", [])) < 10:
            pesan.append(f"bagian D hanya {len(b.get('baris', []))} baris, baris wajib ada 10")
    jawab = d.get("answer") or []
    if len(jawab) < 2:
        pesan.append("section answer harus berisi 2 pertanyaan (peluang profit 5-10% dan jangka panjang)")
    for a in jawab:
        if str(a.get("jawaban", "")).strip().upper() not in ("YA", "TIDAK"):
            pesan.append(f"jawaban answer harus YA atau TIDAK, bukan '{a.get('jawaban', '')}'")
    return pesan


def cari_ukuran(d, mulai, minimum, maks):
    """Turunkan ukuran huruf sampai isi muat dalam `maks` halaman (atau sampai `minimum`)."""
    ukuran = mulai
    while True:
        n = render(d, ukuran, None, io.BytesIO())
        if n <= maks or ukuran - LANGKAH < minimum - 1e-9:
            return ukuran, n
        ukuran -= LANGKAH


def main():
    global EKSTERNAL, DENGAN_E, MERK, TANDA_TANGAN
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    with open(a[0], encoding="utf-8") as f:
        d = json.load(f)
    for p in periksa(d):
        print(f"CATATAN: {p}")
    font = siapkan_font()
    eksternal = "--eksternal" in a
    if eksternal:
        EKSTERNAL, MERK, TANDA_TANGAN = True, "J Stock Analysis", "Analyzed by CJ"

    if "--keluar" in a:
        tujuan = a[a.index("--keluar") + 1]
    else:
        tgl = str(d["tanggal_analisa"])[:10]
        folder = os.path.join(AKAR, "hasil-analisa", tgl[:7])
        tujuan = os.path.join(folder, f"{tgl}_{d['ticker'].upper()}" + ("_eksternal" if eksternal else "") + ".pdf")
    os.makedirs(os.path.dirname(os.path.abspath(tujuan)), exist_ok=True)

    maks = MAKS_HALAMAN
    if eksternal:
        maks = 1
        DENGAN_E = True
        ukuran, n = cari_ukuran(d, UKURAN_AWAL, UKURAN_MIN_E_EKSTERNAL, maks)
        if n > maks:
            DENGAN_E = False
            ukuran, n = cari_ukuran(d, UKURAN_AWAL, UKURAN_MIN, maks)
    else:
        ukuran, n = cari_ukuran(d, UKURAN_AWAL, UKURAN_MIN, maks)
    try:
        render(d, ukuran, n, tujuan)
    except PermissionError:
        cadangan = tujuan[:-4] + "_baru.pdf"
        print(f"CATATAN: {os.path.basename(tujuan)} sedang dibuka di aplikasi lain, jadi tidak bisa ditimpa. "
              f"Disimpan sebagai {os.path.basename(cadangan)}. Tutup PDF lama lalu jalankan ulang kalau ingin nama aslinya.")
        tujuan = cadangan
        render(d, ukuran, n, tujuan)
    print(f"PDF          : {os.path.abspath(tujuan)}")
    print(f"Halaman      : {n} | ukuran huruf {ukuran:g} pt | font {font}")
    if eksternal:
        print("Bagian       : Kesimpulan, ANSWER, C" + (", E" if DENGAN_E else " (E dibuang: tidak muat 1 halaman)"))
    if n > maks:
        print(f"PERINGATAN: lebih dari {maks} halaman walau huruf sudah {UKURAN_MIN} pt. "
              "Ringkas teks di JSON lalu jalankan ulang.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
