"""Theme NET VE - ke chuyen hai nhan vat bang nguoi que va bong bong thoai.

Vi sao them mot theme nua. Bon theme cu deu dung de GIAI THICH mot co che: co o
so chay, co thanh Gantt, co so do he thong. Video ke mot chuyen giua hai nguoi
thi khong can thu nao trong so do - no can loi thoai, va khoang lang giua hai
cau. Nhoi noi dung do vao `bench` thi ra mot ban bao cao ky thuat ve viec di an,
sai hoan toan giong.

Nen theme nay giu dung mot thu tu `sketch.py`: NET VE TAY. Nen giay kem, net
xieu xieu, chu viet tay hien dan tu trai sang phai nhu dang duoc viet ra. Khong
co bang mau accent, khong rail, khong chip chuong - nhung thu do lam khung hinh
trong nhu bang dieu khien, ma bang dieu khien thi khong ke chuyen duoc.

## Bo cuc: hai nguoi dung o duoi, bong bong o tren

Nguoi que dat o y 980 chu khong phai giua khung. Ly do: bong bong thoai phai nam
TREN dau nguoi noi thi moi doc duoc la ai dang noi, nen phai chua san hon 500px
phia tren. Dat nguoi vao giua khung thi bong bong tran len dai tieu de.

## Mot luat phai giu

Nguoi NGHE ve bang muc xam, nguoi NOI ve bang muc den. Thieu quy tac nay thi hai
hinh giong het nhau va nguoi xem phai doc chu moi biet ai dang noi - mat cham
hon tai, nen luc nhan ra thi loi thoai da troi qua mat roi.
"""
from PIL import Image, ImageDraw

import sketch as sk
from style import (AMBER, DOT, GREY, GREY_DARK, H, INK, PAPER, RED,
                   STICKY_YELLOW, W, clamp, color, font, s)
from timing import B

FADE = 0.34          # xoa bang bang cach mo dan ve nen giay

# --------------------------------------------------------------------- bo cuc
LE = 70
CX = W // 2
RONG = W - LE * 2

TIEU_DE_Y = 150                 # dai tieu de viet tay
SAN_Y0, SAN_Y1 = 430, 1300      # san dien
NGUOI_Y = 900                   # dinh dau nguoi que
NGUOI_CO = 2.1                  # ti le nguoi que
NGUOI_CAO = int(170 * NGUOI_CO)
EM_X, CHI_X = 300, 780
PHU_DE_Y = 1350

VAI = {"em": (EM_X, "EM"), "chi": (CHI_X, "CHỊ")}


# ------------------------------------------------------------------- nen giay
_bg = None


def background():
    """Nen giay kem + luoi cham + toi nhe 4 goc. Ve MOT lan roi cache."""
    global _bg
    if _bg is not None:
        return _bg
    img = Image.new("RGBA", (s(W), s(H)), PAPER + (255,))
    d = ImageDraw.Draw(img)
    r = max(1, s(1.6))
    for y in range(26, H, 26):
        for x in range(26, W, 26):
            d.ellipse([s(x) - r, s(y) - r, s(x) + r, s(y) + r],
                      fill=DOT + (255,))
    vig = Image.new("L", (s(W), s(H)), 0)
    vd = ImageDraw.Draw(vig)
    for i in range(26):
        vd.rectangle([i * s(7), i * s(7), s(W) - i * s(7), s(H) - i * s(7)],
                     outline=int(9 * (1 - i / 26)), width=s(8))
    img.alpha_composite(Image.merge("RGBA", (
        Image.new("L", vig.size, 120), Image.new("L", vig.size, 118),
        Image.new("L", vig.size, 108), vig)))
    _bg = img
    return img


# -------------------------------------------------------------- primitive chung
def _khoi_chu(txt, role, co, rong, max_dong=3):
    """Thu nho co chu cho toi khi ngat ra khong qua `max_dong`."""
    f = font(role, co)
    while co > 22:
        f = font(role, co)
        dong = sk.wrap_balanced(txt, f, rong)
        if len(dong) <= max_dong:
            return f, dong
        co -= 2
    return f, sk.wrap_balanced(txt, f, rong)[:max_dong]


def nguoi(d, base, x, ten, dang_noi, p=1.0, the="dung", mat=None, seed=7):
    """Nguoi que + ten duoi chan. Nguoi nghe ve muc xam - xem docstring dau file."""
    muc = INK if dang_noi else GREY
    # nguoi nghe mac dinh mat thuong, nguoi noi mat vui - khoi phai khai tay
    mat = mat or ("vui" if dang_noi else "nghi")
    if p >= 1.0:
        dan_nguoi(base, x, NGUOI_Y, muc, NGUOI_CO, seed, the, mat)
    else:
        _ve_nguoi_tho(d, x, NGUOI_Y, muc, NGUOI_CO, seed, p, the, mat)
    if p > 0.72:
        sk.draw_text(base, [ten], font("display", 34),
                     muc if dang_noi else GREY_DARK, cx=x,
                     y=NGUOI_Y + NGUOI_CAO + 18,
                     p=clamp((p - 0.72) / 0.28), reveal="fade")


def bong_bong(base, d, txt, ben, y0, p=1.0, muc=INK, co=50, duoi_x=None,
              rong=680, seed=11):
    """Bong bong thoai ve tay, co duoi chi ve phia nguoi noi.

    Thu tu hien: khung -> duoi -> chu. Chu hien SAU cung va hien dan tu trai
    sang phai, nen nguoi xem doc kip thay vi bi dap ca cau vao mat mot luc.
    """
    f, dong = _khoi_chu(txt, "body", co, rong - 64)
    lh = sk.line_height(f, 1.30)
    cao = lh * len(dong) + 62
    x0 = LE if ben == "trai" else W - LE - rong
    box = (x0, y0, x0 + rong, y0 + cao)

    sk.rect(d, box, muc, 3, 2.4, seed, clamp(p * 1.9))
    if p > 0.52:
        q = clamp((p - 0.52) / 0.18)
        dx = duoi_x if duoi_x is not None else (x0 + 90)
        dx = min(max(dx, box[0] + 60), box[2] - 60)
        sk.line(d, (dx - 26, box[3]), (dx + 4, box[3] + 42), muc, 3, 1.6,
                seed + 1, q)
        sk.line(d, (dx + 30, box[3]), (dx + 4, box[3] + 42), muc, 3, 1.6,
                seed + 2, q)
    if p > 0.6:
        sk.draw_text(base, dong, f, muc, cx=(box[0] + box[2]) / 2, y=y0 + 30,
                     p=clamp((p - 0.6) / 0.4), reveal="wipe")
    return cao


# ------------------------------------------------------- nguoi que ve san
# Kien truc chung cua tool: moi frame dung lai TU DAU. Dung cho hinh dang duoc
# ve dan, nhung khi hinh da ve xong thi moi frame lai ton cong rasterize lai y
# het. Canh co nguoi DI CHUYEN con nang hon: khong frame nao trung nen bo
# bo-frame-trung cua render.py khong an mieng nao.
#
# Nen: ve xong MOT lan ra mieng RGBA roi cache, cac frame sau chi dan vao. Doi
# lai la mat hieu ung "dang duoc ve" - nen chi dung sprite khi p >= 1, con luc
# he lo van ve dan nhu cu.
_SPRITE = {}

# he toa do trong sprite: goc (0,0) la dinh dau, nguoi nam giua chieu ngang
_BE = 62          # nua be rong sprite theo don vi `co`
_CAO = 182        # chieu cao sprite theo don vi `co`

# TU THE co ten. Moi the: toa do dau ban tay/ban chan theo don vi `co`, tinh tu
# vai va tu hong. Dat ten thay vi truyen so vi screenplay phai doc duoc:
# `the: vay` ro nghia hon `tay: 3, chan: 0`.
# `tay` = tay THANG (dx, dy tu vai). `gap` = tay GAP o khuyu, moi ben mot chuoi
# [(khuyu), (ban tay)]. Anh mau gan nhu khong co tay thang duoi nguoi - tay gap
# moi ra dang "dang lam gi do", nen cac the noi/nghi/vay deu dung `gap`.
THE = {
    "dung":    {"tay": (-40, 34, 40, 34),   "chan": (-34, 56, 34, 56)},
    "vay":     {"tay": (-38, 32, 0, 0),
                "gap": {"phai": [(30, 2), (44, -34)]},
                "chan": (-30, 56, 32, 56)},
    "noi":     {"gap": {"trai": [(-34, 20), (-44, -8)],
                        "phai": [(34, 20), (44, -8)]},
                "chan": (-32, 56, 34, 56)},
    "nghi":    {"tay": (-38, 34, 0, 0),
                "gap": {"phai": [(32, 18), (13, -19)]},
                "chan": (-30, 56, 32, 56)},
    "dua":     {"gap": {"trai": [(-26, 24), (-14, 4)],
                        "phai": [(30, 22), (52, 6)]},
                "chan": (-30, 56, 34, 56)},
    "gio_len": {"tay": (-44, -32, 44, -36), "chan": (-34, 56, 34, 56)},
    "chi":     {"tay": (-38, 34, 0, 0),
                "gap": {"phai": [(36, 6), (40, -44)]},
                "chan": (-32, 56, 34, 56)},
    "ngoi":    {"gap": {"trai": [(-34, 18), (-28, 38)],
                        "phai": [(34, 18), (28, 38)]},
                "chan": (0, 0, 0, 0), "ngoi": True},
    "di_a":    {"tay": (-40, 10, 34, 40),   "chan": (-46, 52, 52, 46)},
    "di_b":    {"tay": (-34, 40, 40, 10),   "chan": (-20, 58, 18, 58)},
}

# MAT: cai lam nguoi que co tinh. Dau tron rong thi hai hinh nao cung giong
# nhau; them hai con mat va mot net mieng la doc duoc ngay dang vui hay dang
# nghi. Ve BEN TRONG dau nen phai neo theo ban kinh dau, khong dung so tuyet doi.
MAT = ("vui", "nghi", "ngac", "buon", "kinh", "khong")


def _ve_mat(d, x, y, co, mau, kieu="vui", seed=1):
    """Hai con mat + net mieng, neo theo ban kinh dau (hr = 26*co)."""
    if kieu == "khong":
        return
    hr = 26 * co
    cy = y + hr                      # tam dau
    r_ = max(2.0, hr * 0.115)
    for sgn in (-1, 1):
        ex = x + sgn * hr * 0.36
        ey = cy - hr * 0.16
        if kieu == "kinh":
            continue                 # da ve kinh o tren, khong ve mat nua
        if kieu == "ngac":           # mat mo to
            sk.ellipse(d, (ex - r_ * 1.5, ey - r_ * 1.5, ex + r_ * 1.5,
                           ey + r_ * 1.5), mau, max(2, int(1.6 * co)), 0.8,
                       seed + sgn, 1.0)
        else:
            d.ellipse([s(ex - r_), s(ey - r_), s(ex + r_), s(ey + r_)],
                      fill=mau + (255,))
    if kieu == "kinh":
        # kinh ram: hai mat kinh + gong noi. Ve DE LEN mat da co nen phai goi
        # truoc khi ve mieng, va phai to hon mat that de doc duoc o co nho.
        rk = hr * 0.30
        for sgn in (-1, 1):
            kx = x + sgn * hr * 0.36
            d.ellipse([s(kx - rk), s(cy - hr * 0.16 - rk * 0.82),
                       s(kx + rk), s(cy - hr * 0.16 + rk * 0.82)],
                      fill=mau + (255,))
        sk.line(d, (x - hr * 0.10, cy - hr * 0.18), (x + hr * 0.10, cy - hr * 0.18),
                mau, max(2, int(1.8 * co)), 0.6, seed + 21, 1.0)
    my = cy + hr * 0.28
    w = hr * 0.42
    if kieu == "vui":                # cuoi: cung vong len
        _net(d, [(x - w, my - hr * 0.06), (x - w * 0.4, my + hr * 0.17),
                 (x + w * 0.4, my + hr * 0.17), (x + w, my - hr * 0.06)],
             mau, max(2, int(1.7 * co)))
    elif kieu == "buon":             # met: cung vong xuong
        _net(d, [(x - w, my + hr * 0.14), (x, my - hr * 0.08),
                 (x + w, my + hr * 0.14)], mau, max(2, int(1.7 * co)))
    elif kieu == "nghi":             # mieng mot net ngang lech
        sk.line(d, (x - w * 0.7, my + hr * 0.04), (x + w * 0.45, my),
                mau, max(2, int(1.7 * co)), 0.8, seed + 9, 1.0)
    elif kieu == "ngac":             # mieng tron
        rr = hr * 0.17
        sk.ellipse(d, (x - rr, my - rr * 0.7, x + rr, my + rr * 1.1), mau,
                   max(2, int(1.6 * co)), 0.8, seed + 11, 1.0)


def _ve_toc(d, x, y, co, mau, seed=1):
    """Mot cong toc nhu trong anh mau - lam dau bot tron trui."""
    hr = 26 * co
    _net(d, [(x - hr * 0.16, y + hr * 0.06), (x - hr * 0.02, y - hr * 0.34),
             (x + hr * 0.3, y - hr * 0.16), (x + hr * 0.12, y + hr * 0.02)],
         mau, max(2, int(1.7 * co)))


def _ve_nguoi_tho(d, x, y, mau, co, seed, p=1.0, the="dung", mat="vui",
                  toc=True):
    """Nguoi que co tu the va co MAT. Toa do LOGIC, `y` la dinh dau."""
    t = THE.get(the, THE["dung"])
    hr = 26 * co
    net = max(2, int(3 * co))
    # amp thap: anh mau la vong tron GON. Amp 1.6 o co lon lam vien dau xu
    # nhu long, nhin ra con gi khac chu khong ra cai dau.
    sk.ellipse(d, (x - hr, y, x + hr, y + hr * 2), mau, net, 0.8, seed,
               clamp(p * 3))
    if p > 0.28:
        q = clamp((p - 0.28) / 0.22)
        if toc:
            _ve_toc(d, x, y, co, mau, seed)
        if q > 0.5:
            _ve_mat(d, x, y, co, mau, mat, seed)
    if p <= 0.33:
        return
    p2 = clamp((p - 0.33) / 0.67)
    co_ = y + hr * 2
    hong = co_ + (54 if t.get("ngoi") else 62) * co
    sk.line(d, (x, co_), (x, hong), mau, net, 1.4, seed + 1, clamp(p2 * 2.4))
    if p2 <= 0.42:
        return
    p3 = clamp((p2 - 0.42) / 0.58)
    vai = co_ + 16 * co
    gap = t.get("gap", {})
    tay = t.get("tay")
    for k, (ben, si) in enumerate((("trai", 2), ("phai", 3))):
        if ben in gap:
            truoc = (x, vai)
            for j, (dx_, dy_) in enumerate(gap[ben]):
                sau = (x + dx_ * co, vai + dy_ * co)
                sk.line(d, truoc, sau, mau, net, 1.2, seed + si + j * 30, p3)
                truoc = sau
        elif tay:
            dx_, dy_ = tay[k * 2], tay[k * 2 + 1]
            if dx_ or dy_:
                sk.line(d, (x, vai), (x + dx_ * co, vai + dy_ * co), mau, net,
                        1.4, seed + si, p3)
    if t.get("ngoi"):
        # Ngoi tren ghe: dui gan NGANG ra truoc, dau goi gap, cang buong thang
        # xuong. Hai chan lech nhau 7co de khong trung thanh mot net duy nhat -
        # trung thi nhin ra mot cai que, khong ra nguoi ngoi.
        for xa, s2 in ((-27, seed + 4), (27, seed + 5)):
            goi = (x + xa * co, hong + 12 * co)
            sk.line(d, (x, hong), goi, mau, net, 1.2, s2, p3)
            sk.line(d, goi, (goi[0] + (4 if xa > 0 else -4) * co,
                             goi[1] + 46 * co), mau, net, 1.2, s2 + 40, p3)
        return
    lx0, ly0, lx1, ly1 = t["chan"]
    sk.line(d, (x, hong), (x + lx0 * co, hong + ly0 * co), mau, net, 1.4,
            seed + 4, p3)
    sk.line(d, (x, hong), (x + lx1 * co, hong + ly1 * co), mau, net, 1.4,
            seed + 5, p3)


def tay_phai_o(x, y, co, the="dung"):
    """Toa do ban tay PHAI cua mot tu the - de gan dao cu (to giay, dien thoai)."""
    t = THE.get(the, THE["dung"])
    vai = y + 26 * co * 2 + 16 * co
    return x + t["tay"][2] * co, vai + t["tay"][3] * co


def sprite_nguoi(mau, co, seed, the="dung", mat="vui", toc=True):
    """Nguoi que da ve xong, tra ve (anh RGBA, lech_x, lech_y). Cache theo tu the."""
    khoa = (mau, round(co, 3), seed, the, mat, toc)
    if khoa in _SPRITE:
        return _SPRITE[khoa]
    rong, cao = int(_BE * 2 * co) + 20, int(_CAO * co) + 20
    lop = Image.new("RGBA", (s(rong), s(cao)), (0, 0, 0, 0))
    _ve_nguoi_tho(ImageDraw.Draw(lop), rong / 2, 10, mau, co, seed, 1.0,
                  the, mat, toc)
    ra = (lop, rong / 2, 10)
    _SPRITE[khoa] = ra
    return ra


def dan_nguoi(base, x, y, mau, co, seed, the="dung", mat="vui", toc=True):
    """Dan nguoi que da ve san vao khung. Chi ton mot phep alpha_composite."""
    lop, lx, ly = sprite_nguoi(mau, co, seed, the, mat, toc)
    base.alpha_composite(lop, (int(s(x - lx)), int(s(y - ly))))


# --------------------------------------------------------------- toa nha
def toa_nha(d, base, x, y, rong, cao, ten, p=1.0, seed=61):
    """Toa nha ve net: than nha, day cua so, cua ra vao, bang hieu co ten."""
    box = (x, y, x + rong, y + cao)
    sk.rect(d, box, INK, 3, 2.2, seed, clamp(p * 2.2))
    if p <= 0.35:
        return
    q = clamp((p - 0.35) / 0.45)
    cw, ch = 46, 38
    cot, hang = 3, 4
    ox = x + (rong - (cot * cw + (cot - 1) * 22)) / 2
    for i in range(cot * hang):
        if q < (i + 1) / (cot * hang + 2):
            break
        r_, c_ = divmod(i, cot)
        bx = ox + c_ * (cw + 22)
        by = y + 96 + r_ * (ch + 22)
        sk.rect(d, (bx, by, bx + cw, by + ch), GREY_DARK, 2, 1.4, seed + i, 1.0)
    # cua ra vao
    dw = 70
    sk.rect(d, (x + rong / 2 - dw / 2, y + cao - 96, x + rong / 2 + dw / 2,
                y + cao), INK, 3, 1.6, seed + 40, clamp(q * 1.6))
    if p > 0.62:
        # bang hieu: chu ten cong ty nam TRONG khung, khong de troi tren noc
        f = font("display_bold", 40)
        w = sk.text_size(ten, f)[0]
        bx0 = x + rong / 2 - w / 2 - 22
        sk.rect(d, (bx0, y + 22, bx0 + w + 44, y + 78), INK, 3, 1.6, seed + 50,
                clamp((p - 0.62) / 0.16))
        sk.draw_text(base, [ten], f, INK, cx=x + rong / 2, y=y + 30,
                     p=clamp((p - 0.7) / 0.3), reveal="wipe")


def tieu_de(b, txt, at=0.0, mau=INK, khoanh=False):
    """Tieu de viet tay o dai tren. `khoanh` = vong khoanh do quanh chu."""
    if not txt:
        return
    f, dong = _khoi_chu(txt, "display", 76, RONG - 20, max_dong=2)
    lh = sk.line_height(f, 1.24)

    def fn(base, d, p):
        sk.draw_text(base, dong, f, mau, cx=CX, y=TIEU_DE_Y, p=p, reveal="wipe")
        if khoanh and p > 0.7:
            w = max(sk.text_size(l, f)[0] for l in dong)
            sk.ellipse(d, (CX - w / 2 - 46, TIEU_DE_Y - 26,
                           CX + w / 2 + 46, TIEU_DE_Y + lh * len(dong) + 18),
                       RED, 4, 3.0, 31, clamp((p - 0.7) / 0.3))
    b.add(fn, dur=0.7, wait=0.0, at=at)


def phu_de(b, txt, at=0.28):
    if not txt:
        return
    f = font("body", 36)
    dong = sk.wrap(txt, f, RONG - 40)[:3]

    def fn(base, d, p):
        sk.draw_text(base, dong, f, GREY_DARK, cx=CX, y=PHU_DE_Y, p=p,
                     reveal="fade")
    b.add(fn, dur=0.6, wait=0.0, at=at)


# ============================================================== CAC LOAI CANH
def sc_thoai(b, sp):
    """Hai nguoi, mot nguoi noi. Loai canh chinh cua theme nay."""
    ai = sp.get("ai", "em")
    if ai not in VAI:
        raise ValueError(f"`ai` phai la 'em' hoac 'chi', khong phai {ai!r}")
    x_noi, ten_noi = VAI[ai]
    kia = "chi" if ai == "em" else "em"
    x_nghe, ten_nghe = VAI[kia]
    ben = "trai" if ai == "em" else "phai"

    if sp.get("boi_canh") == "quan":
        def fn_nen(base, d, p):
            quan_ca_phe(d, base, p)
        b.add(fn_nen, dur=0.8, wait=0.34)   # them TRUOC nguoi -> nam duoi

    the_noi = sp.get("the") or ("gio_len" if sp.get("tay_len") else "noi")

    def fn_noi(base, d, p):
        nguoi(d, base, x_noi, ten_noi, True, p, the_noi, sp.get("mat"), 7)
    b.add(fn_noi, dur=0.85, wait=0.30)

    def fn_nghe(base, d, p):
        nguoi(d, base, x_nghe, ten_nghe, False, p, sp.get("the_nghe", "dung"),
              sp.get("mat_nghe"), 23)
    b.add(fn_nghe, dur=0.85, wait=0.45)

    def fn_bb(base, d, p):
        bong_bong(base, d, sp["noi"], ben, 450, p, INK, sp.get("co", 50),
                  duoi_x=x_noi, rong=sp.get("rong", 690))
    b.add(fn_bb, dur=1.0, wait=0.55)

    if sp.get("dap"):
        def fn_dap(base, d, p):
            bong_bong(base, d, sp["dap"], "phai" if ben == "trai" else "trai",
                      690, p, GREY_DARK, 42, duoi_x=x_nghe, rong=430, seed=41)
        b.add(fn_dap, dur=0.8, wait=0.4)


def sc_mot_nguoi(b, sp):
    """Mot nguoi, bong bong NGHI (duoi la ba vong tron nho dan)."""
    ai = sp.get("ai", "em")
    _, ten = VAI[ai]
    x_ = CX

    def fn_ng(base, d, p):
        the = sp.get("the") or ("gio_len" if sp.get("tay_len") else "nghi")
        mat = sp.get("mat", "nghi")
        if p >= 1.0:
            dan_nguoi(base, x_, NGUOI_Y, INK, NGUOI_CO, 7, the, mat)
        else:
            _ve_nguoi_tho(d, x_, NGUOI_Y, INK, NGUOI_CO, 7, p, the, mat)
        if p > 0.72:
            sk.draw_text(base, [ten], font("display", 34), INK, cx=x_,
                         y=NGUOI_Y + NGUOI_CAO + 18,
                         p=clamp((p - 0.72) / 0.28), reveal="fade")
    b.add(fn_ng, dur=0.9, wait=0.4)

    f, dong = _khoi_chu(sp["nghi"], "body", 52, 520, max_dong=2)
    lh = sk.line_height(f, 1.34)
    # hinh bau can chieu cao du: elip det qua thi chu cham vao net o hai dau
    cao = max(230, lh * len(dong) + 150)
    box = (CX - 350, 420, CX + 350, 420 + cao)

    def fn_bb(base, d, p):
        # bong bong NGHI ve bang hinh bau, khong phai chu nhat: khac hin voi
        # bong bong NOI nen khong can chu thich nguoi xem van hieu
        sk.ellipse(d, box, INK, 3, 3.0, 13, clamp(p * 1.7))
        if p > 0.5:
            q = clamp((p - 0.5) / 0.25)
            for i, (r_, dy) in enumerate(((16, 46), (11, 90), (7, 124))):
                if q > i * 0.3:
                    sk.ellipse(d, (x_ - r_, box[3] + dy - r_, x_ + r_,
                                   box[3] + dy + r_), INK, 3, 1.4, 60 + i,
                               clamp((q - i * 0.3) / 0.3))
        if p > 0.58:
            sk.draw_text(base, dong, f, INK, cx=CX,
                         y=box[1] + cao / 2 - lh * len(dong) / 2,
                         p=clamp((p - 0.58) / 0.42), reveal="wipe")
    b.add(fn_bb, dur=1.1, wait=0.5)


def sc_troiqua(b, sp):
    """Thoi gian troi qua: truc ngang co moc, kem mot con so lon.

    Day la nhip giua loi hua va luc thuc hien. Phai cho THAY no dai, chu khong
    phai noi "mot thoi gian sau" roi di tiep.
    """
    moc = sp.get("moc", [])
    y = 760
    x0, x1 = LE + 30, W - LE - 30

    if sp.get("dem"):
        f, dong = _khoi_chu(sp["dem"], "display_bold", 124, RONG - 40, 2)
        lh = sk.line_height(f, 1.2)

        def fn_dem(base, d, p):
            w = max(sk.text_size(l, f)[0] for l in dong)
            if p > 0.15:
                sk.highlight_behind(
                    base, (CX - w / 2 - 16, 452, CX + w / 2 + 16,
                           452 + lh * len(dong)), AMBER, 3,
                    clamp((p - 0.15) / 0.5))
            sk.draw_text(base, dong, f, INK, cx=CX, y=450, p=p, reveal="wipe")
        b.add(fn_dem, dur=0.85, wait=0.45)

    def fn_truc(base, d, p):
        sk.line(d, (x0, y), (x1, y), INK, 3, 2.0, 5, p)
    b.add(fn_truc, dur=0.7, wait=0.32)

    for i, m in enumerate(moc):
        mx = x0 + (x1 - x0) * (i / max(1, len(moc) - 1))
        cuoi = (i == len(moc) - 1)

        def fn_m(base, d, p, mx=mx, m=m, cuoi=cuoi):
            mau = RED if cuoi else GREY_DARK
            sk.line(d, (mx, y - 22), (mx, y + 22), mau, 3, 1.4,
                    70 + int(mx) % 97, p)
            if p > 0.4:
                sk.draw_text(base, [m], font("body", 34), mau,
                             cx=min(max(mx, LE + 40), W - LE - 40), y=y + 40,
                             p=clamp((p - 0.4) / 0.6), reveal="fade")
        b.add(fn_m, dur=0.4, wait=0.22)

    if sp.get("ghi"):
        f2 = font("body", 42)
        d2 = sk.wrap_balanced(sp["ghi"], f2, RONG - 60)[:2]

        def fn_ghi(base, d, p):
            sk.draw_text(base, d2, f2, GREY_DARK, cx=CX, y=y + 140, p=p,
                         reveal="fade")
        b.add(fn_ghi, dur=0.65, wait=0.32)


def sc_chu(b, sp):
    """Mot cau viet tay that lon. Dung cho cau chot va cau bat cuoi."""
    mau = color(sp.get("mau"), INK)
    f, dong = _khoi_chu(sp["chu"], "display_bold", sp.get("co", 112),
                        RONG - 30, 3)
    lh = sk.line_height(f, 1.22)
    tong = lh * len(dong)
    y0 = (SAN_Y0 + SAN_Y1) / 2 - tong / 2 - (60 if sp.get("sub") else 0)

    def fn(base, d, p):
        sk.draw_text(base, dong, f, mau, cx=CX, y=y0, p=p, reveal="wipe")
        if sp.get("gach") and p > 0.75:
            w = max(sk.text_size(l, f)[0] for l in dong)
            sk.line(d, (CX - w / 2, y0 + tong + 22),
                    (CX + w / 2, y0 + tong + 22), RED, 6, 2.4, 9,
                    clamp((p - 0.75) / 0.25))
    b.add(fn, dur=0.95, wait=0.5)

    if sp.get("khoanh"):
        def fn_kh(base, d, p):
            w = max(sk.text_size(l, f)[0] for l in dong)
            sk.ellipse(d, (CX - w / 2 - 54, y0 - 34, CX + w / 2 + 54,
                           y0 + tong + 24), RED, 5, 3.4, 31, p)
        b.add(fn_kh, dur=0.7, wait=0.35)

    if sp.get("sub"):
        fs = font("body", 44)
        ds = sk.wrap_balanced(sp["sub"], fs, RONG - 60)[:2]

        def fn_s(base, d, p):
            sk.draw_text(base, ds, fs, GREY_DARK, cx=CX, y=y0 + tong + 70,
                         p=p, reveal="fade")
        b.add(fn_s, dur=0.7, wait=0.35)


def sc_the_moi(b, sp):
    """The moi: to giay note vang hoi nghieng, tieu de + cac dong chi tiet.

    Doi lap CO Y voi hai chu "hom nao": o day moi thu deu cu the, va chinh cai
    the nhin thay duoc la bang chung cho viec do.
    """
    dong = sp.get("dong", [])
    f_h = font("display_bold", 58)
    f_d = font("body", 48)
    lh = sk.line_height(f_d, 1.46)
    cao = 158 + lh * len(dong) + (70 if sp.get("ghi") else 30)
    rong = RONG - 40
    x0 = CX - rong / 2
    y0 = (SAN_Y0 + SAN_Y1) / 2 - cao / 2
    box = (x0, y0, x0 + rong, y0 + cao)

    def fn_giay(base, d, p):
        if p <= 0.02:
            return
        # ve nguyen mieng giay roi moi hien chu -> giong dat to giay xuong ban
        sk.fill_rect(base, box, STICKY_YELLOW + (255,), radius=10,
                     rotate=-1.2, shadow=True)
    b.add(fn_giay, dur=0.5, wait=0.3)

    def fn_dau(base, d, p):
        sk.draw_text(base, [sp.get("tieu_de", "LỜI MỜI")], f_h, INK, cx=CX,
                     y=y0 + 44, p=p, reveal="wipe")
        if p > 0.7:
            sk.line(d, (x0 + 56, y0 + 132), (x0 + rong - 56, y0 + 132), INK,
                    3, 2.0, 17, clamp((p - 0.7) / 0.3))
    b.add(fn_dau, dur=0.7, wait=0.4)

    for i, dg in enumerate(dong):
        def fn_d(base, d, p, i=i, dg=dg):
            sk.draw_text(base, [dg], f_d, INK, x=x0 + 62, y=y0 + 164 + i * lh,
                         align="left", p=p, reveal="wipe")
        b.add(fn_d, dur=0.55, wait=0.32)

    if sp.get("ghi"):
        fg = font("body", 36)

        def fn_ghi(base, d, p):
            sk.draw_text(base, [sp["ghi"]], fg, GREY_DARK, cx=CX,
                         y=y0 + cao - 58, p=p, reveal="fade")
        b.add(fn_ghi, dur=0.6, wait=0.3)


def sc_di_den(b, sp):
    """Em di bo toi mot dia diem. Nguoi ve SAN, moi frame chi doi vi tri.

    Day la canh chung minh vi sao can tang sprite: 30 frame/giay, khong frame
    nao trung, neu con rasterize lai nguoi que moi frame thi rieng canh nay ton
    bang ca ba canh tinh cong lai.

    Chan doi tu the theo quang duong da di chu khong theo thoi gian - di cham
    thi buoc thua ra, nhin moi giong di that.
    """
    x0 = float(sp.get("tu_x", 150))
    x1 = float(sp.get("den_x", 560))
    so_buoc = int(sp.get("buoc", 8))
    nha_x, nha_rong = 672, 342
    nha_y = NGUOI_Y - 310
    nha_cao = NGUOI_CAO + 310
    ten = sp.get("noi_den", "CÔNG TY")

    def fn_nha(base, d, p):
        toa_nha(d, base, nha_x, nha_y, nha_rong, nha_cao, ten, p)
    b.add(fn_nha, dur=1.0, wait=0.55)

    def fn_dat(base, d, p):
        # vach dat de nguoi khong bi "lo lung" giua khung
        sk.line(d, (LE, NGUOI_Y + NGUOI_CAO + 6),
                (W - LE, NGUOI_Y + NGUOI_CAO + 6), GREY, 3, 1.8, 77, p)
    b.add(fn_dat, dur=0.6, wait=0.3)

    def fn_di(base, d, p):
        q = clamp(p)
        x = x0 + (x1 - x0) * q
        buoc = int(q * so_buoc)
        dang_di = q < 0.985
        if dang_di:
            the = "di_a" if buoc % 2 == 0 else "di_b"
            nhun = -3 if buoc % 2 == 0 else 0      # nhun nhe cho co nhip
        else:
            the, nhun = sp.get("the_toi", "dung"), 0
        dan_nguoi(base, x, NGUOI_Y + nhun, INK, NGUOI_CO, 7, the, "vui")
        if sp.get("cam_giay", True) and not dang_di:
            # to giay tren tay phai: neo theo dung diem cuoi canh tay tu the 0
            hx, hy = tay_phai_o(x, NGUOI_Y + nhun, NGUOI_CO,
                                sp.get("the_toi", "dung"))
            sk.fill_rect(base, (hx - 6, hy - 8, hx + 34, hy + 46),
                         STICKY_YELLOW + (255,), radius=4, shadow=False)
            sk.rect(d, (hx - 6, hy - 8, hx + 34, hy + 46), INK, 2, 1.2, 88, 1.0)
        sk.draw_text(base, ["EM"], font("display", 34), INK, cx=x,
                     y=NGUOI_Y + NGUOI_CAO + 18, p=1.0, reveal="fade")
    # di suot gan het canh: chuyen dong la noi dung chinh o day
    b.add(fn_di, dur=max(2.0, b.dur * 0.72), wait=b.dur)


def sc_mo_thu(b, sp):
    """To giay gap ba, mo dan ra, roi thong tin moi hien tung dong.

    Thu tu nay quan trong: giay phai mo XONG roi chu moi chay. Cho chu chay
    trong luc giay con dang mo thi mat khong biet nhin vao dau.
    """
    dong = sp.get("dong", [])
    f_h = font("display_bold", 56)
    f_d = font("body", 46)
    lh = sk.line_height(f_d, 1.44)
    cao = 150 + lh * len(dong) + (66 if sp.get("ghi") else 26)
    rong = RONG - 60
    x0 = CX - rong / 2
    y0 = (SAN_Y0 + SAN_Y1) / 2 - cao / 2

    def fn_mo(base, d, p):
        # 0 -> 0.62: be rong giay tang tu 1/3 len ca to (mo gap)
        k = 0.34 + 0.66 * clamp(p / 0.62)
        w = rong * k
        hop = (CX - w / 2, y0, CX + w / 2, y0 + cao)
        sk.fill_rect(base, hop, STICKY_YELLOW + (255,), radius=8, rotate=-1.0,
                     shadow=True)
        # net gap: hai duong doc mo dan, con thay duoc thi nguoi xem hieu la
        # to giay vua duoc mo ra chu khong phai mot cai the bay vao
        if p < 0.92:
            m = 1.0 - clamp((p - 0.5) / 0.42)
            for i in (1, 2):
                gx = hop[0] + w * i / 3
                sk.line(d, (gx, y0 + 8), (gx, y0 + cao - 8), GREY,
                        max(1, int(2 * m)), 1.0, 90 + i, m)
    b.add(fn_mo, dur=1.1, wait=0.72)

    def fn_dau(base, d, p):
        sk.draw_text(base, [sp.get("tieu_de", "LỜI MỜI")], f_h, INK, cx=CX,
                     y=y0 + 42, p=p, reveal="wipe")
        if p > 0.7:
            sk.line(d, (x0 + 52, y0 + 124), (x0 + rong - 52, y0 + 124), INK,
                    3, 2.0, 17, clamp((p - 0.7) / 0.3))
    b.add(fn_dau, dur=0.65, wait=0.4)

    for i, dg in enumerate(dong):
        def fn_d(base, d, p, i=i, dg=dg):
            sk.draw_text(base, [dg], f_d, INK, x=x0 + 58, y=y0 + 156 + i * lh,
                         align="left", p=p, reveal="wipe")
        b.add(fn_d, dur=0.5, wait=0.3)

    if sp.get("ghi"):
        fg = font("body", 34)

        def fn_ghi(base, d, p):
            sk.draw_text(base, [sp["ghi"]], fg, GREY_DARK, cx=CX,
                         y=y0 + cao - 54, p=p, reveal="fade")
        b.add(fn_ghi, dur=0.55, wait=0.3)


# --------------------------------------------------------------- mon an
def _net(d, pts, mau, w=3):
    """Noi mot chuoi diem bang net lien. Dung cho hinh cong tu ve tay."""
    if len(pts) < 2:
        return
    d.line([(s(x), s(y)) for x, y in pts], fill=mau + (255,), width=s(w),
           joint="curve")


def _ic_lau(d, cx, cy, r, mau, seed):
    """Noi lau: than noi hinh thang, hai quai, lua duoi, hoi bay len."""
    w, h = r * 1.15, r * 0.72
    sk.line(d, (cx - w, cy - h * 0.3), (cx - w * 0.78, cy + h), mau, 3, 1.4, seed)
    sk.line(d, (cx + w, cy - h * 0.3), (cx + w * 0.78, cy + h), mau, 3, 1.4, seed + 1)
    sk.line(d, (cx - w * 0.78, cy + h), (cx + w * 0.78, cy + h), mau, 3, 1.4, seed + 2)
    sk.line(d, (cx - w * 1.12, cy - h * 0.3), (cx + w * 1.12, cy - h * 0.3),
            mau, 3, 1.4, seed + 3)
    for sgn in (-1, 1):                      # quai noi
        sk.ellipse(d, (cx + sgn * w * 1.06 - 13, cy - h * 0.3 - 11,
                       cx + sgn * w * 1.06 + 13, cy - h * 0.3 + 15),
                   mau, 3, 1.2, seed + 4 + sgn)
    for i, dx in enumerate((-0.45, 0.0, 0.45)):   # hoi bay
        bx = cx + w * dx
        _net(d, [(bx, cy - h * 0.55 - i % 2 * 4),
                 (bx - 11, cy - h * 0.95), (bx + 11, cy - h * 1.35),
                 (bx - 6, cy - h * 1.72)], GREY, 2)
    zig = []                                  # ngon lua
    for i in range(9):
        zig.append((cx - w * 0.7 + i * (w * 1.4 / 8),
                    cy + h + 12 + (14 if i % 2 else 0)))
    _net(d, zig, mau, 3)


def _ic_oc(d, cx, cy, r, mau, seed):
    """Con oc: xoan oc + hai cai rau."""
    import math
    pts = []
    for i in range(64):
        t = i / 63 * 3.5 * math.pi
        rr = r * 0.12 + r * 0.115 * t
        pts.append((cx + rr * math.cos(t) * 0.92, cy + rr * math.sin(t) * 0.86))
    _net(d, pts, mau, 3)
    dx, dy = pts[-1]
    sk.line(d, (dx, dy), (dx + r * 0.5, dy + r * 0.34), mau, 3, 1.2, seed)
    for sgn in (0, 1):                        # rau
        sk.line(d, (dx + r * 0.5, dy + r * 0.34),
                (dx + r * 0.78, dy + r * (0.02 + sgn * 0.3)), mau, 2, 1.0,
                seed + 5 + sgn)


def _ic_long(d, cx, cy, r, mau, seed):
    """Dia long: dia bau duc + may khoanh ben tren + doi dua."""
    sk.ellipse(d, (cx - r * 1.15, cy - r * 0.34, cx + r * 1.15, cy + r * 0.5),
               mau, 3, 1.6, seed)
    sk.ellipse(d, (cx - r * 0.86, cy - r * 0.24, cx + r * 0.86, cy + r * 0.3),
               GREY, 2, 1.2, seed + 1)
    for i, (ox, oy, rr) in enumerate(((-0.44, -0.16, 0.2), (0.02, -0.3, 0.24),
                                      (0.46, -0.12, 0.19), (-0.1, 0.02, 0.17))):
        sk.ellipse(d, (cx + r * ox - r * rr, cy + r * oy - r * rr * 0.72,
                       cx + r * ox + r * rr, cy + r * oy + r * rr * 0.72),
                   mau, 2, 1.2, seed + 10 + i)
    for i in (0, 1):                          # doi dua gac cheo
        sk.line(d, (cx + r * 0.55 + i * 15, cy - r * 1.25),
                (cx + r * 1.02 + i * 15, cy - r * 0.22), mau, 3, 1.0,
                seed + 20 + i)


def _ic_vit(d, cx, cy, r, mau, seed):
    """Con vit: than bau, co cong, dau, mo, duoi."""
    sk.ellipse(d, (cx - r * 0.92, cy - r * 0.18, cx + r * 0.72, cy + r * 0.78),
               mau, 3, 1.5, seed)
    _net(d, [(cx + r * 0.36, cy - r * 0.05), (cx + r * 0.6, cy - r * 0.62),
             (cx + r * 0.5, cy - r * 1.02)], mau, 3)
    hr = r * 0.3
    sk.ellipse(d, (cx + r * 0.24, cy - r * 1.42, cx + r * 0.24 + hr * 2,
                   cy - r * 1.42 + hr * 2), mau, 3, 1.2, seed + 1)
    _net(d, [(cx + r * 0.24 + hr * 2, cy - r * 1.16),
             (cx + r * 1.08, cy - r * 1.05),
             (cx + r * 0.24 + hr * 2, cy - r * 0.94)], mau, 3)
    _net(d, [(cx - r * 0.86, cy + r * 0.14), (cx - r * 1.24, cy - r * 0.16),
             (cx - r * 0.82, cy - r * 0.06)], mau, 3)


def _ic_suon(d, cx, cy, r, mau, seed):
    """Lau suon bo: noi + mot khuc suon nho len khoi noi + hoi.

    Phai co KHUC SUON nho han han ra ngoai noi, khong thi nhin y het `_ic_lau`
    va bang chon co hai o giong nhau - mat luon y nghia cua viec liet ke.
    """
    w, h = r * 1.05, r * 0.62
    sk.line(d, (cx - w, cy - h * 0.2), (cx - w * 0.8, cy + h), mau, 3, 1.4, seed)
    sk.line(d, (cx + w, cy - h * 0.2), (cx + w * 0.8, cy + h), mau, 3, 1.4,
            seed + 1)
    sk.line(d, (cx - w * 0.8, cy + h), (cx + w * 0.8, cy + h), mau, 3, 1.4,
            seed + 2)
    sk.line(d, (cx - w * 1.1, cy - h * 0.2), (cx + w * 1.1, cy - h * 0.2), mau,
            3, 1.4, seed + 3)
    # khuc suon: hai dau xuong + than xuong, dat cheo nho ra khoi noi
    ax, ay = cx - r * 0.34, cy - h * 0.62
    bx, by = cx + r * 0.42, cy - h * 1.34
    sk.line(d, (ax, ay), (bx, by), mau, 4, 1.0, seed + 4)
    for px, py in ((ax, ay), (bx, by)):
        for sgn in (-1, 1):
            sk.ellipse(d, (px - 9 + sgn * 5, py - 9 - sgn * 5,
                           px + 9 + sgn * 5, py + 9 - sgn * 5), mau, 3, 0.8,
                       seed + 5 + sgn, 1.0)
    for i, dx in enumerate((-0.4, 0.35)):
        bx2 = cx + w * dx
        _net(d, [(bx2, cy - h * 0.42), (bx2 - 10, cy - h * 0.82),
                 (bx2 + 10, cy - h * 1.2)], GREY, 2)


MON = {"lau": _ic_lau, "oc": _ic_oc, "long": _ic_long, "vit": _ic_vit,
       "suon": _ic_suon}


def sc_chon_quan(b, sp):
    """Bang chon quan: 2x2 o, moi o mot mon ve net + ten + mot cau chao hang.

    Danh so tung o de nguoi xem tra loi duoc bang MOT con so. Do la ca ly do
    canh nay ton tai: "chi chon" thi chi phai nghi, con bon o co so thi chi chi
    can bam mot phim.
    """
    quan = sp.get("quan", [])[:6]
    n = len(quan)
    cot = 2
    hang = -(-n // cot)
    y_dau = 452
    o_w = (RONG - 40) / cot
    # Cao mot o co lai khi co nhieu hang. Icon va chu cung nho theo, khong thi
    # ba hang tran xuong qua dai phu de.
    o_h = min(392, (SAN_Y1 - y_dau) / hang)
    gon = o_h < 330
    r_ic = 50 if gon else 66
    co_ten = 38 if gon else 46
    dy_ten = 150 if gon else 208
    dy_loi = 208 if gon else 268

    for i, q in enumerate(quan):
        r_, c_ = divmod(i, cot)
        # hang cuoi thieu o thi can giua cho khoi lech han sang trai
        trong_hang = min(cot, n - r_ * cot)
        lech = (cot - trong_hang) * (o_w + 40) / 2
        ox = LE + lech + c_ * (o_w + 40)
        oy = y_dau + r_ * o_h
        icx, icy = ox + o_w / 2, oy + (86 if gon else 118)

        def fn(base, d, p, q=q, i=i, ox=ox, oy=oy, icx=icx, icy=icy):
            mau = RED if q.get("nhan") else INK
            # so thu tu trong vong tron - de chi tra loi bang mot con so
            nb = ((ox + 2, oy - 12, ox + 46, oy + 32) if gon
                  else (ox + 2, oy - 16, ox + 54, oy + 36))
            sk.ellipse(d, nb, mau, 3, 1.6, 40 + i, clamp(p * 2.4))
            sk.draw_text(base, [str(i + 1)],
                         font("display_bold", 28 if gon else 34), mau,
                         cx=(nb[0] + nb[2]) / 2, y=nb[1] + 8,
                         p=clamp(p * 2.2), reveal="fade")
            if p > 0.22:
                MON.get(q.get("ve", "lau"), _ic_lau)(
                    d, icx, icy, r_ic, mau, 200 + i * 7)
            if p > 0.5:
                sk.draw_text(base, [q["ten"]], font("display_bold", co_ten),
                             mau, cx=icx, y=oy + dy_ten,
                             p=clamp((p - 0.5) / 0.3), reveal="wipe")
            if p > 0.66 and q.get("loi"):
                f = font("body", 26 if gon else 30)
                dg = sk.wrap_balanced(q["loi"], f, o_w - 24)[:2]
                sk.draw_text(base, dg, f, GREY_DARK, cx=icx, y=oy + dy_loi,
                             p=clamp((p - 0.66) / 0.34), reveal="fade")
        b.add(fn, dur=0.7, wait=0.42)


# ============================================================ BOI CANH / NEN
# Nen ve bang muc XAM, khong bao gio dung INK. Ly do giong luat nguoi noi/nguoi
# nghe: neu ban ghe va cua so cung do dam nhu nguoi thi mat khong biet nhin dau.
# Nen la thu de NHAN RA "dang o quan ca phe", khong phai thu de doc.
def quan_ca_phe(d, base, p=1.0):
    """Cua so ben trai + ban giua hai nguoi + hai ly. Ve PHIA SAU nguoi."""
    e = clamp(p * 1.5)
    cs = (96, 604, 292, 872)
    sk.rect(d, cs, GREY, 3, 1.6, 301, e)
    if p > 0.3:
        q = clamp((p - 0.3) / 0.4)
        mx, my = (cs[0] + cs[2]) / 2, (cs[1] + cs[3]) / 2
        sk.line(d, (mx, cs[1]), (mx, cs[3]), GREY, 2, 1.2, 302, q)
        sk.line(d, (cs[0], my), (cs[2], my), GREY, 2, 1.2, 303, q)
    # Ban dat TRUOC chan nguoi nen che luon phan chan - tien the giai quyet cai
    # kho cua tu the ngoi nhin thang.
    if p > 0.34:
        q = clamp((p - 0.34) / 0.5)
        bx0, bx1, by = 392, 700, 1136
        sk.line(d, (bx0, by), (bx1, by), GREY_DARK, 4, 1.6, 310, q)
        for x_ in (bx0 + 34, bx1 - 34):
            sk.line(d, (x_, by), (x_ - 6, by + 118), GREY_DARK, 3, 1.2,
                    311 + int(x_), q)
    if p > 0.6:
        q = clamp((p - 0.6) / 0.4)
        for i, lx in enumerate((452, 604)):
            sk.rect(d, (lx, 1074, lx + 46, 1132), GREY_DARK, 3, 1.2, 320 + i, q)
            sk.line(d, (lx + 5, 1092), (lx + 41, 1092), GREY, 2, 1.0, 330 + i, q)
            sk.ellipse(d, (lx + 44, 1086, lx + 66, 1112), GREY_DARK, 2, 1.0,
                       340 + i, q)


def sc_to_lich(b, sp):
    """To lich khong khop: moi ngay deu co, rieng "HOM NAO" khong biet ghi vao dau.

    Cai joke nam o cho: luoi ngay thang ve day du va rat ngay ngan, roi vong
    khoanh do lai nam NGOAI luoi - khong co o nao de khoanh ca. Ve vong khoanh
    vao trong mot o la mat sach y nghia.
    """
    x0, x1 = LE + 40, W - LE - 40
    y0, dau_h = 452, 84
    cot, ch = 7, 62
    cw = (x1 - x0) / cot

    # Neu screenplay khai `nam` + `thang_so` thi lich tu tinh dung thu cua tung
    # ngay. Bat buoc phai co: ban dau chi do 1..31 tuan tu tu o dau tien, nen
    # ngay 21 thang 8 nam 2026 roi vao cot cuoi trong khi that ra no la thu Sau.
    # Loi doc thi noi "thu Sau" ma hinh chi vao mot cot khac - dung loai sai ma
    # CONG-THUC.md xep vao muc nang nhat.
    nam, thang_so = sp.get("nam"), sp.get("thang_so")
    if nam and thang_so:
        import calendar
        lech, so_ngay = calendar.monthrange(int(nam), int(thang_so))
        co_thu = True
    else:
        lech, so_ngay, co_thu = 0, 31, False
    thu_h = 46 if co_thu else 0
    hang = -(-(lech + so_ngay) // cot)          # lam tron len
    luoi_h = thu_h + hang * ch

    def fn_khung(base, d, p):
        sk.rect(d, (x0, y0, x1, y0 + dau_h + luoi_h), INK, 3, 2.0, 401,
                clamp(p * 1.6))
        if p > 0.5:
            q = clamp((p - 0.5) / 0.5)
            sk.line(d, (x0, y0 + dau_h), (x1, y0 + dau_h), INK, 3, 1.6, 402, q)
            if co_thu:
                sk.line(d, (x0, y0 + dau_h + thu_h), (x1, y0 + dau_h + thu_h),
                        GREY_DARK, 2, 1.2, 403, q)
    b.add(fn_khung, dur=0.7, wait=0.4)

    if co_thu:
        TEN_THU = ("T2", "T3", "T4", "T5", "T6", "T7", "CN")

        def fn_thu(base, d, p):
            f = font("body", 28)
            for i, tt in enumerate(TEN_THU):
                if p < (i + 1) / 9:
                    break
                sk.draw_text(base, [tt], f, GREY_DARK,
                             cx=x0 + i * cw + cw / 2, y=y0 + dau_h + 8, p=1.0,
                             reveal="fade")
        b.add(fn_thu, dur=0.5, wait=0.28)

    def fn_dau(base, d, p):
        sk.draw_text(base, [sp.get("thang", "THÁNG NÀY")],
                     font("display_bold", 46), INK, cx=(x0 + x1) / 2,
                     y=y0 + 18, p=p, reveal="wipe")
    b.add(fn_dau, dur=0.5, wait=0.3)

    dd_ = sp.get("danh_dau")          # so ngay can khoanh, vd 21

    def fn_so(base, d, p):
        f = font("body", 30)
        for i in range(so_ngay):
            if p < (i + 1) / (so_ngay + 3):
                break
            r_, c_ = divmod(lech + i, cot)
            la_dd = dd_ and (i + 1) == int(dd_)
            sk.draw_text(base, [str(i + 1)], f, RED if la_dd else GREY_DARK,
                         cx=x0 + c_ * cw + cw / 2,
                         y=y0 + dau_h + thu_h + r_ * ch + 16, p=1.0,
                         reveal="fade")
    b.add(fn_so, dur=0.9, wait=0.55)

    if dd_:
        r_, c_ = divmod(lech + int(dd_) - 1, cot)
        ox = x0 + c_ * cw + cw / 2
        oy = y0 + dau_h + thu_h + r_ * ch + 26

        def fn_dd(base, d, p):
            # khoanh dung o ngay do, roi ba tia lap lanh quanh no
            sk.ellipse(d, (ox - cw * 0.46, oy - 30, ox + cw * 0.46, oy + 30),
                       RED, 4, 2.6, 420, clamp(p * 1.7))
            if p > 0.5:
                q = clamp((p - 0.5) / 0.5)
                for i, (dx_, dy_) in enumerate(((-1, -1), (1, -1), (1, 1))):
                    bx = ox + dx_ * cw * 0.62
                    by = oy + dy_ * 40
                    sk.line(d, (bx - 9 * dx_, by - 9 * dy_), (bx, by), RED, 3,
                            0.8, 430 + i, q)
        b.add(fn_dd, dur=0.75, wait=0.42)

    ncy = y0 + dau_h + luoi_h + 96

    # Vong khoanh NGOAI luoi la tuy chon. Ban dau viet cung chu "HÔM NÀO" vao
    # day vi luc do chi co mot screenplay dung to lich; den video thu hai thi no
    # lac vao mot canh khong lien quan gi. Bat ky chu cu the nao cua mot
    # screenplay deu phai di ra YAML, khong duoc nam trong code ve.
    ngoai = sp.get("khoanh_ngoai")
    if ngoai:
        f_n = font("display_bold", 62)

        def fn_khoanh(base, d, p):
            w = sk.text_size(ngoai, f_n)[0]
            cx = (x0 + x1) / 2
            sk.draw_text(base, [ngoai], f_n, RED, cx=cx, y=ncy,
                         p=clamp(p * 1.5), reveal="wipe")
            if p > 0.45:
                sk.ellipse(d, (cx - w / 2 - 46, ncy - 26, cx + w / 2 + 46,
                               ncy + 76), RED, 5, 3.2, 410,
                           clamp((p - 0.45) / 0.55))
            if p > 0.72:
                sk.arrow(d, (cx + w / 2 + 70, ncy + 24),
                         (x1 - cw * 0.6, y0 + dau_h + luoi_h - ch * 0.5), RED,
                         3, 2.0, 411, clamp((p - 0.72) / 0.28), head=20,
                         curve=40)
        b.add(fn_khoanh, dur=0.9, wait=0.5)

    if sp.get("ghi"):
        f2 = font("body", 38)
        dg = sk.wrap_balanced(sp["ghi"], f2, RONG - 80)[:2]

        gy = ncy + (112 if ngoai else 4)

        def fn_ghi(base, d, p):
            sk.draw_text(base, dg, f2, GREY_DARK, cx=CX, y=gy, p=p,
                         reveal="fade")
        b.add(fn_ghi, dur=0.6, wait=0.3)


def sc_ban_dem(b, sp):
    """Ban lam viec khuya: den ban, dong ho chi gio, do tren ban, nguoi ngoi.

    Gio hien thanh CHU chu khong ve kim: "11:47" doc duoc ngay, con hai cai kim
    o co nay thi phai nhin ky moi biet may gio - ma khong ai nhin ky mot canh
    dai bay giay.
    """
    mat_ban = 1150
    x0, x1 = LE, W - LE

    def fn_ban(base, d, p):
        e = clamp(p * 1.6)
        sk.line(d, (x0, mat_ban), (x1, mat_ban), GREY_DARK, 4, 1.8, 501, e)
        if p > 0.3:
            q = clamp((p - 0.3) / 0.5)
            for x_ in (x0 + 60, x1 - 60):
                sk.line(d, (x_, mat_ban), (x_, mat_ban + 120), GREY_DARK, 3,
                        1.2, 502 + int(x_), q)
    b.add(fn_ban, dur=0.6, wait=0.34)

    def fn_den(base, d, p):
        e = clamp(p * 1.5)
        dx = x0 + 116
        sk.line(d, (dx, mat_ban), (dx, mat_ban - 196), GREY_DARK, 3, 1.4, 510, e)
        if p > 0.3:
            _net(d, [(dx - 54, mat_ban - 196), (dx + 54, mat_ban - 196),
                     (dx + 30, mat_ban - 254), (dx - 30, mat_ban - 254),
                     (dx - 54, mat_ban - 196)], GREY_DARK, 3)
        if p > 0.6:
            q = clamp((p - 0.6) / 0.4)
            for i, ddx in enumerate((-44, 0, 44)):
                sk.line(d, (dx + ddx * 0.6, mat_ban - 186),
                        (dx + ddx, mat_ban - 132), AMBER, 3, 1.0, 520 + i, q)
    b.add(fn_den, dur=0.7, wait=0.36)

    if sp.get("gio"):
        def fn_gio(base, d, p):
            f = font("display_bold", 52)
            gx = x1 - 190
            sk.rect(d, (gx - 16, mat_ban - 262, gx + 176, mat_ban - 186),
                    GREY_DARK, 3, 1.4, 530, clamp(p * 1.8))
            sk.draw_text(base, [sp["gio"]], f, GREY_DARK, cx=gx + 80,
                         y=mat_ban - 250, p=clamp((p - 0.4) / 0.6),
                         reveal="wipe")
        b.add(fn_gio, dur=0.6, wait=0.32)

    def fn_do(base, d, p):
        e = clamp(p * 1.6)
        cx_ = CX + 40
        if sp.get("do") == "laptop":
            sk.rect(d, (cx_ - 130, mat_ban - 150, cx_ + 130, mat_ban - 16),
                    INK, 3, 1.6, 540, e)
            if p > 0.5:
                q = clamp((p - 0.5) / 0.5)
                for i in range(3):
                    yy = mat_ban - 124 + i * 30
                    sk.line(d, (cx_ - 106, yy), (cx_ + 40 + i * 24, yy), GREY,
                            3, 1.0, 541 + i, q)
                sk.line(d, (cx_ - 150, mat_ban - 10), (cx_ + 150, mat_ban - 10),
                        INK, 4, 1.2, 545, q)
        elif sp.get("do") == "ho_so":
            # tap ho so + kinh ram + tai nghe nam tren ban
            sk.fill_rect(base, (cx_ - 150, mat_ban - 116, cx_ + 110,
                               mat_ban - 6), STICKY_YELLOW + (255,), radius=6,
                         rotate=-2.0, shadow=True)
            sk.rect(d, (cx_ - 150, mat_ban - 116, cx_ + 110, mat_ban - 6), INK,
                    3, 1.4, 580, e)
            if p > 0.45:
                q = clamp((p - 0.45) / 0.55)
                for i in range(3):
                    yy = mat_ban - 92 + i * 26
                    sk.line(d, (cx_ - 126, yy), (cx_ + 30 - i * 22, yy), GREY_DARK,
                            2, 1.0, 581 + i, q)
                # kinh ram dat canh tap ho so
                for sgn in (-1, 1):
                    sk.ellipse(d, (cx_ + 150 + sgn * 26 - 20, mat_ban - 60,
                                   cx_ + 150 + sgn * 26 + 20, mat_ban - 26),
                               INK, 3, 1.0, 590 + sgn, q)
        else:
            sk.rect(d, (cx_ - 44, mat_ban - 128, cx_ + 44, mat_ban - 8), INK,
                    3, 1.4, 550, e)
            if p > 0.5:
                q = clamp((p - 0.5) / 0.5)
                for i in range(3):
                    yy = mat_ban - 104 + i * 26
                    sk.line(d, (cx_ - 28, yy), (cx_ + 20 - i * 8, yy), GREY, 3,
                            1.0, 551 + i, q)
    b.add(fn_do, dur=0.6, wait=0.34)

    if sp.get("nghi"):
        f, dong = _khoi_chu(sp["nghi"], "body", 46, 480, max_dong=2)
        lh = sk.line_height(f, 1.34)
        cao = max(210, lh * len(dong) + 140)
        box = (CX - 300, 430, CX + 300, 430 + cao)

        def fn_bb(base, d, p):
            sk.ellipse(d, box, INK, 3, 3.0, 560, clamp(p * 1.7))
            if p > 0.5:
                q = clamp((p - 0.5) / 0.25)
                for i, (r_, dy) in enumerate(((15, 40), (10, 78), (6, 108))):
                    if q > i * 0.3:
                        sk.ellipse(d, (CX - 130 - r_, box[3] + dy - r_,
                                       CX - 130 + r_, box[3] + dy + r_), INK,
                                   3, 1.4, 570 + i, clamp((q - i * 0.3) / 0.3))
            if p > 0.58:
                sk.draw_text(base, dong, f, INK, cx=CX,
                             y=box[1] + cao / 2 - lh * len(dong) / 2,
                             p=clamp((p - 0.58) / 0.42), reveal="wipe")
        b.add(fn_bb, dur=1.0, wait=0.5)

    def fn_nguoi(base, d, p):
        x_ = CX - 250
        the = sp.get("the", "nghi")
        mat = sp.get("mat", "nghi")
        if p >= 1.0:
            dan_nguoi(base, x_, 856, INK, NGUOI_CO, 7, the, mat)
        else:
            _ve_nguoi_tho(d, x_, 856, INK, NGUOI_CO, 7, p, the, mat)
        if p > 0.72:
            sk.draw_text(base, ["EM"], font("display", 34), INK, cx=x_,
                         y=mat_ban + 26, p=clamp((p - 0.72) / 0.28),
                         reveal="fade")
    b.add(fn_nguoi, dur=0.85, wait=0.4)


# ======================================================= CONCEPT "HO SO MAT"
def _dau_mat(d, base, cx, cy, chu="MẬT", p=1.0, goc=-14):
    """Con dau do xoay cheo. Dung de danh dau tai lieu."""
    f = font("display_bold", 46)
    w = sk.text_size(chu, f)[0]
    box = (cx - w / 2 - 26, cy - 12, cx + w / 2 + 26, cy + 58)
    sk.rect(d, box, RED, 4, 2.6, 601, clamp(p * 1.6))
    sk.rect(d, (box[0] + 8, box[1] + 8, box[2] - 8, box[3] - 8), RED, 2, 2.0,
            602, clamp(p * 1.4))
    sk.draw_text(base, [chu], f, RED, cx=cx, y=cy + 4, p=clamp(p * 1.3),
                 reveal="fade")


def sc_ho_so_bia(b, sp):
    """Bia ho so: cap tai lieu co tai, khung ke, con dau MAT xoay cheo.

    Kich ban goc ghi "man hinh den". Theme nay la giay kem nen den se pha vo
    toan bo mach hinh; thay bang BIA HO SO thi vua giu duoc chat "tai lieu mat"
    vua khong doi chat lieu.
    """
    x0, x1 = LE + 30, W - LE - 30
    y0, y1 = 500, 1120

    def fn_cap(base, d, p):
        # tai cap nho o goc tren trai -> doc ra ngay la tap tai lieu
        e = clamp(p * 1.6)
        sk.line(d, (x0 + 40, y0), (x0 + 190, y0), INK, 3, 1.4, 610, e)
        sk.line(d, (x0 + 190, y0), (x0 + 210, y0 - 34), INK, 3, 1.4, 611, e)
        sk.line(d, (x0 + 210, y0 - 34), (x0 + 380, y0 - 34), INK, 3, 1.4, 612, e)
        sk.rect(d, (x0, y0, x1, y1), INK, 4, 2.2, 613, clamp(p * 1.3))
    b.add(fn_cap, dur=0.8, wait=0.42)

    f_t, dong = _khoi_chu(sp.get("tieu_de", "HỒ SƠ MẬT"), "display_bold", 86,
                          x1 - x0 - 90, max_dong=2)
    lh = sk.line_height(f_t, 1.2)

    def fn_tieu_de(base, d, p):
        sk.draw_text(base, dong, f_t, INK, cx=(x0 + x1) / 2, y=y0 + 96, p=p,
                     reveal="wipe")
        if p > 0.7:
            sk.line(d, (x0 + 70, y0 + 106 + lh * len(dong)),
                    (x1 - 70, y0 + 106 + lh * len(dong)), INK, 3, 1.6, 620,
                    clamp((p - 0.7) / 0.3))
    b.add(fn_tieu_de, dur=0.8, wait=0.46)

    if sp.get("phu"):
        f2 = font("display", 52)

        def fn_phu(base, d, p):
            sk.draw_text(base, [sp["phu"]], f2, GREY_DARK, cx=(x0 + x1) / 2,
                         y=y0 + 150 + lh * len(dong), p=p, reveal="wipe")
        b.add(fn_phu, dur=0.6, wait=0.36)

    def fn_dau(base, d, p):
        _dau_mat(d, base, (x0 + x1) / 2, y1 - 200, sp.get("dau", "MẬT"), p)
    b.add(fn_dau, dur=0.6, wait=0.34)


def sc_ho_so_trang(b, sp):
    """Trang trong ho so: tieu de, o anh nhan vat, cac dong truong du lieu."""
    x0, x1 = LE + 20, W - LE - 20
    y0 = 470
    cao = 700
    anh_w = 250

    def fn_trang(base, d, p):
        sk.rect(d, (x0, y0, x1, y0 + cao), INK, 3, 2.0, 630, clamp(p * 1.6))
        if p > 0.45:
            sk.line(d, (x0, y0 + 96), (x1, y0 + 96), INK, 3, 1.6, 631,
                    clamp((p - 0.45) / 0.55))
    b.add(fn_trang, dur=0.7, wait=0.4)

    def fn_dau(base, d, p):
        sk.draw_text(base, [sp.get("tieu_de", "HỒ SƠ")],
                     font("display_bold", 44), INK, cx=(x0 + x1) / 2, y=y0 + 26,
                     p=p, reveal="wipe")
    b.add(fn_dau, dur=0.5, wait=0.32)

    if sp.get("anh", True):
        ab = (x0 + 40, y0 + 136, x0 + 40 + anh_w, y0 + 136 + 300)

        def fn_anh(base, d, p):
            sk.rect(d, ab, GREY_DARK, 3, 1.6, 640, clamp(p * 1.8))
            if p > 0.35:
                q = clamp((p - 0.35) / 0.65)
                # nhan vat muc tieu ve nho trong o anh
                cx_ = (ab[0] + ab[2]) / 2
                if q >= 1.0:
                    dan_nguoi(base, cx_, ab[1] + 40, INK, 1.05, 91,
                              sp.get("the_anh", "vay"), sp.get("mat_anh", "vui"))
                else:
                    _ve_nguoi_tho(d, cx_, ab[1] + 40, INK, 1.05, 91, q,
                                  sp.get("the_anh", "vay"),
                                  sp.get("mat_anh", "vui"))
        b.add(fn_anh, dur=0.8, wait=0.44)

    dong = sp.get("dong", [])
    f_d = font("body", 40)
    lh = sk.line_height(f_d, 1.5)
    tx = x0 + (anh_w + 80 if sp.get("anh", True) else 44)
    for i, dg in enumerate(dong):
        def fn_d(base, d, p, i=i, dg=dg):
            sk.draw_text(base, [dg], f_d, INK, x=tx, y=y0 + 150 + i * lh,
                         align="left", p=p, reveal="wipe")
        b.add(fn_d, dur=0.5, wait=0.3)

    if sp.get("dau"):
        def fn_dau2(base, d, p):
            _dau_mat(d, base, x1 - 170, y0 + cao - 120, sp["dau"], p)
        b.add(fn_dau2, dur=0.6, wait=0.34)


def sc_man_so(b, sp):
    """Man hinh so: mot khung hien thi, con so that lon, nhan nho phia tren.

    Dung cho gio va cac con so cua nhiem vu. Ve khung co goc vat de trong nhu
    man hinh dien tu, khong phai mot cai hop binh thuong.
    """
    nhan = sp.get("nhan")
    so = str(sp.get("so", ""))
    f_s, dong = _khoi_chu(so, "display_bold", sp.get("co", 150), RONG - 160, 1)
    lh = sk.line_height(f_s, 1.2)
    w = max(sk.text_size(l, f_s)[0] for l in dong) + 140
    h = lh + 150
    cx_, cy_ = CX, (SAN_Y0 + SAN_Y1) / 2
    box = (cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2)

    def fn_khung(base, d, p):
        sk.rect(d, box, INK, 4, 2.0, 650, clamp(p * 1.5))
        if p > 0.4:
            q = clamp((p - 0.4) / 0.6)
            for gx, gy, sx, sy in ((box[0], box[1], 1, 1), (box[2], box[1], -1, 1),
                                   (box[0], box[3], 1, -1), (box[2], box[3], -1, -1)):
                sk.line(d, (gx + 16 * sx, gy + 16 * sy),
                        (gx + 52 * sx, gy + 16 * sy), RED, 3, 0.8, 651, q)
                sk.line(d, (gx + 16 * sx, gy + 16 * sy),
                        (gx + 16 * sx, gy + 52 * sy), RED, 3, 0.8, 652, q)
    b.add(fn_khung, dur=0.65, wait=0.38)

    if nhan:
        def fn_nhan(base, d, p):
            sk.draw_text(base, [nhan], font("body", 36), GREY_DARK, cx=cx_,
                         y=box[1] + 34, p=p, reveal="fade")
        b.add(fn_nhan, dur=0.5, wait=0.3)

    def fn_so(base, d, p):
        sk.draw_text(base, dong, f_s, INK, cx=cx_, y=box[1] + 92, p=p,
                     reveal="wipe")
    b.add(fn_so, dur=0.8, wait=0.44)

    if sp.get("ghi"):
        f2 = font("body", 38)
        dg = sk.wrap_balanced(sp["ghi"], f2, RONG - 80)[:2]

        def fn_ghi(base, d, p):
            sk.draw_text(base, dg, f2, GREY_DARK, cx=cx_, y=box[3] + 40, p=p,
                         reveal="fade")
        b.add(fn_ghi, dur=0.6, wait=0.3)


def sc_ban_do(b, sp):
    """Ban do nhieu diem, cac diem MO DAN, cuoi cung con mot dong chu.

    Cach ke: nhieu lua chon -> loai het -> con mot. Diem mo dan theo p nen mat
    thay duoc qua trinh loai, khac han voi viec hien san mot dong chu.
    """
    x0, x1 = LE + 20, W - LE - 20
    y0, y1 = 480, 1060
    diem = [(0.18, 0.22), (0.42, 0.12), (0.72, 0.26), (0.86, 0.52),
            (0.12, 0.54), (0.30, 0.74), (0.58, 0.68), (0.80, 0.84),
            (0.48, 0.44), (0.24, 0.40)]

    def fn_khung(base, d, p):
        sk.rect(d, (x0, y0, x1, y1), GREY, 3, 2.0, 660, clamp(p * 1.6))
        if p > 0.3:
            q = clamp((p - 0.3) / 0.5)
            for i in range(1, 3):     # luoi ban do mo
                sk.line(d, (x0 + (x1 - x0) * i / 3, y0),
                        (x0 + (x1 - x0) * i / 3, y1), GREY, 2, 1.0, 661 + i, q)
                sk.line(d, (x0, y0 + (y1 - y0) * i / 3),
                        (x1, y0 + (y1 - y0) * i / 3), GREY, 2, 1.0, 664 + i, q)
    b.add(fn_khung, dur=0.7, wait=0.4)

    def fn_diem(base, d, p):
        # p < 0.45: hien dan het diem. p > 0.45: mo dan tung diem
        for i, (fx, fy) in enumerate(diem):
            px = x0 + (x1 - x0) * fx
            py = y0 + (y1 - y0) * fy
            hien = clamp(p / 0.45 * len(diem) - i)
            if hien <= 0:
                continue
            tat = clamp((p - 0.46) / 0.34 * len(diem) - i)
            if tat >= 1.0:
                continue
            mau = GREY_DARK if tat > 0 else INK
            r_ = 13 - 5 * tat
            sk.ellipse(d, (px - r_, py - r_ * 1.15, px + r_, py + r_ * 0.85),
                       mau, 3, 1.0, 670 + i, 1.0)
            sk.line(d, (px, py + r_ * 0.7), (px, py + r_ * 2.1), mau, 3, 1.0,
                    680 + i, 1.0)
    _dur_diem = max(1.6, b.dur * 0.6)
    b.add(fn_diem, dur=_dur_diem, wait=_dur_diem * 0.72)

    if sp.get("nhan"):
        f, dong = _khoi_chu(sp["nhan"], "display_bold", 78, RONG - 120, 2)
        lh = sk.line_height(f, 1.2)

        def fn_nhan(base, d, p):
            cy_ = (y0 + y1) / 2 - lh * len(dong) / 2
            w = max(sk.text_size(l, f)[0] for l in dong)
            if p > 0.2:
                sk.highlight_behind(base, (CX - w / 2 - 20, cy_ + 4,
                                           CX + w / 2 + 20, cy_ + lh * len(dong)),
                                    AMBER, 7, clamp((p - 0.2) / 0.5))
            sk.draw_text(base, dong, f, INK, cx=CX, y=cy_, p=p, reveal="wipe")
        b.add(fn_nhan, dur=0.85, wait=0.5)


def sc_vi_tien(b, sp):
    """Cai vi + thanh ngan sach. `rung` = ve them net rung quanh vi.

    Cho hai canh lien nhau: canh truoc tuyen bo "em lo" dut khoat, canh sau vi
    rung len. Cung mot hinh, chi khac mot co - nen nguoi xem doc ngay duoc la
    van cai vi do dang doi y.
    """
    cx_, cy_ = CX, 760
    w, h = 300, 200
    box = (cx_ - w / 2, cy_ - h / 2, cx_ + w / 2, cy_ + h / 2)

    rong_ = bool(sp.get("rong"))

    def fn_vi(base, d, p):
        e = clamp(p * 1.5)
        sk.rect(d, box, INK, 4, 2.0, 700, e)
        if p > 0.4:
            q = clamp((p - 0.4) / 0.6)
            if rong_:
                # Vi MO RA hai canh: mot duong ban le o giua + mot khe the moi
                # ben, va ben trong khong co gi. Mot dong xu con lai o day -
                # "gan het" doc ro hon "trong tron", va buon cuoi hon.
                sk.line(d, (cx_, box[1] + 6), (cx_, box[3] - 6), INK, 3, 1.2,
                        703, q)
                for sgn in (-1, 1):
                    ox = cx_ + sgn * w * 0.24
                    sk.line(d, (ox - w * 0.16, cy_ - 34), (ox + w * 0.16,
                            cy_ - 34), GREY, 2, 1.2, 704 + sgn, q)
                if q > 0.55:
                    r_ = 17
                    xu_x = cx_ - w * 0.24
                    sk.ellipse(d, (xu_x - r_, box[3] - 40 - r_, xu_x + r_,
                                   box[3] - 40 + r_), GREY_DARK, 3, 1.0, 706,
                               clamp((q - 0.55) / 0.45))
            else:
                # nap vi + hai the the ra ngoai
                sk.line(d, (box[0], cy_ - 18), (box[2], cy_ - 18), INK, 3, 1.4,
                        701, q)
                for i in range(2):
                    tx = box[0] + 56 + i * 74
                    sk.rect(d, (tx, box[1] - 30 + i * 10, tx + 62,
                                box[1] + 22 + i * 10), GREY_DARK, 3, 1.2,
                            702 + i, q)
        if sp.get("rung") and p > 0.62:
            q = clamp((p - 0.62) / 0.38)
            for i, dx_ in enumerate((-1, 1)):
                for j in range(3):
                    ox = box[2] + 22 + j * 16 if dx_ > 0 else box[0] - 22 - j * 16
                    sk.line(d, (ox, cy_ - 30 + j * 12), (ox, cy_ + 18 + j * 12),
                            GREY_DARK, 3, 1.0, 710 + i * 5 + j, q)
    b.add(fn_vi, dur=0.8, wait=0.44)

    if sp.get("nhan"):
        def fn_nhan(base, d, p):
            f = font("display_bold", 66)
            sk.draw_text(base, [sp["nhan"]], f, INK, cx=cx_, y=box[3] + 56,
                         p=p, reveal="wipe")
        b.add(fn_nhan, dur=0.6, wait=0.36)

    if sp.get("thanh") is not None:
        ty = box[3] + 168
        tw = 520

        def fn_thanh(base, d, p):
            sk.rect(d, (cx_ - tw / 2, ty, cx_ + tw / 2, ty + 46), GREY_DARK, 3,
                    1.4, 720, clamp(p * 1.8))
            if p > 0.4:
                q = clamp((p - 0.4) / 0.6)
                muc = float(sp["thanh"]) * q
                sk.fill_rect(base, (cx_ - tw / 2 + 5, ty + 5,
                                    cx_ - tw / 2 + 5 + (tw - 10) * muc, ty + 41),
                             AMBER + (255,), radius=4, shadow=False)
        b.add(fn_thanh, dur=0.7, wait=0.4)

    if sp.get("ghi"):
        f2 = font("body", 40)
        dg = sk.wrap_balanced(sp["ghi"], f2, RONG - 100)[:2]

        def fn_ghi(base, d, p):
            sk.draw_text(base, dg, f2, GREY_DARK, cx=cx_, y=1080, p=p,
                         reveal="fade")
        b.add(fn_ghi, dur=0.6, wait=0.32)


def sc_dien_thoai(b, sp):
    """Dien thoai dung giua khung: khung chat, cac tin nhan, mot cai nut lon.

    `phao` = phao giay bung ra khi bam nut. Chi ve khi CO nut, vi phao giay ma
    khong co hanh dong bam thi khong ai hieu no an mung cai gi.
    """
    w, h = 420, 720
    x0 = CX - w / 2
    y0 = (SAN_Y0 + SAN_Y1) / 2 - h / 2

    def fn_may(base, d, p):
        e = clamp(p * 1.5)
        sk.rect(d, (x0, y0, x0 + w, y0 + h), INK, 4, 1.8, 730, e)
        if p > 0.4:
            q = clamp((p - 0.4) / 0.6)
            sk.rect(d, (x0 + 18, y0 + 60, x0 + w - 18, y0 + h - 90), GREY, 2,
                    1.2, 731, q)
            sk.line(d, (CX - 40, y0 + 34), (CX + 40, y0 + 34), GREY_DARK, 3,
                    1.0, 732, q)      # loa thoai
    b.add(fn_may, dur=0.7, wait=0.4)

    tin = sp.get("tin", [])
    f_t = font("body", 34)
    ty = y0 + 92
    for i, t in enumerate(tin):
        ben_em = (t.get("ai", "em") == "em")
        dong = sk.wrap_balanced(t["text"], f_t, w - 150)[:3]
        lh = sk.line_height(f_t, 1.3)
        bh = lh * len(dong) + 34
        bw = min(w - 70, max(sk.text_size(l, f_t)[0] for l in dong) + 44)
        bx = (x0 + w - 34 - bw) if ben_em else (x0 + 34)

        def fn_t(base, d, p, bx=bx, bw=bw, bh=bh, dong=dong, ty=ty,
                 ben_em=ben_em, i=i):
            sk.rect(d, (bx, ty, bx + bw, ty + bh), INK if ben_em else GREY_DARK,
                    3, 1.4, 740 + i, clamp(p * 1.8))
            if p > 0.4:
                sk.draw_text(base, dong, f_t, INK, cx=bx + bw / 2, y=ty + 16,
                             p=clamp((p - 0.4) / 0.6), reveal="wipe")
        b.add(fn_t, dur=0.6, wait=0.36)
        ty += bh + 22

    if sp.get("nut"):
        nb = (x0 + 44, y0 + h - 200, x0 + w - 44, y0 + h - 116)

        def fn_nut(base, d, p):
            sk.fill_rect(base, nb, STICKY_YELLOW + (255,), radius=12,
                         shadow=True)
            sk.rect(d, nb, INK, 4, 1.6, 750, clamp(p * 1.6))
            if p > 0.4:
                f = _co_vua_nut(sp["nut"], nb[2] - nb[0] - 40)
                oy = (nb[1] + nb[3]) / 2 - sk.text_size(sp["nut"], f)[1] / 2 - 6
                sk.draw_text(base, [sp["nut"]], f, INK,
                             cx=(nb[0] + nb[2]) / 2, y=oy,
                             p=clamp((p - 0.4) / 0.6), reveal="wipe")
        b.add(fn_nut, dur=0.7, wait=0.4)

        if sp.get("phao"):
            def fn_phao(base, d, p):
                # phao giay: cac net ngan toe ra tu tam cai nut
                bcx, bcy = (nb[0] + nb[2]) / 2, nb[1] - 10
                import math
                for i in range(18):
                    a = math.pi * (0.08 + 0.84 * (i / 17))
                    xa = 1.0 - abs(0.5 - i / 17) * 0.5
                    r1 = 90 * p * xa
                    r2 = r1 + 34 * xa
                    sk.line(d, (bcx - math.cos(a) * r1, bcy - math.sin(a) * r1),
                            (bcx - math.cos(a) * r2, bcy - math.sin(a) * r2),
                            (RED if i % 3 == 0 else AMBER) if i % 2 else GREY_DARK,
                            3, 0.8, 760 + i, 1.0)
            b.add(fn_phao, dur=0.8, wait=0.4)


def _co_vua_nut(txt, rong_max):
    for co in (52, 46, 42, 38, 34):
        f = font("display_bold", co)
        if sk.text_size(txt, f)[0] <= rong_max:
            return f
    return font("display_bold", 32)


BUILDERS = {
    "thoai": sc_thoai, "mot_nguoi": sc_mot_nguoi, "troiqua": sc_troiqua,
    "chu": sc_chu, "the_moi": sc_the_moi,
    "di_den": sc_di_den, "mo_thu": sc_mo_thu,
    "chon_quan": sc_chon_quan,
    "to_lich": sc_to_lich, "ban_dem": sc_ban_dem,
    "ho_so_bia": sc_ho_so_bia, "ho_so_trang": sc_ho_so_trang,
    "man_so": sc_man_so, "ban_do": sc_ban_do,
    "vi_tien": sc_vi_tien, "dien_thoai": sc_dien_thoai,
}


def build(sp, dur, doc=None):
    kind = sp.get("scene")
    if kind not in BUILDERS:
        raise ValueError(f"theme net_ve khong co loai canh {kind!r}. "
                         f"Co: {', '.join(sorted(BUILDERS))}")
    b = B(dur)
    tieu_de(b, sp.get("head"), at=0.0, khoanh=sp.get("head_khoanh", False))
    BUILDERS[kind](b, sp)
    b.finish()
    # phu de them SAU khi chuan hoa nhip: no phai hien ngay tu dau cung giong doc
    phu_de(b, sp.get("caption"), at=0.28)
    return b.els
