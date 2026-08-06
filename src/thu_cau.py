"""Thu NHIEU cach dien dat cho cung mot y, roi nghe va do de chon.

    python src/thu_cau.py build/thu_cau.txt --engine omnivoice --voice namtre_v3

`thu_cau.txt`: moi dong mot phuong an (dong trong va dong bat dau bang # bo qua).

Vi sao can file nay: sua narration roi render ca video mat ~45 phut, nen moi lan
chi thu duoc MOT phuong an va phai doan. O day tat ca phuong an duoc gom vao MOT
lan goi model - chi phi nap model (~8s) va warmup (~14s) tra mot lan cho tat ca,
nen thu 5 phuong an gan bang thu 1.

In kem so do de xep hang truoc khi nghe:

  khoi/giay   So khoi am chia thoi gian co am. Thap bat thuong = am dinh vao nhau,
              nghe thanh nuot chu. Do bang AM HOC nen khong phu thuoc van ban.
  lo chet     Vung RMS phang duoi 1e-4 keo dai >=120ms GIUA cau (khong tinh im
              lang co y chen, phan biet bang ty le mau = 0 tuyet doi).
  tut duoi    Cao tan (>6kHz) cua 150ms cuoi so voi ca cau. Cang am cang mo duoi.

So do chi de LOAI phuong an te ro rang. Quyet dinh cuoi cung van la nghe - tai
nguoi dung da bat duoc loi ma bo do nay bo sot.
"""
import argparse
import os
import sys
import wave

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import yaml

import tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out", "thu")


def _load_wav(p):
    with wave.open(p, "rb") as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        y = np.frombuffer(w.readframes(n), dtype=np.int16)
    if ch > 1:
        y = y.reshape(-1, ch).mean(1).astype(np.int16)
    return y, sr


def _env(y, sr, fr=256, hop=64):
    n = 1 + (len(y) - fr) // hop
    return np.sqrt(np.array([np.mean(y[i * hop:i * hop + fr] ** 2)
                             for i in range(n)])), hop


def _hf(seg, sr, n_fft=1024, hop=256):
    if len(seg) < n_fft:
        seg = np.pad(seg, (0, n_fft - len(seg)))
    win = np.hanning(n_fft).astype(np.float32)
    m = np.fft.rfftfreq(n_fft, 1.0 / sr) > 6000
    tot = hi = 0.0
    for i in range(1 + (len(seg) - n_fft) // hop):
        S = np.abs(np.fft.rfft(seg[i * hop:i * hop + n_fft] * win))
        tot += S.sum()
        hi += S[m].sum()
    return float(hi / (tot or 1e-9))


def measure(path):
    yi, sr = _load_wav(path)
    y = yi.astype(np.float32) / 32768.0
    dur = len(y) / sr
    env, hop = _env(y, sr)

    # khoi am: dung nguong tuong doi trong chinh file
    thr = np.percentile(env, 90) * 0.18
    on = env > thr
    blocks, voiced, st = 0, 0.0, None
    for i, v in enumerate(on):
        if v and st is None:
            st = i
        elif not v and st is not None:
            d = (i - st) * hop / sr
            if d >= 0.045:
                blocks += 1
                voiced += d
            st = None

    # lo chet: gan im lang nhung KHONG phai im lang chen (mau = 0 tuyet doi)
    dead, st, holes = env < 1e-4, None, []
    for i, v in enumerate(dead):
        if v and st is None:
            st = i
        elif not v and st is not None:
            ms = (i - st) * hop / sr * 1000
            a0, a1 = st * hop, i * hop
            zf = float((yi[a0:a1] == 0).mean()) if a1 > a0 else 1.0
            if ms >= 120 and zf < 0.90:
                holes.append(ms)
            st = None

    tail = _hf(y[-int(0.15 * sr):], sr)
    whole = _hf(y, sr)
    return dict(dur=dur, blocks=blocks, rate=blocks / (voiced or 1e-9),
                holes=len(holes), hole_max=max(holes) if holes else 0.0,
                tail=(tail / whole - 1) * 100 if whole > 0 else 0.0)


OMNI_TEST = r"D:\omnivoice-test"


def _in_contour(cands, cfg):
    """In he so toc do ma `contour_for()` se ap cho TUNG CAU cua moi phuong an.

    Ly do phai co: `contour_for` chay theo VI TRI cau trong loi doc, khong theo
    noi dung. Cau cuoi bi ha con x0,95 de "ket chac chan". Nghia la thu mot cau
    DUNG MOT MINH thi no chay x0,98, con chinh cau do nam cuoi mot loi doc ba cau
    thi chay x0,95 - lech 3,2%, du de tai nghe ra.

    Da vap dung loi do: nguoi dung bao mot cau nghe khong ro trong video, thu
    rieng cau do thi thay on, va ket luan sai la loi tai cach dien dat. Bang nay
    de lan sau nhin thay ngay phuong an nao dang nam o vi tri bi ha toc.

    Muon thu DUNG dieu kien cua video thi dan CA LOI DOC cua canh vao mot dong,
    dung dan moi mot cau.
    """
    if cfg.get("engine") != "omnivoice":
        return
    try:
        sys.path.insert(0, OMNI_TEST)
        import speak
        import vitext
    except Exception as e:
        print(f"  (khong doc duoc contour: {type(e).__name__})\n")
        return
    base = float(cfg.get("speed", 1.0))
    print("  he so toc do theo VI TRI cau (contour_for):")
    for i, t in enumerate(cands, 1):
        cau = vitext.prepare(t)
        phan = []
        for j, c in enumerate(cau):
            _, sp = speak.contour_for(c, j, len(cau))
            dau = "*" if sp < 0.99 else " "
            phan.append(f"{dau}{base * sp:.3f}")
        print(f"   {i:2}  {len(cau)} cau  " + " ".join(phan))
    print("      (* = cau bi ha toc; cau CUOI luon x0,95)\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="file txt, moi dong mot phuong an")
    ap.add_argument("--screenplay", default="screenplays/cache-stale.yaml",
                    help="lay cau hinh giong (speed/pause_scale/...) tu day")
    ap.add_argument("--engine", choices=["edge", "omnivoice"])
    ap.add_argument("--voice")
    ap.add_argument("--style")
    ap.add_argument("--tts-mode", choices=["lien", "tach"])
    a = ap.parse_args()

    with open(os.path.join(ROOT, a.screenplay), "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    for k, v in (("engine", a.engine), ("voice", a.voice), ("style", a.style),
                 ("mode", a.tts_mode)):
        if v is not None:
            doc[k] = v
    cfg = tts.config(doc)

    with open(a.file, "r", encoding="utf-8") as f:
        cands = [ln.strip() for ln in f
                 if ln.strip() and not ln.strip().startswith("#")]
    if not cands:
        raise SystemExit("file khong co phuong an nao")

    print(f"cau hinh: {cfg}")
    print(f"{len(cands)} phuong an, gom vao MOT lan goi model\n")
    _in_contour(cands, cfg)
    cache = os.path.join(BUILD, "tts")
    tts.prefetch(cands, cache, cfg)

    os.makedirs(OUT, exist_ok=True)
    rows = []
    for i, t in enumerate(cands, 1):
        wav, adur = tts.speak(t, cache, cfg)
        dst = os.path.join(OUT, f"{i:02d}.wav")
        with open(wav, "rb") as s, open(dst, "wb") as d:
            d.write(s.read())
        m = measure(dst)
        rows.append((i, t, m))

    print(f"\n{'#':>3s} {'dài':>6s} {'khối':>5s} {'khối/giây':>10s} "
          f"{'lỗ chết':>8s} {'tụt đuôi':>9s}  phương án")
    print("-" * 108)
    rate_med = float(np.median([m["rate"] for _, _, m in rows]))
    for i, t, m in rows:
        flag = ""
        if m["rate"] < rate_med * 0.85:
            flag += " DÍNH-ÂM"
        if m["holes"]:
            flag += f" LỖ{m['hole_max']:.0f}ms"
        if m["tail"] <= -85:
            flag += " ĐUÔI-MỜ"
        print(f"{i:3d} {m['dur']:5.2f}s {m['blocks']:5d} {m['rate']:9.2f} "
              f"{m['holes']:8d} {m['tail']:+8.1f}%  {t[:52]}{flag}")
    print("-" * 108)
    print(f"trung vị khối/giây = {rate_med:.2f}; thấp hơn 85% mức đó là đáng ngờ")
    print(f"file nghe thử: {OUT}")


if __name__ == "__main__":
    main()
