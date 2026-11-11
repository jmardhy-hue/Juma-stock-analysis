"""Hitung indikator teknikal BEI-APTS dari CSV harian.

Pemakaian:
    python tools/indikator.py data/harga/COIN.csv [--harga 256] [--target 262,266,270,276,284,290]

Format CSV (header wajib, urutan baris bebas - otomatis diurutkan by date):
    date,open,high,low,close,volume
    2026-11-04,266,266,248,256,13280000
"""
import csv
import statistics as st
import sys


def load(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f)]
    rows.sort(key=lambda r: r["date"])
    k = lambda n: [float(r[n]) for r in rows]
    return [r["date"] for r in rows], k("open"), k("high"), k("low"), k("close"), k("volume")


def wilder(vals, n):
    a = sum(vals[:n]) / n
    for v in vals[n:]:
        a = (a * (n - 1) + v) / n
    return a


def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return
    D, O, H, L, C, V = load(a[0])
    harga = float(a[a.index("--harga") + 1]) if "--harga" in a else C[-1]
    targets = [float(x) for x in a[a.index("--target") + 1].split(",")] if "--target" in a else []
    n = len(C)
    out = {}
    print(f"Data: {n} bar, {D[0]} s/d {D[-1]} | harga referensi {harga:g}")
    if n < 15:
        print("INSUFFICIENT_HISTORY: butuh >=15 bar untuk RSI/ATR")
        return

    g = [max(C[i] - C[i - 1], 0) for i in range(1, n)]
    l = [max(C[i - 1] - C[i], 0) for i in range(1, n)]
    ag, al = wilder(g, 14), wilder(l, 14)
    rsi = 100 - 100 / (1 + ag / al) if al else 100.0
    tr = [H[0] - L[0]] + [max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1])) for i in range(1, n)]
    atr = wilder(tr, 14)
    out["RSI14"] = rsi
    status = "oversold teknikal" if rsi < 30 else "mendekati oversold" if rsi <= 35 else "tidak oversold"
    print(f"RSI14        : {rsi:.1f} ({status})")
    print(f"ATR14        : {atr:.1f} ({atr / C[-1]:.1%} dari close) | rata TR 5 hari {st.mean(tr[-5:]):.1f}")

    for p in (5, 10, 20, 50, 100):
        if n >= p:
            ma = st.mean(C[-p:])
            print(f"MA{p:<3}        : {ma:.1f} (harga {harga / ma - 1:+.1%})")

    w = min(20, n)
    ma20, sd = st.mean(C[-w:]), st.pstdev(C[-w:])
    lo, up = ma20 - 2 * sd, ma20 + 2 * sd
    pb = (harga - lo) / (up - lo) if up > lo else 0.5
    print(f"Bollinger{w}  : lower {lo:.1f} / upper {up:.1f} | %B {pb:.2f}")

    def ema(vals, k):
        m, out_ = 2 / (k + 1), [vals[0]]
        for v in vals[1:]:
            out_.append(v * m + out_[-1] * (1 - m))
        return out_
    if n >= 26:
        macd = [x - y for x, y in zip(ema(C, 12), ema(C, 26))]
        sig = ema(macd, 9)
        print(f"MACD         : {macd[-1]:.2f} signal {sig[-1]:.2f} hist {macd[-1] - sig[-1]:+.2f} (sebelumnya {macd[-2] - sig[-2]:+.2f})")
    else:
        print("MACD         : INSUFFICIENT_HISTORY (<26 bar)")

    tp = [(H[i] + L[i] + C[i]) / 3 for i in range(n)]
    pos = sum(tp[i] * V[i] for i in range(n - 14, n) if tp[i] > tp[i - 1])
    neg = sum(tp[i] * V[i] for i in range(n - 14, n) if tp[i] < tp[i - 1])
    mfi = 100 - 100 / (1 + pos / neg) if neg else 100.0
    clv = [(2 * C[i] - H[i] - L[i]) / (H[i] - L[i]) if H[i] > L[i] else 0 for i in range(n)]
    cmf = sum(clv[i] * V[i] for i in range(n - w, n)) / sum(V[-w:])
    rvol = V[-1] / st.median(V[-21:-1]) if n >= 21 else V[-1] / st.median(V[:-1])
    print(f"MFI14        : {mfi:.1f} | CMF{w} {cmf:+.2f} | RVOL {rvol:.2f}x")

    hh = max(H[-w:])
    dd = harga / hh - 1
    zatr = (harga - ma20) / atr
    cl = (C[-1] - L[-1]) / (H[-1] - L[-1]) if H[-1] > L[-1] else 0.5
    print(f"Drawdown     : {dd:+.1%} dari high {w} hari ({hh:g}) | jarak MA20 {zatr:+.2f} ATR")
    print(f"Bar terakhir : O{O[-1]:g} H{H[-1]:g} L{L[-1]:g} C{C[-1]:g} chg {C[-1] / C[-2] - 1:+.2%} | close location {cl:.2f}")
    print(f"Swing        : low {w}h {min(L[-w:]):g} | high {w}h {hh:g} | low 5h {min(L[-5:]):g} | high 5h {max(H[-5:]):g}")

    # Oversold Composite PROXY (skala tetap, bukan percentile 252 sesi)
    comp = [
        (0.35, clip((50 - rsi) / 40)),
        (0.20, clip((0.5 - pb) / 0.5) if pb >= 0 else 1.0),
        (0.20, clip(-zatr / 3)),
        (0.15, clip(-dd / 0.30)),
        (0.10, clip((50 - mfi) / 30)),
    ]
    os_ = 100 * sum(wt * s for wt, s in comp)
    print(f"Oversold Comp: {os_:.0f}/100 (PROXY skala tetap; bukan probabilitas rebound)")

    if targets:
        print("Jarak target :", " | ".join(f"{t:g} {t / harga - 1:+.1%} ({(t - harga) / atr:+.1f} ATR)" for t in targets))


if __name__ == "__main__":
    main()
