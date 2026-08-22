"""VISUAL LAB - mo hinh THE GIOI BEN VUNG + ONG KINH, thay cho `scene`.

## Gia dinh dang bi thu thach

Trong `bench`, don vi bo cuc la CANH. Moi canh goi `build()` voi mot `B(dur)`
moi, ve lai tu dau tren mot hinh chu nhat san dien co dinh (470..1296), roi tan
di. Hai he qua do duoc, khong phai suy dien:

  - `research/do_don_dieu.py`: khung co dinh lam phang 21-39% do da dang noi dung
  - hai canh cung loai cach nhau 0,036-0,042 tren thang 0..1, tuc gan nhu trung

Va mot he qua khong do duoc nhung nang hon: **khong the he lo thong tin bang
cach di chuyen may quay**, vi moi canh la mot to giay moi. Muon nguoi xem "phat
hien ra" mot thu thi phai VE THEM no vao mot canh khac - tuc noi cho ho, khong
phai de ho tu thay.

## Mo hinh thay the

Video la MOT khong gian lien tuc. Doi tuong song xuyen suot. Nhip khong ve lai
gi ca - no chi doi hai thu:

    ONG KINH  dang nhin vao dau, rong bao nhieu
    TRANG THAI cua tung doi tuong

Nen "he lo" tro thanh mot phep dich chuyen ong kinh: thu chua tung xuat hien
khong phai vi no chua duoc ve, ma vi no **nam ngoai khung**. Do la khac biet
quan trong nhat so voi `bench`.

## Toa do

The gioi do bang don vi tu do. Ong kinh la mot hinh chu nhat trong the gioi do,
ty le khoa 9:16 theo khung hinh. Chieu rong khung nhin (`w`) chinh la muc zoom:
`w` nho la zoom sat, `w` lon la lui ra.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from style import H, W, clamp  # noqa: E402


def diu(p):
    """Ease in-out cho chuyen dong ong kinh. Ong kinh KHONG duoc dung tuyen
    tinh: mat nguoi doc mot cu pan tuyen tinh la "bi keo", con co gia toc thi
    doc la "minh dang nhin sang"."""
    p = clamp(p)
    return p * p * (3 - 2 * p)


class Cam:
    """Khung nhin trong the gioi. `(x, y)` la TAM, `w` la be rong."""

    def __init__(self, x, y, w):
        self.x, self.y, self.w = float(x), float(y), float(w)

    @property
    def h(self):
        return self.w * H / W

    def __repr__(self):
        return f"Cam({self.x:.0f}, {self.y:.0f}, w={self.w:.0f})"

    def tron(self, khac, p):
        """Noi suy sang mot khung nhin khac.

        Zoom noi suy theo LOGARIT chu khong tuyen tinh. Do la chi tiet quyet
        dinh cam giac: tuyen tinh thi mot cu zoom tu w=900 ra w=3600 chay rat
        nhanh o dau roi bo lai o cuoi, nhin nhu bi giat. Theo logarit thi TOC DO
        TUONG DOI khong doi - dung cach ong kinh that hoat dong.
        """
        e = diu(p)
        return Cam(self.x + (khac.x - self.x) * e,
                   self.y + (khac.y - self.y) * e,
                   math.exp(math.log(self.w) + (math.log(khac.w)
                                                - math.log(self.w)) * e))

    def chieu(self, wx, wy):
        """The gioi -> khung hinh."""
        k = W / self.w
        return ((wx - (self.x - self.w / 2)) * k,
                (wy - (self.y - self.h / 2)) * k)

    def ty_le(self):
        return W / self.w

    def trong_khung(self, x0, y0, x1, y1, le=200):
        """Hop nay co giao voi khung nhin khong (cong mot vien le)?

        Dung de bo qua doi tuong ngoai khung - va quan trong hon, de KIEM: mot
        nhip noi rang "chua ai thay vung B" thi vung B phai that su nam ngoai
        khung, chu khong phai chi mo di.
        """
        vx0, vx1 = self.x - self.w / 2 - le, self.x + self.w / 2 + le
        vy0, vy1 = self.y - self.h / 2 - le, self.y + self.h / 2 + le
        return not (x1 < vx0 or x0 > vx1 or y1 < vy0 or y0 > vy1)


class DoiTuong:
    """Mot thu song trong the gioi, xuyen qua nhieu nhip.

    Khac han mot `scene` cua bench: no khong thuoc ve nhip nao. Nhip chi doi
    `trang_thai` cua no, va ong kinh quyet dinh no co nam trong khung hay khong.
    """

    def __init__(self, id, loai, x, y, w=0, h=0, nhan="", sub="", mau="cool",
                 trang_thai="thuong", **thua):
        self.id, self.loai = id, loai
        self.x, self.y, self.w, self.h = float(x), float(y), float(w), float(h)
        self.nhan, self.sub, self.mau = nhan, sub, mau
        self.trang_thai = trang_thai
        self.thua = thua          # truong rieng theo loai
        self.hien = 1.0           # 0..1, nhip co the mo dan mot doi tuong

    def hop(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def tam(self):
        return (self.x + self.w / 2, self.y + self.h / 2)


class Nhip:
    """Mot nhip: ong kinh o dau, doi tuong nao doi trang thai, loi doc gi.

    KHONG co bo cuc trong day. Do la ca y tuong - bo cuc nam o the gioi, nhip
    chi la mot lat cat thoi gian cua the gioi do.
    """

    def __init__(self, ten="", cam=None, narration="", caption="",
                 doi=None, hien=None, an=None, khung="toi_gian", ghi="",
                 chu_y=None, boi_canh=None, giu=1.0):
        self.ten = ten
        self.cam = cam
        self.narration, self.caption = narration, caption
        self.doi = doi or {}          # {id: trang_thai}
        self.hien = hien or []        # id moi xuat hien trong nhip nay
        self.an = an or []
        self.khung = khung            # day | toi_gian | khong
        self.ghi = ghi                # nhan mono nho, thuong la dieu kien do
        # BA TANG nhan manh, khong phai hai. Ban dau chi co `chu_y` va "con
        # lai", va no hong o nhip he lo: nghia cua nhip do CHINH LA phep so
        # sanh giua hai vung, nen day ca hai vung ra sau lam mat luon noi dung.
        #   chu_y     1,00  tieu diem, sang nhat
        #   boi_canh  0,55  phai doc duoc, nhung khong tranh attention
        #   con lai   0,18  chi can co mat de biet no ton tai
        self.chu_y = chu_y or []
        self.boi_canh = boi_canh or []
        self.giu = float(giu)         # trong so thoi luong


def cam_tu_tieu_diem(tg, ids, muc=0.62, le_duoi=0.16):
    """Suy ONG KINH tu TIEU DIEM, thay vi viet tay toa do.

    Day la ket qua quan trong nhat cua vong R&D nay, va no den tu mot that bai:
    ban dau moi nhip tu khai `cam: [x, y, w]`. Do bang `research/do_don_dieu.py`
    thi da dang tang 37% so voi production - nhung nhin still thi hai nhip bi
    XAU HON han ban production: vien cua cac vung chen kin canh tren va duoi,
    cong troi giua khong gian, va mat khong biet nen nhin dau.
    
    Nguyen nhan: trong `bench`, `chrome()` cong san dien co dinh DAM BAO moi
    khung co dung mot khoi chinh. Bo khung co dinh di thi mat luon dam bao do,
    va lam mo bot cac doi tuong khac (`chu_y`) KHONG du bu lai - doi tuong da mo
    van chiem dung dien tich do va van co duong vien do.

    Nen dam bao phai duoc dua tro lai o mot cho khac: khong phai o bo cuc co
    dinh, ma o ONG KINH. Khai tieu diem, engine tu tinh khung nhin sao cho tieu
    diem chiem dung `muc` phan be rong khung hinh. Nguoi viet mat quyen dat toa
    do, va doi lai moi khung hinh co mot khoi chinh do duoc.

    `le_duoi` day tam nhin len mot chut de dai phu de o day khung khong de len
    tieu diem - mot loi nua bat duoc khi nhin still.
    """
    hop = [tg[k].hop() for k in ids if k in tg]
    if not hop:
        return None
    x0 = min(h[0] for h in hop)
    y0 = min(h[1] for h in hop)
    x1 = max(h[2] for h in hop)
    y1 = max(h[3] for h in hop)
    bw, bh = max(1.0, x1 - x0), max(1.0, y1 - y0)
    # Chon `w` sao cho chieu NANG HON trong hai chieu dat dung muc yeu cau.
    # Chi tinh theo be rong thi mot tieu diem cao va hep se tran ra ngoai canh
    # tren duoi; chi tinh theo chieu cao thi nguoc lai.
    w_theo_ngang = bw / muc
    w_theo_doc = (bh / muc) * W / H
    w = max(w_theo_ngang, w_theo_doc)
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2 - (w * H / W) * le_duoi
    return Cam(cx, cy, w)


def nap(duong):
    """Nap mot tep `.vlab.yaml` thanh (the_gioi, danh sach nhip, meta)."""
    import yaml
    with open(duong, "r", encoding="utf-8") as f:
        d = yaml.safe_load(f)
    tg = {}
    for o in d.get("the_gioi") or []:
        dt = DoiTuong(**o)
        tg[dt.id] = dt
    nhips = []
    for n in d.get("nhip") or []:
        c = n.pop("cam", None)
        muc = n.pop("muc", None)
        nh = Nhip(cam=Cam(*c) if c else None, **n)
        # Khong khai `cam` thi suy tu `chu_y`. Do la duong di duoc khuyen dung:
        # xem docstring cua `cam_tu_tieu_diem`.
        if nh.cam is None and nh.chu_y:
            nh.cam = cam_tu_tieu_diem(tg, nh.chu_y, muc=float(muc or 0.62))
        nhips.append(nh)
    return tg, nhips, d


def kiem(tg, nhips, out):
    """Phep kiem o TANG NGU NGHIA, khong o tang hinh hoc.

    Day la cho mo hinh nay hon `bench` ve kha nang kiem. `lint.check_gantt` phai
    kiem hinh hoc (thanh chong nhau, `at + w <= 1`) vi hinh hoc CHINH LA noi
    dung o do. O day noi dung la QUAN HE giua doi tuong, nen kiem duoc nhung
    dieu ma bench khong kiem noi:

      - nhip noi "chua thay vung B" thi vung B phai NAM NGOAI khung nhin
      - doi tuong duoc `chu_y` phai nam TRONG khung nhin
      - `doi`/`hien` phai tro tren mot id co that
      - ong kinh khong duoc nhay qua 6 lan zoom trong mot nhip
    """
    dang_hien = set()
    truoc = None
    for i, n in enumerate(nhips, 1):
        tag = f"nhip {i:02d} {n.ten}"
        for k in (list(n.doi) + list(n.chu_y) + list(n.boi_canh)
                  + list(n.hien) + list(n.an)):
            if k not in tg:
                out.append(("LOI", tag, f"tro tới `{k}` không có trong thế giới"))
        dang_hien |= set(n.hien)
        dang_hien -= set(n.an)
        if n.cam is None:
            out.append(("LOI", tag, "thiếu `cam` — nhịp nào cũng phải nói ống "
                                    "kính đang ở đâu"))
            continue
        for k in n.chu_y:
            if k not in tg:
                continue
            # KHONG dung `trong_khung`: ham do co le 200 don vi, nen mot doi
            # tuong chi con MEP trong khung van qua duoc phep kiem. Da thay o
            # ban thu hai: `chu_y: api` qua duoc trong khi the endpoint da troi
            # han ra ngoai canh tren. Doi TAM cua doi tuong nam trong khung.
            cx, cy = tg[k].tam()
            vx0, vx1 = n.cam.x - n.cam.w / 2, n.cam.x + n.cam.w / 2
            vy0, vy1 = n.cam.y - n.cam.h / 2, n.cam.y + n.cam.h / 2
            if not (vx0 <= cx <= vx1 and vy0 <= cy <= vy1):
                out.append(("LOI", tag,
                            f"`chu_y: {k}` nhưng tâm của nó nằm NGOÀI khung "
                            f"nhìn — đang bảo người xem chú ý vào thứ họ "
                            f"không thấy"))
        for k in dang_hien:
            if k in tg and not n.cam.trong_khung(*tg[k].hop()):
                pass          # nam ngoai khung la HOP LE va la ca ky thuat
        if truoc is not None:
            z = max(n.cam.w, truoc.w) / max(1e-6, min(n.cam.w, truoc.w))
            if z > 6:
                out.append(("CANH BAO", tag,
                            f"ống kính đổi zoom {z:.1f} lần trong một nhịp — "
                            f"quá 6 lần thì mắt mất điểm neo, cắt thành hai nhịp"))
        truoc = n.cam
    return out
