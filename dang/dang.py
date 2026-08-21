# -*- coding: utf-8 -*-
"""CLI dang video len TikTok.

    py dang/dang.py auth                      dang nhap mot lan, luu token
    py dang/dang.py creator                   xem gioi han that cua tai khoan
    py dang/dang.py dang out/x.mp4 --dry-run  xem chinh xac se gui gi
    py dang/dang.py dang out/x.mp4 --tieu-de "..."
    py dang/dang.py trang-thai <publish_id>

Mac dinh privacy la SELF_ONLY. Do la lua chon co y: app chua qua audit thi TikTok
khoa moi bai o che do rieng tu bat ke minh dat gi, nen dat PUBLIC_TO_EVERYONE luc
do chi lam minh tuong da public. Doi PUBLIC phai go tuong minh.
"""
import argparse
import json
import os
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiktok as tt  # noqa: E402

SO_DANG = os.path.join(tt.GOC, "da-dang.json")


def _doc_so():
    if os.path.exists(SO_DANG):
        return json.load(open(SO_DANG, encoding="utf-8"))
    return {}


def _ghi_so(so):
    with open(SO_DANG, "w", encoding="utf-8") as f:
        json.dump(so, f, ensure_ascii=False, indent=2)


# --------------------------------------------------------------------- auth
def lenh_auth(a):
    """Dang nhap mot lan bang luong Desktop + PKCE, bat `code` tu dong.

    Duoc dung HTTP server local tro lai vi platform Desktop cua Login Kit cho phep
    loopback: "Only `localhost` or loopback IP `127.0.0.1` are allowed host names".
    Nen `code` di tu browser sang tool qua localhost, KHONG qua internet.

    PKCE la bat buoc o luong nay. `code_verifier` chi ton tai trong tien trinh nay,
    khong ghi ra dia - no chi can song tu luc mo browser den luc doi token.
    """
    cf = tt.cau_hinh()
    ru = urlparse(cf["TIKTOK_REDIRECT_URI"])
    if ru.hostname not in ("127.0.0.1", "localhost"):
        raise SystemExit(
            f"redirect_uri phai la loopback cho luong Desktop, dang la "
            f"{cf['TIKTOK_REDIRECT_URI']!r}.\n"
            f"  Dat TIKTOK_REDIRECT_URI=http://127.0.0.1:8723/callback/")
    cong = ru.port or 80
    verifier, challenge = tt._pkce()
    got = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            got.update({k: v[0] for k, v in
                        parse_qs(urlparse(self.path).query).items()})
            xong = "code" in got
            than = (
                "<!doctype html><meta charset=utf-8>"
                "<body style='font:16px/1.6 system-ui;max-width:34rem;"
                "margin:4rem auto;padding:0 1.5rem;color:#222'>"
                + ("<h2>Xong.</h2><p>Dong tab nay va quay lai terminal.</p>"
                   if xong else
                   "<h2>Khong thay <code>code</code> trong callback.</h2>"
                   "<p>Xem terminal de biet chi tiet.</p>")
                + "</body>").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(than)))
            self.end_headers()
            self.wfile.write(than)

    url = tt.url_dang_nhap(scope=a.scope, code_challenge=challenge)
    print(f"scope       : {a.scope}")
    print(f"redirect_uri: {cf['TIKTOK_REDIRECT_URI']}  (platform Desktop, PKCE S256)")
    print(f"\nTrang dang nhap se mo. Neu khong, mo tay:\n  {url}\n")
    try:
        srv = HTTPServer((ru.hostname, cong), H)
    except OSError as e:
        raise SystemExit(
            f"khong mo duoc cong {cong} ({e}).\n"
            f"  Co tien trinh khac dang giu cong do. Dong no, hoac doi ca\n"
            f"  TIKTOK_REDIRECT_URI va Redirect URI trong app TikTok sang cong khac.")
    webbrowser.open(url)
    print(f"dang cho callback tren cong {cong}... (Ctrl+C de huy)")
    srv.handle_request()
    srv.server_close()

    if got.get("error"):
        raise SystemExit(f"TikTok tu choi: {got['error']} "
                         f"{got.get('error_description', '')}")
    if "code" not in got:
        raise SystemExit(
            f"callback khong co `code`: {json.dumps(got, ensure_ascii=False)}\n"
            f"  Thuong la do Redirect URI trong app TikTok khac voi "
            f"{cf['TIKTOK_REDIRECT_URI']}")

    # `code` cua TikTok co ky tu `*` bi url-encode thanh `%2A`. parse_qs da giai ma
    # roi, nhung giu ghi chu nay vi day la bay da vap khi con dan URL bang tay.
    t = tt.doi_code_lay_token(got["code"], code_verifier=verifier)
    print(f"\nda luu token vao {tt.tep_token()}")
    print(f"  open_id       : {t.get('open_id')}")
    print(f"  scope         : {t.get('scope')}")
    print(f"  access_token  : het han sau {t.get('expires_in')}s (~24 gio)")
    print(f"  refresh_token : het han sau {t.get('refresh_expires_in')}s (~365 ngay)")
    co = t.get("scope") or ""
    thieu = [x for x in tt.SCOPE_DANG.split(",") if x not in co]
    if thieu:
        print(f"\n  CANH BAO: token thieu scope {', '.join(thieu)}.")
        print("  Bat product tuong ung trong app TikTok roi chay lai `auth`.")
    if tt.SCOPE_SO_LIEU not in co:
        # Khong phai loi: Display API la product rieng va TikTok khong mo
        # cho moi app. Noi ro hau qua thay vi de bang so lieu trong im lang.
        print(f"\n  Khong co `{tt.SCOPE_SO_LIEU}` -> bang so lieu (view, comment) se trong.")
        print("  Can product Display API trong app TikTok.")


# ------------------------------------------------------------------ creator
def lenh_creator(a):
    d = tt.thong_tin_creator()
    print(json.dumps(d, ensure_ascii=False, indent=2))
    print("\nDoc ky `privacy_level_options`: day la danh sach TikTok thuc su cho "
          "phep voi tai khoan nay.")


# --------------------------------------------------------------------- dang
def lenh_dang(a):
    if not os.path.exists(a.video):
        raise SystemExit(f"khong thay {a.video}")
    size = os.path.getsize(a.video)
    bam = tt.bam_file(a.video)
    so = _doc_so()

    if bam in so and not a.lai:
        cu = so[bam]
        raise SystemExit(
            f"file nay da dang roi:\n"
            f"  luc     : {cu.get('luc')}\n"
            f"  publish : {cu.get('publish_id')}\n"
            f"  privacy : {cu.get('privacy')}\n"
            f"Them --lai neu that su muon dang lai. (So tinh theo NOI DUNG file, "
            f"nen doi ten file khong qua duoc - va do la co y: lich chay tu dong "
            f"khong duoc dang trung.)")

    tieu_de = a.tieu_de or os.path.splitext(os.path.basename(a.video))[0]
    if len(tieu_de) > 2200:
        raise SystemExit(f"tieu de {len(tieu_de)} ky tu, TikTok gioi han 2200")

    chunk, n_chunk = tt.ke_hoach_chunk(size)
    print(f"video    : {a.video}  ({size/tt.MB:.1f} MB)")
    print(f"cach     : {'inbox (nhap, tu hoan tat trong app)' if a.inbox else 'dang truc tiep'}")
    if a.inbox:
        print("           tieu de / quyen xem / hashtag dat trong app TikTok")
    else:
        print(f"tieu de  : {tieu_de}")
        print(f"privacy  : {a.privacy}")
        print(f"is_aigc  : {not a.khong_aigc}")
    print(f"chunk    : {chunk/tt.MB:.1f} MB x {n_chunk}")

    if a.privacy == "PUBLIC_TO_EVERYONE" and not a.inbox and not a.dry_run:
        print("\nLUU Y: app chua qua audit thi TikTok van khoa bai o rieng tu, "
              "bat ke privacy_level. Kiem bang `creator` truoc.")

    if a.inbox:
        pid, up, than = tt.khoi_tao_inbox(a.video, dry_run=a.dry_run)
    else:
        pid, up, than = tt.khoi_tao(
            a.video, title=tieu_de, privacy=a.privacy,
            is_aigc=not a.khong_aigc, disable_comment=a.tat_binh_luan,
            disable_duet=a.tat_duet, disable_stitch=a.tat_stitch,
            cover_ms=a.cover_ms, dry_run=a.dry_run)

    if a.dry_run:
        duong_api = "/inbox/video/init/" if a.inbox else "/video/init/"
        print(f"\n--- DRY RUN: than JSON se gui toi {duong_api} ---")
        print(json.dumps(than, ensure_ascii=False, indent=2))
        print("\nKhong goi mang, khong ghi so. Bo --dry-run de dang that.")
        return

    print(f"\npublish_id: {pid}")
    print("dang day file...")
    tt.day_file(up, a.video, chunk, n_chunk)

    if a.cho:
        print("cho TikTok xu ly...")
        # Duong inbox dung o SEND_TO_USER_INBOX, khong bao gio len
        # PUBLISH_COMPLETE - vi buoc dang cuoi do nguoi lam trong app.
        tt.cho_xong(pid, gioi_han_s=a.gioi_han,
                    xong_o=("SEND_TO_USER_INBOX",) if a.inbox else None)

    import datetime as _dt
    so[bam] = {"file": os.path.abspath(a.video), "publish_id": pid,
               "cach": "inbox" if a.inbox else "truc_tiep",
               "privacy": "-" if a.inbox else a.privacy, "tieu_de": tieu_de,
               "luc": _dt.datetime.now().isoformat(timespec="seconds")}
    _ghi_so(so)
    print(f"\nxong. da ghi vao {SO_DANG}")
    print(f"kiem lai bat ky luc nao: py dang/dang.py trang-thai {pid}")


def lenh_so_lieu(a):
    vids, _, _ = tt.danh_sach_da_dang(a.so)
    if not vids:
        print("chua co video nao tren TikTok (hoac token thieu scope video.list)")
        return
    print(f"{'view':>8} {'like':>7} {'cmt':>6} {'share':>6}  {'giay':>5}  tieu de")
    for v in vids:
        print(f"{v.get('view_count', 0):>8} {v.get('like_count', 0):>7} "
              f"{v.get('comment_count', 0):>6} {v.get('share_count', 0):>6} "
              f"{v.get('duration', 0):>6}  "
              f"{(v.get('title') or v.get('video_description') or '')[:52]}")


def lenh_trang_thai(a):
    print(json.dumps(tt.trang_thai(a.publish_id), ensure_ascii=False, indent=2))


# --------------------------------------------------------------------- main
def lenh_cau_hinh(a):
    """In ra chinh xac nhung gi phai khai trong portal TikTok.

    Ton tai vi mot ly do cu the: Redirect URI phai trung Y NGUYEN giua `.env` va
    o khai trong Login Kit. Lech mot ky tu - thieu dau `/` cuoi, hoac `http` vs
    `https` - thi TikTok tu choi voi loi khong noi duoc nguyen nhan. Chep tu day
    thi khong the go sai.

    KHONG goi `tt.cau_hinh()`: no raise khi thieu key, ma lenh nay phai chay duoc
    TRUOC khi co key - do la luc can no nhat.
    """
    e = tt._doc_env()
    ru = e.get("TIKTOK_REDIRECT_URI") or "http://127.0.0.1:8723/callback/"
    print("Khai trong app TikTok (Login Kit -> Redirect URI -> tab Desktop):")
    print(f"\n    {ru}\n")
    print("Scope (den TU product, khong khai tay o Add scopes):")
    for sc, tu in (("user.info.basic", "Login Kit"),
                   ("video.upload", "Content Posting API"),
                   ("video.publish", "Content Posting API + cong tac Direct Post")):
        print(f"    {sc:<18} {tu}")
    print(f"\n{tt.TEP_ENV}:")
    for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET"):
        v = e.get(k)
        print(f"    {k:<22} {'co (' + str(len(v)) + ' ky tu)' if v else 'CHUA CO'}")
    print(f"    {'TIKTOK_REDIRECT_URI':<22} {ru}"
          f"{'' if e.get('TIKTOK_REDIRECT_URI') else '   (mac dinh)'}")
    print(f"\nToken se luu vao: {tt.tep_token()}")


def main():
    ap = argparse.ArgumentParser(prog="dang.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)

    p = sub.add_parser("auth", help="dang nhap mot lan, luu token")
    p.add_argument("--scope", default=tt.SCOPE_DANG,
                   help=f"mac dinh {tt.SCOPE_DANG} (Login Kit + Content Posting "
                        f"API). Chi them video.list khi app da bat Display API: "
                        f"--scope {tt.SCOPE_DAY_DU}")
    p.set_defaults(fn=lenh_auth)

    p = sub.add_parser("creator", help="xem gioi han that cua tai khoan")
    p.set_defaults(fn=lenh_creator)

    p = sub.add_parser("dang", help="dang mot video")
    p.add_argument("video")
    p.add_argument("--tieu-de", help="mac dinh: ten file")
    p.add_argument("--privacy", default="SELF_ONLY", choices=tt.PRIVACY,
                   help="chi co nghia voi direct post, khong dung voi --inbox")
    # Truoc khi app qua audit, day la duong DUY NHAT ra video public that: bai cuoi
    # do nguoi bam dang trong app TikTok nen khong bi han che chua-audit.
    p.add_argument("--inbox", action="store_true",
                   help="day vao inbox dang nhap (scope video.upload) thay vi "
                        "dang truc tiep; tieu de va quyen xem dat trong app TikTok")
    p.add_argument("--dry-run", action="store_true",
                   help="in than JSON se gui, khong goi mang")
    p.add_argument("--cho", action="store_true", help="cho den khi TikTok xu ly xong")
    p.add_argument("--gioi-han", type=int, default=600, help="giay, dung voi --cho")
    p.add_argument("--lai", action="store_true", help="dang lai file da dang")
    p.add_argument("--khong-aigc", action="store_true",
                   help="TAT co bao noi dung AI (mac dinh BAT vi giong la AI sinh)")
    p.add_argument("--tat-binh-luan", action="store_true")
    p.add_argument("--tat-duet", action="store_true")
    p.add_argument("--tat-stitch", action="store_true")
    p.add_argument("--cover-ms", type=int, default=0, help="moc thoi gian lam anh bia")
    p.set_defaults(fn=lenh_dang)

    p = sub.add_parser("so-lieu", help="view/like/binh luan cua video da dang")
    p.add_argument("--so", type=int, default=20, help="so video, toi da 20")
    p.set_defaults(fn=lenh_so_lieu)

    p = sub.add_parser("cau-hinh",
                       help="in dung chuoi phai khai trong portal TikTok")
    p.set_defaults(fn=lenh_cau_hinh)

    p = sub.add_parser("trang-thai", help="hoi trang thai theo publish_id")
    p.add_argument("publish_id")
    p.set_defaults(fn=lenh_trang_thai)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
