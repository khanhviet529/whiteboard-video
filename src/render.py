"""CLI render: screenplay YAML -> mp4 1080x1920 co giong doc tieng Viet.

    python src/render.py screenplays/cache-invalidation.yaml
    python src/render.py <yaml> --stills          # 1 PNG/canh de soi style
    python src/render.py <yaml> --stills --scene 3
    python src/render.py <yaml> --no-audio        # render nhanh, khong goi TTS

Toi uu: frame nao co trang thai y het frame truoc thi dung lai frame cu,
khong ve lai. Video kieu nay giu hinh rat nhieu nen tiet kiem dang ke.
"""
import argparse
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import importlib

import yaml
from PIL import Image, ImageDraw

import lint
import tts
from style import FPS, H, SS, W, clamp

# theme -> module dung de dung canh. Moi module tu lo `background()`, `build()`
# va hang so FADE (0 = cat thang khong mo dan).
THEMES = {"bench": "bench", "phongtoi": "phongtoi", "brutalist": "brutal",
          "whiteboard": "scenes", "net_ve": "net_ve"}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
OUT = os.path.join(ROOT, "out")

PRE_PAD = 0.45    # im lang truoc khi giong doc vao
POST_PAD = 0.85   # giu hinh sau khi doc xong
MIN_SCENE = 2.8


def pads(doc):
    """(pre, post) - screenplay ghi de duoc bang `pre_pad:` / `post_pad:`.

    Phai cho ghi de vi hai gia tri nay cong lai la 1,3 giay MOI DIEM CAT: mot
    video 13 canh mat 15,6 giay chi de im lang. Muc do chiu duoc con tuy engine
    va tung noi dung, nen de cung trong code la sai cho.
    """
    d = doc or {}
    return float(d.get("pre_pad", PRE_PAD)), float(d.get("post_pad", POST_PAD))


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


# Truong giong mot CANH duoc phep ghi de len cap document. Can cho video co
# hai nhan vat: em mot giong, chi mot giong khac.
GIONG_KEYS = ("engine", "voice", "omni_voice", "style", "mode", "speed",
              "num_step", "pause_scale", "rate", "pitch", "phien_am",
              "seed", "guidance_scale")


def cfg_canh(doc, sp):
    rieng = {k: sp[k] for k in GIONG_KEYS if k in sp}
    return tts.config({**doc, **rieng} if rieng else doc)


def prepare(doc, use_audio):
    """Sinh TTS, do duration, chot thoi luong tung canh."""
    cache = os.path.join(BUILD, "tts")
    cfgs = [cfg_canh(doc, sp) for sp in doc["scenes"]]
    if use_audio:
        # Gom cau theo TUNG cau hinh giong roi sinh moi nhom mot lan. Voi
        # duong WSL cu day la bat buoc (nap model ~8s + warmup ~14s moi
        # process). Voicestudio la server thuong tru nen khong con bat buoc,
        # nhung van gom: moi cau hinh giong la mot doan mau khac va mot khoa
        # cache khac, in theo nhom thi doc log de hon.
        nhom = {}
        for sp, c in zip(doc["scenes"], cfgs):
            nhom.setdefault(json.dumps(c, sort_keys=True, ensure_ascii=False),
                            [c, []])[1].append(sp.get("narration", ""))
        for i, (c, texts) in enumerate(nhom.values(), 1):
            if len(nhom) > 1:
                print(f"  --- giong {i}/{len(nhom)}: {c.get('voice')} "
                      f"/ {c.get('style', '-')}")
            tts.prefetch(texts, cache, c)
    pre, post = pads(doc)
    plan = []
    for i, (sp, cfg) in enumerate(zip(doc["scenes"], cfgs), 1):
        wav, adur = (None, 0.0)
        if use_audio:
            wav, adur = tts.speak(sp.get("narration", ""), cache, cfg)
        if adur:
            dur = pre + adur + post
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
    if hasattr(THEME, "chuan_bi"):
        THEME.chuan_bi(doc)
    bg = THEME.background()
    for i, item in enumerate(plan, 1):
        if only and i != only:
            continue
        els = THEME.build(item["spec"], item["dur"], doc)
        # tranh lay dung luc dai quet chuyen canh dang phu kin khung
        tail = max(FADE, getattr(THEME, "WIPE_OUT", 0.0))
        t = item["dur"] - tail - 0.10
        img = render_scene_frame(bg, els, t)
        _thu_nho(img).save(
            os.path.join(outdir, f"scene-{i:02d}-{item['spec']['scene']}.png"))
        print(f"  stills: canh {i:02d} -> {item['spec']['scene']}")
    print("xuat tai:", outdir)


_DA_CANH_BAO_SS = False


def _thu_nho(img):
    """W*SS x H*SS -> W x H. Bat buoc goi o MOI frame khong dung lai duoc.

    Do tren may nay (PIL 12, anh 2160x3840): LANCZOS 73,7 ms - reduce(2) 7,3 ms,
    tuc 10 lan. Voi video 2 phut @30fps la 265s so voi 26s chi rieng buoc nay,
    nhan len so tien trinh song song.

    `reduce(n)` lay trung binh khoi n*n - dung la bo loc ma supersample can. LANCZOS
    o dung ty le 1/n thi lam viec khac: no sharpening/ringing o bien, nen cho `max`
    lech 34-37/255 do duoc giua hai cach nam o pixel bien chinh la LANCZOS vot qua,
    khong phai reduce lam nhoe. Do lai tren hai canh nhieu chu nhat (probe mono nho,
    statement chu lon): gradient trung binh lech 0,2-0,7%, tuc trong nhieu.

    `reduce` nhan MOI so nguyen, khong rieng 2 - nen dieu kien la "SS nguyen" chu
    khong phai "SS == 2". Vach nhanh/cham o day la 10 lan: neu ai doi SS thanh mot
    so khong nguyen roi im lang roi ve LANCZOS thi render cham 10x ma khong co gi
    bao. Vi vay nhanh roi ve co in canh bao mot lan.
    """
    global _DA_CANH_BAO_SS
    rgb = img.convert("RGB")
    if rgb.size == (W, H):
        return rgb                      # SS=1: khong co gi de thu nho
    if isinstance(SS, int) and SS > 1 and rgb.size == (W * SS, H * SS):
        return rgb.reduce(SS)
    if not _DA_CANH_BAO_SS:
        _DA_CANH_BAO_SS = True
        print(f"  (canh bao: SS={SS!r} khong phai so nguyen >1, hoac anh "
              f"{rgb.size} khong khop {(W * SS, H * SS)} - roi ve LANCZOS, "
              f"cham hon ~10 lan moi frame)")
    return rgb.resize((W, H), Image.LANCZOS)


# --------------------------------------------------------------- dung song song
# Frame phai GHI dung thu tu, nhung TINH thi khong. Cach hien nhien la gui frame
# ve tien trinh chinh de ghi - khong duoc: moi frame 1080x1920x3 = 6,2 MB, 3000
# frame la 18 GB qua pipe, cham hon ca ve tuan tu.
#
# Cach dung: moi tien trinh ENCODE luon doan cua no ra mot file rieng, roi ffmpeg
# concat lai. Khong co frame nao di qua IPC, chi co duong dan file.
#
# Chia theo SO FRAME BANG NHAU chu khong theo canh: hai canh `gantt` dai gap ba
# lan canh khac nen chia theo canh se lech tai nang.
_W = {}

# Ghi de tu dong lenh. Tien trinh con tren Windows la spawn nen KHONG thua huong
# bien module cua tien trinh cha - phai truyen qua `initargs` cua Pool.
_PRESET = "medium"
_FPS = FPS


def _worker_init(theme_name, doc, specs, preset, fps):
    """Moi tien trinh tu dung lai theme va phan tu - closure khong pickle duoc."""
    use_theme(theme_name)
    _W["doc"] = doc
    if hasattr(THEME, "chuan_bi"):
        THEME.chuan_bi(doc)
    _W["bg"] = THEME.background()
    _W["built"] = [THEME.build(sp, d, doc) for sp, d in specs]
    _W["durs"] = [d for _, d in specs]
    _W["preset"] = preset
    _W["fps"] = fps


def _worker_chunk(job):
    """Ve frame [a,b) roi encode ra mot file mp4 rieng. Tra ve duong dan."""
    import imageio_ffmpeg
    k, a, b, path = job
    bg, built, durs = _W["bg"], _W["built"], _W["durs"]
    bounds, acc = [], 0.0
    for d in durs:
        bounds.append((acc, acc + d))
        acc += d

    fps = _W["fps"]
    w = imageio_ffmpeg.write_frames(
        path, (W, H), fps=fps, codec="libx264", pix_fmt_in="rgb24",
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "18", "-pix_fmt", "yuv420p",
                       "-preset", _W["preset"]])
    w.send(None)
    last_sig = last_bytes = None
    reused = 0
    for n in range(a, b):
        t = n / fps
        si = 0
        while si < len(bounds) - 1 and t >= bounds[si][1]:
            si += 1
        local = t - bounds[si][0]
        dur, els = durs[si], built[si]
        sig = (si,) + signature(els, local, dur)
        if sig == last_sig and last_bytes is not None:
            w.send(last_bytes)
            reused += 1
            continue
        img = render_scene_frame(bg, els, local)
        if FADE > 0 and local > dur - FADE:
            img = Image.blend(bg, img, clamp((dur - local) / FADE))
        last_bytes = _thu_nho(img).tobytes()
        last_sig = sig
        w.send(last_bytes)
    w.close()
    return k, path, b - a, reused


def render_parallel(doc, plan, nframes, jobs, theme_name):
    """Dung frame bang nhieu tien trinh, tra ve duong dan video chua co tieng."""
    import multiprocessing as mp
    import subprocess as sp_

    specs = [(p["spec"], p["dur"]) for p in plan]
    edges = [round(nframes * i / jobs) for i in range(jobs + 1)]
    parts = [(k, edges[k], edges[k + 1],
              os.path.join(BUILD, f"part-{k:02d}.mp4"))
             for k in range(jobs) if edges[k + 1] > edges[k]]

    t0 = time.time()
    print(f"  dung {len(parts)} doan song song tren {jobs} tien trinh...")
    with mp.Pool(jobs, initializer=_worker_init,
                 initargs=(theme_name, doc, specs, _PRESET, _FPS)) as pool:
        done = []
        for k, path, n, reused in pool.imap_unordered(_worker_chunk, parts):
            done.append((k, path))
            print(f"    doan {k:02d} xong: {n} frame, dung lai {reused}", flush=True)
    done.sort()

    lst = os.path.join(BUILD, "parts.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for _, p in done:
            f.write(f"file '{os.path.abspath(p)}'\n")
    out = os.path.join(BUILD, "video-noaudio.mp4")
    sp_.run([tts.FFMPEG, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
             "-i", lst, "-c", "copy", out], check=True)
    for _, p in done:
        os.remove(p)
    os.remove(lst)
    print(f"  dung frame xong trong {(time.time() - t0) / 60:.1f} phut")
    return out


def render(doc, plan, out_path, use_audio, jobs=1, theme_name=None):
    import imageio_ffmpeg

    total = sum(p["dur"] for p in plan)
    nframes = int(round(total * _FPS))
    print(f"\ntong: {total:.2f}s = {nframes} frame @ {_FPS}fps"
          f"  (ve o {W*SS}x{H*SS} roi thu nho, preset {_PRESET})")

    # ---- audio: im lang + giong doc + im lang, noi lien mach
    audio_path = None
    if use_audio and any(p["wav"] for p in plan):
        pre, _ = pads(doc)     # PHAI dung cung gia tri voi prepare(), khong thi
        segs = []              # audio lech khoi hinh
        for p in plan:
            if p["wav"]:
                tail = p["dur"] - pre - p["adur"]
                segs += [("silence", pre), ("wav", p["wav"]),
                         ("silence", max(0.0, tail))]
            else:
                segs.append(("silence", p["dur"]))
        audio_path = tts.concat(segs, os.path.join(BUILD, "voice.wav"))
        print("audio:", audio_path)

    if jobs > 1:
        tmp_video = render_parallel(doc, plan, nframes, jobs, theme_name)
        _mux(tmp_video, audio_path, out_path, total)
        return

    if hasattr(THEME, "chuan_bi"):
        THEME.chuan_bi(doc)
    bg = THEME.background()
    built = [THEME.build(p["spec"], p["dur"], doc) for p in plan]

    tmp_video = os.path.join(BUILD, "video-noaudio.mp4")
    writer = imageio_ffmpeg.write_frames(
        tmp_video, (W, H), fps=_FPS, codec="libx264", pix_fmt_in="rgb24",
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", "18", "-pix_fmt", "yuv420p",
                       "-preset", _PRESET])
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
        t = n / _FPS
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
        frame = _thu_nho(img)
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

    _mux(tmp_video, audio_path, out_path, total)


def _mux(tmp_video, audio_path, out_path, total):
    """Ghep tieng vao hinh. Dung chung cho ca nhanh tuan tu va song song."""
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
    # Vong lap nghe: bo han buoc dung frame (~10 phut) va chi sinh dung canh dang
    # sua. Voi voicestudio tren GPU, sinh 1 cau mat vai giay so voi ~45 phut
    # ca video, nen day la cach duy nhat de thu loi doc nhieu lan trong mot
    # buoi.
    ap.add_argument("--audio-only", action="store_true",
                    help="chi xuat wav loi doc, khong dung video")
    ap.add_argument("--scenes",
                    help="chi lam cac canh nay, vi du 8 hoac 4,8,11")
    ap.add_argument("--theme", choices=sorted(THEMES),
                    help="ghi de theme khai bao trong screenplay")
    ap.add_argument("--no-lint", action="store_true",
                    help="bo qua buoc kiem screenplay")
    ap.add_argument("--strict", action="store_true",
                    help="dung lai neu kiem thay LOI")
    # Ghi de cau hinh giong tu CLI -> doi giong khong phai nhan ban screenplay.
    # `omnivoice` la ten cu, tts.config() tu doi thanh `voicestudio`. `edge` da
    # bo khoi tool - de trong day thi tts.config() bao loi kem huong dan.
    ap.add_argument("--engine", choices=["voicestudio", "omnivoice"])
    ap.add_argument("--voice")
    ap.add_argument("--style",
                    help="chi con y nghia voi duong WSL cu; voicestudio bo qua")
    ap.add_argument("--tts-mode", choices=["lien", "tach"],
                    help="chi con y nghia voi duong WSL cu; voicestudio bo qua")
    ap.add_argument("--num-step", type=int,
                    help="voicestudio: it hon = nhanh hon (mac dinh 16)")
    # Ghim seed = tai lap duoc dung audio cu. Duong WSL khong co, nen truoc day
    # doi mot chu trong narration la ca canh sinh lai mot giong khac.
    ap.add_argument("--seed", type=int,
                    help="voicestudio: ghim seed de re-render ra dung audio cu")
    # Doi dich khong can dat bien moi truong: --vs-api tien hon khi tunnel Colab
    # doi URL moi lan mo lai session.
    ap.add_argument("--vs-api",
                    help="URL backend VoiceStudio (mac dinh $VS_API hoac "
                         "http://127.0.0.1:3900)")
    # Hai co toi uu thoi gian dung.
    #
    # `--preset`: preset nhanh tat bot phan tich nen chat luong TREN MOI BIT giam;
    # CRF giu muc tieu chat luong, nen ket qua la chat luong xap xi bang nhau va
    # FILE TO HON. Noi "khong doi chat luong" la noi tat: neu co luc so dung luong
    # giua hai luot render ma quen preset khac nhau thi con so se gay nham.
    #
    # `--fps`: it frame hon nen nhanh hon, nhung hat thoi gian tho hon (50ms o
    # 20fps so voi 33ms o 30fps). Thoi luong canh sinh tu audio (so thuc) con so
    # frame la round(tong * FPS), nen phan du lam tron lon hon -> audio co the lech
    # hinh mot chut. O 30fps do duoc khop 0,00s. Chi dung cho ban nhap; dung dung
    # `--fps 20` cho ban cuoi roi di do sync.
    ap.add_argument("--preset", default="medium",
                    help="x264 preset: veryfast cho ban nhap (file to hon, chat "
                         "luong xap xi), medium cho ban cuoi")
    ap.add_argument("--fps", type=int,
                    help="ghi de FPS (mac dinh 30). 20 cho ban nhap - dung dung "
                         "cho ban cuoi vi lam tron thoi luong tho hon")
    ap.add_argument("-j", "--jobs", type=int, default=1,
                    help="so tien trinh dung frame song song (0 = tu chon theo so nhan)")
    a = ap.parse_args()

    os.makedirs(BUILD, exist_ok=True)
    doc = load(a.screenplay)
    if a.vs_api:
        tts.VS_API = a.vs_api.rstrip("/")
    for k, v in (("engine", a.engine), ("voice", a.voice), ("style", a.style),
                 ("mode", a.tts_mode), ("num_step", a.num_step),
                 ("seed", a.seed)):
        if v is not None:
            doc[k] = v
    # `--voice` phai ghi de CA `omni_voice:` khai trong screenplay. Khong lam vay
    # thi tren 89 screenplay dang khai `omni_voice: namtre_v2`, co `--voice
    # namtre_v3` la MOT NO-OP IM LANG: tts.config() doc `omni_voice` truoc, nen
    # gia tri tren dong lenh bi bo qua ma khong co dong canh bao nao. Doi lai:
    # cai gi go tren dong lenh thi thang.
    if a.voice is not None:
        doc["omni_voice"] = a.voice
    theme_name = a.theme or doc.get("theme", "whiteboard")
    use_theme(theme_name)
    use_audio = not a.no_audio and not a.stills
    print(f"screenplay: {a.screenplay}  ({len(doc['scenes'])} canh)  "
          f"theme={theme_name}")

    # Kiem TRUOC khi ton 10 phut render. Canh mo phong khong tu kiem duoc bang
    # mat: mot moc `at` lech chi lam animation noi sai chu khong lam no gay.
    if not a.no_lint:
        nerr = lint.report(doc)
        if nerr and a.strict:
            raise SystemExit("dung lai vi --strict va co LOI")

    # Loc canh TRUOC khi prepare(): loc sau thi van phai sinh giong het 13 cau,
    # tuc mat het y nghia cua vong lap nghe nhanh.
    if a.scenes:
        want = [int(x) for x in a.scenes.replace(" ", "").split(",") if x]
        bad = [i for i in want if not 1 <= i <= len(doc["scenes"])]
        if bad:
            raise SystemExit(f"canh khong ton tai: {bad} "
                             f"(screenplay co {len(doc['scenes'])} canh)")
        doc["scenes"] = [doc["scenes"][i - 1] for i in want]
        print(f"  chi lam canh: {', '.join(map(str, want))}")

    plan = prepare(doc, use_audio)

    if a.stills:
        stills(doc, plan, a.scene)
        return

    if a.audio_only:
        if not any(p["wav"] for p in plan):
            raise SystemExit("khong co giong doc nao (dung --no-audio?)")
        pre, _ = pads(doc)
        segs = []
        for p in plan:
            if p["wav"]:
                segs += [("silence", pre), ("wav", p["wav"]),
                         ("silence", max(0.0, p["dur"] - pre - p["adur"]))]
            else:
                segs.append(("silence", p["dur"]))
        os.makedirs(OUT, exist_ok=True)
        stem = os.path.splitext(os.path.basename(a.screenplay))[0]
        if a.scenes:
            stem += "-canh" + a.scenes.replace(",", "_")
        out = a.out or os.path.join(OUT, stem + ".wav")
        tts.concat(segs, out)
        total = sum(p["dur"] for p in plan)
        mb = os.path.getsize(out) / 1024 / 1024
        print(f"\nXONG (chi audio) -> {out}  ({mb:.1f} MB, {total:.1f}s)")
        return

    # Doi engine thi thoi luong canh doi theo -> file ra phai co ten khac, khong
    # thi ban edge da render vua bi ghi de mat.
    stem = os.path.splitext(os.path.basename(a.screenplay))[0]
    if a.engine:
        stem += "-" + a.engine
    out = a.out or os.path.join(OUT, stem + ".mp4")
    # Chua het nhan: encode cua ffmpeg trong moi tien trinh cung an CPU, lay het
    # nhan thi cac tien trinh gianh nhau va cham hon.
    global _PRESET, _FPS
    _PRESET = a.preset
    if a.fps:
        _FPS = a.fps
    jobs = a.jobs if a.jobs > 0 else max(1, (os.cpu_count() or 2) - 2)
    render(doc, plan, out, use_audio, jobs=jobs, theme_name=theme_name)


if __name__ == "__main__":
    main()
