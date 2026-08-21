# -*- coding: utf-8 -*-
"""Kiem tool dang TikTok bang mot server GIA, khong can key va khong goi mang that.

    py dang/thu.py

Vi sao can: tool nay chua tung upload that lan nao. Nhung cho de sai nhat khong
hien ra o dry-run - `Content-Range` tung chunk, bien vong lap chunk, polling trang
thai, nhanh inbox vs direct, guard scope, ghi so. Sai mot trong so do thi phat hien
qua API that la mat lan goi, va con lam ban tai khoan bang mot bai nhap loi.

Server gia bat dung hop dong tai lieu TikTok: nhan multipart, kiem field, tra
publish_id + upload_url, nhan PUT tung chunk roi doi chieu byte, va tra trang thai
theo dung enum. Cai gi khong khop la loi cua tool, khong phai cua server.
"""
import io
import json
import os
import sys
import tempfile
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiktok as tt  # noqa: E402

# ---- trang thai server gia -------------------------------------------------
NHAN = {}          # cai gi server nhan duoc o lan goi cuoi
CHUNKS = []        # (dau, cuoi, tong, so_byte) cua tung PUT
TRA_LOI = {}       # dieu khien: server nen tra gi
loi = []


def kiem(ten, dk, ct=""):
    print(("  OK   " if dk else "  LOI  ") + ten + ("" if dk else f"  <- {ct}"))
    if not dk:
        loi.append(ten)


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def _json(self, ma, than):
        b = json.dumps(than).encode()
        self.send_response(ma)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_PUT(self):
        n = int(self.headers.get("Content-Length", 0))
        data = self.rfile.read(n)
        cr = self.headers.get("Content-Range", "")
        # "bytes A-B/TOTAL"
        try:
            phan, tong = cr.split("bytes ", 1)[1].split("/")
            a, b = (int(x) for x in phan.split("-"))
            CHUNKS.append((a, b, int(tong), len(data)))
        except Exception:
            CHUNKS.append(("KHONG PARSE DUOC", cr, None, len(data)))
        self.send_response(TRA_LOI.get("ma_put", 201))
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_POST(self):
        u = urllib.parse.urlparse(self.path).path
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n)
        NHAN["path"] = u
        NHAN["auth"] = self.headers.get("Authorization", "")
        NHAN["ctype"] = self.headers.get("Content-Type", "")

        if u == "/token":
            NHAN["form"] = urllib.parse.parse_qs(raw.decode())
            return self._json(200, TRA_LOI.get("token") or {
                "access_token": "AT-moi", "refresh_token": "RT-moi",
                "expires_in": 86400, "refresh_expires_in": 31536000,
                "open_id": "oid", "scope": "video.publish,video.upload",
                "token_type": "Bearer",
            })

        NHAN["body"] = json.loads(raw) if raw else {}
        if u == "/creator":
            return self._json(200, {"data": {"creator_username": "toi",
                                             "privacy_level_options":
                                             ["SELF_ONLY"]}, "error":
                                    {"code": "ok"}})
        if u in ("/init", "/init_inbox"):
            if TRA_LOI.get("init_loi"):
                return self._json(200, TRA_LOI["init_loi"])
            return self._json(200, {
                "data": {"publish_id": "PID-1",
                         "upload_url": TRA_LOI["upload_url"]},
                "error": {"code": "ok"}})
        if u == "/status":
            return self._json(200, {"data": TRA_LOI.get("status", {
                "status": "PUBLISH_COMPLETE"}), "error": {"code": "ok"}})
        self._json(404, {"error": {"code": "not_found"}})


def bat_server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    goc = f"http://127.0.0.1:{srv.server_address[1]}"
    tt.URL_TOKEN = goc + "/token"
    tt.URL_CREATOR = goc + "/creator"
    tt.URL_INIT = goc + "/init"
    tt.URL_INIT_INBOX = goc + "/init_inbox"
    tt.URL_STATUS = goc + "/status"
    TRA_LOI["upload_url"] = goc + "/upload"
    return srv, goc


def dat_token(scope="video.publish,video.upload", con_song=86400):
    import time
    t = {"access_token": "AT-cu", "refresh_token": "RT-cu", "scope": scope,
         "het_han_luc": int(time.time()) + con_song,
         "refresh_het_han_luc": int(time.time()) + 31536000}
    io.open(tt.tep_token(), "w", encoding="utf-8").write(json.dumps(t))
    return t


def tep_video(so_byte):
    f = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
    f.write(bytes(range(256)) * (so_byte // 256) + b"\x00" * (so_byte % 256))
    f.close()
    return f.name


def main():
    tam = tempfile.mkdtemp(prefix="thu-tiktok-")
    tt.GOC = tam
    tt.TEP_TOKEN = os.path.join(tam, "token.json")
    tt.TEP_ENV = os.path.join(tam, ".env")
    os.environ["TIKTOK_CLIENT_KEY"] = "CK"
    os.environ["TIKTOK_CLIENT_SECRET"] = "CS"
    srv, goc = bat_server()

    print("\n1. dry-run khong goi mang, khong can token")
    v = tep_video(3 * tt.MB)
    NHAN.clear()
    pid, up, than = tt.khoi_tao(v, title="tieu de", dry_run=True)
    kiem("khong goi server", not NHAN, NHAN)
    kiem("post_info + source_info", set(than) == {"post_info", "source_info"}, than)
    kiem("privacy mac dinh SELF_ONLY",
         than["post_info"]["privacy_level"] == "SELF_ONLY", than)
    kiem("is_aigc bat mac dinh", than["post_info"]["is_aigc"] is True, than)

    print("\n2. inbox chi gui source_info, KHONG gui post_info")
    _, _, than_ib = tt.khoi_tao_inbox(v, dry_run=True)
    kiem("chi co source_info", set(than_ib) == {"source_info"}, than_ib)

    print("\n3. guard scope: token chi co video.upload thi khong dang truc tiep")
    dat_token(scope="video.upload")
    try:
        tt.khoi_tao(v, title="x")
        kiem("chan dung", False, "khong raise")
    except SystemExit as e:
        kiem("chan dung, bao ro", "video.publish" in str(e), str(e)[:70])
    try:
        tt.khoi_tao_inbox(v)
        kiem("inbox van cho qua", True)
    except SystemExit as e:
        kiem("inbox van cho qua", False, str(e)[:70])

    print("\n4. init: header Bearer, JSON, dung endpoint")
    dat_token()
    NHAN.clear(); CHUNKS.clear()
    pid, up, than = tt.khoi_tao(v, title="tieu de", privacy="SELF_ONLY")
    kiem("goi /init", NHAN["path"] == "/init", NHAN.get("path"))
    kiem("Bearer dung token", NHAN["auth"] == "Bearer AT-cu", NHAN.get("auth"))
    kiem("Content-Type JSON", "application/json" in NHAN["ctype"], NHAN.get("ctype"))
    kiem("publish_id tra ve", pid == "PID-1", pid)
    NHAN.clear()
    tt.khoi_tao_inbox(v)
    kiem("inbox goi /init_inbox", NHAN["path"] == "/init_inbox", NHAN.get("path"))

    print("\n5. day file MOT chunk: Content-Range phu dung het file")
    CHUNKS.clear()
    size = os.path.getsize(v)
    c, sc = tt.ke_hoach_chunk(size)
    tt.day_file(up, v, c, sc, in_ra=lambda *_: None)
    kiem("1 chunk", len(CHUNKS) == 1, CHUNKS)
    kiem("range 0-(size-1)/size", CHUNKS[0][:3] == (0, size - 1, size), CHUNKS[0])
    kiem("so byte thuc = ca file", CHUNKS[0][3] == size, CHUNKS[0])

    print("\n6. day file NHIEU chunk: lien tuc, khong chong, phu het")
    cu_max = tt.CHUNK_MAX
    tt.CHUNK_MAX = 1 * tt.MB          # ep chia nho de kiem bien vong lap
    v2 = tep_video(int(3.5 * tt.MB))
    size2 = os.path.getsize(v2)
    c2, sc2 = tt.ke_hoach_chunk(size2)
    CHUNKS.clear()
    tt.day_file(up, v2, c2, sc2, in_ra=lambda *_: None)
    tt.CHUNK_MAX = cu_max
    kiem(f"so chunk = {sc2}", len(CHUNKS) == sc2, CHUNKS)
    lien = all(CHUNKS[i][0] == CHUNKS[i - 1][1] + 1 for i in range(1, len(CHUNKS)))
    kiem("lien tuc, khong chong lan", lien, [c[:2] for c in CHUNKS])
    kiem("bat dau tu 0", CHUNKS[0][0] == 0, CHUNKS[0])
    kiem("ket thuc o size-1", CHUNKS[-1][1] == size2 - 1, CHUNKS[-1])
    kiem("tong byte = size", sum(x[3] for x in CHUNKS) == size2,
         (sum(x[3] for x in CHUNKS), size2))
    kiem("tong trong Content-Range luon = size",
         all(x[2] == size2 for x in CHUNKS), [x[2] for x in CHUNKS])

    print("\n7. HTTP 200 nhung error.code != ok -> phai nem loi")
    TRA_LOI["init_loi"] = {"error": {"code": "spam_risk_too_many_posts",
                                    "message": "qua nhieu bai",
                                    "log_id": "LID"}}
    try:
        tt.khoi_tao(v, title="x")
        kiem("khong bo qua loi ngam", False, "khong raise")
    except SystemExit as e:
        kiem("khong bo qua loi ngam",
             "spam_risk_too_many_posts" in str(e) and "LID" in str(e), str(e)[:80])
    TRA_LOI.pop("init_loi")

    print("\n8. cho_xong: direct doi PUBLISH_COMPLETE, inbox dung o inbox")
    TRA_LOI["status"] = {"status": "PUBLISH_COMPLETE"}
    kiem("direct: PUBLISH_COMPLETE la xong",
         tt.cho_xong("PID-1", nhip_s=0, in_ra=lambda *_: None)["status"]
         == "PUBLISH_COMPLETE")
    TRA_LOI["status"] = {"status": "SEND_TO_USER_INBOX"}
    kiem("inbox: SEND_TO_USER_INBOX la xong",
         tt.cho_xong("PID-1", nhip_s=0, in_ra=lambda *_: None,
                     xong_o=("SEND_TO_USER_INBOX",))["status"]
         == "SEND_TO_USER_INBOX")
    try:
        tt.cho_xong("PID-1", nhip_s=0, gioi_han_s=1, in_ra=lambda *_: None)
        kiem("direct KHONG coi inbox la xong", False, "khong raise")
    except SystemExit as e:
        kiem("direct KHONG coi inbox la xong", "chua xong" in str(e), str(e)[:60])

    print("\n9. FAILED -> nem kem fail_reason")
    TRA_LOI["status"] = {"status": "FAILED",
                         "fail_reason": "frame_rate_check_failed"}
    try:
        tt.cho_xong("PID-1", nhip_s=0, in_ra=lambda *_: None)
        kiem("bao fail_reason", False, "khong raise")
    except SystemExit as e:
        kiem("bao fail_reason", "frame_rate_check_failed" in str(e), str(e)[:70])
    TRA_LOI["status"] = {"status": "PUBLISH_COMPLETE"}

    print("\n10. token het han -> tu refresh truoc khi goi")
    dat_token(con_song=60)             # con 60s < nguong 300s
    NHAN.clear()
    tk = tt.lay_token()
    kiem("da goi /token", NHAN.get("path") == "/token", NHAN.get("path"))
    kiem("grant_type=refresh_token",
         NHAN["form"]["grant_type"] == ["refresh_token"], NHAN.get("form"))
    kiem("gui refresh_token cu",
         NHAN["form"]["refresh_token"] == ["RT-cu"], NHAN.get("form"))
    kiem("dung token moi", tk == "AT-moi", tk)

    print("\n11. refresh_token het han -> bat dang nhap lai")
    t = json.loads(io.open(tt.tep_token(), encoding="utf-8").read())
    t["refresh_het_han_luc"] = 0
    io.open(tt.tep_token(), "w", encoding="utf-8").write(json.dumps(t))
    try:
        tt.lay_token()
        kiem("bao het han", False, "khong raise")
    except SystemExit as e:
        kiem("bao het han", "365 ngay" in str(e), str(e)[:60])

    print("\n12. creator_info goi duoc")
    dat_token()
    d = tt.thong_tin_creator()
    kiem("tra privacy_level_options", "privacy_level_options" in d, d)

    print("\n13. token tach theo client_key (sandbox vs production)")
    # Truoc day ca hai moi truong ghi vao MOT file: doi key xong token cu van
    # nam do, TikTok tra 401 ma file token nhin thi van "co". Rat kho doan.
    goc_key = os.environ["TIKTOK_CLIENT_KEY"]
    dat_token()
    duong_a = tt.tep_token()
    os.environ["TIKTOK_CLIENT_KEY"] = "CK-sandbox"
    duong_b = tt.tep_token()
    kiem("hai key -> hai duong dan", duong_a != duong_b, (duong_a, duong_b))
    kiem("khong doc token cua key khac", not os.path.exists(duong_b), duong_b)
    try:
        tt.lay_token()
        kiem("bat `auth` khi doi key", False, "khong raise")
    except SystemExit as e:
        kiem("bat `auth` khi doi key", "auth" in str(e), str(e)[:70])
    os.environ["TIKTOK_CLIENT_KEY"] = goc_key
    kiem("doi ve key cu thi token con nguyen", tt.lay_token() == "AT-cu",
         tt.tep_token())

    srv.shutdown()
    for f in (v, v2):
        os.unlink(f)
    print("\n" + ("TAT CA DAT" if not loi else f"TRUOT: {loi}"))
    return 1 if loi else 0


if __name__ == "__main__":
    sys.exit(main())
