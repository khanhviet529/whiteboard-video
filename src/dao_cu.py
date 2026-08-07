"""Dao cu: hinh nho gan duoc vao BAT KY canh nao, khong phai loai canh rieng.

Ly do co tang nay. Do tren nhung loai canh da lam: `gantt` 167 dong, `queue`
khoang 150, `topology` 130. Voi mot hinh chi dung MOT lan cho tam giay man hinh
thi ty le do rat te khi nhan voi 90 video.

Nhung co nhung hinh vua cu the vua dung lai duoc nhieu lan. Cai dien thoai co
nut bam xuat hien o tru tien hai lan, idempotency, retry, race condition. Dai
ngay dem xuat hien o cron chay dem, cache het han, job batch, "sang hom sau moi
phat hien". Do la tang nay: 30-60 dong moi cai, gan duoc vao moi canh.

## MOT LUAT PHAI GIU

Canh mo phong van phai co it nhat MOT con so dang doi. Dien thoai nhap nhay
CONG bo dem "da gui 2 request" thi manh; dien thoai nhap nhay khong kem gi la
hoat hinh. The manh rieng cua kenh nay la dong ho do chay that - README ghi
thang "nguoi xem khong doc bieu do, ho doc so". Dao cu de lam ro BOI CANH, khong
de thay cho con so.

## Cach dung

    prop:
      loai: dien_thoai
      goc: tren-phai          # tren-trai | tren-phai | duoi-trai | duoi-phai
      lan: 2                  # so lan bam
      nhan: KHÁCH BẤM 2 LẦN

Dao cu ve DE LEN canh, nen nguoi viet phai tu chon goc con trong. Soi bang
`--stills` truoc khi render.
"""
from PIL import Image, ImageDraw

import typo
from style import W, clamp, s
from typo import expo_out, glow, mono, track_w, ttext

# Kich thuoc va vi tri lay tu bench luc chay, de dao cu khong phai biet bo cuc.
RONG = 200


def _co_vua(txt, rong_max, co=18, tr=2.2, min_co=13):
    """Co chu nho dan cho toi khi vua be ngang cho phep.

    Bat buoc vi nhan cua dao cu do NGUOI VIET dat: "SANG THU BAY" dai hon "SANG"
    gap ba lan, ma khung thi co dinh. Khong co ham nay thi chu tran ra ngoai
    khung - da thay dung loi do o lan ve dau tien.
    """
    while co > min_co and track_w(txt, typo.mono_font(co, 700), tr) > rong_max:
        co -= 1
    return co


def _neo(goc, rong, cao, khung):
    """Goc -> toa do. `khung` la (x0, y0, x1, y1) cua san dien."""
    x0, y0, x1, y1 = khung
    m = 8
    return {
        "tren-trai": (x0 + m, y0 + m),
        "tren-phai": (x1 - rong - m, y0 + m),
        "duoi-trai": (x0 + m, y1 - cao - m),
        "duoi-phai": (x1 - rong - m, y1 - cao - m),
    }.get(goc, (x1 - rong - m, y0 + m))


# --------------------------------------------------------------- dien thoai

def dien_thoai(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Dien thoai co nut, va ngon tay bam `lan` lan.

    Dung khi kich ban noi "khach bam mot lan" - cho nguoi xem thay CU BAM chu
    khong chi nghe ke. Moi cu bam la mot vet loang toa ra, nen dem duoc bang mat.
    """
    lan = int(sp.get("lan", 1))
    rong, cao = 132, 250
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao + 34, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return

    # than may + man hinh
    e = expo_out(q)
    d.rounded_rectangle([s(x), s(y), s(x + rong), s(y + cao)], radius=s(18),
                        fill=nen + (255,), outline=vien + (255,), width=s(3))
    d.rounded_rectangle([s(x + 10), s(y + 22), s(x + rong - 10), s(y + cao - 40)],
                        radius=s(8), fill=(0, 0, 0, 255))
    d.rounded_rectangle([s(x + rong / 2 - 18), s(y + 10), s(x + rong / 2 + 18),
                         s(y + 15)], radius=s(3), fill=vien + (255,))

    # nut trong man hinh
    ny = y + cao - 92
    nx0, nx1 = x + 24, x + rong - 24
    d.rounded_rectangle([s(nx0), s(ny), s(nx1), s(ny + 38)], radius=s(8),
                        fill=mau + (255,))
    nut = sp.get("nut", "ĐẶT HÀNG")
    co = _co_vua(nut, nx1 - nx0 - 16, 15, 1.2, 10)
    mono(base, nut, (nx0 + 8, ny + 12), (10, 10, 12), q, co, 1.2, 700)

    # cac cu bam: moi cu mot vet loang, cach nhau deu trong khoang 0,25..0,80
    cx, cy = (nx0 + nx1) / 2, ny + 19
    for i in range(lan):
        t0 = 0.25 + i * (0.50 / max(1, lan))
        k = clamp((p - t0) / 0.16)
        if k <= 0:
            continue
        r = 14 + 46 * k
        lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        ImageDraw.Draw(lay).ellipse(
            [s(cx - r), s(cy - r), s(cx + r), s(cy + r)],
            outline=mau + (int(210 * (1 - k)),), width=s(3))
        base.alpha_composite(lay)
        if k < 0.55:                      # dau ngon tay, tat nhanh hon vet loang
            d.ellipse([s(cx - 13), s(cy - 13), s(cx + 13), s(cy + 13)],
                      fill=mau + (255,))

    if sp.get("nhan"):
        co = _co_vua(sp["nhan"], rong + 30, 19, 2.5)
        mono(base, sp["nhan"], (x, y + cao + 14), chu, clamp((p - 0.30) / 0.2),
             co, 2.5, 700)


# ----------------------------------------------------------------- ngay dem

def ngay_dem(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Dai chuyen tu dem sang sang. Cho "sang hom sau moi phat hien".

    Ve mat trang mo dan di va mat troi hien dan len tren cung mot cho, kem mot
    vach thoi gian chay ngang. Doi cho cho nhau chu khong dat canh nhau: hai
    thu canh nhau doc thanh "hai lua chon", con thay the nhau moi doc thanh
    "thoi gian troi qua".
    """
    rong, cao = 230, 92
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return
    d.rounded_rectangle([s(x), s(y), s(x + rong), s(y + cao)], radius=s(12),
                        fill=nen + (255,), outline=vien + (255,), width=s(2))

    # tien do chuyen dem -> sang
    gp = clamp((p - 0.28) / 0.44)
    cx, cy, r = x + 46, y + 42, 20

    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(lay)
    # mat trang: dia tron bi khuyet mot mieng ben phai
    a_dem = int(255 * (1 - gp))
    if a_dem > 4:
        ld.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)],
                   fill=(214, 218, 236, a_dem))
        ld.ellipse([s(cx - r + 9), s(cy - r - 3), s(cx + r + 9), s(cy + r - 3)],
                   fill=nen + (a_dem,))
    # mat troi: dia dac kem tia
    a_sang = int(255 * gp)
    if a_sang > 4:
        ld.ellipse([s(cx - r + 4), s(cy - r + 4), s(cx + r - 4), s(cy + r - 4)],
                   fill=mau + (a_sang,))
        import math
        for i in range(8):
            g = math.radians(i * 45 + 22)
            ld.line([s(cx + math.cos(g) * (r + 2)), s(cy + math.sin(g) * (r + 2)),
                     s(cx + math.cos(g) * (r + 11)), s(cy + math.sin(g) * (r + 11))],
                    fill=mau + (a_sang,), width=s(3))
    base.alpha_composite(lay)

    # vach thoi gian
    tx0, tx1 = x + 82, x + rong - 18
    d.line([s(tx0), s(cy + 22), s(tx1), s(cy + 22)], fill=vien + (255,),
           width=s(2))
    d.ellipse([s(tx0 + (tx1 - tx0) * gp - 5), s(cy + 17),
               s(tx0 + (tx1 - tx0) * gp + 5), s(cy + 27)], fill=mau + (255,))

    nhan = (sp.get("nhan_dem", "ĐÊM") if gp < 0.5
            else sp.get("nhan_sang", "SÁNG HÔM SAU"))
    co = _co_vua(nhan, tx1 - tx0)
    mono(base, nhan, (tx0, y + 16), chu if gp >= 0.5 else mo, q, co, 2.2, 700)


DAO_CU = {"dien_thoai": dien_thoai, "ngay_dem": ngay_dem}


def them(b, sp, khung, mau, nen, vien, chu, mo):
    """Gan dao cu vao mot canh. Goi tu `bench.build()` sau khi dung canh xong."""
    c = sp.get("prop")
    if not c:
        return
    loai = c.get("loai") if isinstance(c, dict) else str(c)
    ve = DAO_CU.get(loai)
    if ve is None:
        raise ValueError(f"khong co dao cu {loai!r}. Co: {', '.join(DAO_CU)}")
    cfg = c if isinstance(c, dict) else {}

    def fn(base, d, p):
        ve(base, p, cfg, khung, mau, nen, vien, chu, mo)
    b.add(fn, dur=max(2.0, b.dur * 0.82), wait=b.dur)
