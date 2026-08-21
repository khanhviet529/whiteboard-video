# -*- coding: utf-8 -*-
"""Quay demo video cho app review cua TikTok.

    py dang/quay.py --thu          dien tap: khong goi mang, khong can key
    py dang/quay.py out/x.mp4      quay that

Tu bat ffmpeg (gdigrab), chay dung thu tu ma reviewer can thay, roi cat thanh
tung file mot scope. Viec cua nguoi quay chi con: dang nhap TikTok khi browser
mo, va bam Enter o vai cho.

Vi sao cat thanh nhieu file thay vi mot file dai: TikTok cho tai 5 file, moi file
<=50MB. Mot file cho mot scope thi reviewer doi chieu duoc ngay, khong phai tua
tim trong video 2 phut.

Chu tren man hinh la TIENG ANH co y - reviewer cua TikTok doc tieng Anh. Terminal
in ra tieng Viet khong ai doc duoc thi coi nhu khong co bang chung.
"""
import argparse
import os
import subprocess
import sys
import time
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiktok as tt  # noqa: E402

tt.bat_utf8()

RONG = 78
# Raw capture ra .mkv chu khong .mp4: mp4 ghi moov atom o CUOI file, nen neu
# tien trinh bi kill giua duong thi file khong mo duoc. mkv thi van xem duoc.
THO = os.path.join(tt.GOC, "quay-tho.mkv")


def _khung(tieu_de, dong):
    """Banner to, de doc duoc trong video sau khi nen."""
    print("\n" + "=" * RONG)
    print("  " + tieu_de.upper())
    print("=" * RONG)
    for d in dong:
        print("  " + d)
    print("=" * RONG + "\n")
    sys.stdout.flush()


def _cho(nhac):
    print(f"\n  >>> {nhac}")
    print("  >>> Roi bam Enter.")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("huy giua duong - file tho van con o " + THO)


def _chay(lenh, thu=False):
    """Chay mot lenh cua tool, de output chay thang ra man hinh dang quay."""
    print(f"$ {' '.join(lenh)}")
    sys.stdout.flush()
    if thu:
        print("  (dien tap: khong goi mang)")
        time.sleep(1.5)
        return 0
    return subprocess.call(lenh)


# ------------------------------------------------------------------- ffmpeg
def _bat_ffmpeg():
    lenh = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "gdigrab", "-framerate", "15", "-i", "desktop",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
            "-pix_fmt", "yuv420p", THO]
    p = subprocess.Popen(lenh, stdin=subprocess.PIPE)
    time.sleep(2)                      # cho ffmpeg vao nhip truoc canh dau
    if p.poll() is not None:
        raise SystemExit("ffmpeg chet ngay khi bat. Chay thu:\n  " + " ".join(lenh))
    return p


def _tat_ffmpeg(p):
    """Gui 'q' thay vi kill: ffmpeg can dong file tu te."""
    try:
        p.stdin.write(b"q")
        p.stdin.flush()
    except OSError:
        pass
    try:
        p.wait(timeout=30)
    except subprocess.TimeoutExpired:
        p.terminate()
        p.wait(timeout=10)


def _cat(a, b, ra):
    """Cat [a, b] tu file tho. Re-encode de cat dung frame, khong lech keyframe."""
    os.makedirs(os.path.dirname(ra) or ".", exist_ok=True)
    lenh = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            # `-ss` truoc `-i` (input seek, nhanh) + `-t` sau `-i` (do dai output).
            # Khong dung `-to` truoc `-i`: tai lieu ffmpeg khong noc ro no tinh tu
            # dau file hay tu `-ss`, va doan sai thi cat lech ca canh.
            "-ss", f"{a:.2f}", "-i", THO, "-t", f"{max(0.1, b - a):.2f}",
            # Cap be rong 1600 de chac chan duoi 50MB, van doc duoc chu terminal.
            # trunc(.../2)*2 vi yuv420p doi kich thuoc chan.
            "-vf", "scale='min(1600,iw)':-2,scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:v", "libx264", "-preset", "slow", "-crf", "28",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", ra]
    if subprocess.call(lenh) != 0:
        return None
    return os.path.getsize(ra)


# -------------------------------------------------------------------- canh
def canh_website(a):
    _khung("1 / 5  official website", [
        "https://khanhviet529.github.io/whiteboard-video/",
        "",
        "This is the Website URL declared in the app settings.",
        "The tool below is a DESKTOP app; this page documents it.",
    ])
    if not a.thu:
        webbrowser.open("https://khanhviet529.github.io/whiteboard-video/")
    _cho("Doi sang browser, cuon trang mot luot cho thay Terms + Privacy")


def canh_login(a):
    _khung("2 / 5  login kit  (scope: user.info.basic)", [
        "The app opens TikTok's authorization page.",
        "The code returns to a LOOPBACK redirect on this machine:",
        "    http://127.0.0.1:8723/callback/",
        "PKCE is used, with a hex SHA256 code_challenge.",
        "",
        "No token ever leaves this computer.",
    ])
    _chay([sys.executable, os.path.join(tt.GOC, "dang.py"), "auth"], a.thu)
    _cho("Neu browser vua mo: dang nhap va bam Authorize, cho tool in scope")


def canh_creator(a):
    _khung("3 / 5  creator info  (scope: user.info.basic)", [
        "GET /v2/post/publish/creator_info/query/",
        "",
        "The app reads the account's REAL limits before uploading:",
        "which privacy levels are allowed, max duration, daily quota.",
        "It never assumes a limit.",
    ])
    _chay([sys.executable, os.path.join(tt.GOC, "dang.py"), "creator"], a.thu)
    time.sleep(3)


def canh_upload(a):
    _khung("4 / 5  upload to inbox  (scope: video.upload)", [
        "POST /v2/post/publish/inbox/video/init/",
        "then chunked FILE_UPLOAD, then poll status/fetch",
        "until SEND_TO_USER_INBOX.",
        "",
        "The video lands in the creator's own TikTok inbox as a DRAFT.",
        "The creator writes the caption and publishes it in the app.",
    ])
    lenh = [sys.executable, os.path.join(tt.GOC, "dang.py"), "dang", a.video,
            "--inbox", "--cho"]
    _chay(lenh, a.thu)
    _cho("Mo tiktok.com (hoac app TikTok) cho thay ban NHAP vua toi Inbox")


def canh_publish(a):
    _khung("5 / 5  direct post  (scope: video.publish)", [
        "POST /v2/post/publish/video/init/",
        "same chunked upload, then poll until PUBLISH_COMPLETE.",
        "",
        "A finished video with its caption is posted directly.",
        "is_aigc=true on every upload: the voice-over is AI-generated.",
        "privacy_level=SELF_ONLY here, as an unaudited client.",
    ])
    lenh = [sys.executable, os.path.join(tt.GOC, "dang.py"), "dang", a.video,
            "--tieu-de", a.tieu_de, "--cho", "--lai"]
    _chay(lenh, a.thu)
    _cho("Mo tiktok.com cho thay video vua DANG len profile")


CANH = [
    ("01-website", canh_website),
    ("02-login-kit", canh_login),
    ("03-creator-info", canh_creator),
    ("04-video-upload", canh_upload),
    ("05-video-publish", canh_publish),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", nargs="?", help="mp4 de dang thu trong demo")
    ap.add_argument("--thu", action="store_true",
                    help="dien tap: khong goi mang, khong can key. Dung de kiem "
                         "khung hinh va nhip truoc khi quay that")
    ap.add_argument("--ra", default=os.path.join(tt.GOC, "demo"),
                    help="thu muc chua cac file cat ra")
    ap.add_argument("--tieu-de", default="Test upload from Whiteboard Video Uploader")
    ap.add_argument("--giu-tho", action="store_true", help="giu lai file mkv goc")
    a = ap.parse_args()

    if a.thu:
        # `_chay` in ca lenh ra truoc khi biet la dien tap, nen `video` khong duoc
        # phep la None - `" ".join` se no TypeError.
        a.video = a.video or os.path.join("out", "vi-du.mp4")
    else:
        if not a.video:
            raise SystemExit("thieu duong dan video. Hoac dien tap: --thu")
        if not os.path.exists(a.video):
            raise SystemExit(f"khong thay {a.video}")
        # Fail fast: het nua video moi phat hien thieu key la mat cong quay lai.
        tt.cau_hinh()

    _khung("chuan bi", [
        "1. Terminal nay phong TO HET man hinh - reviewer phai doc duoc chu.",
        "2. Dong het cua so khong lien quan (ca thong bao, ca tab rieng tu).",
        "3. Chuan bi mot tab browser san de mo tiktok.com khi duoc nhac.",
        "4. Ca man hinh se bi quay, ke ca ten file va thong bao hien ra.",
    ])
    _cho("San sang thi bam Enter de bat dau quay")

    p = _bat_ffmpeg()
    t0 = time.time()
    moc = []
    try:
        for ten, fn in CANH:
            batdau = time.time() - t0
            fn(a)
            moc.append((ten, batdau, time.time() - t0))
    finally:
        _tat_ffmpeg(p)

    if not os.path.exists(THO) or os.path.getsize(THO) == 0:
        raise SystemExit("ffmpeg khong ghi duoc gi. Kiem quyen ghi vao " + tt.GOC)

    print("\n" + "=" * RONG)
    print(f"  cat {len(moc)} canh tu {os.path.getsize(THO) / 1e6:.1f} MB")
    print("=" * RONG)
    qua = []
    for ten, a1, b1 in moc:
        ra = os.path.join(a.ra, ten + ".mp4")
        # Dem 0.5s truoc/sau: cat dung sat khien banner bi mat frame dau.
        n = _cat(max(0, a1 - 0.5), b1 + 0.5, ra)
        if n is None:
            print(f"  LOI  {ten}")
            continue
        mb = n / 1e6
        print(f"  {'OK ' if mb <= 50 else 'TO '} {ten:<18} {b1 - a1:6.1f}s  {mb:6.1f} MB")
        if mb > 50:
            qua.append(ten)

    if qua:
        print(f"\n  {len(qua)} file qua 50MB. Nen them:")
        print("    ffmpeg -i <file> -vf scale=1280:-2 -crf 32 -preset slow <ra>.mp4")
    if not a.giu_tho:
        os.unlink(THO)
    else:
        print(f"\n  file tho: {THO}")
    print(f"\n  Tai {len(moc)} file trong {a.ra} len muc App review cua TikTok.")


if __name__ == "__main__":
    main()
