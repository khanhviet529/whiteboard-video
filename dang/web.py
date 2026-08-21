# -*- coding: utf-8 -*-
"""UI local de bam dang video len TikTok, va xem so lieu bai da dang. Chi stdlib.

    py dang/web.py        ->  http://127.0.0.1:8724

Vi sao co file nay khi da co CLI: quy trinh test la "chu dong bam dang", va nhin
mot bang co san thumbnail / fps / da dang chua thi quyet dinh nhanh hon nhieu so
voi go duong dan file. Day cung la buoc dem sang ban chay theo gio - cung mot ham
`dang_mot_video`, chi khac ai goi.

Hai thu UI lam ma app TikTok khong lam duoc:
  * Loc ra dung ban CHINH THUC cua tung so - `out/` lan ca ban nhap, ban thu CRF,
    ban thu animation. Bam nham mot ban `CUOI2` len TikTok thi phai xoa bai.
  * Noi so lieu bai dang voi metadata cua CHINH BAN: screenplay nao sinh ra bai
    nao. TikTok chi biet bai cua no, khong biet nguon.

CHI bind 127.0.0.1. Khong co xac thuc, va khong duoc mo ra ngoai: bat ky ai vao
duoc trang nay la dang duoc video len tai khoan TikTok cua ban.
"""
import html
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tiktok as tt  # noqa: E402

REPO = os.path.dirname(tt.GOC)
OUT = os.path.join(REPO, "out")
KICH_BAN = os.path.join(REPO, "screenplays")
THUMB = os.path.join(REPO, "build", "thumb")
CONG = int(os.environ.get("DANG_WEB_PORT", "8724"))

# Hau to engine ma render.py them vao ten file khi co --engine.
HAU_ENGINE = ("-voicestudio", "-omnivoice", "-edge")

VIEC = {}                 # ma_viec -> {log, xong, loi}
KHOA = threading.Lock()
SO_LIEU = {"luc": 0, "video": [], "loi": None}


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


# --------------------------------------------------------------------- video
def _thong_tin(duong):
    """(giay, fps, (w,h)) doc tu ffmpeg. fps de chan ban nhap --fps 20."""
    try:
        r = subprocess.run([_ffmpeg(), "-hide_banner", "-i", duong],
                           capture_output=True, text=True, timeout=30,
                           errors="replace")
        s = r.stderr
        giay = fps = kt = None
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", s)
        if m:
            giay = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        m = re.search(r"(\d+(?:\.\d+)?) fps", s)
        if m:
            fps = float(m.group(1))
        m = re.search(r", (\d{3,4})x(\d{3,4})", s)
        if m:
            kt = (int(m.group(1)), int(m.group(2)))
        return giay, fps, kt
    except Exception:
        return None, None, None


def _kich_ban_cua(ten_file):
    """Ten file mp4 -> ten screenplay tuong ung, hoac None. Day la bo loc.

    `render.py` dat ten `<stem>[-engine].mp4` tu `screenplays/<stem>.yaml`. File nao
    khong lan ra screenplay nao thi la ban thu (`cache-stale-CUOI2`, `hero-crf18`,
    `angle_0-doi_mau`...) - an di theo mac dinh, vi bam nham mot ban thu len TikTok
    thi phai xoa bai.
    """
    stem = os.path.splitext(ten_file)[0]
    for h in HAU_ENGINE:
        if stem.endswith(h):
            stem = stem[:-len(h)]
            break
    return stem if os.path.exists(os.path.join(KICH_BAN, stem + ".yaml")) else None


def _so():
    p = os.path.join(tt.GOC, "da-dang.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}


def _danh_sach():
    if not os.path.isdir(OUT):
        return []
    so = _so()
    ra = []
    for f in sorted(os.listdir(OUT)):
        if not f.lower().endswith(".mp4"):
            continue
        d = os.path.join(OUT, f)
        giay, fps, kt = _thong_tin(d)
        bam = tt.bam_file(d)
        ra.append({
            "ten": f, "duong": d, "bam": bam,
            "mb": os.path.getsize(d) / tt.MB,
            "giay": giay, "fps": fps, "kt": kt,
            "kich_ban": _kich_ban_cua(f),
            "da_dang": so.get(bam),
            "sua_luc": os.path.getmtime(d),
        })
    # Mot screenplay co the co NHIEU file: `cache-stale.mp4`,
    # `cache-stale-voicestudio.mp4`, `-edge`, `-omnivoice`... Bo loc giu ca bon vi
    # ca bon deu "chinh thuc" theo ten. Nhung dang thi chi dang MOT, nen danh dau
    # ban moi nhat cua tung screenplay - mat nhin vao dung dong can bam.
    moi_nhat = {}
    for v in ra:
        k = v["kich_ban"]
        if k and v["sua_luc"] > moi_nhat.get(k, (0, None))[0]:
            moi_nhat[k] = (v["sua_luc"], v["bam"])
    for v in ra:
        v["moi_nhat"] = (v["kich_ban"] is not None
                         and moi_nhat.get(v["kich_ban"], (0, None))[1] == v["bam"])
    # Ban chinh len truoc, trong do ban moi nhat len truoc, roi moi den thoi gian.
    ra.sort(key=lambda x: (x["kich_ban"] is None, not x["moi_nhat"], -x["sua_luc"]))
    return ra


def _thumbnail(duong, bam):
    """Anh 1 frame, cache trong build/thumb. Sinh LAZY qua /thumb.

    Sinh het 34 thumbnail luc dung trang la doi ~35 giay truoc khi thay gi. De
    browser goi tung anh thi no tai song song va trang hien ngay.
    """
    os.makedirs(THUMB, exist_ok=True)
    p = os.path.join(THUMB, bam + ".jpg")
    if os.path.exists(p):
        return open(p, "rb").read()
    try:
        subprocess.run(
            [_ffmpeg(), "-hide_banner", "-loglevel", "error", "-ss", "3",
             "-i", duong, "-frames:v", "1", "-vf", "scale=96:-1",
             "-f", "image2", "-c:v", "mjpeg", "-y", p],
            capture_output=True, timeout=40)
        return open(p, "rb").read() if os.path.exists(p) else None
    except Exception:
        return None


# ------------------------------------------------------------------ dang
def dang_mot_video(duong, tieu_de, privacy, is_aigc, ma_viec, cach="inbox"):
    def log(*a):
        with KHOA:
            VIEC[ma_viec]["log"].append(" ".join(str(x) for x in a))

    try:
        size = os.path.getsize(duong)
        chunk, n = tt.ke_hoach_chunk(size)
        log(f"{os.path.basename(duong)}  {size/tt.MB:.1f}MB  "
            f"chunk {chunk/tt.MB:.1f}MB x{n}")
        if cach == "inbox":
            log("cach: inbox - tieu de/quyen xem dat trong app TikTok")
            pid, up, _ = tt.khoi_tao_inbox(duong)
        else:
            log(f"cach: dang truc tiep  privacy {privacy}  is_aigc {is_aigc}")
            pid, up, _ = tt.khoi_tao(duong, title=tieu_de, privacy=privacy,
                                     is_aigc=is_aigc)
        log(f"publish_id {pid}")
        tt.day_file(up, duong, chunk, n, in_ra=log)
        log("cho TikTok xu ly...")
        d = tt.cho_xong(pid, in_ra=log,
                        xong_o=("SEND_TO_USER_INBOX",) if cach == "inbox" else None)
        if cach == "inbox":
            log("Da vao inbox TikTok. Mo app, bam thong bao de hoan tat dang.")

        # Ghi so SAU khi TikTok bao xong, khong phai sau khi day xong chunk: day
        # xong ma TikTok tu choi thi chua dang duoc, ghi so luc do la chan lan thu
        # lai. Luu ca `tra_ve` de lan dau chay that biet TikTok co tra id bai hay
        # khong - neu co thi doi chieu voi Display API duoc chinh xac.
        so = _so()
        so[tt.bam_file(duong)] = {
            "file": duong, "publish_id": pid, "cach": cach,
            "privacy": "-" if cach == "inbox" else privacy,
            "tieu_de": tieu_de, "kich_ban": _kich_ban_cua(os.path.basename(duong)),
            "luc": time.strftime("%Y-%m-%dT%H:%M:%S"), "tra_ve": d,
        }
        with open(os.path.join(tt.GOC, "da-dang.json"), "w",
                  encoding="utf-8") as f:
            json.dump(so, f, ensure_ascii=False, indent=2)
        log("XONG")
        with KHOA:
            VIEC[ma_viec]["xong"] = True
    except BaseException as e:      # SystemExit cua tool cung phai vao log
        log(f"LOI {type(e).__name__}: {e}")
        with KHOA:
            VIEC[ma_viec].update(xong=True, loi=True)


def lay_so_lieu():
    try:
        vids, _, _ = tt.danh_sach_da_dang(20)
        SO_LIEU.update(luc=time.time(), video=vids, loi=None)
    except BaseException as e:
        SO_LIEU.update(luc=time.time(), loi=f"{type(e).__name__}: {e}")


# ------------------------------------------------------------------- trang
CSS = """
:root{color-scheme:dark;--n:#8d857a;--v:#221e1a;--nen:#14110f;--chu:#e8e2d9}
*{box-sizing:border-box}
body{background:var(--nen);color:var(--chu);margin:0;padding:26px 30px 60px;
     font:14px/1.5 ui-sans-serif,system-ui,"Segoe UI";max-width:1240px}
h1{font-size:20px;margin:0 0 4px;letter-spacing:-.01em}
h2{font-size:11px;letter-spacing:.11em;text-transform:uppercase;color:var(--n);
   margin:34px 0 12px;display:flex;align-items:center;gap:12px;font-weight:600}
h2 .d{flex:1;height:1px;background:var(--v)}
.phu{color:var(--n);font-size:12.5px;line-height:1.65}
.phu b{color:#c9c1b6;font-weight:600}
code{font:12px ui-monospace;background:#1e1a17;padding:1px 5px;border-radius:4px}
table{border-collapse:collapse;width:100%}
th{text-align:left;font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;
   color:var(--n);border-bottom:1px solid #302a25;padding:0 12px 8px 0;font-weight:600}
td{border-bottom:1px solid var(--v);padding:10px 12px 10px 0;vertical-align:middle}
tr:hover td{background:#191512}
img.th{width:48px;height:85px;object-fit:cover;border-radius:4px;
       background:#1e1a17;display:block}
.ten{font-weight:600;letter-spacing:-.005em}
.nho{color:var(--n);font-size:11.5px}
.so{font:13px ui-monospace;text-align:right;white-space:nowrap}
input,select{background:#1e1a17;color:var(--chu);border:1px solid #3a332c;
             border-radius:5px;padding:6px 8px;font:13px inherit}
input:disabled,select:disabled{opacity:.42}
input[type=text]{width:100%;min-width:170px}
button{background:#d98a7a;color:#14110f;border:0;border-radius:5px;
       padding:7px 16px;font:600 13px inherit;cursor:pointer;white-space:nowrap}
button.phu2{background:#2a251f;color:var(--chu);font-weight:500}
button:disabled{background:#332e28;color:#7a736a;cursor:default}
.ok{color:#8fbf7a}.canh{color:#e0b552}.loi{color:#e0736a}
.chip{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:99px;
      background:#2a251f;color:var(--n)}
.chip.g{background:#243020;color:#8fbf7a}
.chip.c{background:#332a1c;color:#e0b552}
pre{background:#0e0c0a;border:1px solid #2a251f;border-radius:6px;padding:11px;
    font:11.5px/1.5 ui-monospace;max-height:240px;overflow:auto;
    white-space:pre-wrap;margin:8px 0 0}
a{color:#cfa08f}
label.tg{display:inline-flex;align-items:center;gap:6px;font-size:12px;
         color:var(--n);cursor:pointer;font-weight:400;letter-spacing:0;
         text-transform:none}
"""

JS = """
function dang(bam){
  const r=document.getElementById('r-'+bam), b=r.querySelector('button.go');
  b.disabled=true; b.textContent='dang gui...';
  fetch('/dang',{method:'POST',body:new URLSearchParams({
    bam, cach:r.querySelector('[name=cach]').value,
    tieu_de:r.querySelector('[name=tieu_de]').value,
    privacy:r.querySelector('[name=privacy]').value,
    aigc:r.querySelector('[name=aigc]').checked?'1':'0'})})
   .then(x=>x.json()).then(j=>{
     if(j.loi){b.disabled=false;b.textContent='Dang';alert(j.loi);return;}
     theo(j.ma,bam);});
}
function theo(ma,bam){
  const o=document.getElementById('log-'+bam); o.style.display='block';
  const t=setInterval(()=>fetch('/log?ma='+ma).then(x=>x.json()).then(j=>{
    o.textContent=j.log.join('\\n'); o.scrollTop=o.scrollHeight;
    if(j.xong){clearInterval(t);
      const b=document.querySelector('#r-'+bam+' button.go');
      b.textContent=j.loi?'Loi - xem log':'Da dang';
      if(j.loi)b.disabled=false; else setTimeout(()=>location.reload(),1800);}
  }),1200);
}
function doi_cach(s){
  const r=s.closest('tr'), ib=s.value==='inbox';
  ['privacy','tieu_de','aigc'].forEach(n=>r.querySelector('[name='+n+']').disabled=ib);
}
function loc(c){ location.search = c.checked ? '?tat_ca=1' : ''; }
function so_lieu(b){
  b.disabled=true; b.textContent='dang goi TikTok...';
  fetch('/so-lieu',{method:'POST'}).then(()=>location.reload());
}
"""


def _hms(g):
    return f"{int(g)//60}:{int(g)%60:02d}" if g else "?"


def _trang_thai_token():
    try:
        tt.cau_hinh()
    except SystemExit as e:
        return f"<b class=loi>{html.escape(str(e).splitlines()[0])}</b>"
    if not os.path.exists(tt.tep_token()):
        return ("<b class=canh>chua dang nhap</b> &mdash; chay "
                "<code>py dang/dang.py auth</code> mot lan")
    t = json.load(open(tt.tep_token(), encoding="utf-8"))
    con = max(0, int(t.get("het_han_luc", 0) - time.time())) // 60
    sc = t.get("scope") or ""
    thieu = [s for s in ("video.upload", "video.publish", "video.list")
             if s not in sc]
    return (f"<b class=ok>da dang nhap</b> &middot; token con {con} phut "
            f"(tu refresh) &middot; "
            + (f"<span class=canh>thieu scope: {', '.join(thieu)}</span>"
               if thieu else "du scope"))


def _hang_video(v):
    bam, fps = v["bam"], v["fps"]
    canh = []
    if fps and abs(fps - 30) > .5:
        canh.append(f"<span class=canh>{fps:g} fps &middot; ban nhap</span>")
    if v["kt"] and v["kt"] != (1080, 1920):
        canh.append(f"<span class=canh>{v['kt'][0]}&times;{v['kt'][1]}</span>")
    if not v["kich_ban"]:
        kb = "<span class=chip>ban thu</span>"
    elif v["moi_nhat"]:
        kb = f"<span class='chip g'>{html.escape(v['kich_ban'])}</span>"
    else:
        kb = (f"<span class=chip>{html.escape(v['kich_ban'])}</span>"
              f" <span class='chip c'>ban cu hon</span>")
    dd = v["da_dang"]
    if dd:
        nut = "<button class=go disabled>Da dang</button>"
        tt_ = (f"<span class=ok>da dang</span><br><span class=nho>"
               f"{html.escape(dd.get('cach', '?'))} &middot; "
               f"{html.escape((dd.get('luc') or '')[:16])}</span>")
    else:
        # Ban cu hon van dang duoc, nhung nut mo hon de mat khong bam nham.
        lop = "go" if (v["moi_nhat"] or not v["kich_ban"]) else "go phu2"
        nut = f"<button class='{lop}' onclick=\"dang('{bam}')\">Dang</button>"
        tt_ = "<span class=nho>chua dang</span>"
    mac_dinh = (v["kich_ban"] or os.path.splitext(v["ten"])[0]).replace("-", " ")
    return f"""
<tr id="r-{bam}">
  <td><img class=th loading=lazy src="/thumb?bam={bam}" alt=""></td>
  <td><div class=ten>{html.escape(v['ten'])}</div>
      <div class=nho>{kb} &middot; {v['mb']:.1f} MB &middot; {_hms(v['giay'])}
      {' &middot; ' + ' '.join(canh) if canh else ''}</div></td>
  <td><select name=cach onchange="doi_cach(this)">
        <option value=inbox selected>Nhap vao inbox</option>
        <option value=truc_tiep>Dang truc tiep</option>
      </select></td>
  <td><input type=text name=tieu_de disabled value="{html.escape(mac_dinh)}">
      <div style="margin-top:5px">
        <select name=privacy disabled>
          <option value=SELF_ONLY>Rieng tu</option>
          <option value=FOLLOWER_OF_CREATOR>Nguoi theo doi</option>
          <option value=MUTUAL_FOLLOW_FRIENDS>Ban be</option>
          <option value=PUBLIC_TO_EVERYONE>Cong khai</option>
        </select>
        <label class=tg><input type=checkbox name=aigc checked disabled> AI</label>
      </div></td>
  <td>{tt_}</td>
  <td>{nut}<pre id="log-{bam}" style="display:none"></pre></td>
</tr>"""


def _khoi_so_lieu():
    so = _so()
    theo_td = {(x.get("tieu_de") or "").strip().lower(): x for x in so.values()}
    if SO_LIEU["loi"]:
        return f"<div class=phu><span class=loi>{html.escape(SO_LIEU['loi'])}</span></div>"
    if not SO_LIEU["video"]:
        return ("<div class=phu>Chua lay so lieu. Bam <b>Lam moi</b> &mdash; can "
                "scope <code>video.list</code>.</div>")
    hang = []
    for v in SO_LIEU["video"]:
        td = (v.get("title") or v.get("video_description") or "").strip()
        khop = theo_td.get(td.lower())
        nguon = (f"<span class='chip g'>{html.escape(khop['kich_ban'])}</span>"
                 if khop and khop.get("kich_ban") else "<span class=nho>&mdash;</span>")
        link = v.get("share_url")
        hang.append(f"""
<tr><td><div class=ten>{html.escape(td[:58]) or '(khong tieu de)'}</div>
        <div class=nho>
        {time.strftime('%Y-%m-%d %H:%M', time.localtime(v.get('create_time') or 0))}
        &middot; {_hms(v.get('duration'))}</div></td>
    <td>{nguon}</td>
    <td class=so>{v.get('view_count') or 0:,}</td>
    <td class=so>{v.get('like_count') or 0:,}</td>
    <td class=so>{v.get('comment_count') or 0:,}</td>
    <td class=so>{v.get('share_count') or 0:,}</td>
    <td>{f'<a href="{html.escape(link)}" target=_blank>mo</a>' if link else ''}</td>
</tr>""")
    return f"""<table>
<tr><th>Video<th>Tu screenplay<th>View<th>Like<th>Binh luan<th>Share<th></tr>
{''.join(hang)}</table>
<div class=phu style="margin-top:9px">Cap nhat
{time.strftime('%H:%M:%S', time.localtime(SO_LIEU['luc']))} &middot; TikTok tra
toi da 20 video gan nhat</div>"""


def _trang(tat_ca=False):
    ds = _danh_sach()
    chinh = [v for v in ds if v["kich_ban"]]
    hien = ds if tat_ca else chinh
    an = len(ds) - len(chinh)
    hang = "".join(_hang_video(v) for v in hien)
    return f"""<!doctype html><meta charset=utf-8><title>Dang TikTok</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>{CSS}</style>
<h1>Dang video len TikTok</h1>
<div class=phu>{_trang_thai_token()}<br>
<b>Nhap vao inbox</b> (mac dinh) &mdash; video vao inbox, ban bam thong bao de tu
hoan tat; tieu de va quyen xem dat trong app. Day la duong duy nhat ra video
<b>public that</b> khi app chua qua audit.<br>
<b>Dang truc tiep</b> &mdash; dang thang len trang, nhung app chua audit thi TikTok
khoa moi bai o rieng tu bat ke quyen xem chon o day.</div>

<h2>Cho dang &middot; {len(hien)}<span class=d></span>
  <label class=tg><input type=checkbox onchange="loc(this)"
    {'checked' if tat_ca else ''}> hien ca {an} ban thu</label></h2>
<table>
<tr><th><th>Video<th>Cach dang<th>Tieu de &middot; quyen xem<th>Trang thai<th></tr>
{hang or '<tr><td colspan=6 class=nho>Khong co video nao</td></tr>'}
</table>

<h2>Da dang tren TikTok<span class=d></span>
  <button class=phu2 onclick="so_lieu(this)">Lam moi so lieu</button></h2>
{_khoi_so_lieu()}
<script>{JS}</script>"""


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *_):
        pass

    def _tra(self, ma, kieu, than, cache=None):
        self.send_response(ma)
        self.send_header("Content-Type", kieu)
        if cache:
            self.send_header("Cache-Control", cache)
        self.send_header("Content-Length", str(len(than)))
        self.end_headers()
        self.wfile.write(than)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/":
            return self._tra(200, "text/html; charset=utf-8",
                             _trang(tat_ca=bool(q.get("tat_ca"))).encode("utf-8"))
        if u.path == "/thumb":
            bam = q.get("bam", [""])[0]
            v = next((x for x in _danh_sach() if x["bam"] == bam), None)
            b = _thumbnail(v["duong"], bam) if v else None
            if not b:
                return self._tra(404, "text/plain", b"")
            return self._tra(200, "image/jpeg", b, cache="max-age=86400")
        if u.path == "/log":
            with KHOA:
                v = VIEC.get(q.get("ma", [""])[0],
                             {"log": ["khong thay viec"], "xong": True})
                t = json.dumps({"log": v["log"], "xong": v.get("xong", False),
                                "loi": v.get("loi", False)})
            return self._tra(200, "application/json", t.encode("utf-8"))
        self._tra(404, "text/plain", b"404")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path).path
        if u == "/so-lieu":
            lay_so_lieu()
            return self._tra(200, "application/json", b"{}")
        if u != "/dang":
            return self._tra(404, "text/plain", b"404")
        n = int(self.headers.get("Content-Length", 0))
        f = urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8"))
        bam = f.get("bam", [""])[0]
        v = next((x for x in _danh_sach() if x["bam"] == bam), None)
        if not v or v["da_dang"]:
            return self._tra(200, "application/json", json.dumps(
                {"loi": "khong thay video" if not v else "file nay da dang roi"}
            ).encode())
        ma = f"{bam}-{int(time.time())}"
        with KHOA:
            VIEC[ma] = {"log": [], "xong": False}
        threading.Thread(target=dang_mot_video, daemon=True, args=(
            v["duong"], f.get("tieu_de", [v["ten"]])[0],
            f.get("privacy", ["SELF_ONLY"])[0],
            f.get("aigc", ["1"])[0] == "1", ma,
            f.get("cach", ["inbox"])[0])).start()
        self._tra(200, "application/json", json.dumps({"ma": ma}).encode())


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        """Browser dong ket noi keep-alive la BINH THUONG, khong phai loi.

        Voi HTTP/1.1 keep-alive, moi tab dong hay moi lan reload deu de lai mot
        ket noi bi dong phia client. Mac dinh socketserver nem ca traceback ra
        terminal - nhin nhu tool dang loi, va lam log that bi lut.
        """
        if sys.exc_info()[0] in (ConnectionResetError, ConnectionAbortedError,
                                 BrokenPipeError):
            return
        super().handle_error(request, client_address)


def main():
    srv = Server(("127.0.0.1", CONG), H)
    print(f"UI dang video: http://127.0.0.1:{CONG}")
    print(f"thu muc video: {OUT}")
    print("Ctrl+C de dung. Chi bind 127.0.0.1 - dung mo ra ngoai.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\ndung.")


if __name__ == "__main__":
    main()
