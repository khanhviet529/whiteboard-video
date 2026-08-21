# -*- coding: utf-8 -*-
"""UI local de bam dang video len TikTok. Chi stdlib.

    python dang/web.py        ->  http://127.0.0.1:8724

Vi sao co file nay khi da co CLI: quy trinh test la "chu dong bam dang", va nhin
mot bang co san ten / dung luong / fps / da dang chua thi quyet dinh nhanh hon
nhieu so voi go duong dan file. Day cung la buoc dem sang ban chay theo gio - cung
mot ham `dang_mot_video`, chi khac ai goi.

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
CONG = int(os.environ.get("DANG_WEB_PORT", "8724"))

# publish_id -> danh sach dong log. Giu trong RAM: phien lam viec ngan, va khong
# muon ghi them file trong thu muc da co token.
VIEC = {}
KHOA = threading.Lock()


def _ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def _thong_tin_video(duong):
    """(giay, fps, w, h) doc tu ffmpeg. Tra ve None neu khong doc duoc.

    Doc fps de chan ban nhap: `--fps 20` la de lap noi dung, dang len TikTok co
    the an `frame_rate_check_failed`, va ban nhap con lech sync nhe.
    """
    try:
        r = subprocess.run([_ffmpeg(), "-hide_banner", "-i", duong],
                           capture_output=True, text=True, timeout=30,
                           errors="replace")
        s = r.stderr
        giay = None
        m = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", s)
        if m:
            giay = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
        fps = None
        m = re.search(r"(\d+(?:\.\d+)?) fps", s)
        if m:
            fps = float(m.group(1))
        kt = None
        m = re.search(r", (\d{3,4})x(\d{3,4})", s)
        if m:
            kt = (int(m.group(1)), int(m.group(2)))
        return giay, fps, kt
    except Exception:
        return None, None, None


def _so():
    p = os.path.join(tt.GOC, "da-dang.json")
    if os.path.exists(p):
        return json.load(open(p, encoding="utf-8"))
    return {}


def _danh_sach():
    if not os.path.isdir(OUT):
        return []
    so = _so()
    ra = []
    for f in sorted(os.listdir(OUT)):
        if not f.lower().endswith(".mp4"):
            continue
        d = os.path.join(OUT, f)
        giay, fps, kt = _thong_tin_video(d)
        bam = tt.bam_file(d)
        ra.append({
            "ten": f, "duong": d, "mb": os.path.getsize(d) / tt.MB,
            "giay": giay, "fps": fps, "kt": kt, "bam": bam,
            "da_dang": so.get(bam),
            "sua_luc": time.strftime("%Y-%m-%d %H:%M",
                                     time.localtime(os.path.getmtime(d))),
        })
    ra.sort(key=lambda x: x["sua_luc"], reverse=True)
    return ra


# ------------------------------------------------------------------ dang
def dang_mot_video(duong, tieu_de, privacy, is_aigc, ma_viec):
    """Chay trong thread rieng. Ghi log vao VIEC[ma_viec] de trang tu doc."""
    def log(*a):
        with KHOA:
            VIEC[ma_viec]["log"].append(" ".join(str(x) for x in a))

    try:
        size = os.path.getsize(duong)
        chunk, n = tt.ke_hoach_chunk(size)
        log(f"file {os.path.basename(duong)}  {size/tt.MB:.1f}MB  "
            f"chunk {chunk/tt.MB:.1f}MB x{n}")
        log(f"privacy {privacy}  is_aigc {is_aigc}")
        pid, up, _ = tt.khoi_tao(duong, title=tieu_de, privacy=privacy,
                                 is_aigc=is_aigc)
        log(f"publish_id {pid}")
        with KHOA:
            VIEC[ma_viec]["publish_id"] = pid
        tt.day_file(up, duong, chunk, n, in_ra=log)
        log("cho TikTok xu ly...")
        tt.cho_xong(pid, in_ra=log)
        # Ghi so SAU khi TikTok bao xong, khong phai sau khi day xong: day xong ma
        # TikTok tu choi thi chua dang duoc, ghi so luc do la chan lan thu lai.
        p = os.path.join(tt.GOC, "da-dang.json")
        so = _so()
        so[tt.bam_file(duong)] = {
            "file": duong, "publish_id": pid, "privacy": privacy,
            "tieu_de": tieu_de,
            "luc": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        with open(p, "w", encoding="utf-8") as f:
            json.dump(so, f, ensure_ascii=False, indent=2)
        log("XONG")
        with KHOA:
            VIEC[ma_viec]["xong"] = True
    except SystemExit as e:
        log("LOI:", e)
        with KHOA:
            VIEC[ma_viec]["xong"] = True
            VIEC[ma_viec]["loi"] = True
    except Exception as e:  # noqa: BLE001
        log(f"LOI {type(e).__name__}: {e}")
        with KHOA:
            VIEC[ma_viec]["xong"] = True
            VIEC[ma_viec]["loi"] = True


# ------------------------------------------------------------------- trang
CSS = """
:root{color-scheme:dark}
body{background:#14110f;color:#e8e2d9;font:14px/1.55 ui-sans-serif,system-ui;
     margin:0;padding:28px 32px;max-width:1150px}
h1{font-size:19px;margin:0 0 4px}
.phu{color:#8d857a;font-size:12.5px;margin-bottom:22px}
table{border-collapse:collapse;width:100%}
th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;
   color:#8d857a;border-bottom:1px solid #302a25;padding:0 10px 7px 0;font-weight:600}
td{border-bottom:1px solid #221e1a;padding:11px 10px 11px 0;vertical-align:top}
.ten{font-weight:600}
.nho{color:#8d857a;font-size:12px}
input,select{background:#1e1a17;color:#e8e2d9;border:1px solid #3a332c;
             border-radius:5px;padding:6px 8px;font:13px inherit}
input[type=text]{width:270px}
button{background:#d98a7a;color:#14110f;border:0;border-radius:5px;
       padding:7px 15px;font:600 13px inherit;cursor:pointer}
button:disabled{background:#3a332c;color:#7a736a;cursor:default}
.ok{color:#8fbf7a}.canh{color:#e0b552}.loi{color:#e0736a}
pre{background:#0e0c0a;border:1px solid #2a251f;border-radius:6px;
    padding:12px;font:12px ui-monospace;overflow:auto;max-height:280px;
    white-space:pre-wrap;margin:8px 0 0}
"""

JS = """
function dang(bam){
  const r = document.getElementById('r-'+bam);
  const b = r.querySelector('button');
  b.disabled = true; b.textContent = 'dang gui...';
  const fd = new URLSearchParams({
    bam: bam,
    tieu_de: r.querySelector('[name=tieu_de]').value,
    privacy: r.querySelector('[name=privacy]').value,
    aigc: r.querySelector('[name=aigc]').checked ? '1' : '0'
  });
  fetch('/dang', {method:'POST', body:fd}).then(x=>x.json()).then(j=>{
    if(j.loi){ b.disabled=false; b.textContent='Đăng'; alert(j.loi); return; }
    theo(j.ma, bam);
  });
}
function theo(ma, bam){
  const o = document.getElementById('log-'+bam);
  o.style.display='block';
  const t = setInterval(()=>{
    fetch('/log?ma='+ma).then(x=>x.json()).then(j=>{
      o.textContent = j.log.join('\\n');
      o.scrollTop = o.scrollHeight;
      if(j.xong){ clearInterval(t);
        const b=document.querySelector('#r-'+bam+' button');
        b.textContent = j.loi ? 'Lỗi — xem log' : 'Đã đăng';
        if(j.loi) b.disabled=false;
        if(!j.loi) setTimeout(()=>location.reload(), 1500);
      }
    });
  }, 1200);
}
"""


def _trang():
    ds = _danh_sach()
    # Trang thai token: cho biet co dang nhap chua, khong in token.
    try:
        tt.cau_hinh()
        if os.path.exists(tt.TEP_TOKEN):
            t = json.load(open(tt.TEP_TOKEN, encoding="utf-8"))
            con = int(t.get("het_han_luc", 0) - time.time())
            tt_token = (f"<span class=ok>đã đăng nhập</span> · access_token còn "
                        f"{max(0, con)//60} phút (tự refresh)")
        else:
            tt_token = ("<span class=canh>chưa đăng nhập</span> — chạy "
                        "<code>python dang/dang.py auth</code> một lần")
    except SystemExit as e:
        tt_token = f"<span class=loi>{html.escape(str(e).splitlines()[0])}</span>"

    hang = []
    for v in ds:
        bam = v["bam"]
        fps = v["fps"]
        canh = []
        if fps and abs(fps - 30) > 0.5:
            canh.append(f"<span class=canh>{fps:g} fps — bản nháp, "
                        f"TikTok có thể từ chối</span>")
        if v["kt"] and v["kt"] != (1080, 1920):
            canh.append(f"<span class=canh>{v['kt'][0]}x{v['kt'][1]} — "
                        f"không phải 9:16</span>")
        meta = (f"{v['mb']:.1f} MB · "
                f"{('%d:%02d' % (int(v['giay'])//60, int(v['giay'])%60)) if v['giay'] else '?'}"
                f" · {fps:g} fps" if fps else f"{v['mb']:.1f} MB")
        dd = v["da_dang"]
        if dd:
            hd = (f"<span class=ok>đã đăng</span> {html.escape(dd.get('luc',''))}"
                  f"<br><span class=nho>{html.escape(dd.get('privacy',''))} · "
                  f"{html.escape(dd.get('publish_id','')[:24])}</span>")
            nut = "<button disabled>Đã đăng</button>"
        else:
            hd = "<span class=nho>chưa đăng</span>"
            nut = f"<button onclick=\"dang('{bam}')\">Đăng</button>"
        mac_dinh = os.path.splitext(v["ten"])[0].replace("-", " ")
        hang.append(f"""
<tr id="r-{bam}">
  <td><div class=ten>{html.escape(v['ten'])}</div>
      <div class=nho>{meta} · {v['sua_luc']}</div>
      {'<div>' + ' '.join(canh) + '</div>' if canh else ''}</td>
  <td><input type=text name=tieu_de value="{html.escape(mac_dinh)}"></td>
  <td><select name=privacy>
        <option value=SELF_ONLY selected>SELF_ONLY (riêng tư)</option>
        <option value=FOLLOWER_OF_CREATOR>FOLLOWER_OF_CREATOR</option>
        <option value=MUTUAL_FOLLOW_FRIENDS>MUTUAL_FOLLOW_FRIENDS</option>
        <option value=PUBLIC_TO_EVERYONE>PUBLIC_TO_EVERYONE</option>
      </select>
      <label class=nho><input type=checkbox name=aigc checked> is_aigc</label></td>
  <td>{hd}</td>
  <td>{nut}<pre id="log-{bam}" style="display:none"></pre></td>
</tr>""")

    return f"""<!doctype html><meta charset=utf-8>
<title>Đăng TikTok</title><style>{CSS}</style>
<h1>Đăng video lên TikTok</h1>
<div class=phu>{tt_token}<br>
Thư mục: <code>{html.escape(OUT)}</code> · {len(ds)} video ·
App chưa qua audit thì TikTok khoá mọi bài ở chế độ riêng tư, bất kể privacy chọn ở đây.</div>
<table><tr><th>Video<th>Tiêu đề<th>Quyền xem<th>Trạng thái<th></tr>
{''.join(hang) if hang else '<tr><td colspan=5 class=nho>Không có mp4 nào trong out/</td></tr>'}
</table>
<script>{JS}</script>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def _tra(self, ma, kieu, than):
        self.send_response(ma)
        self.send_header("Content-Type", kieu)
        self.send_header("Content-Length", str(len(than)))
        self.end_headers()
        self.wfile.write(than)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path == "/":
            return self._tra(200, "text/html; charset=utf-8",
                             _trang().encode("utf-8"))
        if u.path == "/log":
            ma = urllib.parse.parse_qs(u.query).get("ma", [""])[0]
            with KHOA:
                v = VIEC.get(ma, {"log": ["khong thay viec"], "xong": True})
                than = json.dumps({"log": v["log"], "xong": v.get("xong", False),
                                   "loi": v.get("loi", False)})
            return self._tra(200, "application/json", than.encode("utf-8"))
        self._tra(404, "text/plain", b"404")

    def do_POST(self):
        if urllib.parse.urlparse(self.path).path != "/dang":
            return self._tra(404, "text/plain", b"404")
        n = int(self.headers.get("Content-Length", 0))
        f = urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8"))
        bam = f.get("bam", [""])[0]
        v = next((x for x in _danh_sach() if x["bam"] == bam), None)
        if not v:
            return self._tra(200, "application/json",
                             json.dumps({"loi": "khong thay video"}).encode())
        if v["da_dang"]:
            return self._tra(200, "application/json",
                             json.dumps({"loi": "file nay da dang roi"}).encode())
        ma = f"{bam}-{int(time.time())}"
        with KHOA:
            VIEC[ma] = {"log": [], "xong": False}
        threading.Thread(target=dang_mot_video, daemon=True, args=(
            v["duong"], f.get("tieu_de", [v["ten"]])[0],
            f.get("privacy", ["SELF_ONLY"])[0],
            f.get("aigc", ["1"])[0] == "1", ma)).start()
        self._tra(200, "application/json", json.dumps({"ma": ma}).encode())


def main():
    srv = ThreadingHTTPServer(("127.0.0.1", CONG), H)
    print(f"UI dang video: http://127.0.0.1:{CONG}")
    print(f"thu muc video: {OUT}")
    print("Ctrl+C de dung. Chi bind 127.0.0.1 - dung mo ra ngoai.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\ndung.")


if __name__ == "__main__":
    main()
