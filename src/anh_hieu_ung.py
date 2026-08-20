"""Hieu ung video tu MOT tam anh xe. Ba kieu, dung cho hero trang web.

    python src/anh_hieu_ung.py img/angle_0.png doi_mau  --giay 8
    python src/anh_hieu_ung.py img/angle_0.png hien_ra  --giay 4
    python src/anh_hieu_ung.py img/angle_0.png lo_lung  --giay 6

## Cai gi lam duoc va cai gi khong, do tu chinh tam anh

Da do tren `img/angle_0.png` (1376x768, xe do trong studio toi):

  mask MAU (bao hoa > 70, hue do)  -> 4,72% khung, bao hoa 173 so voi nen 93.
                                      TACH SACH than xe. Doi mau duoc.
  mask VUNG TOI (V < 55)           -> 70% khung. Banh xe, gam, luoi tan nhiet
                                      den lan het vao nen studio toi. KHONG
                                      tach duoc hinh xe khoi nen.
  nen hai bien                     -> lech chuan 23,4, co dai sang va bong.
                                      Nen KHONG phang nen mot nguong khong du.

Ket luan: moi hieu ung KHONG can tach xe khoi nen thi lam duoc. Hieu ung nao
doi hoi dat xe len mot canh khac (mat trang, ngoai khong gian) thi khong, vi
phai co mask hinh xe ma anh nay khong cho ra duoc.

## Moi kieu la GENERATOR, khong tra ve list

Ban dau moi ham dung ca danh sach frame roi tra ve. Voi 180 frame anh
1376x768 o float32 la 180 x 12,7 MB = 2,3 GB -> x264 bao
`malloc of size 6103360 failed` va vo duong ong ghi. Sinh tung frame roi ghi
ngay thi bo nho dung o muc mot frame.

`lo_lung` la truong hop bien: no CAN dich xe ma khong dich nen, nen o day dung
mask vung trung tam co vien mem. Bien do phai NHO (10-16px) - nen toi va it chi
tiet nen vet noi khong nhin ra. Bien do lon la lo vet ngay.
"""
import argparse
import math
import os
import sys

import numpy as np
from PIL import Image, ImageFilter

FPS = 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "out")


def _nap(path):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    return im.crop((0, 0, w - w % 2, h - h % 2))


def mask_than_xe(im, s_min=70, v_min=40):
    """Mask than xe theo MAU (khong theo do sang). Tra ve mang 0..1 da lam mem.

    Dung mau chu khong dung do sang vi than xe do bao hoa cao con nen studio la
    xam - do duoc 173 so 93. Neu dung do sang thi banh xe den va nen toi lan vao
    nhau, mask thanh vo dung (xem docstring dau file).
    """
    hsv = np.asarray(im.convert("HSV")).astype(np.float32)
    Hh, S, V = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ((S > s_min) & (V > v_min) & ((Hh < 22) | (Hh > 225))).astype(np.float32)
    # lam mem vien: cat cung thi khi doi mau se thay duong ranh rang cua
    return np.asarray(Image.fromarray((m * 255).astype(np.uint8))
                      .filter(ImageFilter.GaussianBlur(2))).astype(np.float32) / 255.0


def mask_giua(im, no=0.30):
    """Mask vung trung tam co vien RAT mem - dung cho `lo_lung`.

    Khong phai hinh xe. Chi la mot vung bau quanh xe, vien mem den muc dich vai
    chuc pixel thi khong thay vet. Bien do lon thi se lo, xem docstring dau file.
    """
    W, H = im.size
    m = Image.new("L", (W, H), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).ellipse(
        [int(W * 0.20), int(H * 0.14), int(W * 0.80), int(H * 0.86)], fill=255)
    r = int(min(W, H) * no)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(r))
                      ).astype(np.float32)[..., None] / 255.0


def _doi_hue(a, mask, dich_hue, giu_v=True):
    """Doi mau vung mask sang `dich_hue` (0..255 he HSV cua PIL)."""
    im = Image.fromarray(a.astype(np.uint8))
    hsv = np.asarray(im.convert("HSV")).astype(np.float32)
    h2 = hsv.copy()
    h2[..., 0] = dich_hue
    moi = np.asarray(Image.fromarray(h2.astype(np.uint8), "HSV").convert("RGB")
                     ).astype(np.float32)
    m = mask[..., None]
    return a * (1 - m) + moi * m


# --------------------------------------------------------------------- kieu
def kieu_doi_mau(im, n, tuy):
    """Than xe doi mau qua tung phuong an. Dung nhat cho trang ban xe."""
    a = np.asarray(im).astype(np.float32)
    mask = mask_than_xe(im)
    mau = tuy.get("mau") or [(0, "đỏ"), (155, "xanh dương"), (60, "xanh lá"),
                             (28, "vàng cam"), (200, "tím")]
    moi_mau = max(1, n // len(mau))
    for i in range(n):
        k = min(len(mau) - 1, i // moi_mau)
        k2 = min(len(mau) - 1, k + 1)
        # chuyen mau muot o 25% cuoi moi doan
        p = (i - k * moi_mau) / moi_mau
        h = mau[k][0] if p < 0.75 else (
            mau[k][0] + (mau[k2][0] - mau[k][0]) * (p - 0.75) / 0.25)
        yield _doi_hue(a, mask, h)


def kieu_hien_ra(im, n, tuy):
    """Toi den -> den bat sang -> quang sang lan ra -> hien ca xe.

    Manh nhat trong ba kieu vi no dung dung chat lieu cua tam anh: xe dat trong
    studio toi, nen viec "hien ra tu toi" khong phai hieu ung dan vao ma la thu
    co san trong anh.
    """
    a = np.asarray(im).astype(np.float32)
    vung = tuy.get("vung") or [(0.28, 0.43, 0.42, 0.53), (0.59, 0.43, 0.73, 0.53),
                               (0.28, 0.64, 0.40, 0.71), (0.67, 0.64, 0.79, 0.71)]
    W, H = im.size
    hat = np.zeros((H, W, 3), np.float32)
    for (fx0, fy0, fx1, fy1) in vung:
        x0, y0, x1, y1 = (int(fx0 * W), int(fy0 * H), int(fx1 * W), int(fy1 * H))
        o = a[y0:y1, x0:x1]
        lum = o.mean(axis=2)
        m = np.clip((lum - 170) / 85.0, 0, 1)[..., None]
        hat[y0:y1, x0:x1] = np.maximum(hat[y0:y1, x0:x1], o * m)
    quang = np.asarray(Image.fromarray(np.clip(hat, 0, 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(
                           max(8, int(min(W, H) * 0.07))))).astype(np.float32)
    for i in range(n):
        p = i / max(1, n - 1)
        # Nhip da sua. Ban dau: den toi 0.42 moi bat dau hien xe, va hien theo
        # luy thua 1.4 -> do duoc la GAN 4 GIAY den tren video 6 giay. Hero ma
        # den 4 giay thi nguoi xem da cuon qua roi.
        #   0.00-0.06  den
        #   0.06-0.26  den xe bat, quang sang lan ra (day la cho "wow")
        #   0.22-0.72  ca xe sang dan len
        den = min(1.0, max(0.0, (p - 0.06) / 0.20))
        hien = min(1.0, max(0.0, (p - 0.22) / 0.50)) ** 1.05
        nen = a * (0.06 + 0.94 * hien)
        b = np.clip(quang * (3.2 * den * (1.0 - 0.30 * hien)), 0, 255)
        yield 255.0 - (255.0 - nen) * (255.0 - b) / 255.0


def kieu_lo_lung(im, n, tuy):
    """Xe nhap nho len xuong. Bien do NHO - xem docstring dau file ve vet noi."""
    a = np.asarray(im).astype(np.float32)
    m = mask_giua(im)
    bien = float(tuy.get("bien", 14))
    for i in range(n):
        p = i / n
        dy = -bien * math.sin(2 * math.pi * p)
        dich = np.roll(a, int(round(dy)), axis=0)
        yield a * (1 - m) + dich * m


KIEU = {"doi_mau": kieu_doi_mau, "hien_ra": kieu_hien_ra,
        "lo_lung": kieu_lo_lung}


def lam(path, kieu, giay=6.0, crf=24, ra=None, **tuy):
    import imageio_ffmpeg
    if kieu not in KIEU:
        raise SystemExit(f"khong co kieu {kieu!r}. Co: {', '.join(KIEU)}")
    im = _nap(path)
    n = int(round(giay * FPS))
    print(f"{kieu}: anh {im.size[0]}x{im.size[1]} | {giay}s = {n} frame | crf {crf}")
    os.makedirs(OUT, exist_ok=True)
    ten = os.path.splitext(os.path.basename(path))[0]
    dich = ra or os.path.join(OUT, f"{ten}-{kieu}.mp4")
    w = imageio_ffmpeg.write_frames(
        dich, im.size, fps=FPS, codec="libx264", pix_fmt_in="rgb24",
        macro_block_size=1, ffmpeg_log_level="error",
        output_params=["-crf", str(crf), "-pix_fmt", "yuv420p", "-preset", "slow",
                       "-movflags", "+faststart"])
    w.send(None)
    for f in KIEU[kieu](im, n, tuy):      # generator: giu dung MOT frame
        w.send(np.clip(f, 0, 255).astype(np.uint8).tobytes())
    w.close()
    print(f"XONG -> {dich}  ({os.path.getsize(dich)/1024:.0f} KB)")
    return dich


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("anh")
    ap.add_argument("kieu", choices=sorted(KIEU))
    ap.add_argument("--giay", type=float, default=6.0)
    ap.add_argument("--crf", type=int, default=24)
    ap.add_argument("--bien", type=float, default=14, help="lo_lung: bien do px")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    lam(a.anh, a.kieu, a.giay, a.crf, a.out, bien=a.bien)


if __name__ == "__main__":
    main()
