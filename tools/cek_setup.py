"""Cek apakah Juma Stock Analysis siap dipakai di komputer ini.

Pemakaian (dari akar folder Juma Stock Analysis):
    python tools/cek_setup.py

Yang dicek: versi Python, library, font, struktur folder, skill, ketiga skrip
(indikator, pola PL, PDF) memakai data contoh. PDF uji dibuat di folder sementara
lalu dihapus, jadi folder hasil-analisa tidak tersentuh.
Kode keluar: 0 = semua lolos, 1 = ada yang gagal.
"""
import os
import subprocess
import sys
import tempfile

AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
hasil = []


def cek(nama, ok, info=""):
    hasil.append(ok)
    print(f"  [{'OK' if ok else 'GAGAL'}] {nama}" + (f" — {info}" if info else ""))


def jalankan(*argumen):
    p = subprocess.run([sys.executable, *argumen], cwd=AKAR, capture_output=True, text=True, encoding="utf-8")
    return p.returncode, (p.stdout + p.stderr).strip()


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # supaya tanda — tampil benar di konsol Windows
    except (AttributeError, ValueError):
        pass
    print(f"Juma Stock Analysis — cek setup\nFolder: {AKAR}\n")

    print("1. Python & library")
    cek("Python >= 3.9", sys.version_info >= (3, 9), sys.version.split()[0])
    try:
        import reportlab
        cek("reportlab", True, reportlab.Version)
    except ImportError:
        cek("reportlab", False, "jalankan: python -m pip install -r requirements.txt")

    print("\n2. Struktur folder & file")
    wajib = [
        "CLAUDE.md", "MULAI-DI-KOMPUTER-BARU.md", "requirements.txt",
        ".claude/skills/juma-stock-analysis/SKILL.md",
        ".claude/skills/juma-stock-analysis/referensi/A-data.md",
        ".claude/skills/juma-stock-analysis/referensi/B-teknikal.md",
        ".claude/skills/juma-stock-analysis/referensi/C-berita-fundamental.md",
        ".claude/skills/juma-stock-analysis/referensi/D-validasi.md",
        ".claude/skills/juma-stock-analysis/referensi/format-pdf.md",
        ".claude/skills/pola-pantul-lantai/SKILL.md",
        "tools/indikator.py", "tools/pola_pantul_lantai.py", "tools/buat_pdf.py",
        "tools/contoh/contoh-COIN.csv", "tools/contoh/contoh-hasil.json",
        "log-perubahan/CHANGELOG.md",
    ]
    hilang = [f for f in wajib if not os.path.exists(os.path.join(AKAR, f))]
    cek(f"{len(wajib)} file inti", not hilang, "hilang: " + ", ".join(hilang) if hilang else "lengkap")
    for folder in ("data/harga", "data/json", "hasil-analisa", "log-perubahan", "dokumen"):
        p = os.path.join(AKAR, folder)
        if not os.path.isdir(p):
            os.makedirs(p, exist_ok=True)
            cek(f"folder {folder}", True, "dibuat karena belum ada")
        else:
            cek(f"folder {folder}", True)

    print("\n3. Skrip")
    kode, out = jalankan("tools/indikator.py", "tools/contoh/contoh-COIN.csv", "--harga", "292", "--target", "298,310")
    cek("indikator.py", kode == 0 and "RSI14" in out, out.splitlines()[1] if kode == 0 and len(out.splitlines()) > 1 else out[-200:])
    kode, out = jalankan("tools/pola_pantul_lantai.py", "tools/contoh/contoh-COIN.csv")
    baris = [b for b in out.splitlines() if b.startswith("Status")]
    cek("pola_pantul_lantai.py", kode == 0 and bool(baris), baris[0] if baris else out[-200:])

    with tempfile.TemporaryDirectory() as tmp:
        tujuan = os.path.join(tmp, "uji.pdf")
        kode, out = jalankan("tools/buat_pdf.py", "tools/contoh/contoh-hasil.json", "--keluar", tujuan)
        info = [b for b in out.splitlines() if b.startswith("Halaman")]
        ok = kode == 0 and os.path.exists(tujuan)
        cek("buat_pdf.py (PDF 2 halaman)", ok, info[0] if info else out[-300:])
        if ok and "Helvetica" in out:
            print("        catatan: font Arial/DejaVu tidak ditemukan, beberapa simbol (− ≥ ▲) diganti teks biasa.")

    lolos = all(hasil)
    print(f"\nHasil: {'SEMUA LOLOS — sistem siap dipakai' if lolos else 'ADA YANG GAGAL — lihat baris [GAGAL] di atas'}")
    return 0 if lolos else 1


if __name__ == "__main__":
    sys.exit(main())
