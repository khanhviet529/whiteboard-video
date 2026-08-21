"""VISUAL LAB - dung khung hinh tu mot tep `.vlab.yaml`.

    py src/vlab/dung.py vlab/129-idor-huong-c.vlab.yaml
    py src/vlab/dung.py <tep> --dai 6      # 6 khung moi nhip, de soi chuyen dong

Xuat ra `build/vlab/<ten>/`. KHONG sinh giong noi, khong ghep video - day la
prototype de danh gia HINH, va vong lap danh gia hinh phai tinh bang giay.

## Ba che do khung (chrome)

Gia dinh dang bi thu thach: "rail + chip chuong + tieu de + the phu de + dong
chan phai co o MOI canh". Do do duoc la lam phang 21-39% do da dang
(`research/do_don_dieu.py`). Nen o day khung la mot THAM SO CUA NHIP:

    day        giong bench: rail, chuong, tieu de, phu de, chan
    toi_gian   chi rail mo + phu de. Sân dien la ca khung hinh
    khong      khong gi ca. Dung cho nhip he lo va nhip cao trao

Luat duy nhat giu lai: **nhip dau va nhip cuoi phai `day`**. Do la cho nguoi
xem nhan ra kenh; o giua thi khong can, va giu no o giua chinh la cho hong.
"""
import os
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

import numpy as np  # noqa: E402
import sketch as sk  # noqa: E402
import typo  # noqa: E402
import ve  # noqa: E402
from style import H, SS, W, clamp, font, s  # noqa: E402
from the_gioi import Cam, kiem, nap  # noqa: E402

MARGIN = 60
CX = W // 2


# ------------------------------------------------------------------------ nen
_NEN = None


def nen():
    """Nen: luoi cham + bloom, giu y nguyen chat lieu cua `bench`.

    Day la mot trong nhung thu KHONG thu nghiem: nen la nhan dien, va doi nen
    thi mat luon phan brand ma bo khung vua nhuong lai.
    """
    global _NEN
    if _NEN is not None:
        return _NEN.copy()
    img = Image.new("RGBA", (s(W), s(H)), ve.BG + (255,))
    d = ImageDraw.Draw(img)
    r = max(1, s(1.2))
    for y in range(0, H + 1, 46):
        for x in range(0, W + 1, 46):
            d.ellipse([s(x) - r, s(y) - r, s(x) + r, s(y) + r],
                      fill=(26, 26, 33, 255))
    a = np.array(img.convert("RGB")).astype(np.float32)
    hh, ww = a.shape[:2]
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    nx = (xx / ww - 0.5) / 0.62
    ny = (yy / hh - 0.44) / 0.40
    fall = np.clip(1.0 - (nx * nx + ny * ny), 0.0, 1.0) ** 2.1
    for i, tint in enumerate((30.0, 20.0, 52.0)):
        a[:, :, i] += fall * tint
    rng = np.random.default_rng(7)
    a += rng.normal(0, 5.5, (hh, ww, 1))
    _NEN = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
    return _NEN.copy()


# --------------------------------------------------------------------- khung
def khung(base, che_do, meta, nhip, p):
    """Ba che do. Xem docstring dau file ve ly do khung la tham so cua nhip."""
    if che_do == "khong":
        return
    d = ImageDraw.Draw(base)
    brand = meta.get("brand", "")
    if brand:
        mo = 1.0 if che_do == "day" else 0.45
        col = tuple(int(ve.BG[i] + (ve.HOT[i] - ve.BG[i]) * mo)
                    for i in range(3))
        typo.mono(base, brand, (MARGIN, 62), col, 1.0, 24, 5.0, 700)
    if che_do == "day":
        tag = meta.get("tag", "")
        if tag:
            f = typo.mono_font(22, 400)
            typo.ttext(base, tag, f, ve.DIM, 64,
                       x=W - MARGIN - typo.track_w(tag, f, 3.0), track=3.0)
        d.line([s(MARGIN), s(116), s(W - MARGIN), s(116)],
               fill=ve.EDGE + (255,), width=s(2))
        if nhip.ten:
            f, lines, lh = typo.headline(nhip.ten, W - MARGIN * 2, 150, 74, 48,
                                         -2.0, "grot_black")
            for i, ln in enumerate(lines[:2]):
                typo.ttext(base, ln, f, ve.FG, 152 + i * lh, x=MARGIN,
                           track=-2.0)
    if nhip.ghi:
        typo.mono(base, nhip.ghi, (MARGIN, H - 128), ve.DIM, 1.0, 21, 3.5)


def phu_de(base, txt, at=1.0):
    """The phu de. Vi tri KHONG co dinh o day: no bam day khung.

    `bench` dat no o y=1332 co dinh, tuc no chiem mot dai ngang giua khung o moi
    canh. Day la mot trong nhung thu lam moi khung hinh giong nhau.
    """
    if not txt:
        return
    for co in (34, 32, 30, 28, 26):
        f = font("grot_med", co)
        lines = sk.wrap(txt, f, W - MARGIN * 2 - 96)
        lh = sk.line_height(f, 1.34)
        if lh * len(lines) + 44 <= 190:
            break
    hh = lh * len(lines) + 44
    y0 = H - 232 - hh
    box = (MARGIN, y0, W - MARGIN, y0 + hh)
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).rounded_rectangle(
        [s(box[0]), s(box[1]), s(box[2]), s(box[3])], radius=s(14),
        fill=ve.SURF + (232,), outline=ve.EDGE + (255,), width=s(2))
    base.alpha_composite(lay)
    d = ImageDraw.Draw(base)
    d.line([s(box[0] + 2), s(box[1] + 12), s(box[0] + 2), s(box[3] - 12)],
           fill=ve.HOT + (255,), width=s(5))
    for i, ln in enumerate(lines):
        typo.ttext(base, ln, f, ve.FG, box[1] + 22 + i * lh, x=box[0] + 34,
                   track=0)


# ------------------------------------------------------------------ mot khung
def mot_khung(tg, nhips, meta, i, p):
    """Dung khung hinh cua nhip `i` tai tien do `p` trong nhip do."""
    nhip = nhips[i]
    truoc = nhips[i - 1] if i else None
    # Ong kinh: 34% dau nhip la doan DI CHUYEN tu vi tri cu sang vi tri moi.
    # Sau do dung yen. Chuyen dong lien tuc suot nhip lam mat khong bam duoc
    # vao gi - da thu va bo, xem README cua lab.
    if truoc is not None and truoc.cam is not None:
        cam = truoc.cam.tron(nhip.cam, clamp(p / 0.34))
    else:
        cam = nhip.cam

    dang = set()
    for k in range(i + 1):
        dang |= set(nhips[k].hien)
        dang -= set(nhips[k].an)
        for oid, tt in nhips[k].doi.items():
            if oid in tg:
                tg[oid].trang_thai = tt
    # Doi tuong VUA hien trong nhip nay thi mo dan
    for oid in tg:
        tg[oid].hien = 1.0
    if nhip.hien:
        moc = clamp((p - 0.30) / 0.28)
        for oid in nhip.hien:
            if oid in tg:
                tg[oid].hien = moc

    base = nen()
    ve.ve_the_gioi(base, tg, cam, dang, chu_y=tuple(nhip.chu_y),
                   boi_canh=tuple(nhip.boi_canh))
    khung(base, nhip.khung, meta, nhip, p)
    phu_de(base, nhip.caption)
    rgb = base.convert("RGB")
    return rgb.reduce(SS) if isinstance(SS, int) and SS > 1 else rgb


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    duong = args[0]
    dai = 1
    if "--dai" in sys.argv:
        dai = int(sys.argv[sys.argv.index("--dai") + 1])

    tg, nhips, meta = nap(duong)
    loi = kiem(tg, nhips, [])
    n_loi = sum(1 for k, _, _ in loi if k == "LOI")
    if loi:
        print(f"kiem ngu nghia: {n_loi} loi, {len(loi) - n_loi} canh bao")
        for k, w, m in loi:
            print(f"  [{k:8s}] {w}: {m}")
    else:
        print("kiem ngu nghia: khong thay gi dang ngo")
    if n_loi:
        return 1

    ten = os.path.basename(duong).replace(".vlab.yaml", "")
    out = os.path.join(os.path.dirname(HERE), "..", "build", "vlab", ten)
    out = os.path.abspath(out)
    os.makedirs(out, exist_ok=True)
    for f in os.listdir(out):
        if f.endswith(".png"):
            os.remove(os.path.join(out, f))

    for i, nhip in enumerate(nhips):
        for j in range(dai):
            # Mot khung: lay o 0,80 nhip - sau khi ong kinh da dung va doi tuong
            # da hien. Nhieu khung: rai deu de soi chuyen dong.
            p = 0.80 if dai == 1 else (j + 0.5) / dai
            im = mot_khung(dict(tg), nhips, meta, i, p)
            hau = "" if dai == 1 else f"-{j}"
            im.save(os.path.join(out, f"nhip-{i + 1:02d}{hau}-{nhip.khung}.png"))
        print(f"  nhip {i + 1:02d} [{nhip.khung:9s}] {nhip.ten[:44]}")
    print(f"xuat tai: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
