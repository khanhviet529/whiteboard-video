# -*- coding: utf-8 -*-
"""CLI dang video len TikTok.

    python dang/dang.py auth                      dang nhap mot lan, luu token
    python dang/dang.py creator                   xem gioi han that cua tai khoan
    python dang/dang.py dang out/x.mp4 --dry-run  xem chinh xac se gui gi
    python dang/dang.py dang out/x.mp4 --tieu-de "..."
    python dang/dang.py trang-thai <publish_id>

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
    """Mo browser, bat `code` bang mot HTTP server tam tren localhost.

    Phai co server tam vi TikTok tra `code` qua redirect_uri chu khong in ra man
    hinh. Cong lay tu redirect_uri da khai trong app - hai ben phai TRUNG nhau,
    lech mot ky tu la TikTok tu choi.
    """
    cf = tt.cau_hinh()
    ru = urlparse(cf["TIKTOK_REDIRECT_URI"])
    cong = ru.port or 80
    got = {}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def do_GET(self):
            q = parse_qs(urlparse(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            xong = "code" in got
            self.wfile.write(
                ("<h2>" + ("Xong. Dong tab nay va quay lai terminal."
                           if xong else
                           "Khong thay `code` trong callback. Xem terminal.")
                 + "</h2>").encode("utf-8"))

    url = tt.url_dang_nhap(scope=a.scope)
    print(f"scope       : {a.scope}")
    print(f"redirect_uri: {cf['TIKTOK_REDIRECT_URI']}")
    print(f"\nMo trang nay de dang nhap (neu browser khong tu mo):\n  {url}\n")
    srv = HTTPServer((ru.hostname or "127.0.0.1", cong), H)
    webbrowser.open(url)
    print(f"dang cho callback tren cong {cong}... (Ctrl+C de huy)")
    srv.handle_request()
    srv.server_close()

    if "code" not in got:
        raise SystemExit(
            f"callback khong co `code`: {json.dumps(got, ensure_ascii=False)}\n"
            f"  Thuong la do redirect_uri trong app TikTok khac voi "
            f"{cf['TIKTOK_REDIRECT_URI']}")
    t = tt.doi_code_lay_token(got["code"])
    print(f"\nda luu token vao {tt.TEP_TOKEN}")
    print(f"  open_id        : {t.get('open_id')}")
    print(f"  scope          : {t.get('scope')}")
    print(f"  access_token   : het han sau {t.get('expires_in')}s (~24 gio)")
    print(f"  refresh_token  : het han sau {t.get('refresh_expires_in')}s (~365 ngay)")
    if "video.publish" not in (t.get("scope") or ""):
        print("\n  CANH BAO: token khong co scope `video.publish` - chi upload vao "
              "inbox duoc, khong dang truc tiep duoc.")


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
    print(f"tieu de  : {tieu_de}")
    print(f"privacy  : {a.privacy}")
    print(f"is_aigc  : {not a.khong_aigc}")
    print(f"chunk    : {chunk/tt.MB:.1f} MB x {n_chunk}")

    if a.privacy == "PUBLIC_TO_EVERYONE" and not a.dry_run:
        print("\nLUU Y: app chua qua audit thi TikTok van khoa bai o rieng tu, "
              "bat ke privacy_level. Kiem bang `creator` truoc.")

    pid, up, than = tt.khoi_tao(
        a.video, title=tieu_de, privacy=a.privacy,
        is_aigc=not a.khong_aigc, disable_comment=a.tat_binh_luan,
        disable_duet=a.tat_duet, disable_stitch=a.tat_stitch,
        cover_ms=a.cover_ms, dry_run=a.dry_run)

    if a.dry_run:
        print("\n--- DRY RUN: than JSON se gui toi /video/init/ ---")
        print(json.dumps(than, ensure_ascii=False, indent=2))
        print("\nKhong goi mang, khong ghi so. Bo --dry-run de dang that.")
        return

    print(f"\npublish_id: {pid}")
    print("dang day file...")
    tt.day_file(up, a.video, chunk, n_chunk)

    if a.cho:
        print("cho TikTok xu ly...")
        tt.cho_xong(pid, gioi_han_s=a.gioi_han)

    import datetime as _dt
    so[bam] = {"file": os.path.abspath(a.video), "publish_id": pid,
               "privacy": a.privacy, "tieu_de": tieu_de,
               "luc": _dt.datetime.now().isoformat(timespec="seconds")}
    _ghi_so(so)
    print(f"\nxong. da ghi vao {SO_DANG}")
    print(f"kiem lai bat ky luc nao: python dang/dang.py trang-thai {pid}")


def lenh_trang_thai(a):
    print(json.dumps(tt.trang_thai(a.publish_id), ensure_ascii=False, indent=2))


# --------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(prog="dang.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)

    p = sub.add_parser("auth", help="dang nhap mot lan, luu token")
    p.add_argument("--scope", default="video.publish",
                   help="video.publish = dang truc tiep; video.upload = chi vao inbox")
    p.set_defaults(fn=lenh_auth)

    p = sub.add_parser("creator", help="xem gioi han that cua tai khoan")
    p.set_defaults(fn=lenh_creator)

    p = sub.add_parser("dang", help="dang mot video")
    p.add_argument("video")
    p.add_argument("--tieu-de", help="mac dinh: ten file")
    p.add_argument("--privacy", default="SELF_ONLY", choices=tt.PRIVACY)
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

    p = sub.add_parser("trang-thai", help="hoi trang thai theo publish_id")
    p.add_argument("publish_id")
    p.set_defaults(fn=lenh_trang_thai)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
