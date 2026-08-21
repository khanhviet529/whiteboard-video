# -*- coding: utf-8 -*-
"""Client Content Posting API cua TikTok. Chi stdlib, khong them phu thuoc.

Hop dong lay tu tai lieu chinh thuc (kiem 2026-08-20):

  POST /v2/oauth/token/                    doi code -> token, va refresh
  POST /v2/post/publish/creator_info/query/  phai goi TRUOC khi dang
  POST /v2/post/publish/video/init/        khoi tao, tra publish_id + upload_url
  PUT  {upload_url}                        day tung chunk
  POST /v2/post/publish/status/fetch/      hoi trang thai bang publish_id

Ba dieu tai lieu noi ro, anh huong truc tiep cach dung:

  * "All content posted by unaudited clients will be restricted to private
    viewing mode." App chua qua audit thi dat privacy_level nao cung ra rieng tu.
    Vi vay mac dinh o day la SELF_ONLY - dat PUBLIC_TO_EVERYONE khi chua audit
    chi lam nguoi dung tuong da public.
  * access_token song 24 gio, refresh_token 365 ngay. Nen phai co cho luu ben va
    tu refresh, khong thi hom sau cron chay la chet.
  * chunk: toi thieu 5MB, toi da 64MB (chunk CUOI duoc vuot chunk_size, toi 128MB),
    toi da 1000 chunk, file toi da 4GB. File duoi 5MB phai day nguyen mot lan.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://open.tiktokapis.com"
URL_TOKEN = f"{BASE}/v2/oauth/token/"
URL_CREATOR = f"{BASE}/v2/post/publish/creator_info/query/"
URL_INIT = f"{BASE}/v2/post/publish/video/init/"
URL_STATUS = f"{BASE}/v2/post/publish/status/fetch/"
URL_AUTH = "https://www.tiktok.com/v2/auth/authorize/"

MB = 1024 * 1024
CHUNK_MIN = 5 * MB
CHUNK_MAX = 64 * MB
CHUNK_CUOI_MAX = 128 * MB
CHUNK_SO_MAX = 1000
FILE_MAX = 4 * 1024 * MB

PRIVACY = ("SELF_ONLY", "FOLLOWER_OF_CREATOR", "MUTUAL_FOLLOW_FRIENDS",
           "PUBLIC_TO_EVERYONE")

GOC = os.path.dirname(os.path.abspath(__file__))
TEP_TOKEN = os.path.join(GOC, "token.json")
TEP_ENV = os.path.join(GOC, ".env")


# ------------------------------------------------------------------ cau hinh
def _doc_env():
    """Doc client_key/secret tu bien moi truong, hoac tu dang/.env.

    `.env` bi gitignore. Khong bao gio in gia tri ra log - repo nay la public.
    """
    ra = {}
    if os.path.exists(TEP_ENV):
        for dong in open(TEP_ENV, encoding="utf-8"):
            dong = dong.strip()
            if not dong or dong.startswith("#") or "=" not in dong:
                continue
            k, v = dong.split("=", 1)
            ra[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REDIRECT_URI"):
        if os.environ.get(k):
            ra[k] = os.environ[k]
    return ra


def cau_hinh():
    e = _doc_env()
    thieu = [k for k in ("TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET") if not e.get(k)]
    if thieu:
        raise SystemExit(
            f"thieu {', '.join(thieu)}.\n"
            f"  Tao {TEP_ENV} theo mau .env.example, hoac dat bien moi truong.\n"
            f"  Lay key o https://developers.tiktok.com/apps")
    e.setdefault("TIKTOK_REDIRECT_URI", "http://127.0.0.1:8723/callback")
    return e


# --------------------------------------------------------------------- HTTP
def _goi(url, *, data=None, form=None, token=None, method=None, timeout=60):
    """Mot cho duy nhat goi HTTP. Tra ve (ma, dict|bytes).

    Loi KHONG bi che: TikTok tra chi tiet trong body, va do la thu duy nhat giup
    sua duoc khi API doi. Nem nguyen van body ra ngoai.
    """
    headers = {}
    body = None
    if form is not None:
        body = urllib.parse.urlencode(form).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    elif data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=UTF-8"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as ex:
        raw = ex.read().decode("utf-8", "replace")
        try:
            return ex.code, json.loads(raw)
        except Exception:
            return ex.code, {"raw": raw[:2000]}


def _bat_loi(ma, than, o_dau):
    """TikTok tra HTTP 200 kem `error.code != 'ok'` - phai kiem CA HAI."""
    loi = (than or {}).get("error") or {}
    if ma >= 400 or (loi.get("code") and loi["code"] != "ok"):
        raise SystemExit(
            f"{o_dau} that bai (HTTP {ma})\n"
            f"  code    : {loi.get('code')}\n"
            f"  message : {loi.get('message')}\n"
            f"  log_id  : {loi.get('log_id')}\n"
            f"  than    : {json.dumps(than, ensure_ascii=False)[:600]}")
    return than


# -------------------------------------------------------------------- token
def _luu_token(t):
    t = dict(t)
    t["het_han_luc"] = int(time.time()) + int(t.get("expires_in", 0))
    t["refresh_het_han_luc"] = int(time.time()) + int(t.get("refresh_expires_in", 0))
    with open(TEP_TOKEN, "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=2)
    try:
        os.chmod(TEP_TOKEN, 0o600)
    except OSError:
        pass       # Windows bo qua, khong phai loi
    return t


def doi_code_lay_token(code, code_verifier=None):
    cf = cau_hinh()
    form = {
        "client_key": cf["TIKTOK_CLIENT_KEY"],
        "client_secret": cf["TIKTOK_CLIENT_SECRET"],
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": cf["TIKTOK_REDIRECT_URI"],
    }
    if code_verifier:
        form["code_verifier"] = code_verifier
    ma, than = _goi(URL_TOKEN, form=form)
    _bat_loi(ma, than, "doi code lay token")
    return _luu_token(than)


def _refresh(t):
    cf = cau_hinh()
    ma, than = _goi(URL_TOKEN, form={
        "client_key": cf["TIKTOK_CLIENT_KEY"],
        "client_secret": cf["TIKTOK_CLIENT_SECRET"],
        "grant_type": "refresh_token",
        "refresh_token": t["refresh_token"],
    })
    _bat_loi(ma, than, "refresh token")
    return _luu_token(than)


def lay_token():
    """Tra ve access_token con hieu luc. Tu refresh khi con duoi 5 phut.

    Refresh SOM (5 phut) chu khong doi het han: mot lan day video 17MB co the mat
    vai phut, va token het han giua duong thi chunk cuoi that bai - luc do da mat
    ca lan upload.
    """
    # Kiem key TRUOC khi kiem token: khi chua setup gi ca thi van de dau tien la
    # thieu client_key, khong phai thieu token. Bao dung thu tu de nguoi dung lam
    # dung buoc 1 thay vi di tim token.json khong ton tai.
    cau_hinh()
    if not os.path.exists(TEP_TOKEN):
        raise SystemExit(
            f"chua co {TEP_TOKEN}. Chay `py dang/dang.py auth` mot lan de "
            f"dang nhap va luu token.")
    t = json.load(open(TEP_TOKEN, encoding="utf-8"))
    if time.time() > t.get("refresh_het_han_luc", 0):
        raise SystemExit("refresh_token da het han (365 ngay). Chay lai `auth`.")
    if time.time() > t.get("het_han_luc", 0) - 300:
        t = _refresh(t)
    return t["access_token"]


def url_dang_nhap(scope="video.publish", state="wbv"):
    cf = cau_hinh()
    return URL_AUTH + "?" + urllib.parse.urlencode({
        "client_key": cf["TIKTOK_CLIENT_KEY"],
        "scope": scope,
        "response_type": "code",
        "redirect_uri": cf["TIKTOK_REDIRECT_URI"],
        "state": state,
    })


# ----------------------------------------------------------------- creator
def thong_tin_creator():
    """Tai lieu yeu cau goi TRUOC khi dang. Tra ve gioi han that cua tai khoan."""
    tk = lay_token()
    ma, than = _goi(URL_CREATOR, data={}, token=tk)
    return _bat_loi(ma, than, "creator_info")["data"]


# ------------------------------------------------------------------ upload
def ke_hoach_chunk(size):
    """(chunk_size, total_chunk_count) hop le theo rang buoc tai lieu.

    File <= 64MB day nguyen MOT chunk: vua dung luat "duoi 5MB phai day nguyen",
    vua tranh han "moi chunk toi thieu 5MB" (chia doi mot file 6MB thanh 2 chunk
    3MB la sai). Tren 64MB moi chia, phan du don vao chunk cuoi - tai lieu cho
    chunk cuoi vuot chunk_size toi 128MB.
    """
    if size <= 0:
        raise SystemExit("file rong")
    if size > FILE_MAX:
        raise SystemExit(f"file {size/MB:.0f}MB vuot gioi han 4GB cua TikTok")
    if size <= CHUNK_MAX:
        return size, 1
    chunk = CHUNK_MAX
    so = size // chunk
    if so > CHUNK_SO_MAX:
        raise SystemExit(f"file {size/MB:.0f}MB can {so} chunk, vuot han 1000")
    if size - chunk * (so - 1) > CHUNK_CUOI_MAX:
        so += 1
    return chunk, so


def khoi_tao(duong_video, *, title, privacy="SELF_ONLY", is_aigc=True,
             disable_comment=False, disable_duet=False, disable_stitch=False,
             cover_ms=0, dry_run=False):
    """Goi /video/init/. Tra ve (publish_id, upload_url, than_gui)."""
    if privacy not in PRIVACY:
        raise SystemExit(f"privacy_level khong hop le: {privacy!r}. Co: {PRIVACY}")
    size = os.path.getsize(duong_video)
    chunk, so = ke_hoach_chunk(size)
    than = {
        "post_info": {
            "title": title,
            "privacy_level": privacy,
            "disable_comment": disable_comment,
            "disable_duet": disable_duet,
            "disable_stitch": disable_stitch,
            "video_cover_timestamp_ms": int(cover_ms),
            # Giong doc la AI sinh -> phai cong bo. TikTok co truong rieng cho
            # viec nay, va day la yeu cau ve noi dung AI cua ho.
            "is_aigc": bool(is_aigc),
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": chunk,
            "total_chunk_count": so,
        },
    }
    if dry_run:
        return None, None, than
    tk = lay_token()
    ma, tra = _goi(URL_INIT, data=than, token=tk)
    d = _bat_loi(ma, tra, "video/init")["data"]
    return d["publish_id"], d["upload_url"], than


def day_file(upload_url, duong_video, chunk_size, total_chunk_count, *, in_ra=print):
    """PUT tung chunk. upload_url chi song 1 gio.

    Content-Range dung chi so BYTE tuyet doi cua ca file, khong phai cua chunk.
    Chunk cuoi lay het phan du.
    """
    size = os.path.getsize(duong_video)
    with open(duong_video, "rb") as f:
        for i in range(total_chunk_count):
            dau = i * chunk_size
            cuoi = size - 1 if i == total_chunk_count - 1 else dau + chunk_size - 1
            f.seek(dau)
            data = f.read(cuoi - dau + 1)
            req = urllib.request.Request(
                upload_url, data=data, method="PUT",
                headers={
                    "Content-Type": "video/mp4",
                    "Content-Length": str(len(data)),
                    "Content-Range": f"bytes {dau}-{cuoi}/{size}",
                })
            try:
                with urllib.request.urlopen(req, timeout=600) as r:
                    ma = r.status
            except urllib.error.HTTPError as ex:
                raise SystemExit(
                    f"day chunk {i+1}/{total_chunk_count} that bai "
                    f"(HTTP {ex.code}): {ex.read().decode('utf-8','replace')[:500]}")
            in_ra(f"    chunk {i+1}/{total_chunk_count}  "
                  f"{len(data)/MB:.1f}MB  HTTP {ma}")


def trang_thai(publish_id):
    tk = lay_token()
    ma, than = _goi(URL_STATUS, data={"publish_id": publish_id}, token=tk)
    return _bat_loi(ma, than, "status/fetch")["data"]


def cho_xong(publish_id, *, gioi_han_s=600, nhip_s=5, in_ra=print):
    """Hoi trang thai den khi PUBLISH_COMPLETE hoac FAILED."""
    han = time.time() + gioi_han_s
    da_in = None
    while time.time() < han:
        d = trang_thai(publish_id)
        st = d.get("status")
        if st != da_in:
            da_in = st
            in_ra(f"    {st}")
        if st == "PUBLISH_COMPLETE":
            return d
        if st == "FAILED":
            raise SystemExit(
                f"TikTok tu choi: {d.get('fail_reason')}\n"
                f"  than: {json.dumps(d, ensure_ascii=False)[:400]}")
        time.sleep(nhip_s)
    raise SystemExit(f"qua {gioi_han_s}s van chua xong, trang thai cuoi: {da_in}")


def bam_file(duong):
    h = hashlib.sha1()
    with open(duong, "rb") as f:
        for khoi in iter(lambda: f.read(1 << 20), b""):
            h.update(khoi)
    return h.hexdigest()[:16]
