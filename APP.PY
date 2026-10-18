import difflib
import hashlib
import html
import json
import math
import re
from collections import Counter
from datetime import date
from urllib.parse import quote

import pandas as pd
import streamlit as st

# ==========================================
# 1. KONFIGURASI
# ==========================================
st.set_page_config(
    page_title="ASISTEN KLAIM PETTY CASH",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)


TEKS = "#0F172A"           # warna teks utama (hampir hitam)
TEKS_SEKUNDER = "#1E293B"  # warna keterangan (tetap gelap dan terbaca)
NAVY = "#0B2545"
BIRU = "#1E3A8A"


def tulis(isi: str):
    """Tampilkan HTML (spasi dan baris baru dirapatkan agar tidak dianggap kode)."""
    st.markdown(re.sub(r"\s*\n\s*", " ", isi), unsafe_allow_html=True)


tulis(
    f"""
    <style>
    :root {{ color-scheme: light; }}
    .stApp, [data-testid="stAppViewContainer"] {{ background:#F4F6FA; color:{TEKS}; font-size:16px; }}
    [data-testid="stSidebar"] {{ background:#E2E8F0; }}
    [data-testid="stSidebar"] * {{ color:{TEKS}; }}
    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li,
    [data-testid="stWidgetLabel"] p, label, [data-testid="stCaptionContainer"],
    [data-testid="stRadio"] p {{ color:{TEKS} !important; }}
    [data-testid="stWidgetLabel"] p, [data-testid="stRadio"] label p {{
        font-weight:800; text-transform:uppercase; font-size:13px; letter-spacing:0.5px; }}
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, input {{
        background:#FFFFFF !important; color:{TEKS} !important; font-weight:700; }}
    div[data-baseweb="select"] * {{ color:{TEKS} !important; }}
    [data-baseweb="popover"] ul, [data-baseweb="popover"] li {{ background:#FFFFFF !important; color:{TEKS} !important; }}
    .stButton button, .stDownloadButton button {{ background:{BIRU}; border:0; }}
    .stButton button *, .stDownloadButton button * {{ color:#FFFFFF !important; font-weight:800; letter-spacing:0.4px; }}
    #MainMenu, footer {{ visibility:hidden; }}
    .block-container {{ padding-top:1.5rem; padding-bottom:3rem; }}

    .stTabs [data-baseweb="tab-list"] {{ gap:6px; border-bottom:2px solid #94A3B8; }}
    .stTabs [data-baseweb="tab"] {{ background:#E2E8F0; border-radius:8px 8px 0 0; padding:10px 18px; }}
    .stTabs [data-baseweb="tab"] p {{ color:{TEKS} !important; font-weight:800; font-size:13px;
        letter-spacing:0.5px; text-transform:uppercase; }}
    .stTabs [aria-selected="true"] {{ background:{BIRU}; }}
    .stTabs [aria-selected="true"] p {{ color:#FFFFFF !important; }}

    .banner {{ background:linear-gradient(135deg,{NAVY} 0%,{BIRU} 100%); border-radius:14px;
        padding:26px 30px; margin-bottom:22px; box-shadow:0 8px 20px rgba(11,37,69,0.25); }}
    .b-title {{ color:#FFFFFF; font-size:28px; font-weight:800; letter-spacing:1px; }}
    .b-sub {{ color:#FFFFFF; font-size:14px; font-weight:700; letter-spacing:1.2px; margin-top:4px; }}
    .b-chip {{ display:inline-block; background:#FFFFFF; color:{NAVY};
        font-size:12px; font-weight:800; letter-spacing:0.6px; padding:6px 14px;
        border-radius:20px; margin-top:14px; margin-right:8px; }}

    .metric-container {{ display:flex; flex-wrap:wrap; gap:14px; margin-bottom:22px; }}
    .metric-box {{ flex:1 1 180px; background:#FFFFFF; border:1px solid #94A3B8; padding:18px 18px 16px;
        border-radius:12px; box-shadow:0 4px 10px rgba(15,23,42,0.08); border-top:5px solid {BIRU}; }}
    .k-amber {{ border-top-color:#D97706; }}
    .k-green {{ border-top-color:#059669; }}
    .metric-title {{ font-size:12px; font-weight:800; color:{TEKS}; letter-spacing:0.8px; margin-bottom:8px; }}
    .metric-value {{ font-size:34px; font-weight:800; color:{TEKS}; line-height:1.1; }}
    .metric-sub {{ font-size:12px; font-weight:700; color:{TEKS_SEKUNDER}; margin-top:8px; letter-spacing:0.3px; }}

    .sec {{ color:{NAVY}; font-size:18px; font-weight:800; letter-spacing:0.8px; text-transform:uppercase;
        border-left:6px solid {BIRU}; padding-left:12px; margin:28px 0 6px; }}
    .note {{ color:{TEKS_SEKUNDER}; font-size:13px; font-weight:700; letter-spacing:0.3px;
        text-transform:uppercase; margin:0 0 12px 18px; }}

    .insight {{ background:#FFFFFF; border:1px solid #94A3B8; border-left:6px solid {BIRU};
        border-radius:10px; padding:18px 22px; margin-bottom:18px; box-shadow:0 4px 10px rgba(15,23,42,0.07); }}
    .insight .i-title {{ color:{NAVY}; font-size:16px; font-weight:800; letter-spacing:0.8px; margin-bottom:10px; }}
    .insight .i-line {{ color:{TEKS}; font-size:15px; font-weight:700; line-height:1.6;
        text-transform:uppercase; margin-bottom:6px; }}

    .rec {{ background:#FFFFFF; border:1px solid #94A3B8; border-radius:10px; padding:16px 22px;
        margin-bottom:14px; box-shadow:0 4px 10px rgba(15,23,42,0.07); }}
    .rec .r-title {{ color:{NAVY}; font-size:16px; font-weight:800; letter-spacing:0.6px; }}
    .rec .r-meta {{ color:{BIRU}; font-size:13px; font-weight:800; letter-spacing:0.5px; margin:2px 0 8px; }}
    .rec .r-desc {{ color:{TEKS_SEKUNDER}; font-size:13px; font-weight:700; text-transform:uppercase; margin-bottom:8px; }}
    .rec ul {{ margin:0; padding-left:20px; }}
    .rec li {{ color:{TEKS}; font-size:14px; font-weight:700; line-height:1.7; text-transform:uppercase; }}

    .tbl-wrap {{ overflow:auto; border:1px solid #94A3B8; border-radius:10px; background:#FFFFFF; margin-bottom:18px; }}
    .tbl {{ width:100%; border-collapse:collapse; font-size:14px; color:{TEKS}; }}
    .tbl th {{ position:sticky; top:0; background:{NAVY}; color:#FFFFFF; text-align:left; padding:11px 14px;
        font-size:12px; letter-spacing:0.7px; font-weight:800; text-transform:uppercase; white-space:nowrap; }}
    .tbl td {{ padding:11px 14px; border-bottom:1px solid #CBD5E1; font-weight:700; vertical-align:top;
        line-height:1.55; text-transform:uppercase; color:{TEKS}; background:#FFFFFF; }}
    .tbl tr:nth-child(even) td {{ background:#F1F5F9; }}
    .tbl td.num {{ text-align:right; white-space:nowrap; }}
    .tbl td.wide {{ min-width:340px; }}

    .bl-wrap {{ background:#FFFFFF; border:1px solid #94A3B8; border-radius:10px; padding:18px 20px; margin-bottom:18px; }}
    .bl-row {{ display:grid; grid-template-columns:minmax(160px,300px) 1fr 140px; gap:14px; align-items:center; margin-bottom:12px; }}
    .bl-row:last-child {{ margin-bottom:0; }}
    .bl-label {{ color:{TEKS}; font-size:13px; font-weight:800; text-transform:uppercase; letter-spacing:0.3px; line-height:1.3; }}
    .bl-track {{ background:#E2E8F0; height:20px; border-radius:10px; overflow:hidden; }}
    .bl-fill {{ height:100%; border-radius:10px; background:{BIRU}; }}
    .bl-val {{ color:{TEKS}; font-size:14px; font-weight:800; text-align:right; white-space:nowrap; }}
    @media (max-width:700px) {{ .bl-row {{ grid-template-columns:1fr 110px; }} .bl-label {{ grid-column:1 / -1; }} }}
    .cols-wrap {{ background:#FFFFFF; border:1px solid #94A3B8; border-radius:10px; padding:16px 18px 12px; margin-bottom:18px; overflow-x:auto; }}
    .cols {{ display:flex; align-items:flex-end; gap:12px; min-height:210px; }}
    .c {{ flex:0 0 58px; display:flex; flex-direction:column; align-items:center; justify-content:flex-end; }}
    .c-val {{ color:{TEKS}; font-size:14px; font-weight:800; margin-bottom:4px; }}
    .c-bar {{ width:100%; background:{BIRU}; border-radius:6px 6px 0 0; }}
    .c-lab {{ color:{TEKS}; font-size:12px; font-weight:800; margin-top:6px; white-space:nowrap; }}
    .c-sub {{ color:{TEKS_SEKUNDER}; font-size:11px; font-weight:700; white-space:nowrap; }}
    .prio {{ display:inline-block; color:#FFFFFF; font-size:11px; font-weight:800; letter-spacing:0.5px;
        padding:3px 10px; border-radius:12px; margin-left:8px; vertical-align:middle; background:{BIRU}; }}
    .prio.tinggi {{ background:#B45309; }}
    .prio.rendah {{ background:#047857; }}
    .rec .r-lbl {{ color:{BIRU}; font-size:12px; font-weight:800; letter-spacing:0.6px; margin-top:10px; }}
    .rec .r-txt {{ color:{TEKS}; font-size:14px; font-weight:700; text-transform:uppercase; line-height:1.6; }}
    .ai-note {{ color:{TEKS_SEKUNDER}; font-size:12px; font-weight:700; text-transform:uppercase; margin:6px 0 14px 4px; }}

    .putusan {{ background:#FFFFFF; border-radius:12px; padding:20px 24px; margin:6px 0 18px; border:2px solid #94A3B8;
        box-shadow:0 4px 10px rgba(15,23,42,0.07); }}
    .putusan.p-ok {{ border-color:#059669; border-left-width:10px; }}
    .putusan.p-cek {{ border-color:#D97706; border-left-width:10px; }}
    .putusan.p-no {{ border-color:#B91C1C; border-left-width:10px; }}
    .putusan .p-title {{ color:{TEKS}; font-size:26px; font-weight:800; letter-spacing:0.8px; }}
    .putusan .p-sub {{ color:{TEKS_SEKUNDER}; font-size:13px; font-weight:700; text-transform:uppercase; margin-top:6px; letter-spacing:0.4px; }}
    .rec.ok {{ border-left:6px solid #059669; }}
    .rec.cek {{ border-left:6px solid #D97706; }}
    .rec.no {{ border-left:6px solid #B91C1C; }}
    [data-testid="stChatMessage"] {{ background:#FFFFFF; border:1px solid #CBD5E1; border-radius:12px; padding:14px 18px; margin-bottom:10px; }}
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {{ color:{TEKS} !important; font-size:15px; line-height:1.65; }}
    [data-testid="stChatMessage"] strong {{ color:{NAVY}; }}
    [data-testid="stChatInput"] textarea {{ color:{TEKS} !important; background:#FFFFFF !important; font-size:15px; }}
    [data-testid="stBottom"] > div {{ background:#F4F6FA; }}
    .src {{ background:#F8FAFC; border:1px solid #CBD5E1; border-left:5px solid #94A3B8; border-radius:8px; padding:10px 14px;
        margin-bottom:8px; color:{TEKS}; font-size:13px; font-weight:600; line-height:1.5; }}
    .src.dipakai {{ border-left-color:#059669; }}
    .src b {{ color:{NAVY}; }}
    .src .s-tag {{ display:inline-block; background:{BIRU}; color:#FFFFFF; font-size:11px; font-weight:800; padding:2px 8px; border-radius:10px; margin-right:6px; }}
    .foot {{ color:{TEKS_SEKUNDER}; font-size:12px; font-weight:800; letter-spacing:0.5px;
        text-transform:uppercase; margin-top:30px; border-top:1px solid #94A3B8; padding-top:12px; }}
    </style>
    """
)

# ==========================================
# 2. MESIN PENGOLAH DATA
# ==========================================
# --- KB START ---
STOP = {
    "yang", "dan", "di", "ke", "dari", "pada", "untuk", "utk", "dgn", "dengan", "atau", "ini", "itu",
    "apa", "mana", "masuk", "bagaimana", "gimana", "apakah", "bisa", "boleh", "harus", "dong", "ya",
    "nya", "kah", "saya", "kami", "kita", "mau", "ingin", "tolong", "klaim", "claim", "sudah", "belum",
    "tgl", "tanggal", "rp", "no", "nomor", "oleh", "karena", "adalah", "yg", "tidak", "jika", "bila",
    "akun", "coa", "account", "contoh", "uraian", "riwayat", "dipakai", "kali",
}
AWALAN = ("memper", "mem", "men", "meng", "per", "pem", "pen", "ber", "ter", "di", "me", "pe")
AKHIRAN = ("kan", "nya", "an", "i")


def stem(k: str) -> str:
    """Stemmer ringan agar 'perbaikan', 'memperbaiki', 'diperbaiki' saling cocok."""
    if len(k) <= 4 or k.isdigit():
        return k
    for a in AKHIRAN:
        if k.endswith(a) and len(k) - len(a) >= 4:
            k = k[: -len(a)]
            break
    for p in AWALAN:
        if k.startswith(p) and len(k) - len(p) >= 4:
            k = k[len(p):]
            break
    return k


def tokenise(teks: str) -> list:
    kata = re.findall(r"[a-z0-9]+", str(teks).lower())
    return [stem(k) for k in kata if len(k) > 1 and k not in STOP]


def bangun_indeks(daftar) -> dict:
    docs = [Counter(tokenise(t)) for t in daftar]
    n = len(docs)
    dfc = Counter()
    for d in docs:
        dfc.update(d.keys())
    idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in dfc.items()}
    vecs = []
    for d in docs:
        v = {t: (1 + math.log(c)) * idf[t] for t, c in d.items()}
        norma = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({t: x / norma for t, x in v.items()})
    return {"idf": idf, "vecs": vecs}


def hitung_kemiripan(indeks: dict, teks: str) -> list:
    idf = indeks["idf"]
    cnt = Counter(tokenise(teks))
    q = {t: (1 + math.log(c)) * idf[t] for t, c in cnt.items() if t in idf}
    norma = math.sqrt(sum(x * x for x in q.values()))
    if not q or norma == 0:
        return [0.0] * len(indeks["vecs"])
    q = {t: x / norma for t, x in q.items()}
    return [sum(w * v.get(t, 0.0) for t, w in q.items()) for v in indeks["vecs"]]


def norm_nama(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s).lower())


def siapkan_tabel(raw: pd.DataFrame):
    """Cari baris judul kolom (baris pertama yang terisi >= 3 sel), kembalikan (judul, data)."""
    raw = raw.fillna("").astype(str).apply(lambda c: c.str.strip())
    raw = raw.loc[(raw != "").any(axis=1), (raw != "").any(axis=0)]
    if raw.empty:
        return [], pd.DataFrame()
    pos = None
    for i in range(min(len(raw), 8)):
        if (raw.iloc[i] != "").sum() >= 3:
            pos = i
            break
    if pos is None:
        return [], pd.DataFrame()
    judul = []
    for n, h in enumerate(raw.iloc[pos].tolist(), 1):
        judul.append(h if h else f"KOLOM {n}")
    data = raw.iloc[pos + 1:].reset_index(drop=True)
    data.columns = judul
    return judul, data


def potong(teks: str, maks: int = 700) -> str:
    teks = re.sub(r"\s+", " ", str(teks)).strip()
    return teks if len(teks) <= maks else teks[: maks - 1].rstrip() + "…"


def potongan_baris(judul, data, sumber, jenis, unit=None):
    """Satu baris tabel = satu potongan: 'KOLOM: nilai | KOLOM: nilai'."""
    hasil = []
    for _, r in data.iterrows():
        bagian = [f"{h}: {r[h]}" for h in judul if str(r[h]).strip()]
        if len(bagian) >= 2:
            hasil.append({"sumber": sumber, "jenis": jenis, "unit": unit, "teks": potong(" | ".join(bagian))})
    return hasil


def peta_master(judul, data):
    """Daftar (nama_normal, 'NO. G/L - Sub-category') dari master COA untuk mencocokkan nama akun di kamus."""
    kolom_no = next((h for h in judul if "g/l" in h.lower() or "account" in h.lower()), judul[0] if judul else None)
    kolom_nama = [h for h in judul if any(k in h.lower() for k in ("fbcj", "sub"))]
    peta = {}
    for _, r in data.iterrows():
        no = str(r[kolom_no]).strip() if kolom_no else ""
        if not no:
            continue
        sub = next((str(r[h]).strip() for h in judul if "sub" in h.lower() and str(r[h]).strip()), "")
        label = f"{no} - {sub}" if sub else no
        for h in kolom_nama:
            nama = norm_nama(r[h])
            if nama:
                peta[nama] = label
    return peta


def potongan_kamus(judul, data, tab, peta):
    unit = tab.strip().upper()
    sumber = f"KAMUS PETTY CASH / {unit}"

    def kolom(*kunci):
        for h in judul:
            if any(k in h.upper() for k in kunci):
                return h
        return None

    k_coa, k_text = kolom("COA"), kolom("TEXT", "URAIAN")
    k_ket, k_cc, k_note = kolom("KETERANGAN"), kolom("COST CENTER"), kolom("NOTE", "CATATAN", "ATURAN")
    hasil = []
    if k_note:  # kolom NOTE berisi aturan klaim yang berdiri sendiri
        for teks in data[k_note].tolist():
            if len(str(teks).strip()) >= 10:
                hasil.append({"sumber": sumber + " / ATURAN", "jenis": "aturan", "unit": unit, "teks": potong(teks)})
    if k_coa and k_text:
        kelompok = {}
        for _, r in data.iterrows():
            coa, teks = str(r[k_coa]).strip(), str(r[k_text]).strip()
            if coa and teks:
                kelompok.setdefault(coa, []).append((teks, str(r[k_ket]).strip() if k_ket else "",
                                                     str(r[k_cc]).strip() if k_cc else ""))
        norms = list(peta.keys())
        for coa, daftar in kelompok.items():
            unik, lihat = [], set()
            for teks, _, _ in daftar:
                kunci = re.sub(r"[\d./@:,\-]+", " ", teks.lower()).split()
                kunci = " ".join(kunci)
                if kunci not in lihat:
                    lihat.add(kunci)
                    unik.append(teks)
            ket = next((k for _, k, _ in daftar if k), "")
            cc = next((c for _, _, c in daftar if c), "")
            cocok = difflib.get_close_matches(norm_nama(coa), norms, n=1, cutoff=0.85) if norms else []
            padanan = f" | PADANAN G/L DI MASTER COA: {peta[cocok[0]]}" if cocok else ""
            isi = (f"RIWAYAT KLAIM ({unit}): AKUN/COA '{coa}' DIPAKAI {len(daftar)} KALI{padanan}. "
                   f"CONTOH URAIAN: " + "; ".join(unik[:8]))
            if cc:
                isi += f" | COST CENTER: {cc}"
            if ket:
                isi += f" | KETERANGAN: {ket}"
            hasil.append({"sumber": sumber, "jenis": "contoh", "unit": unit, "teks": potong(isi)})
    return hasil


def potongan_dokumen(teks: str, sumber="DOKUMEN ATURAN KLAIM"):
    paragraf = [p.strip() for p in re.split(r"\n\s*\n", str(teks).replace("\r", "")) if p.strip()]
    hasil, buf = [], ""
    for p in paragraf:
        p = re.sub(r"\s+", " ", p)
        if len(buf) + len(p) < 800:
            buf = (buf + " " + p).strip()
        else:
            if buf:
                hasil.append(buf)
            buf = p
    if buf:
        hasil.append(buf)
    return [{"sumber": sumber, "jenis": "aturan", "unit": None, "teks": potong(h, 900)} for h in hasil if len(h) >= 15]


KUOTA = {"master": 4, "aturan": 5, "contoh": 3, "histori": 3}


def cari_konteks(indeks, potongan, pertanyaan, unit="SEMUA", batas=0.04):
    sims = hitung_kemiripan(indeks, pertanyaan)
    urut = sorted(range(len(sims)), key=lambda i: -sims[i])
    puncak = max(sims) if sims else 0.0
    batas = max(batas, 0.45 * puncak)  # buang potongan yang jauh kurang relevan dibanding yang terbaik
    terpilih = []
    for jenis, n in KUOTA.items():
        ambil = [
            i for i in urut
            if potongan[i]["jenis"] == jenis and sims[i] >= batas
            and (unit == "SEMUA" or potongan[i]["unit"] in (None, unit))
        ][:n]
        terpilih += ambil
    terpilih.sort(key=lambda i: -sims[i])
    return [(i, sims[i]) for i in terpilih[:14]]
# --- KB END ---

def rahasia(kunci, bawaan=None):
    try:
        return st.secrets[kunci]
    except Exception:
        return bawaan


# ---------- fungsi tampilan ----------
def esc(x) -> str:
    return html.escape(str(x))


def sec(judul: str, catatan: str = ""):
    isi = f'<div class="sec">{esc(judul)}</div>'
    if catatan:
        isi += f'<div class="note">{esc(catatan)}</div>'
    tulis(isi)


def kartu(judul, nilai, sub, warna=""):
    return (
        f'<div class="metric-box {warna}"><div class="metric-title">{esc(judul)}</div>'
        f'<div class="metric-value">{esc(nilai)}</div><div class="metric-sub">{esc(sub)}</div></div>'
    )


def tabel_html(data: pd.DataFrame, kolom_angka=(), kolom_lebar=(), tinggi=520):
    """Tabel sederhana: teks gelap, huruf besar, header navy. Selalu terbaca di tema apa pun."""
    kepala = "".join(f"<th>{esc(c)}</th>" for c in data.columns)
    baris = []
    for _, r in data.iterrows():
        sel = []
        for c in data.columns:
            kelas = "num" if c in kolom_angka else ("wide" if c in kolom_lebar else "")
            sel.append(f'<td class="{kelas}">{esc(r[c])}</td>')
        baris.append("<tr>" + "".join(sel) + "</tr>")
    return (
        f'<div class="tbl-wrap" style="max-height:{tinggi}px"><table class="tbl">'
        f"<thead><tr>{kepala}</tr></thead><tbody>{''.join(baris)}</tbody></table></div>"
    )


def bar_list(data) -> str:
    """Grafik batang horizontal sederhana. data = [(label, nilai, teks, warna_opsional), ...]"""
    if not data:
        return ""
    maks = max(d[1] for d in data) or 1
    baris = []
    for d in data:
        label, nilai, teks = d[0], d[1], d[2]
        warna = d[3] if len(d) > 3 else None
        lebar = max(2.0, nilai / maks * 100) if nilai > 0 else 0
        gaya = f"width:{lebar:.1f}%" + (f";background:{warna}" if warna else "")
        baris.append(
            f'<div class="bl-row"><div class="bl-label">{esc(label)}</div>'
            f'<div class="bl-track"><div class="bl-fill" style="{gaya}"></div></div>'
            f'<div class="bl-val">{esc(teks)}</div></div>'
        )
    return '<div class="bl-wrap">' + "".join(baris) + "</div>"


def kolom_chart(data) -> str:
    """Grafik batang vertikal sederhana. data = [(label, nilai, sub), ...]"""
    if not data:
        return ""
    maks = max(d[1] for d in data) or 1
    isi = []
    for label, nilai, sub in data:
        tinggi = max(4, int(nilai / maks * 170)) if nilai > 0 else 2
        isi.append(
            f'<div class="c"><div class="c-val">{esc(nilai)}</div>'
            f'<div class="c-bar" style="height:{tinggi}px"></div>'
            f'<div class="c-lab">{esc(label)}</div><div class="c-sub">{esc(sub)}</div></div>'
        )
    return f'<div class="cols-wrap"><div class="cols">{"".join(isi)}</div></div>'



import hmac
import urllib.request

S = st.session_state

# ==========================================
# 3. SUMBER DATA (UBAH DI SINI BILA PERLU)
# ==========================================
ID_KAMUS = "1fjzpfQNVNmtMBJ9-ihmILOncZOsjJHhJv3uptZhQH6c"   # KAMUS PETTY CASH (tab RETAIL, DC)
ID_MASTER = "1SmLN23EHaZOR-ujT9SJifnnFC4tkzIjo9o3KYmXBFD4"  # MASTER COA
ID_DOKUMEN = "1mx8BqBj8FsTf0LIdkIXkrXb-DeLmGmt-_ndpdv99nto"  # Google Doc aturan klaim (harus dibagikan 'Anyone with the link')
MAKS_TANYA = 40  # batas pertanyaan per sesi (menjaga biaya AI)

SISTEM = (
    "Anda adalah Asisten Klaim Petty Cash untuk kasir dan staf store/DC. "
    "Anda menjawab HANYA berdasarkan KONTEKS DATABASE yang diberikan (potongan dari Master COA, Kamus Petty Cash, "
    "aturan klaim, dan riwayat klaim). Aturan menjawab:\n"
    "1. Mulai dengan jawaban langsung: nomor G/L dan nama akun COA yang tepat, lalu alasan singkat.\n"
    "2. Sebutkan syarat, dokumen, atau approval wajib bila ada pada konteks, sebagai poin singkat.\n"
    "3. Bila ada lebih dari satu kemungkinan (misalnya membeli barang vs jasa perbaikan, atau perbaikan yang "
    "mengubah bentuk bangunan), jelaskan perbedaannya dan ajukan SATU pertanyaan klarifikasi.\n"
    "4. Rujuk sumber dengan kode seperti [S1], [S2] sesuai nomor pada konteks.\n"
    "5. Bila konteks tidak memuat jawabannya, katakan belum ditemukan di database dan sarankan menghubungi "
    "Accounting/Tax. JANGAN menebak nomor COA, nominal, atau aturan.\n"
    "6. Gunakan Bahasa Indonesia sederhana, ramah, dan ringkas (sekitar 150 kata, kecuali diminta rinci). "
    "Jangan membahas hal di luar pertanyaan."
)

CONTOH_PERTANYAAN = [
    "Biaya perbaikan lampu masuk ke COA mana?",
    "Pembelian materai harus di mana dan apa syaratnya?",
    "Dokumen apa yang wajib untuk klaim ATK bulanan?",
]


def rahasia(kunci, bawaan=None):
    try:
        return st.secrets[kunci]
    except Exception:
        return bawaan


def baca_sheet(sid: str, tab: str) -> pd.DataFrame:
    url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&sheet={quote(tab)}"
    return pd.read_csv(url, header=None, dtype=str, keep_default_na=False)


def baca_dokumen(did: str) -> str:
    url = f"https://docs.google.com/document/d/{did}/export?format=txt"
    with urllib.request.urlopen(url, timeout=20) as r:
        return r.read().decode("utf-8", errors="replace")


@st.cache_data(ttl=600, show_spinner="MEMBACA DATABASE KLAIM...")
def muat_pengetahuan(id_kamus: str, id_master: str, id_dokumen: str):
    potongan, status = [], []

    # 1) Master COA (dibaca dulu agar nama akun di kamus bisa dipadankan dengan nomor G/L)
    peta = {}
    for tab, jenis in (("Daftar_COA_PC", "master"), ("Text_COA", "master"), ("Histori Claim", "histori")):
        try:
            judul, data = siapkan_tabel(baca_sheet(id_master, tab))
            if not judul:
                raise ValueError("tabel kosong")
            if tab == "Daftar_COA_PC":
                peta = peta_master(judul, data)
            baru = potongan_baris(judul, data, f"MASTER COA / {tab}", jenis)
            potongan += baru
            status.append((f"MASTER COA / {tab}", len(baru), ""))
        except Exception as e:
            status.append((f"MASTER COA / {tab}", 0, str(e)[:80]))

    # 2) Kamus Petty Cash (RETAIL & DC)
    for tab in ("RETAIL", "DC"):
        try:
            judul, data = siapkan_tabel(baca_sheet(id_kamus, tab))
            if not judul:
                raise ValueError("tabel kosong")
            baru = potongan_kamus(judul, data, tab, peta)
            potongan += baru
            status.append((f"KAMUS PETTY CASH / {tab}", len(baru), ""))
        except Exception as e:
            status.append((f"KAMUS PETTY CASH / {tab}", 0, str(e)[:80]))

    # 3) Dokumen aturan klaim
    try:
        baru = potongan_dokumen(baca_dokumen(id_dokumen))
        potongan += baru
        status.append(("DOKUMEN ATURAN KLAIM", len(baru), ""))
    except Exception:
        status.append(("DOKUMEN ATURAN KLAIM", 0, "BELUM BISA DIBACA - BAGIKAN 'ANYONE WITH THE LINK'"))

    indeks = bangun_indeks([p["teks"] for p in potongan]) if potongan else None
    return potongan, indeks, status


# ==========================================
# 4. AKSES (OPSIONAL)
# ==========================================
kode_akses = rahasia("KODE_AKSES")
if kode_akses and not S.get("lolos"):
    tulis('<div class="banner"><div class="b-title">ASISTEN KLAIM PETTY CASH</div>'
          '<div class="b-sub">MASUKKAN KODE AKSES UNTUK MELANJUTKAN</div></div>')
    masuk = st.text_input("KODE AKSES", type="password")
    if st.button("MASUK"):
        if hmac.compare_digest(str(kode_akses), masuk):
            S["lolos"] = True
            st.rerun()
        else:
            st.error("KODE AKSES TIDAK SESUAI.")
    st.stop()

api_ok = bool(rahasia("ANTHROPIC_API_KEY"))
model_ai = rahasia("ANTHROPIC_MODEL", "claude-sonnet-5-5")

# ==========================================
# 5. SIDEBAR
# ==========================================
st.sidebar.markdown("### PENGATURAN")
unit = st.sidebar.selectbox("UNIT / BU", ["SEMUA", "RETAIL", "DC"])
huruf_besar = st.sidebar.checkbox("JAWABAN HURUF BESAR", value=False)
if st.sidebar.button("MUAT ULANG DATA"):
    st.cache_data.clear()
    st.rerun()
if st.sidebar.button("HAPUS PERCAKAPAN"):
    S["chat"] = []
    S["jumlah_tanya"] = 0
    st.rerun()

potongan, indeks, status = muat_pengetahuan(ID_KAMUS, ID_MASTER, str(rahasia("ID_DOKUMEN", ID_DOKUMEN)))

st.sidebar.markdown("### STATUS DATA")
st.sidebar.markdown(re.sub(r"\s*\n\s*", " ", "".join(
    f'<div class="note" style="margin-left:0">{esc(n)}: {j} POTONGAN'
    f'{(" - " + esc(p)) if p else ""}</div>' for n, j, p in status
)), unsafe_allow_html=True)

# ==========================================
# 6. HEADER
# ==========================================
tulis(
    f"""
    <div class="banner">
        <div class="b-title">ASISTEN KLAIM PETTY CASH</div>
        <div class="b-sub">TANYA JAWAB BERDASARKAN MASTER COA, KAMUS, DAN ATURAN KLAIM</div>
        <span class="b-chip">DATA: {len(potongan)} POTONGAN</span>
        <span class="b-chip">UNIT: {esc(unit)}</span>
        <span class="b-chip">AI: {"AKTIF" if api_ok else "BELUM AKTIF"}</span>
    </div>
    """
)

if not potongan or indeks is None:
    st.error("DATABASE TIDAK BERHASIL DIBACA. PASTIKAN SEMUA GOOGLE SHEET DIBAGIKAN 'ANYONE WITH THE LINK' (VIEWER).")
    st.stop()

S.setdefault("chat", [])
S.setdefault("jumlah_tanya", 0)


def html_sumber(daftar, jawaban=""):
    isi = []
    for n, (i, sim) in enumerate(daftar, 1):
        p = potongan[i]
        dipakai = f"[S{n}]" in jawaban
        isi.append(
            f'<div class="src {"dipakai" if dipakai else ""}"><span class="s-tag">S{n}</span>'
            f'<b>{esc(p["sumber"])}</b> (KECOCOKAN {sim * 100:.0f}%)<br>{esc(p["teks"])}</div>'
        )
    return "".join(isi)


def tampil_pesan(m):
    with st.chat_message(m["role"]):
        st.markdown(m["content"])
        if m.get("sumber"):
            with st.expander("SUMBER DATA YANG DIGUNAKAN"):
                tulis(html_sumber(m["sumber"], m["content"]))


for m in S["chat"]:
    tampil_pesan(m)

# ---- contoh pertanyaan (hanya saat percakapan kosong) ----
dipilih = None
tempat_contoh = st.empty()
if not S["chat"]:
    with tempat_contoh.container():
        tulis('<div class="note" style="margin-left:0">CONTOH PERTANYAAN</div>')
        for n, q in enumerate(CONTOH_PERTANYAAN):
            if st.button(q, key=f"contoh_{n}"):
                dipilih = q

pertanyaan = st.chat_input("Tulis pertanyaan Anda, misalnya: biaya perbaikan lampu masuk COA mana?") or dipilih


# ==========================================
# 7. PROSES PERTANYAAN
# ==========================================
def konteks_teks(daftar):
    return "\n".join(f"[S{n}] ({potongan[i]['sumber']}) {potongan[i]['teks']}" for n, (i, _) in enumerate(daftar, 1))


def aliran_jawaban(sistem, pesan):
    """Hasilkan jawaban AI sebagai aliran teks; bila streaming gagal, pakai permintaan biasa."""
    import anthropic

    klien = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    ada_teks = False
    try:
        with klien.messages.stream(model=model_ai, max_tokens=1000, system=sistem, messages=pesan) as aliran:
            for t in aliran.text_stream:
                ada_teks = True
                yield t
    except Exception:
        if ada_teks:
            raise
        jawab = klien.messages.create(model=model_ai, max_tokens=1000, system=sistem, messages=pesan)
        yield "".join(b.text for b in jawab.content if getattr(b, "type", "") == "text")


if pertanyaan:
    tempat_contoh.empty()
    if S["jumlah_tanya"] >= MAKS_TANYA:
        st.warning("BATAS PERTANYAAN UNTUK SESI INI TERCAPAI. MUAT ULANG HALAMAN UNTUK MEMULAI SESI BARU.")
        st.stop()
    S["jumlah_tanya"] += 1

    with st.chat_message("user"):
        st.markdown(pertanyaan)

    # pertanyaan lanjutan yang singkat dilengkapi dengan pertanyaan sebelumnya agar pencarian tetap relevan
    kueri = pertanyaan
    if len(pertanyaan.split()) < 6:
        sebelumnya = [m["content"] for m in S["chat"] if m["role"] == "user"]
        if sebelumnya:
            kueri = sebelumnya[-1] + " " + pertanyaan
    hasil = cari_konteks(indeks, potongan, kueri, unit)

    with st.chat_message("assistant"):
        if not hasil:
            jawaban = ("Saya belum menemukan data yang cocok di database untuk pertanyaan ini. "
                       "Coba gunakan kata lain (misalnya nama barang atau jenis biayanya), atau hubungi Accounting/Tax.")
            st.markdown(jawaban)
        elif not api_ok:
            baris = [f"- **{potongan[i]['sumber']}**: {potongan[i]['teks']}" for i, _ in hasil[:4]]
            jawaban = ("AI belum aktif (ANTHROPIC_API_KEY belum diisi), jadi berikut data paling relevan dari database:\n\n"
                       + "\n".join(baris))
            st.markdown(jawaban)
        else:
            sistem = SISTEM + (" Tulis jawaban seluruhnya dengan HURUF KAPITAL." if huruf_besar else "")
            pesan = [{"role": m["role"], "content": m["content"]} for m in S["chat"][-6:]]
            pesan.append({"role": "user", "content": f"KONTEKS DATABASE:\n{konteks_teks(hasil)}\n\nPERTANYAAN: {pertanyaan}"})
            try:
                jawaban = st.write_stream(aliran_jawaban(sistem, pesan))
            except Exception as e:
                jawaban = f"AI sedang tidak dapat diakses ({e}). Silakan coba lagi sebentar lagi."
                st.markdown(jawaban)
        if hasil:
            with st.expander("SUMBER DATA YANG DIGUNAKAN"):
                tulis(html_sumber(hasil, jawaban))

    S["chat"].append({"role": "user", "content": pertanyaan})
    S["chat"].append({"role": "assistant", "content": jawaban, "sumber": hasil})

tulis('<div class="foot">JAWABAN DISUSUN AI BERDASARKAN DATABASE KLAIM DAN COA; UNTUK KASUS KHUSUS TETAP KONFIRMASI KE ACCOUNTING / TAX</div>')
