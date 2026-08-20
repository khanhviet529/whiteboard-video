"""Sinh giong doc tieng Viet qua backend VoiceStudio. Mot engine duy nhat.

    engine: voicestudio   (mac dinh) HTTP POST /generate - giong clone tu doan mau

`engine: omnivoice` van nhan, la ten cu cua duong nay va tu doi thanh
voicestudio - nen screenplay dang khai khong phai sua.

Hai duong da bo:
  * WSL/say.py  - giong hay bi nhieu, khong co seed nen sinh lai la xo so, va moi
                  lan goi phai nap lai model (~8s + warmup 14s).
  * edge-tts    - nhanh (~1s/cau) nhung giong khong dat yeu cau; ca kho giong
                  clone o omnivoice-test sinh ra chinh vi ly do do.

Mat xich quan trong nhat cua tool khong doi: sinh audio TRUOC, do duration THAT,
roi lay do lam thoi luong canh. Khong bao gio canh timing bang tay.

Vong lap nhanh de chot cau chu, sau khi bo edge: tro VS_API sang backend co GPU
(Colab T4 ~3s/cau) roi chay render voi `--audio-only` - bo han buoc dung frame.

Ket qua cache theo hash (noi dung + toan bo cau hinh giong), nen doi mot canh
thi chi sinh lai dung cau do.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
import wave

import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

SR = 48000        # tan so lay mau chuan cho mp4
MIN_AUDIO = 1024  # nho hon nay chac chan la file loi


# ---------------------------------------------------------------- voicestudio
# Backend VoiceStudio (FastAPI). Doi dich bang bien moi truong, khong sua code:
#   VS_API=http://127.0.0.1:3900           backend chay tren may nay
#   VS_API=https://xxx.trycloudflare.com   backend chay tren Colab T4 qua tunnel
VS_API = os.environ.get("VS_API", "http://127.0.0.1:3900").rstrip("/")
VS_TIMEOUT = float(os.environ.get("VS_TIMEOUT", "1800"))
# Cho backend nap xong ML runtime. Backend tu dat ngan sach 300s cho pha do
# (`Startup watchdog armed: ... if startup exceeds 300s`), nen 300 la con so
# dung chu khong phai so tron.
VS_CHO_KHOI_DONG = float(os.environ.get("VS_CHO_KHOI_DONG", "300"))

# Kho giong clone: `<repo>/giong/manifest.json`, moi giong co file wav va
# ref_text. Gui CA HAI sang /generate - ref_text giup model can chinh dung doan
# mau, thieu no thi clone kem hon. Duong WSL cu khong gui truong nay.
#
# Duong dan TUONG DOI theo repo, khong tro sang D:\omnivoice-test nua: repo do la
# noi ra doi cua duong WSL/say.py da bo, va de tai san cua tool nam trong mot repo
# khac nghia la clone repo nay ve may khac la khong chay duoc. Kho giong la thu
# KHONG the mat: 90 video phai dung dung mot clip mau, mat clip la mat giong kenh.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VS_VOICES = os.environ.get("VS_VOICES", os.path.join(ROOT, "giong", "manifest.json"))

# Nguoi dung nghe bon giong tren cung mot doan roi chon. Quyet dinh mot lan cho
# ca 90 so, xem VIET-KICH-BAN.md muc "chon giong".
VS_DEFAULT_VOICE = "namtre_v2"

# Khai TUONG MINH thay vi nhan mac dinh cua backend. Upstream co hai mac dinh khac
# nhau cho cung mot model - `/generate` dung 16, con duong audiobook dung 32
# ("quality" preset cua model). Nhan ngam thi mot lan upstream doi mac dinh la ca
# 90 video sinh lai voi chat luong khac ma khong ai biet. Va vi no nam trong cfg
# nen no vao KHOA CACHE: doi gia tri o day la sinh lai, dung nhu ky vong.
VS_DEFAULT_NUM_STEP = 16

# Khoang nghi giua cau, don vi ms. 0 = tat (giu nguyen hanh vi truoc khi co co nay).
#
# Vi sao can: do tren cung mot screenplay, tach duoc thoi gian doc thanh hai phan
#   edge-tts : 49,4 ms/ky tu  +  772 ms/cau
#   /generate: 48,7 ms/ky tu  +   -7 ms/cau
# Toc do doc GIONG NHAU trong 1,4%; toan bo chenh lech 31 giay tren video 2 phut
# nam o khoang nghi giua cau. Cong nghiem thu cung xac nhan: `0.00 lo chet/phut`
# nghia la KHONG co khoang lang nao >=300ms trong 73 giay voi 38 cau - cac cau noi
# lien nhau. `pause_scale: 0.70` cua say.py truoc day rut ngan khoang nghi; gio
# khong con gi de rut, phai chen vao.
#
# Chon gia tri - DO THAT tren T4, cau 3 menh de, seed co dinh:
#
#   pause_ms |  audio  | them moi ranh gioi
#         0  |  4,11s  |     0 ms   (tat marker: MOT lan sinh duy nhat)
#       100  |  5,06s  |   475 ms
#       200  |  5,26s  |   575 ms
#       400  |  5,66s  |   775 ms
#
# Hieu = pause_ms + 375 ms, offset dung 375 o ca ba diem. 375 ms do la im lang
# dau/duoi ma model tu them cho MOI span sinh rieng - bat marker la moi cau thanh
# mot lan sinh, nen khong the xuong duoi 375 ms mot khi da bat.
#
# Doi chieu: ban omnivoice cu ~1p40 so voi clone 1p25 tren cung screenplay, tuc
# ~400 ms/cau -> `pause_ms: 25` la ve dung nhip da quen. edge la ~772 ms/cau ->
# `pause_ms: 400`. Thoi gian sinh tang ~50% (3,9s -> 5,5-6,4s cho 3 cau).
VS_DEFAULT_PAUSE_MS = 0

# Ranh gioi cau de chen marker. Co y GIONG regex du phong trong lint.py va
# thu_cau.py - ba cho phai cat giong nhau, khong thi so dem cau lech nhau.
_RANH_CAU = re.compile(r"(?<=[.!?…])\s+")

# say.py co `style`, `mode`, `pause_scale`; /generate khong co cai nao. Tuyet doi
# KHONG doi chung sang `instruct`: instruct la tu vung thiet ke tieng Anh da qua
# validator, nhet "camhung" vao la 400 "Unsupported instruct items". Sac thai bay
# gio den tu doan MAU (ref_audio), khong tu tham so.
VS_BO_QUA = ("style", "mode", "pause_scale")

_VOICES = None
_DA_NOI = set()
_DA_KIEM = set()


def _kho_giong():
    global _VOICES
    if _VOICES is None:
        try:
            with open(VS_VOICES, encoding="utf-8") as f:
                _VOICES = json.load(f)
        except Exception as e:
            raise SystemExit(f"khong doc duoc kho giong {VS_VOICES}: {e}")
    return _VOICES


def _mau_giong(ten):
    """Ten giong -> (duong_dan_wav, ref_text). Bao kem danh sach neu sai ten."""
    reg = _kho_giong()
    m = reg.get(ten)
    if not m:
        raise SystemExit(f"khong co giong {ten!r} trong {VS_VOICES}.\n"
                         f"co: {', '.join(sorted(reg))}")
    goc = os.path.dirname(os.path.dirname(os.path.abspath(VS_VOICES)))
    wav = os.path.join(goc, str(m["file"]).replace("/", os.sep))
    if not os.path.exists(wav):
        raise SystemExit(f"giong {ten!r} tro toi file khong ton tai: {wav}")
    return wav, m.get("ref_text") or None


def kiem_backend():
    """Goi /health mot lan truoc khi sinh. Tra ve dict, hoac dung han neu chet.

    Ly do phai co: mot luot render 90 canh la vai chuc phut. Truoc day duong WSL
    that bai ngay o cau dau nen biet lien; bay gio dich la mot URL - tunnel Colab
    het han hay quen bat backend deu chi lo ra khi da doi. Kiem truoc mot lan.

    In ca `device` vi day la cho de sai am tham nhat: cung mot URL, cung mot ket
    qua, chi khac cpu voi cuda la thoi gian render lech 40 lan.
    """
    global _DA_KIEM
    # Backend khoi dong hai pha: socket mo sau ~1s nhung /health tra 503 kem
    # `{"status":"starting","step":...}` cho tan khi nap xong PyTorch va DB.
    # Chay `bun run dev` roi go lenh ngay la roi dung vao cua so do - va lan
    # dau gap thi thong bao "chua bat backend" chi sai huong hoan toan. Nen
    # doi han: 503 co than "starting" thi CHO, moi thu khac moi la loi.
    han = time.time() + VS_CHO_KHOI_DONG
    buoc_da_in = None
    while True:
        try:
            with urllib.request.urlopen(f"{VS_API}/health", timeout=10) as r:
                tt = json.load(r)
            break
        except urllib.error.HTTPError as e:
            than = {}
            try:
                than = json.loads(e.read().decode("utf-8", "replace"))
            except Exception:
                pass
            if e.code != 503 or than.get("status") != "starting":
                raise SystemExit(
                    f"{VS_API}/health tra ve HTTP {e.code}: "
                    f"{str(than)[:200] or '(khong co than)'}")
            if time.time() > han:
                raise SystemExit(
                    f"backend tai {VS_API} khoi dong qua "
                    f"{VS_CHO_KHOI_DONG:.0f}s ma chua xong (dang o buoc "
                    f"{than.get('step')!r}).\n"
                    f"  Xem log cua `bun run dev`, hoac nang "
                    f"VS_CHO_KHOI_DONG.")
            if than.get("step") != buoc_da_in:
                buoc_da_in = than.get("step")
                print(f"  backend dang khoi dong: "
                      f"{than.get('label') or buoc_da_in} - cho...")
            time.sleep(3)
        except Exception as e:
            raise SystemExit(
                f"khong goi duoc {VS_API}/health "
                f"({type(e).__name__}: {e}).\n"
                f"  May nay: cd D:\\Project\\VoiceStudio && bun run dev\n"
                f"  Colab:   dat VS_API=https://<ten>.trycloudflare.com")
    if VS_API not in _DA_KIEM:
        _DA_KIEM.add(VS_API)
        print(f"  backend: {VS_API}  device={tt.get('device')}  "
              f"v{tt.get('version')}")
        if str(tt.get("device", "")).startswith("cpu"):
            print("  (device=cpu - sinh giong se cham nhu duong WSL cu; "
                  "tro VS_API sang may co GPU neu render ca video)")
    return tt


# ---------------------------------------------------------------- cau hinh giong
def config(doc):
    """Doc cau hinh giong tu screenplay. Dung lam ca khoa cache."""
    doc = doc or {}
    # Mac dinh la voicestudio, khong con edge: 91 screenplay khong khai `engine:`
    # nen mac dinh chinh la thu chung dung.
    eng = str(doc.get("engine", "voicestudio")).lower()
    if eng in ("omnivoice", "voicestudio", "vs"):
        eng = "voicestudio"
    if eng == "edge":
        raise SystemExit(
            "engine `edge` da bo khoi tool. Giong edge-tts khong dat yeu cau -\n"
            "do la ly do kho giong clone o D:\\omnivoice-test ra doi.\n"
            "Bo dong `engine: edge` trong screenplay (mac dinh gio la voicestudio),\n"
            "hoac `git log -- src/tts.py` neu can lay lai ban cu.")
    if eng != "voicestudio":
        raise SystemExit(f"engine khong biet: {eng!r}. Chi co: voicestudio")
    # `voice: female` / `male` la ten giong cua edge-tts, con nam trong 90
    # screenplay cu. Engine voicestudio dung ten giong clone trong kho
    # (namtre_v2, namtre_v3...), khong biet nhung ten do - nen van bat o day.
    #
    # Bat o day chu khong de backend bao, va cang khong tu thay bang giong mac
    # dinh: thay ngam thi doi luon KHOA CACHE, nen lan render sau se sinh lai het
    # ma khong ai hieu vi sao.
    # `omni_voice:` de screenplay khai duoc CA HAI engine cung luc: `voice:` cho
    # edge, `omni_voice:` cho voicestudio. Giu nguyen ten khoa cu de 89 screenplay
    # da viet khong phai sua. `voice:` van doc lam duong lui khi khong co
    # `omni_voice:`, nhung ten giong edge thi bi tu choi ngay ben duoi.
    v = doc.get("omni_voice") or doc.get("voice", VS_DEFAULT_VOICE)
    if v in ("female", "male", "nu", "nam"):
        raise SystemExit(
            f"screenplay khai `voice: {v}` - do la ten giong cua edge-tts, kho "
            f"giong clone khong co.\n"
            f"Them `omni_voice: {VS_DEFAULT_VOICE}` (hoac ten khac trong "
            f"{VS_VOICES}).")
    cfg = {"engine": "voicestudio", "voice": v,
           "num_step": doc.get("num_step", VS_DEFAULT_NUM_STEP)}
    if doc.get("pause_ms") is not None:
        cfg["pause_ms"] = int(doc["pause_ms"])
    elif VS_DEFAULT_PAUSE_MS:
        cfg["pause_ms"] = VS_DEFAULT_PAUSE_MS
    for k in ("speed", "seed", "guidance_scale", "effect_preset",
              "denoise", "postprocess"):
        if doc.get(k) is not None:
            cfg[k] = doc[k]
    # style/mode/pause_scale la khai niem cua say.py. Noi to mot lan chu khong bo
    # im: 89 screenplay dang khai chung, va am thanh ra SE khac ban da duyet truoc
    # day. Khong cho vao cfg vi chung khong con anh huong audio - de vao thi khoa
    # cache doi ma tieng khong doi.
    bo = tuple(k for k in VS_BO_QUA if doc.get(k) is not None)
    if bo and bo not in _DA_NOI:
        _DA_NOI.add(bo)
        print(f"  (voicestudio bo qua: {', '.join(bo)} "
              f"- sac thai lay tu doan mau ref_audio)")
    # Tat mac dinh. Ba screenplay dau da viet phien am thang vao `narration`,
    # bat len se doi khoa cache va sinh lai audio DA DUYET.
    if doc.get("phien_am"):
        cfg["phien_am"] = True
    return cfg


def doc_nhu(text, cfg):
    """Van ban DUNG DE DOC. Khac van ban trong screenplay khi bat `phien_am`.

    Goi o DAU moi duong vao (`prefetch`, `speak`) chu khong goi truoc khi bam
    khoa mot cach rieng le: nhu vay khoa cache tinh tren ban DA PHIEN AM, nen
    sua tu dien la audio tu sinh lai. Ap sau khi bam khoa thi doi tu dien ma
    khoa khong doi - dung cai bay ma `speed` trong speak.py da vap.
    """
    if not cfg.get("phien_am") or not text:
        return text
    import phienam
    return phienam.phien_am(text)


def _key(text, cfg):
    # `phien_am` KHONG vao khoa: chinh van ban da bien doi roi, nen bat co them
    # no vao thi mot screenplay khong co tu nao can phien am cung bi doi khoa va
    # sinh lai audio y het. Con khi CO tu can phien am thi van ban khac nhau da
    # du lam khoa khac nhau.
    c = {k: v for k, v in cfg.items() if k != "phien_am"}
    blob = json.dumps({"t": text, **c}, ensure_ascii=False, sort_keys=True)
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:16]


def _wav_path(cache_dir, text, cfg):
    return os.path.join(cache_dir, f"{_key(text, cfg)}.wav")


def _to_48k_stereo(src, dst):
    """Chuan hoa ve 48k stereo. Ghi ra file TAM roi doi ten.

    Bat buoc: /generate tra ve 24k mono, con `concat()` ghi thang byte nen moi
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


# ---------------------------------------------------------------- voicestudio
def _chen_nghi(text, cfg):
    """Chen `[pause Nms]` sau moi cau, tru cau cuoi.

    Backend parse marker nay (`omnivoice/utils/text.py::parse_pause_markers`,
    issue #276) roi tong hop TUNG SPAN rieng va gap silence vao giua. Nen day cung
    la danh doi: bat `pause_ms` = moi cau thanh mot lan sinh rieng, giong dung
    `mode: tach` cua say.py. Tren T4 mot cau ~3s nen tra duoc; nhung ngu dieu co
    the troi nhe giua cac cau vi chung khong con sinh trong cung mot lan.

    Khong chen sau cau CUOI: `render.py` da cong `post_pad` im lang cuoi moi canh,
    chen thang nua la nghi doi.
    """
    n = int(cfg.get("pause_ms") or 0)
    if n <= 0:
        return text
    cau = [c for c in _RANH_CAU.split(text) if c.strip()]
    if len(cau) < 2:
        return text
    return f" [pause {n}ms] ".join(cau)


def _multipart(fields, duong_wav, du_lieu):
    """Dong goi multipart/form-data bang stdlib.

    Khong dung `requests`: Python cua tool khong co goi do, va them mot phu thuoc
    chi de POST mot file la khong dang.
    """
    bd = "----wbv" + hashlib.sha1(os.urandom(16)).hexdigest()[:16]
    out = bytearray()
    for k, v in fields.items():
        out += (f"--{bd}\r\n"
                f'Content-Disposition: form-data; name="{k}"\r\n\r\n').encode()
        out += str(v).encode("utf-8") + b"\r\n"
    out += (f"--{bd}\r\n"
            f'Content-Disposition: form-data; name="ref_audio"; '
            f'filename="{os.path.basename(duong_wav)}"\r\n'
            f"Content-Type: audio/wav\r\n\r\n").encode()
    out += du_lieu + b"\r\n"
    out += f"--{bd}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={bd}"


def _vs_one(text, cache_dir, cfg, seed=None):
    """Sinh MOT cau qua POST /generate, ghi thang vao cache.

    /generate tra ve WAV bytes truc tiep, kem header X-Audio-Duration /
    X-Gen-Time / X-Seed. Ghi ra file tam roi `_to_48k_stereo` doi ten - cung
    dinh dang cuoi luon la 48k stereo, nen `concat()` ghi thang byte duoc.
    """
    wav_mau, ref_text = _mau_giong(cfg["voice"])
    fields = {"text": _chen_nghi(text, cfg), "language": "Vietnamese"}
    if ref_text:
        fields["ref_text"] = ref_text
    for k in ("num_step", "speed", "guidance_scale", "effect_preset"):
        if cfg.get(k) is not None:
            fields[k] = cfg[k]
    for k, api in (("denoise", "denoise"),
                   ("postprocess", "postprocess_output")):
        if cfg.get(k) is not None:
            fields[api] = "true" if cfg[k] else "false"
    s = seed if seed is not None else cfg.get("seed")
    if s is not None:
        fields["seed"] = int(s)

    with open(wav_mau, "rb") as f:
        body, ctype = _multipart(fields, wav_mau, f.read())
    req = urllib.request.Request(f"{VS_API}/generate", data=body,
                                 headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=VS_TIMEOUT) as r:
            audio = r.read()
            gen = r.headers.get("X-Gen-Time")
            dung = r.headers.get("X-Seed")
    except urllib.error.HTTPError as e:
        chi_tiet = e.read().decode("utf-8", "replace")[:800]
        raise RuntimeError(f"/generate tra ve HTTP {e.code}\n{chi_tiet}\n"
                           f"  cau: {text[:70]}...")
    except urllib.error.URLError as e:
        raise SystemExit(
            f"khong ket noi duoc backend VoiceStudio tai {VS_API} "
            f"({e.reason}).\n"
            f"  May nay: cd D:\\Project\\VoiceStudio && bun run dev\n"
            f"  Colab:   dat VS_API=https://<ten>.trycloudflare.com")
    # Guard hop dong: `/generate` la route NOI BO cua upstream, khong phai API
    # cong khai on dinh. Da co tien le phan ky ngay trong upstream - audiobook.py
    # ghi "take's pinned seed silently did nothing here while /generate honored
    # it". Neu mot ban nang cap ngung ton trong seed thi ta mat tinh tai lap ma
    # khong co dau hieu nao, va vong sinh lai o `_nghiem_thu` cung thanh vo dung.
    # Bat ngay tai lan goi dau, khong doi den luc phat hien qua audio.
    if s is not None and dung is not None and str(dung) != str(int(s)):
        raise SystemExit(
            f"backend khong ton trong seed: gui {int(s)}, tra ve {dung}.\n"
            f"  Ghim seed la co so de re-render ra dung audio cu, va la dieu kien\n"
            f"  de vong sinh lai o nghiemthu.py cai thien duoc gi.\n"
            f"  Kiem lai phien ban backend tai {VS_API}/health truoc khi render.")
    if len(audio) < MIN_AUDIO:
        raise RuntimeError(f"/generate tra ve {len(audio)}B "
                           f"- cau: {text[:70]}...")

    tmp = os.path.join(cache_dir, f"_vs_{os.getpid()}.wav")
    with open(tmp, "wb") as f:
        f.write(audio)
    try:
        _to_48k_stereo(tmp, _wav_path(cache_dir, text, cfg))
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    return gen, dung


# --------------------------------------------------------------------- API
def prefetch(texts, cache_dir, cfg):
    """Sinh truoc moi cau con thieu. Goi MOT lan truoc vong lap canh.

    Mot cho duy nhat lo viec sinh, nen `speak()` chi con doc cache.
    """
    os.makedirs(cache_dir, exist_ok=True)
    texts = [doc_nhu(t, cfg) for t in texts]
    want = [t for t in dict.fromkeys(t.strip() for t in texts if t and t.strip())]
    missing = [t for t in want if not os.path.exists(_wav_path(cache_dir, t, cfg))]
    if not missing:
        if want:
            print(f"  giong doc: {len(want)}/{len(want)} cau lay tu cache")
        # VAN chay cong nghiem thu du khong sinh cau nao. Chi do thi rat nhanh,
        # va cong phai la thu quyet dinh cuoi cung - khong the vi audio nam san
        # trong cache ma bo qua. Cache co the la ban sinh tu truoc khi co cong.
        if cfg["engine"] == "voicestudio" and want:
            _nghiem_thu(want, cache_dir, cfg)
        return
    print(f"  giong doc: {len(want) - len(missing)}/{len(want)} cau co san, "
          f"can sinh {len(missing)} cau")
    if cfg["engine"] == "voicestudio":
        kiem_backend()
        t0 = time.time()
        for n, t in enumerate(missing, 1):
            gen, dung = _vs_one(t, cache_dir, cfg)
            print(f"    [{n}/{len(missing)}] {gen or '?'}s"
                  f"{f' seed={dung}' if dung else ''}")
        print(f"  voicestudio: xong {len(missing)} cau trong "
              f"{(time.time() - t0) / 60:.1f} phut")
        _nghiem_thu(want, cache_dir, cfg)


def _nghiem_thu(texts, cache_dir, cfg):
    """Do audio vua sinh, sinh lai nhung cau xau nhat neu ca video truot.

    Day la thu thay viec ngoi nghe tung doan. /generate CO seed, nen sinh lai ma
    khong doi seed se ra y het file cu va vong lap khong bao gio cai thien: moi
    vong phai doi seed. Co `seed` trong screenplay thi cong them so vong, khong
    co thi de trong cho server tu chon.

    Gac o muc VIDEO chu khong muc cau: xem `nghiemthu.py`, muc "ban dau toi
    thiet ke sai". Tom tat: tieu chi muc cau tu choi sach ca ban da duyet.

    Sinh lai KHONG bao gio lam xau di - luon so diem roi giu ban tot hon. Xau
    nhat la khong cai thien gi va mat them thoi gian may.
    """
    try:
        import nghiemthu as nt
    except Exception as e:
        print(f"  (bo qua nghiem thu: {type(e).__name__})")
        return
    duong = [_wav_path(cache_dir, t, cfg) for t in texts]
    if not all(os.path.exists(p) for p in duong):
        return
    do = [nt.do(p) for p in duong]
    dat, ty, xau = nt.nghiem_thu(do)
    n_tho = sum(m.get("tho_dem", 0) for m in do)
    print(f"  nghiem thu: {ty:.2f} lo chet/phut (nguong {nt.LO_MOI_PHUT})"
          f" | {n_tho} cuc nhieu -> {'DAT' if dat else 'TRUOT'}")
    if dat or not xau:
        return

    tam = os.path.join(cache_dir, "_thu_lai")
    for vong in range(nt.VONG_TOI_DA):
        chon = [i for i in xau[:nt.SINH_LAI_TOI_DA]]
        if not chon:
            break
        print(f"  sinh lai vong {vong + 1}: {len(chon)} cau xau nhat")
        os.makedirs(tam, exist_ok=True)
        try:
            goc_seed = cfg.get("seed")
            for i in chon:
                _vs_one(texts[i], tam, cfg,
                        seed=(int(goc_seed) + vong + 1)
                        if goc_seed is not None else None)
        except Exception as e:
            print(f"  (sinh lai that bai: {e})")
            break
        for i in chon:
            moi = _wav_path(tam, texts[i], cfg)
            if not os.path.exists(moi):
                continue
            m2 = nt.do(moi)
            if nt.diem(m2) < nt.diem(do[i]):
                os.replace(moi, duong[i])
                do[i] = m2
                print(f"    cau {i + 1}: thay ban tot hon")
            else:
                os.remove(moi)
        dat, ty, xau = nt.nghiem_thu(do)
        n_tho = sum(m.get("tho_dem", 0) for m in do)
        print(f"  sau vong {vong + 1}: {ty:.2f} lo chet/phut"
              f" | {n_tho} cuc nhieu -> {'DAT' if dat else 'van TRUOT'}")
        if dat:
            break
    if os.path.isdir(tam):
        for f in os.listdir(tam):
            os.remove(os.path.join(tam, f))
        os.rmdir(tam)
    if not dat:
        print("  van truot sau khi sinh lai - nghe lai canh dang ngo nhat, "
              "co the la van de o cau chu chu khong o lan sinh")


def speak(text, cache_dir, cfg):
    """text -> (duong_dan_wav, so_giay). Tra ve (None, 0) neu text rong.

    Sau `prefetch()` thi ham nay chi doc cache. Neu vi ly do gi chua co thi no
    tu sinh - duong lui khi ai goi `speak()` truc tiep ma chua prefetch.
    """
    text = doc_nhu((text or "").strip(), cfg)
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
    # thu nhanh mot cau: python src/tts.py voicestudio "Xin chao"
    eng = sys.argv[1] if len(sys.argv) > 1 else "voicestudio"
    txt = sys.argv[2] if len(sys.argv) > 2 else "Xin chào, kiểm tra giọng đọc."
    cfg = config({"engine": eng})
    w, d = speak(txt, os.path.join("build", "tts"), cfg)
    print(f"-> {w}  {d:.2f}s")
