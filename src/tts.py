"""Sinh giong doc tieng Viet. Hai engine, chon bang `engine:` trong screenplay.

    engine: edge        (mac dinh) edge-tts, mien phi, nhanh, khong can cai gi
    engine: omnivoice   OmniVoice qua WSL - giong clone tu mau, tu nhien hon

Mat xich quan trong nhat cua tool khong doi: sinh audio TRUOC, do duration THAT,
roi lay do lam thoi luong canh. Khong bao gio canh timing bang tay.

Hai engine khac nhau o mot cho anh huong toi thiet ke:

  edge       goi tung cau, nhanh (~1s/cau), goi lai bao nhieu lan cung duoc
  omnivoice  nap model ~8s + warmup, RTF 10-30 tren CPU. Goi tung cau la tu sat:
             13 cau = 13 lan nap model. Nen phai GOM het cau con thieu vao MOT
             lan goi process -> xem `prefetch()`.

Ket qua cache theo hash (noi dung + toan bo cau hinh giong), nen doi mot canh
thi chi sinh lai dung cau do.
"""
import asyncio
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import wave

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

SR = 48000        # tan so lay mau chuan cho mp4
MIN_AUDIO = 1024  # nho hon nay chac chan la file loi
TRIES = 4         # edge-tts thi thoang tra ve rong -> thu lai

EDGE_VOICES = {
    "female": "vi-VN-HoaiMyNeural",
    "male": "vi-VN-NamMinhNeural",
}

# ------------------------------------------------------------------- omnivoice
# Duong dan lay tu D:\omnivoice-test\say.ps1 - giu dong bo neu ben do doi.
OMNI_DISTRO = "Ubuntu"
OMNI_PY = "/root/omnivoice-env/bin/python"
OMNI_SAY = "/mnt/d/omnivoice-test/say.py"
OMNI_HF = "/mnt/d/hf-cache"     # khong truyen thi model 2,45 GB tai lai vao VHDX
OMNI_DEFAULT_VOICE = "namtre_v3"
OMNI_DEFAULT_STYLE = "tunhien"


def _to_wsl(path):
    """D:\\a\\b -> /mnt/d/a/b. say.ps1 lam viec nay bang PowerShell; o day tu lam
    vi ta goi wsl.exe truc tiep (Python truyen argv sach hon PowerShell)."""
    p = os.path.abspath(path)
    m = re.match(r"^([A-Za-z]):[\\/](.*)$", p)
    if not m:
        return p.replace("\\", "/")
    return f"/mnt/{m.group(1).lower()}/" + m.group(2).replace("\\", "/")


# ---------------------------------------------------------------- cau hinh giong
def config(doc):
    """Doc cau hinh giong tu screenplay. Dung lam ca khoa cache."""
    doc = doc or {}
    eng = str(doc.get("engine", "edge")).lower()
    if eng not in ("edge", "omnivoice"):
        raise SystemExit(f"engine khong biet: {eng!r}. Co: edge, omnivoice")
    if eng == "edge":
        return {"engine": "edge",
                "voice": doc.get("voice", "female"),
                "rate": doc.get("rate", "+6%"),
                "pitch": doc.get("pitch", "+0Hz")}
    cfg = {"engine": "omnivoice",
           "voice": doc.get("voice", OMNI_DEFAULT_VOICE),
           "style": doc.get("style", OMNI_DEFAULT_STYLE)}
    for k in ("num_step", "speed", "pause_scale", "mode"):
        if doc.get(k) is not None:
            cfg[k] = doc[k]
    return cfg


def _key(text, cfg):
    blob = json.dumps({"t": text, **cfg}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def _wav_path(cache_dir, text, cfg):
    return os.path.join(cache_dir, f"{_key(text, cfg)}.wav")


def _to_48k_stereo(src, dst):
    """Chuan hoa ve 48k stereo. Ghi ra file TAM roi doi ten.

    Bat buoc: omnivoice tra ve 24k mono, con `concat()` ghi thang byte nen moi
    doan phai cung dinh dang. Ghi truc tiep vao `dst` thi mot lan ffmpeg fail
    se de lai file hong nam mai trong cache.
    """
    tmp = dst + ".part"
    try:
        # `-f wav` la bat buoc: ffmpeg suy ra dinh dang tu duoi file, ma
        # ".wav.part" thi no khong biet la gi (vang exit -22).
        subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-i", src,
                        "-ar", str(SR), "-ac", "2", "-f", "wav", tmp],
                       check=True)
        if os.path.getsize(tmp) < MIN_AUDIO:
            raise RuntimeError(f"ffmpeg ra file {os.path.getsize(tmp)}B")
        os.replace(tmp, dst)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def duration(wav):
    with wave.open(wav, "rb") as w:
        return w.getnframes() / w.getframerate()


# ------------------------------------------------------------------- edge-tts
async def _edge_synth(text, voice, rate, pitch, out_mp3):
    import edge_tts
    c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch)
    await c.save(out_mp3)


def _edge_one(text, cache_dir, cfg):
    """Sinh mp3 vao file TAM roi moi doi ten. Thu lai neu dich vu tra ve rong.

    Ghi thang vao file dich la mot cai bay: edge-tts thi thoang nem
    `NoAudioReceived`, nhung file rong da kip nam lai trong cache. Lan chay sau
    thay file ton tai nen bo qua buoc sinh, roi ffmpeg vap phai file rong va
    cau do KHONG BAO GIO doc duoc nua - phai vao xoa cache bang tay moi thoat.
    """
    v = EDGE_VOICES.get(cfg["voice"], cfg["voice"])
    mp3 = os.path.join(cache_dir, f"{_key(text, cfg)}.mp3")
    tmp = mp3 + ".part"
    last = None
    for i in range(TRIES):
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
            asyncio.run(_edge_synth(text, v, cfg["rate"], cfg["pitch"], tmp))
            if os.path.getsize(tmp) >= MIN_AUDIO:
                os.replace(tmp, mp3)
                return mp3
            last = RuntimeError(f"edge-tts tra ve file {os.path.getsize(tmp)}B")
        except Exception as e:
            last = e
        time.sleep(1.2 * (i + 1))
    if os.path.exists(tmp):
        os.remove(tmp)
    raise RuntimeError(
        f"khong sinh duoc giong doc sau {TRIES} lan: {last}\n  cau: {text[:70]}…")


# ------------------------------------------------------------------ omnivoice
def _omni_batch(texts, cache_dir, cfg):
    """Sinh NHIEU cau trong MOT lan goi process.

    say.py nhan nhieu text va ghi ra `<base>_1.wav`, `<base>_2.wav`... theo dung
    thu tu tham so (khi chi co MOT text thi ghi thang vao `-o`). Ta dua vao mot
    ten tam roi doi tung file sang ten cache that.

    Phai gom nhu vay vi nap model mat ~8s va cau dau moi process con them warmup
    ~14s; goi tung cau thi rieng chi phi co dinh da vuot thoi gian sinh.
    """
    base = os.path.join(cache_dir, "_omni_batch.wav")
    for f in _batch_files(base, len(texts)):
        if os.path.exists(f):
            os.remove(f)

    cmd = ["wsl.exe", "-d", OMNI_DISTRO, "--", "env", f"HF_HOME={OMNI_HF}",
           OMNI_PY, OMNI_SAY]
    cmd += list(texts)
    cmd += ["--voice", str(cfg["voice"]), "--style", str(cfg["style"]),
            "-o", _to_wsl(base)]
    for k, flag in (("num_step", "--num-step"), ("speed", "--speed"),
                    ("pause_scale", "--pause-scale"), ("mode", "--mode")):
        if cfg.get(k) is not None:
            cmd += [flag, str(cfg[k])]

    print(f"  omnivoice: sinh {len(texts)} cau trong 1 lan goi "
          f"(giong={cfg['voice']} style={cfg['style']})...")
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True)
    out = r.stdout.decode("utf-8", "replace")
    err = r.stderr.decode("utf-8", "replace")
    for ln in out.splitlines():
        if ln.strip().startswith("["):
            print("   ", ln.strip())
    if r.returncode != 0:
        raise RuntimeError(
            f"say.py that bai (ma {r.returncode}).\n{(err or out)[-1500:]}")

    made = _batch_files(base, len(texts))
    missing = [f for f in made if not os.path.exists(f)]
    if missing:
        raise RuntimeError(
            f"say.py chay xong nhung thieu {len(missing)}/{len(texts)} file.\n"
            f"{(out + err)[-1500:]}")
    for text, src in zip(texts, made):
        _to_48k_stereo(src, _wav_path(cache_dir, text, cfg))
        os.remove(src)
    print(f"  omnivoice: xong trong {(time.time() - t0) / 60:.1f} phut")


def _batch_files(base, n):
    if n == 1:
        return [base]
    b, ext = os.path.splitext(base)
    return [f"{b}_{i + 1}{ext}" for i in range(n)]


# --------------------------------------------------------------------- API
def prefetch(texts, cache_dir, cfg):
    """Sinh truoc moi cau con thieu. Goi MOT lan truoc vong lap canh.

    Voi edge thi khong can (goi tung cau van nhanh), nhung van don cache o day
    cho mot cho duy nhat lo viec do.
    """
    os.makedirs(cache_dir, exist_ok=True)
    want = [t for t in dict.fromkeys(t.strip() for t in texts if t and t.strip())]
    missing = [t for t in want if not os.path.exists(_wav_path(cache_dir, t, cfg))]
    if not missing:
        if want:
            print(f"  giong doc: {len(want)}/{len(want)} cau lay tu cache")
        return
    print(f"  giong doc: {len(want) - len(missing)}/{len(want)} cau co san, "
          f"can sinh {len(missing)} cau")
    if cfg["engine"] == "omnivoice":
        _omni_batch(missing, cache_dir, cfg)
    else:
        for t in missing:
            mp3 = _edge_one(t, cache_dir, cfg)
            _to_48k_stereo(mp3, _wav_path(cache_dir, t, cfg))


def speak(text, cache_dir, cfg):
    """text -> (duong_dan_wav, so_giay). Tra ve (None, 0) neu text rong.

    Sau `prefetch()` thi ham nay chi doc cache. Neu vi ly do gi chua co thi no
    tu sinh (duong lui, va la duong duy nhat voi edge khi goi le).
    """
    text = (text or "").strip()
    if not text:
        return None, 0.0
    wav = _wav_path(cache_dir, text, cfg)
    if not os.path.exists(wav):
        prefetch([text], cache_dir, cfg)
    return wav, duration(wav)


def silence(seconds, path):
    """Tao doan im lang de chen truoc/sau moi cau."""
    n = int(SR * seconds)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"\x00\x00\x00\x00" * n)
    return path


def concat(segments, out_path):
    """Noi cac doan wav (48k stereo 16-bit) thanh mot track duy nhat."""
    with wave.open(out_path, "wb") as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        for kind, val in segments:
            if kind == "silence":
                out.writeframes(b"\x00\x00\x00\x00" * int(SR * val))
            else:
                with wave.open(val, "rb") as w:
                    if (w.getnchannels(), w.getframerate(), w.getsampwidth()) \
                            != (2, SR, 2):
                        raise RuntimeError(
                            f"{val} khong phai 48k stereo 16-bit - noi thang byte "
                            f"se ra tieng nhieu. Xoa cache roi sinh lai.")
                    out.writeframes(w.readframes(w.getnframes()))
    return out_path


if __name__ == "__main__":
    # thu nhanh mot cau: python src/tts.py omnivoice "Xin chao"
    eng = sys.argv[1] if len(sys.argv) > 1 else "edge"
    txt = sys.argv[2] if len(sys.argv) > 2 else "Xin chào, kiểm tra giọng đọc."
    cfg = config({"engine": eng})
    w, d = speak(txt, os.path.join("build", "tts"), cfg)
    print(f"-> {w}  {d:.2f}s")
