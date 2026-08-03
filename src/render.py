"""CLI render: screenplay YAML -> mp4 1080x1920 co giong doc tieng Viet.

    python src/render.py screenplays/cache-invalidation.yaml
    python src/render.py <yaml> --stills          # 1 PNG/canh de soi style
    python src/render.py <yaml> --stills --scene 3
    python src/render.py <yaml> --no-audio        # render nhanh, khong goi TTS

Toi uu: frame nao co trang thai y het frame truoc thi dung lai frame cu,
khong ve lai. Video kieu nay giu hinh rat nhieu nen tiet kiem dang ke.
"""
import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib

import yaml
from PIL import Image, ImageDraw

import tts
from style import FPS, H, SS, W, clamp

# theme -> module dung de dung canh. Moi module tu lo `background()`, `build()`
# va hang so FADE (0 = cat thang khong mo dan).
THEMES = {"phongtoi": "phongtoi", "brutalist": "brutal",
          "whiteboard": "scenes"}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")

PRE_PAD = 0.45    # im lang truoc khi giong doc vao
POST_PAD = 0.85   # giu hinh sau khi doc xong
MIN_SCENE = 2.8

THEME = None      # module theme dang dung
FADE = 0.30       # xoa bang cuoi canh; brutalist dat 0 = cat thang


def use_theme(name):
    global THEME, FADE
    mod = THEMES.get(name)
    if not mod:
        raise SystemExit(
            f"theme khong biet: {name!r}. Co: {', '.join(sorted(THEMES))}")
    THEME = importlib.import_module(mod)
    FADE = getattr(THEME, "FADE", 0.30)
    return THEME


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    if isinstance(doc, list):
        doc = {"scenes": doc}
    if not doc.get("scenes"):
        raise SystemExit("screenplay khong co canh nao")
    for i, sp in enumerate(doc["scenes"], 1):
        if "scene" not in sp:
            raise SystemExit(f"canh {i} thieu truong 'scene'")
        if sp.get("caption") is None and sp.get("narration"):
            sp["caption"] = sp["narration"]
    return doc


def prepare(doc, use_audio):
    """Sinh TTS, do duration, chot thoi luong tung canh."""
    cache = os.path.join(BUILD, "tts")
    voice = doc.get("voice", "female")
    rate = doc.get("rate", "+6%")
    plan = []
    for i, sp in enumerate(doc["scenes"], 1):
        wav, adur = (None, 0.0)
        if use_audio:
            wav, adur = tts.speak(sp.get("narration", ""), cache, voice, rate)
        if adur:
            dur = PRE_PAD + adur + POST_PAD
        else:
            dur = sp.get("duration", 4.0)
        dur = max(MIN_SCENE, sp.get("min_duration", 0), dur)
        plan.append({"spec": sp, "dur": dur, "wav": wav, "adur": adur})
        print(f"  canh {i:02d} [{sp['scene']:9s}] {dur:5.2f}s"
              f"{'  (audio %.2fs)' % adur if adur else ''}")
    return plan


def render_scene_frame(bg, els, t):
    base = bg.copy()
    d = ImageDraw.Draw(base)
    for start, edur, fn in els:
        p = clamp((t - start) / edur) if edur > 0 else 1.0
        if p <= 0:
            continue
        fn(base, d, p)
    return base


def signature(els, t, dur):
    sig = []
    for start, edur, _ in els:
        p = clamp((t - start) / edur) if edur > 0 else 1.0
        sig.append(round(p, 3))
    fade = round(clamp((dur - t) / FADE), 3) if (FADE > 0 and t > dur - FADE) else 1.0
    sig.append(fade)
    return tuple(sig)


def stills(doc, plan, only=None):
    """Xuat 1 PNG/canh o thoi diem hinh day nhat -> de soi style bang mat."""
    outdir = os.path.join(BUILD, "stills")
    os.makedirs(outdir, exist_ok=True)
    bg = THEME.background()
    for i, item in enumerate(plan, 1):
        if only and i != only:
            continue
        els = THEME.build(item["spec"], item["dur"], doc)
        # tranh lay dung luc dai quet chuyen canh dang phu kin khung
        tail = max(FADE, getattr(THEME, "WIPE_OUT", 0.0))
        t = item["dur"] - tail - 0.10
        img = render_scene_frame(bg, els, t)
        img.convert("RGB").resize((W, H), Image.LANCZOS).save(
            os.path.join(outdir, f"scene-{i:02d}-{item['spec']['scene']}.png"))
        print(f"  stills: canh {i:02d} -> {item['spec']['scene']}")
    print("xuat tai:", outdir)


def render(doc, plan, out_path, use_audio):
    import imageio_ffmpeg

    total = sum(p["dur"] for p in plan)
    nframes = int(round(total * FPS))
    print(f"\ntong: {total:.2f}s = {nframes} frame @ {FPS}fps"
          f"  (ve o {W*SS}x{H*SS} roi thu nho)")

    # ---- audio: im lang + giong doc + im lang, noi lien mach
    audio_path = None
    if use_audio and any(p["wav"] for p in plan):
        segs = []
        for p in plan:
            if p["wav"]:
                tail = p["dur"] - PRE_PAD - p["adur"]
                segs += [("silence", PRE_PAD), ("wav", p["wav"]),
                         ("silence", max(0.0, tail))]
            else:
                segs.append(("silence", p["dur"]))
        audio_path = tts.concat(segs, os.path.join(BUILD, "voice.wav"))
        print("audio:", audio_path)

    bg = THEME.background()
    built = [THEME.build(p["spec"], p["dur"], doc) for p in plan]

    tmp_video = os.path.join(BUILD, "video-noaudio.mp4")
    writer = imageio_ffmpeg.write_frames(
        tmp_video, (W, H), fps=FPS, codec="libx264", pix_fmt_in="rgb24",
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "18", "-pix_fmt", "yuv420p", "-preset", "medium"])
    writer.send(None)

    bounds = []
    acc = 0.0
    for p in plan:
        bounds.append((acc, acc + p["dur"]))
        acc += p["dur"]

    last_sig = None
    last_bytes = None
    reused = 0
    t0 = time.time()

    for n in range(nframes):
        t = n / FPS
        si = 0
        while si < len(bounds) - 1 and t >= bounds[si][1]:
            si += 1
        local = t - bounds[si][0]
        dur = plan[si]["dur"]
        els = built[si]

        sig = (si,) + signature(els, local, dur)
        if sig == last_sig and last_bytes is not None:
            writer.send(last_bytes)
            reused += 1
            continue

        img = render_scene_frame(bg, els, local)
        if FADE > 0 and local > dur - FADE:
            a = clamp((dur - local) / FADE)
            img = Image.blend(bg, img, a)
        frame = img.convert("RGB").resize((W, H), Image.LANCZOS)
        last_bytes = frame.tobytes()
        last_sig = sig
        writer.send(last_bytes)

        if n % 150 == 0 and n:
            el = time.time() - t0
            eta = el / n * (nframes - n)
            print(f"  frame {n}/{nframes}  ({n/nframes*100:4.1f}%)  "
                  f"da dung lai {reused}  con ~{eta/60:.1f} phut")

    writer.close()
    print(f"video xong trong {(time.time()-t0)/60:.1f} phut, "
          f"dung lai {reused}/{nframes} frame")

    os.makedirs(OUT, exist_ok=True)
    if audio_path:
        subprocess.run(
            [tts.FFMPEG, "-y", "-loglevel", "error", "-i", tmp_video,
             "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", out_path], check=True)
    else:
        subprocess.run([tts.FFMPEG, "-y", "-loglevel", "error", "-i", tmp_video,
                        "-c", "copy", out_path], check=True)
    mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nXONG -> {out_path}  ({mb:.1f} MB, {total:.1f}s, {W}x{H})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("screenplay")
    ap.add_argument("-o", "--out")
    ap.add_argument("--stills", action="store_true",
                    help="chi xuat 1 PNG/canh de soi style")
    ap.add_argument("--scene", type=int, help="chi lam canh so N (voi --stills)")
    ap.add_argument("--no-audio", action="store_true")
    ap.add_argument("--theme", choices=sorted(THEMES),
                    help="ghi de theme khai bao trong screenplay")
    a = ap.parse_args()

    os.makedirs(BUILD, exist_ok=True)
    doc = load(a.screenplay)
    theme_name = a.theme or doc.get("theme", "whiteboard")
    use_theme(theme_name)
    use_audio = not a.no_audio and not a.stills
    print(f"screenplay: {a.screenplay}  ({len(doc['scenes'])} canh)  "
          f"theme={theme_name}")
    plan = prepare(doc, use_audio)

    if a.stills:
        stills(doc, plan, a.scene)
        return

    out = a.out or os.path.join(
        OUT, os.path.splitext(os.path.basename(a.screenplay))[0] + ".mp4")
    render(doc, plan, out, use_audio)


if __name__ == "__main__":
    main()
