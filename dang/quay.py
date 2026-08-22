# -*- coding: utf-8 -*-
"""Quay demo video cho app review cua TikTok.

    py dang/quay.py --thu          dien tap: khong day video, khong can key
    py dang/quay.py                quay that

Tu bat ffmpeg (gdigrab), dung san UI o 127.0.0.1, chay dung thu tu ma reviewer
can thay, roi cat thanh tung file mot scope.

Vi sao cat thanh nhieu file thay vi mot file dai: TikTok cho tai 5 file, moi file
<=50MB. Mot file cho mot scope thi reviewer doi chieu duoc ngay, khong phai tua
tim trong video hai phut.

Vi sao demo qua UI (`web.py`) chu khong qua CLI: TikTok doi "The video should
clearly show the user interface and user interactions". Terminal kho tinh la
user interface, va do la ly do tu choi khong tranh luan duoc. `auth` thi van o
terminal vi khong co UI nao cho OAuth - nhung trang dong y cua TikTok chinh la
user interaction o canh do.

Chu tren man hinh la TIENG ANH co y - reviewer cua TikTok doc tieng Anh. Terminal
in ra tieng Viet khong ai doc duoc thi coi nhu khong co bang chung.
"""
import argparse
import os
import socket
import subprocess
import sys
import time
import webbrowser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiktok as tt  # noqa: E402

tt.bat_utf8()

RONG = 78
CONG_WEB = int(os.environ.get("DANG_WEB_PORT", "8724"))
URL_WEB = f"http://127.0.0.1:{CONG_WEB}"
URL_TRANG = "https://khanhviet529.github.io/whiteboard-video/"
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


def _cho(*nhac):
    for n in nhac:
        print(f"  >>> {n}")
    print("  >>> Roi bam Enter.")
    sys.stdout.flush()
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("huy giua duong - file tho van con o " + THO)


def _chay(lenh, thu=False):
    """Chay mot lenh cua tool, de output chay thang ra man hinh dang quay."""
    print(f"$ {' '.join(lenh)}")
    sys.stdout.flush()
    if thu:
        print("  (dien tap: bo qua)")
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


# ---------------------------------------------------------------------- UI
def _cong_mo(cong, han=15):
    het = time.time() + han
    while time.time() < het:
        with socket.socket() as s:
            s.settimeout(0.5)
            if s.connect_ex(("127.0.0.1", cong)) == 0:
                return True
        time.sleep(0.3)
    return False


def _bat_web():
    """Dung san UI truoc khi quay, de canh 3 khong phai doi no khoi dong."""
    if _cong_mo(CONG_WEB, han=1):
        print(f"  ({URL_WEB} da chay san - dung luon)")
        return None                    # khong phai cua minh thi khong tat
    p = subprocess.Popen([sys.executable, os.path.join(tt.GOC, "web.py")],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if not _cong_mo(CONG_WEB):
        p.terminate()
        raise SystemExit(f"UI khong mo duoc tren {URL_WEB}. Chay tay xem loi gi:\n"
                         f"  py dang\\web.py")
    return p


# -------------------------------------------------------------------- canh
def canh_website(a):
    _khung("1 / 5  official website", [
        URL_TRANG,
        "",
        "This is the Website URL declared in the app settings.",
        "The app itself is a DESKTOP tool; this page documents it,",
        "including its Terms of Service and Privacy Policy.",
    ])
    webbrowser.open(URL_TRANG)
    _cho("Doi sang browser, cuon trang mot luot cho thay Terms + Privacy")


def canh_login(a):
    _khung("2 / 5  login kit  (scope: user.info.basic)", [
        "The user signs in with TikTok. The app opens TikTok's",
        "authorization page and receives the code on a LOOPBACK",
        "redirect on this machine:",
        "    http://127.0.0.1:8723/callback/",
        "PKCE is used, with a hex SHA256 code_challenge.",
        "",
        "Then creator_info is queried, which returns the account's",
        "own display name and real posting limits.",
        "",
        "No token ever leaves this computer.",
    ])
    _chay([sys.executable, os.path.join(tt.GOC, "dang.py"), "auth"], a.thu)
    _cho("Neu browser vua mo: dang nhap va bam Authorize, cho tool in scope")
    _chay([sys.executable, os.path.join(tt.GOC, "dang.py"), "creator"], a.thu)
    _cho("Doc xong creator_info thi bam Enter")


def canh_ui(a):
    _khung("3 / 5  the app's user interface", [
        URL_WEB,
        "",
        "The app serves its UI on the loopback interface only.",
        "Every rendered video is listed with a thumbnail. For each one",
        "the user chooses:",
        "",
        "  - Inbox draft, or Direct post",
        "  - the privacy level, from the account's own allowed list",
        "  - the caption",
        "  - the AI-generated-content flag (on by default)",
        "",
        "Videos already posted are marked and cannot be posted twice.",
    ])
    webbrowser.open(URL_WEB)
    _cho("Doi sang browser, cuon bang video mot luot",
         "Mo o chon Inbox/Direct va o Privacy cho thay cac lua chon")


def canh_upload(a):
    _khung("4 / 5  upload to inbox  (scope: video.upload)", [
        "In the UI: pick a video, choose INBOX, click the post button.",
        "",
        "The app calls /v2/post/publish/inbox/video/init/, uploads the",
        "file in chunks as FILE_UPLOAD, then polls status/fetch until",
        "SEND_TO_USER_INBOX. The live log shows every step.",
        "",
        "The video lands in the creator's own TikTok inbox as a DRAFT.",
        "The creator writes the caption and publishes it in the app.",
    ])
    if a.thu:
        print("  (dien tap: KHONG bam Dang - chi xem giao dien)\n")
    _cho("Chon mot video, dat Inbox, bam Dang",
         "Cho log chay den SEND_TO_USER_INBOX",
         "Roi mo tiktok.com cho thay ban NHAP vua toi Inbox")


def canh_publish(a):
    _khung("5 / 5  direct post  (scope: video.publish)", [
        "In the UI: pick another video, choose DIRECT POST, set the",
        "privacy level and the caption, keep the AI flag on, then post.",
        "",
        "The app calls /v2/post/publish/video/init/, uploads the same",
        "way, and polls until PUBLISH_COMPLETE. A finished video with",
        "its caption is published without any further step.",
        "",
        "is_aigc is always true: the voice-over is AI-generated.",
        "In Sandbox the result stays private, as documented.",
    ])
    if a.thu:
        print("  (dien tap: KHONG bam Dang - chi xem giao dien)\n")
    _cho("Chon video KHAC, dat Direct post, bam Dang",
         "Cho log chay den PUBLISH_COMPLETE",
         "Roi mo tiktok.com cho thay video vua len profile")


CANH = [
    ("01-website", canh_website),
    ("02-login-kit", canh_login),
    ("03-app-ui", canh_ui),
    ("04-video-upload", canh_upload),
    ("05-video-publish", canh_publish),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--thu", action="store_true",
                    help="dien tap: khong day video len TikTok. Dung de kiem "
                         "khung hinh va nhip TRUOC khi quay that")
    ap.add_argument("--ra", default=os.path.join(tt.GOC, "demo"),
                    help="thu muc chua cac file cat ra")
    ap.add_argument("--giu-tho", action="store_true", help="giu lai file mkv goc")
    a = ap.parse_args()

    # Fail fast: het nua buoi quay moi phat hien thieu key la mat cong quay lai.
    if not a.thu:
        tt.cau_hinh()

    _khung("chuan bi", [
        "1. Phong TO cua so terminal va browser - reviewer phai doc duoc chu.",
        "2. Dong het cua so khong lien quan (ca thong bao, ca tab rieng tu).",
        "3. Ca man hinh se bi quay, ke ca ten file va thong bao hien ra.",
        "4. Canh 4 va 5 can HAI video khac nhau chua tung dang.",
        "",
        "Neu muon man hinh dong y cua TikTok hien lai o canh 2, thu hoi quyen",
        "truoc: app TikTok -> Settings and privacy -> Security and permissions",
        "-> Manage app permissions -> xoa app nay.",
    ])
    _cho("San sang thi bam Enter de bat dau quay")

    web = _bat_web()
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
        if web is not None:
            web.terminate()

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
