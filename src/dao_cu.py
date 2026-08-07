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


# ------------------------------------------------------------ trinh duyet

def trinh_duyet(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Cua so trinh duyet: thanh tab, thanh dia chi, khung noi dung.

    Dao cu dung nhieu nhat theo bang dem tren 90 chu de - gan nhu ca mua 5.
    `dong` la cac dong chu gia trong khung noi dung; dong nao `bad` thi to mau
    nhan, dung de chi "cho nay hien sai".
    """
    rong, cao = 250, 180
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao + 30, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return
    d.rounded_rectangle([s(x), s(y), s(x + rong), s(y + cao)], radius=s(10),
                        fill=nen + (255,), outline=vien + (255,), width=s(2))
    # ba cham + thanh dia chi
    for i in range(3):
        cx, cy = x + 16 + i * 13, y + 15
        d.ellipse([s(cx - 4), s(cy - 4), s(cx + 4), s(cy + 4)],
                  fill=vien + (255,))
    d.rounded_rectangle([s(x + 62), s(y + 8), s(x + rong - 12), s(y + 24)],
                        radius=s(6), fill=(0, 0, 0, 255))
    if sp.get("url"):
        co = _co_vua(sp["url"], rong - 90, 13, 1.0, 9)
        mono(base, sp["url"], (x + 70, y + 12), mo, q, co, 1.0, 500)
    d.line([s(x), s(y + 32), s(x + rong), s(y + 32)], fill=vien + (255,),
           width=s(2))

    # dong noi dung, hien dan
    dong = sp.get("dong") or []
    for i, ln in enumerate(dong[:5]):
        k = clamp((p - 0.22 - i * 0.07) / 0.20)
        if k <= 0:
            continue
        txt = ln if isinstance(ln, str) else str(ln.get("text", ""))
        xau = isinstance(ln, dict) and ln.get("bad")
        yy = y + 46 + i * 26
        co = _co_vua(txt, rong - 32, 15, 1.0, 10)
        mono(base, txt, (x + 16, yy), mau if xau else chu, k, co, 1.0,
             700 if xau else 500)
    if sp.get("nhan"):
        co = _co_vua(sp["nhan"], rong, 19, 2.5)
        mono(base, sp["nhan"], (x, y + cao + 12), chu, clamp((p - 0.3) / 0.2),
             co, 2.5, 700)


# ------------------------------------------------------------------- khoa

def khoa(base, p, sp, khung, mau, nen, vien, chu, mo):
    """O khoa dong roi mo, hoac nguoc lai.

    `mo_luc` la moc p ma khoa bat ra. De 0 thi khoa mo san tu dau, de 1,1 thi
    no dong suot ca canh - dung cho "cho nay bi giu suot".
    """
    rong, cao = 120, 150
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao + 30, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return
    mo_luc = float(sp.get("mo_luc", 0.62))
    dang_mo = p >= mo_luc
    # Khoa DONG to mau nhan (day la cho dang bi giu), khoa MO thi chu thuong.
    col = chu if dang_mo else mau

    # quai khoa: dong thi thang, mo thi lech sang trai
    lech = 16 if dang_mo else 0
    bx, by = x + rong / 2 - lech, y + 18
    d.arc([s(bx - 26), s(by - 26), s(bx + 26), s(by + 26)], 180, 360,
          fill=col + (255,), width=s(7))
    d.line([s(bx - 26), s(by), s(bx - 26), s(by + 26)], fill=col + (255,),
           width=s(7))
    if not dang_mo:
        d.line([s(bx + 26), s(by), s(bx + 26), s(by + 26)], fill=col + (255,),
               width=s(7))

    # than khoa
    d.rounded_rectangle([s(x + 14), s(y + 44), s(x + rong - 14), s(y + cao - 8)],
                        radius=s(12), fill=col + (255,))
    d.ellipse([s(x + rong / 2 - 9), s(y + 78), s(x + rong / 2 + 9), s(y + 96)],
              fill=nen + (255,))
    nhan = sp.get("nhan_mo" if dang_mo else "nhan_dong")
    if nhan:
        co = _co_vua(nhan, rong + 60, 19, 2.5)
        mono(base, nhan, (x, y + cao + 10), chu, q, co, 2.5, 700)


# --------------------------------------------------------------- dong ho

def dong_ho(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Dong ho co kim quet mot vong. Cho TTL, timeout, cron.

    Khac `ngay_dem` o cho: `ngay_dem` ke MOT lan chuyen doi, con cai nay ke
    thoi gian TROI DEU. Vach do danh dau moc het han.
    """
    import math
    r = 46
    rong, cao = r * 2 + 20, r * 2 + 20
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao + 30, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return
    cx, cy = x + rong / 2, y + cao / 2
    d.ellipse([s(cx - r), s(cy - r), s(cx + r), s(cy + r)], fill=nen + (255,),
              outline=vien + (255,), width=s(3))
    for i in range(12):
        g = math.radians(i * 30 - 90)
        d.line([s(cx + math.cos(g) * (r - 9)), s(cy + math.sin(g) * (r - 9)),
                s(cx + math.cos(g) * (r - 4)), s(cy + math.sin(g) * (r - 4))],
               fill=vien + (255,), width=s(2))
    # vach het han
    hh = float(sp.get("het_han", 0.75))
    gh = math.radians(hh * 360 - 90)
    d.line([s(cx), s(cy), s(cx + math.cos(gh) * (r - 6)),
            s(cy + math.sin(gh) * (r - 6))], fill=mau + (110,), width=s(3))
    # kim
    gp = clamp((p - 0.20) / 0.62)
    g = math.radians(gp * 360 - 90)
    col = mau if gp >= hh else chu
    d.line([s(cx), s(cy), s(cx + math.cos(g) * (r - 12)),
            s(cy + math.sin(g) * (r - 12))], fill=col + (255,), width=s(5))
    d.ellipse([s(cx - 5), s(cy - 5), s(cx + 5), s(cy + 5)], fill=col + (255,))
    nhan = sp.get("nhan_het") if gp >= hh else sp.get("nhan")
    if nhan:
        co = _co_vua(nhan, rong + 70, 19, 2.5)
        mono(base, nhan, (x - 20, y + cao + 10), col, q, co, 2.5, 700)


# ----------------------------------------------------------- nhieu nguoi

def nhieu_nguoi(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Day bieu tuong nguoi hien dan. Cho "n nguoi cung luc".

    Ve toi da 24 hinh; nhieu hon thi ghi "+N nua" - y het cach `multiply` lam,
    va cung mot ly do: qua nhieu thi thanh mang mau, mat het y nghia dem.
    """
    tong = int(sp.get("so", 12))
    cot = int(sp.get("cot", 6))
    ve = min(tong, 24)
    rong = cot * 26 + 8
    hang = (ve + cot - 1) // cot
    cao = hang * 30 + 6
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao + 30, khung)
    d = ImageDraw.Draw(base)
    hien = int(clamp((p - 0.18) / 0.52) * ve)
    for i in range(hien):
        r_, c_ = divmod(i, cot)
        px, py = x + 6 + c_ * 26, y + 6 + r_ * 30
        col = mau if (i == 0 and sp.get("dau_khac")) else chu
        d.ellipse([s(px), s(py), s(px + 13), s(py + 13)], fill=col + (255,))
        d.rounded_rectangle([s(px - 3), s(py + 16), s(px + 16), s(py + 26)],
                            radius=s(5), fill=col + (255,))
    day = 0
    if tong > ve and hien >= ve:
        mono(base, f"+{tong - ve} nữa", (x + 6, y + cao + 2), mo, 1.0, 16,
             2.0, 700)
        day = 24          # nhan duoi phai lui xuong, khong thi hai dong chong
    if sp.get("nhan"):
        co = _co_vua(sp["nhan"], rong + 60, 19, 2.5)
        mono(base, sp["nhan"], (x, y + cao + 16 + day), chu,
             clamp((p - 0.3) / 0.2), co, 2.5, 700)


# ------------------------------------------------------------- thanh day

def thanh_day(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Thanh do day dan - bo nho, dia, dung luong bang.

    Khac canh `queue` o cho: `queue` ve DUONG CONG theo thoi gian va chiem ca
    san dien, con cai nay chi la mot vach day dan o goc, de canh khac van la
    canh chinh. Vach `nguong` la muc gioi han; vuot qua thi doi mau.
    """
    rong, cao = 190, 34
    x, y = _neo(sp.get("goc", "tren-phai"), rong, cao + 56, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return
    if sp.get("nhan"):
        co = _co_vua(sp["nhan"], rong, 18, 2.2)
        mono(base, sp["nhan"], (x, y), mo, q, co, 2.2, 700)
    yy = y + 26
    d.rounded_rectangle([s(x), s(yy), s(x + rong), s(yy + cao)], radius=s(7),
                        fill=nen + (255,), outline=vien + (255,), width=s(2))
    day = clamp(float(sp.get("day", 1.0))) * clamp((p - 0.20) / 0.58)
    ng = float(sp.get("nguong", 1.1))
    col = mau if day >= ng else chu
    if day > 0.01:
        d.rounded_rectangle([s(x + 3), s(yy + 3), s(x + 3 + (rong - 6) * day),
                             s(yy + cao - 3)], radius=s(5), fill=col + (255,))
    if ng <= 1.0:
        nx = x + 3 + (rong - 6) * ng
        d.line([s(nx), s(yy - 5), s(nx), s(yy + cao + 5)], fill=mau + (190,),
               width=s(3))
    so = sp.get("so")
    if so:
        co = _co_vua(str(so), rong, 22, 1.5)
        mono(base, str(so), (x, yy + cao + 12), col, q, co, 1.5, 700)


# --------------------------------------------------------------------- tep

def tep(base, p, sp, khung, mau, nen, vien, chu, mo):
    """Chong tep, moi tep mot dong ghi. Cho log, CRLF, BOM, ban ghi.

    `dong` la cac dong trong tep tren cung; dong nao `bad` thi to mau nhan.
    Chong phia sau chi de bao "con nhieu nua", khong mang thong tin.
    """
    rong, cao = 210, 150
    x, y = _neo(sp.get("goc", "tren-phai"), rong + 14, cao + 44, khung)
    d = ImageDraw.Draw(base)
    q = clamp(p / 0.18)
    if q <= 0:
        return
    # hai tep phia sau, lech ra de thanh chong
    for k in (2, 1):
        d.rounded_rectangle([s(x + k * 7), s(y + k * 7), s(x + rong + k * 7),
                             s(y + cao + k * 7)], radius=s(8),
                            fill=nen + (255,), outline=vien + (255,), width=s(2))
    d.rounded_rectangle([s(x), s(y), s(x + rong), s(y + cao)], radius=s(8),
                        fill=nen + (255,), outline=vien + (255,), width=s(2))
    # goc gap
    d.polygon([(s(x + rong - 26), s(y)), (s(x + rong), s(y + 26)),
               (s(x + rong - 26), s(y + 26))], fill=vien + (255,))
    if sp.get("ten"):
        co = _co_vua(sp["ten"], rong - 46, 15, 1.0, 10)
        mono(base, sp["ten"], (x + 12, y + 10), mo, q, co, 1.0, 700)
    d.line([s(x + 10), s(y + 32), s(x + rong - 10), s(y + 32)],
           fill=vien + (255,), width=s(2))
    for i, ln in enumerate((sp.get("dong") or [])[:4]):
        k = clamp((p - 0.24 - i * 0.08) / 0.20)
        if k <= 0:
            continue
        txt = ln if isinstance(ln, str) else str(ln.get("text", ""))
        xau = isinstance(ln, dict) and ln.get("bad")
        co = _co_vua(txt, rong - 24, 14, 0.8, 9)
        mono(base, txt, (x + 12, y + 44 + i * 24), mau if xau else chu, k, co,
             0.8, 700 if xau else 500)
    if sp.get("nhan"):
        co = _co_vua(sp["nhan"], rong + 40, 19, 2.5)
        mono(base, sp["nhan"], (x, y + cao + 26), chu, clamp((p - 0.3) / 0.2),
             co, 2.5, 700)


DAO_CU = {
    "dien_thoai": dien_thoai, "ngay_dem": ngay_dem,
    "trinh_duyet": trinh_duyet, "khoa": khoa,
    "dong_ho": dong_ho, "nhieu_nguoi": nhieu_nguoi,
    "thanh_day": thanh_day, "tep": tep,
}


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
