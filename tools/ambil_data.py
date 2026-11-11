"""Ambil data harga harian saham BEI dari stockanalysis.com lalu simpan ke CSV.

Pemakaian:
    python tools/ambil_data.py DSSA
    python tools/ambil_data.py COIN --keluar data/harga/COIN.csv

Hasil: data/harga/<TICKER>.csv dengan header date,open,high,low,close,volume
(volume dalam lembar). Kalau file sudah ada, bar baru digabung tanpa membuat tanggal ganda.
Catatan: halaman ini berisi sekitar 50 bar terakhir. Cloudflare memblokir User-Agent buatan,
jadi skrip memanggil curl (User-Agent bawaan curl). curl ada di Windows 10+, Mac, dan Linux.
Kode keluar: 0 = berhasil, 1 = gagal (jaringan, ticker tidak ditemukan, atau data tidak masuk akal).
"""
import csv
import os
import re
import subprocess
import sys
from datetime import datetime

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://stockanalysis.com/quote/idx/{t}/history/"
MIN_BAR = 26  # MACD butuh 26 bar, pola PL butuh 21 bar


def angka(teks):
    return float(teks.replace(",", "").strip())


def ambil(ticker):
    p = subprocess.run(["curl", "-sS", "-L", "-m", "40", URL.format(t=ticker.upper())],
                       capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if p.returncode != 0:
        raise OSError(p.stderr.strip() or f"curl kode {p.returncode}")
    return p.stdout


def urai(html):
    baris = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S):
        sel = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S)]
        if len(sel) < 8 or sel[0] == "Date":
            continue
        try:
            tgl = datetime.strptime(sel[0], "%b %d, %Y").strftime("%Y-%m-%d")
            baris.append({"date": tgl, "open": angka(sel[1]), "high": angka(sel[2]), "low": angka(sel[3]),
                          "close": angka(sel[4]), "volume": angka(sel[7])})
        except ValueError:
            continue
    return baris


def valid(b):
    return b["high"] >= max(b["open"], b["close"], b["low"]) and b["low"] <= min(b["open"], b["close"], b["high"]) \
        and b["low"] > 0


def fmt(x):
    return str(int(x)) if x == int(x) else str(x)


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    ticker = a[0].upper()
    tujuan = a[a.index("--keluar") + 1] if "--keluar" in a else os.path.join(AKAR, "data", "harga", ticker + ".csv")
    try:
        baru = urai(ambil(ticker))
    except (OSError, FileNotFoundError) as e:
        print(f"GAGAL: tidak bisa mengambil {ticker} ({e}). Cek apakah stockanalysis.com diizinkan di jaringan.")
        return 1
    if not baru:
        print(f"GAGAL: tabel harga {ticker} tidak ditemukan (ticker salah atau format halaman berubah).")
        return 1
    rusak = [b["date"] for b in baru if not valid(b)]
    if rusak:
        print("GAGAL: bar tidak masuk akal (high/low terbalik), tanggal: " + ", ".join(rusak))
        return 1
    data = {}
    if os.path.exists(tujuan):
        with open(tujuan, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                data[r["date"]] = {k: (r[k] if k == "date" else float(r[k])) for k in
                                   ("date", "open", "high", "low", "close", "volume")}
    lama = len(data)
    for b in baru:
        data[b["date"]] = b
    urut = [data[k] for k in sorted(data)]
    os.makedirs(os.path.dirname(os.path.abspath(tujuan)), exist_ok=True)
    with open(tujuan, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["date", "open", "high", "low", "close", "volume"])
        for b in urut:
            w.writerow([b["date"], fmt(b["open"]), fmt(b["high"]), fmt(b["low"]), fmt(b["close"]), fmt(b["volume"])])
    t = urut[-1]
    print(f"Ticker       : {ticker} | sumber stockanalysis.com | {len(urut)} bar ({len(urut) - lama} baru)")
    print(f"Rentang      : {urut[0]['date']} s/d {t['date']}")
    print(f"Bar terakhir : O{fmt(t['open'])} H{fmt(t['high'])} L{fmt(t['low'])} C{fmt(t['close'])} vol {fmt(t['volume'])}")
    print(f"File         : {os.path.abspath(tujuan)}")
    if len(urut) < MIN_BAR:
        print(f"PERINGATAN: baru {len(urut)} bar, butuh minimal {MIN_BAR} untuk MACD.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
