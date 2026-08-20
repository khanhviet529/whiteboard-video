"""
Do "san" trong giong doc: quet ca file, xep hang cac cho dang nghi nhat.

    python soi_san.py duong/dan/audio.wav
    python soi_san.py "D:/Project/whiteboard-video/out/cache-stale-omnivoice.mp4"

Do BA loai loi khac nhau. Ly do phai co ba: lan dau tôi chi do loai (3) nen BO SOT
mot lo chet 459ms giua cau - nguoi dung nghe ra, may thi khong. Vung tieng bi chat
vun bi cat thanh nhieu manh ngan roi bi loai, con lo chet thi bi dem la im lang.

  (1) LO CHET     RMS phang li duoi 1e-4 (~ -80 dB) keo dai >=120ms GIUA cau.
                  Im lang tu nhien doc -40..-60 dB va co dao dong; phang li o
                  -90 dB la mot cai ho. Day la loai nang nhat, nghe ro nhat.

  (2) CHAT VUN    Trong cua so 0,8s co >=3 lan tut duoi nguong im lang roi len
                  lai. Tieng con day nhung nua so am gan nhu khong nghe duoc.

  (3) DUOI NHOE   Cao tan (>6kHz) cua 150ms cuoi cum tut >=85% so voi ca cum.
                  Phu am cuoi tieng Viet (-t -c -p -ch) nam o day.

Moc thoi gian in ra dang m:ss.s de doi chieu truc tiep khi xem video.
"""
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np

DEAD_RMS = 1e-4        # nguong "lo chet"
DEAD_MS = 120
CHOP_WIN = 0.8         # cua so xet chat vun
# 3 lan tut / 0,8s la NGUONG QUA LONG: tieng Viet von ngat giua cac am tiet nen
# no bao 36 cho tren mot file 94s, khong xep hang duoc. 5 lan moi la bat thuong.
CHOP_DIPS = 5
TAIL_DROP = -85.0      # % - duoi muc nay coi la duoi nhoe


def load(path):
    """Nhan ca wav va mp4 (mp4 thi rut audio ra file tam bang ffmpeg)."""
    if path.lower().endswith((".mp4", ".m4a", ".mkv", ".mov", ".mp3")):
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ff = "ffmpeg"
        tmp = os.path.join(tempfile.gettempdir(), "soi_san_tmp.wav")
        subprocess.run([ff, "-v", "error", "-y", "-i", path, "-vn", "-ac", "1",
                        "-ar", "24000", "-c:a", "pcm_s16le", tmp], check=True)
        path = tmp
    with wave.open(path, "rb") as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        y = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        y = y.reshape(-1, ch).mean(1)
    return y, sr


def envelope(y, sr, fr=512, hop=128):
    n = 1 + (len(y) - fr) // hop
    e = np.sqrt(np.array([np.mean(y[i * hop:i * hop + fr] ** 2) for i in range(n)]))
    return e, hop


def hf(seg, sr, n_fft=1024, hop=256):
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


def mmss(t):
    return f"{int(t // 60)}:{t % 60:04.1f}"


def scan(path):
    y, sr = load(path)
    env, hop = envelope(y, sr)
    dur = len(y) / sr
    thr = np.percentile(env, 99) * 0.05

    # vung co tieng lien tuc, de biet cai gi la "giua cau" va cai gi la ranh gioi
    quiet = env < thr
    speech, st = [], None
    for i, q in enumerate(quiet):
        if not q and st is None:
            st = i
        elif q and st is not None:
            speech.append((st * hop / sr, i * hop / sr))
            st = None
    if st is not None:
        speech.append((st * hop / sr, len(quiet) * hop / sr))
    # khoang lang DAI (>=1,15s) = ranh gioi canh, moi loi trong do khong tinh
    longsil, st = [], None
    for i, q in enumerate(quiet):
        if q and st is None:
            st = i
        elif not q and st is not None:
            if (i - st) * hop / sr >= 1.15:
                longsil.append((st * hop / sr, i * hop / sr))
            st = None
    def in_boundary(t):
        return any(a - 0.05 <= t <= b + 0.05 for a, b in longsil)

    found = []

    # --- (1) LO CHET ---
    # PHAI phan biet voi im lang CO Y CHEN. `pause_after` chen np.zeros() nen mau
    # dung bang 0 tuyet doi; con lo chet cua model do duoc ~3e-5 - nho nhung KHAC
    # 0. Khong phan biet thi bo do bao het moi khoang nghi hop le thanh loi (lan
    # dau chay ra 35 canh bao rac dung vi the).
    dead = env < DEAD_RMS
    st = None
    for i, d in enumerate(dead):
        if d and st is None:
            st = i
        elif not d and st is not None:
            t0, ms = st * hop / sr, (i - st) * hop / sr * 1000
            if ms >= DEAD_MS and not in_boundary(t0):
                a0, a1 = int(t0 * sr), int((t0 + ms / 1000) * sr)
                zero_frac = float((y[a0:a1] == 0).mean()) if a1 > a0 else 1.0
                if zero_frac < 0.90:      # >=90% mau bang 0 -> im lang chen, bo qua
                    found.append((ms, "LỖ CHẾT", t0,
                                  f"{ms:.0f}ms gần im lặng ({zero_frac*100:.0f}% mẫu =0)"))
            st = None

    # --- (2) CHAT VUN ---
    w = int(CHOP_WIN * sr / hop)
    i = 0
    while i < len(env) - w:
        win = env[i:i + w]
        dips = 0
        prev_low = False
        for v in win:
            low = v < thr
            if low and not prev_low:
                dips += 1
            prev_low = low
        loud = float(np.percentile(win, 90))
        t0 = i * hop / sr
        if dips >= CHOP_DIPS and loud > thr * 3 and not in_boundary(t0):
            found.append((dips * 100.0, "CHẶT VỤN", t0,
                          f"{dips} lần tụt dưới ngưỡng trong {CHOP_WIN}s"))
            i += w          # khong bao trung lap
        else:
            i += max(1, w // 4)

    # --- (3) DUOI NHOE ---
    for a, b in speech:
        if b - a < 0.28:
            continue
        s = y[int(a * sr):int(b * sr)]
        h = hf(s, sr)
        t = hf(s[-int(0.15 * sr):], sr)
        if h <= 0:
            continue
        drop = (t / h - 1) * 100
        if drop <= TAIL_DROP:
            found.append((-drop, "ĐUÔI NHOÈ", a, f"cao tần cuối cụm {drop:+.1f}%"))

    print(f"{os.path.basename(path)}  {mmss(dur)}  ({dur:.1f}s)")
    print(f"ngưỡng im lặng {thr:.5f} | {len(speech)} cụm | "
          f"{len(longsil)} ranh giới cảnh (bỏ qua lỗi trong đó)\n")
    order = {"LỖ CHẾT": 0, "CHẶT VỤN": 1, "ĐUÔI NHOÈ": 2}
    found.sort(key=lambda f: (order[f[1]], -f[0]))
    if not found:
        print("không thấy gì đáng ngờ")
        return
    print(f"{'#':>3s} {'mốc':>8s} {'loại':10s} chi tiết")
    print("-" * 66)
    for k, (score, kind, t0, note) in enumerate(found, 1):
        print(f"{k:3d} {mmss(t0):>8s} {kind:10s} {note}")
    print("-" * 66)
    for kind in ("LỖ CHẾT", "CHẶT VỤN", "ĐUÔI NHOÈ"):
        c = sum(1 for f in found if f[1] == kind)
        print(f"  {kind}: {c}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        scan(p)
        print()
