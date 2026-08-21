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
import urllib.parse
import webbrowser
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
    """Mo browser de dang nhap, roi nhan `code` bang cach DAN URL vao terminal.

    Vi sao khong bat `code` tu dong bang HTTP server nhu phan lon tool khac:
    TikTok bat buoc `redirect_uri` phai la `https` (Login Kit web doc), nen khong
    the dung `http://127.0.0.1`. Dung mot server HTTPS local thi phai co chung chi
    tu ky - stdlib Python khong tao duoc, va them phu thuoc chi cho mot buoc lam
    MOT LAN trong 365 ngay la khong dang.

    Dung `https://127.0.0.1` lam redirect_uri: browser khong ket noi duoc, dung o
    trang loi, nhung `code` van nam trong thanh dia chi. Ma uy quyen KHONG di ra
    khoi may - khac han voi viec khai domain cua nguoi khac.
    """
    cf = tt.cau_hinh()
    url = tt.url_dang_nhap(scope=a.scope)
    print(f"scope       : {a.scope}")
    print(f"redirect_uri: {cf['TIKTOK_REDIRECT_URI']}")
    print("\nBa buoc:")
    print("  1. Trang dang nhap TikTok se mo (neu khong, mo tay URL duoi day)")
    print("  2. Dang nhap va dong y. Browser se bao loi khong ket noi duoc")
    print(f"     {cf['TIKTOK_REDIRECT_URI']} - DUNG LA NHU VAY, khong phai loi")
    print("  3. Copy TOAN BO url tren thanh dia chi, dan vao day")
    print(f"\n{url}\n")
    webbrowser.open(url)

    dan = input("Dan url (hoac chi rieng code) roi Enter: ").strip()
    code = None
    if "code=" in dan:
        q = parse_qs(urlparse(dan).query or dan.split("?", 1)[-1])
        code = (q.get("code") or [None])[0]
        if q.get("error"):
            raise SystemExit(f"TikTok tu choi: {q['error']} "
                             f"{q.get('error_description', [''])[0]}")
    elif dan:
        code = dan
    if not code:
        raise SystemExit("khong tim thay `code` trong chuoi vua dan")
    # `code` cua TikTok bi url-encode trong thanh dia chi (dau `*` thanh `%2A`).
    # Khong giai ma thi doi token that bai voi loi mo ho.
    code = urllib.parse.unquote(code)

    t = tt.doi_code_lay_token(code)
    print(f"\nda luu token vao {tt.TEP_TOKEN}")
    print(f"  open_id       : {t.get('open_id')}")
    print(f"  scope         : {t.get('scope')}")
    print(f"  access_token  : het han sau {t.get('expires_in')}s (~24 gio)")
    print(f"  refresh_token : het han sau {t.get('refresh_expires_in')}s (~365 ngay)")
    thieu = [x for x in ("video.upload", "video.publish", "video.list")
             if x not in (t.get("scope") or "")]
    if thieu:
        print(f"\n  CANH BAO: token thieu scope {', '.join(thieu)}.")
        print("  Bat chung trong app TikTok roi chay lai `auth`.")


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
def main():
    ap = argparse.ArgumentParser(prog="dang.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)

    p = sub.add_parser("auth", help="dang nhap mot lan, luu token")
    p.add_argument("--scope", default=tt.SCOPE_DAY_DU,
                   help="mac dinh xin het 4 scope: upload + publish + list + "
                        "info.basic, de sau khong phai auth lai")
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

    p = sub.add_parser("trang-thai", help="hoi trang thai theo publish_id")
    p.add_argument("publish_id")
    p.set_defaults(fn=lenh_trang_thai)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
