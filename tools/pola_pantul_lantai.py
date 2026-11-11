"""Deteksi pola PANTUL LANTAI (PL) pada CSV harian BEI.

Pola: saham oversold setelah turun tajam, dasarnya (lantai) bertahan, lalu hari sinyal
ditutup naik. Entry dilakukan di pullback/pembukaan turun ke dekat lantai, dengan target
harian DEKAT (high hari sinyal s/d +0,3 ATR), bukan target jauh.

Pemakaian:
    python tools/pola_pantul_lantai.py data/harga/ISAT.csv                     # bar terakhir = hari sinyal
    python tools/pola_pantul_lantai.py data/harga/ISAT.csv --tanggal 2026-11-05 # uji mundur di tanggal itu

Kalau ada bar sesudah --tanggal, skrip juga menampilkan hasil hari berikutnya
(apakah target harian tersentuh, apakah stop tersentuh).

Status: UNCALIBRATED. Skor adalah jumlah syarat yang terpenuhi, BUKAN probabilitas.
"""
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indikator import load, wilder  # noqa: E402

TOL_LANTAI = 0.015   # low hari sinyal boleh di bawah lantai lama maks 1,5%
RSI_MAKS = 35.0
JARAK_MA20_ATR = -1.5
CLV_MIN = 0.35
RVOL_MIN = 0.7
ZONA_ATR = 0.35      # zona entry: close - 0,35 ATR s/d close
KEJAR_ATR = 0.10     # di atas close + 0,1 ATR = jangan kejar
TARGET_ATR = 0.30


def rsi_at(C, i):
    g = [max(C[k] - C[k - 1], 0) for k in range(1, i + 1)]
    l = [max(C[k - 1] - C[k], 0) for k in range(1, i + 1)]
    ag, al = wilder(g, 14), wilder(l, 14)
    return 100 - 100 / (1 + ag / al) if al else 100.0


def atr_at(H, L, C, i):
    tr = [H[0] - L[0]] + [max(H[k] - L[k], abs(H[k] - C[k - 1]), abs(L[k] - C[k - 1])) for k in range(1, i + 1)]
    return wilder(tr, 14)


def macd_hist(C, i):
    def ema(vals, k):
        m, out = 2 / (k + 1), [vals[0]]
        for v in vals[1:]:
            out.append(v * m + out[-1] * (1 - m))
        return out
    c = C[: i + 1]
    macd = [x - y for x, y in zip(ema(c, 12), ema(c, 26))]
    sig = ema(macd, 9)
    return macd[-1] - sig[-1], macd[-2] - sig[-2]


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    D, O, H, L, C, V = load(a[0])
    i = D.index(a[a.index("--tanggal") + 1]) if "--tanggal" in a else len(C) - 1
    if i < 20:
        print("INSUFFICIENT_HISTORY: butuh >=21 bar sampai hari sinyal")
        return

    rsi, rsi_prev = rsi_at(C, i), rsi_at(C, i - 1)
    atr = atr_at(H, L, C, i)
    ma20 = st.mean(C[i - 19: i + 1])
    jarak = (C[i] - ma20) / atr
    lantai = min(L[i - 5: i])           # low 5 hari sebelum hari sinyal
    clv = (C[i] - L[i]) / (H[i] - L[i]) if H[i] > L[i] else 0.5
    rvol = V[i] / st.median(V[i - 20: i])
    naik = C[i] > C[i - 1]
    if i >= 26:
        h, hp = macd_hist(C, i)
        mom_ok, mom_txt = h > hp, f"MACD hist {hp:+.1f} -> {h:+.1f}"
    else:
        mom_ok, mom_txt = rsi > rsi_prev, f"RSI {rsi_prev:.1f} -> {rsi:.1f} (MACD n/a)"

    syarat = [
        ("W", "Konteks oversold", rsi < RSI_MAKS and jarak <= JARAK_MA20_ATR,
         f"RSI {rsi:.1f}, jarak MA20 {jarak:+.2f} ATR"),
        ("W", "Lantai bertahan", L[i] >= lantai * (1 - TOL_LANTAI),
         f"low {L[i]:g} vs lantai 5h {lantai:g}"),
        ("W", "Hari sinyal naik", naik, f"chg {C[i] / C[i - 1] - 1:+.2%}"),
        ("P", "Tidak ditutup di low", clv >= CLV_MIN, f"close location {clv:.2f}"),
        ("P", "Volume ikut di hari naik", naik and rvol >= RVOL_MIN, f"RVOL {rvol:.2f}x"),
        ("P", "Momentum membaik", mom_ok, mom_txt),
    ]
    wajib_ok = all(ok for t, _, ok, _ in syarat if t == "W")
    skor = sum(ok for *_, ok, _ in syarat)

    print(f"PANTUL LANTAI | {os.path.basename(a[0])} | hari sinyal {D[i]} | close {C[i]:g} | ATR {atr:.1f}")
    for t, nama, ok, info in syarat:
        print(f"  [{'x' if ok else ' '}] {'WAJIB ' if t == 'W' else 'PENDUK'} {nama:<26} {info}")
    if wajib_ok and skor == 6:
        status = "AKTIF (6/6)"
    elif wajib_ok and skor >= 4:
        status = f"KANDIDAT ({skor}/6) - entry kecil atau tunggu syarat yang kurang"
    else:
        status = f"TIDAK ADA POLA ({skor}/6{', syarat wajib gagal' if not wajib_ok else ''})"
    print(f"Status       : {status}")

    z_lo, z_hi = C[i] - ZONA_ATR * atr, C[i]
    kejar = C[i] + KEJAR_ATR * atr
    t_lo, t_hi = sorted((H[i], C[i] + TARGET_ATR * atr))
    stop = min(L[i - 2: i + 1])          # swing low terdekat: low hari sinyal & 2 hari sebelumnya
    z_lo = max(z_lo, stop)
    e_mid = (z_lo + z_hi) / 2
    rr = f"{(t_lo - e_mid) / (e_mid - stop):.2f}" if e_mid > stop else "n/a"
    if wajib_ok:
        print(f"Zona entry   : {z_lo:.0f} - {z_hi:.0f} (pullback/pembukaan turun). Jangan kejar > {kejar:.0f}")
        print(f"Target harian: {t_lo:.0f} - {t_hi:.0f} (high hari sinyal s/d +{TARGET_ATR} ATR)")
        print(f"Stop/batal   : close < {stop:g} (swing low terdekat). R/R kasar dari {e_mid:.0f} ke {t_lo:.0f}: {rr}")
        print("Catatan      : bulatkan ke fraksi harga BEI; biaya ~0,4% pulang-pergi (asumsi).")
    else:
        print("Rencana PL   : tidak dibuat karena syarat wajib gagal. Pakai analisa standar.")

    if i + 1 < len(C):
        j = i + 1
        kena_t = H[j] >= t_lo
        isi = L[j] <= z_hi
        print(f"Hari berikut : {D[j]} O{O[j]:g} H{H[j]:g} L{L[j]:g} C{C[j]:g} | "
              f"zona entry {'terisi' if isi else 'tidak terisi'} | "
              f"target {'TERSENTUH' if kena_t else 'belum'} | "
              f"stop close {'KENA' if C[j] < stop else 'aman'}")


if __name__ == "__main__":
    main()
