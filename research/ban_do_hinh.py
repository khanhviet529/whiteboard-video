"""BAN DO PHU HINH ANH - 292 chu de trong `files/ke-hoach/` xep theo Y NGHIA HINH.

    py research/ban_do_hinh.py            # bang dem + cho con thieu
    py research/ban_do_hinh.py --chi-tiet # liet ke tung chu de

## Vi sao co file nay

Cau hoi "renderer nen dau tu primitive nao truoc" chi tra loi duoc bang cach
DEM, khong doan. Va dem tren corpus nao moi dung: `screenplays/` chi co 32 file
hoan chinh (70 file con lai la khung tu sinh, chua co loi doc), qua it de rut ra
mot bo pattern. Con `files/ke-hoach/` co 292 de tai da qua cua loc noi dung.

Nen: dem tren 292 de tai, khong dem tren 32 kich ban.

## Cach xep

Moi de tai duoc gan MOT y nghia hinh - la cau hoi ma canh mo phong cua no phai
tra loi. Xep theo NGUYEN NHAN bug xuat hien, khong xep theo cong nghe: "cron
chay 3 instance", "rate limit dem trong RAM", "session trong RAM" khac nhau ve
cong nghe nhung CUNG MOT hinh - N ban sao, moi ban mot gia tri.

`khong_mo_phong` la nhung de tai truot Cua 2 cua Y-TUONG.md: khong co dai luong
nao dang doi, nen lam o tool nay cung khong hon mot video nguoi noi.

## Ban xep nay la MOT LUOT DOC, khong phai mot phep do

Do la gioi han phai ghi ro. Toi doc tung de tai roi gan nhan bang tay, nen bien
gioi giua vai nhom la lua chon chu khong phai su that - `so_huu` va `luong` chong
lan o nhung de tai ve phan quyen theo tang, `tich_tu` va `theo_quy_mo` chong lan
o nhung de tai ve dung luong. Con so tong thi on dinh, con +-3 giua hai nhom
canh nhau thi khong.
"""
import json
import os
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 16 y nghia hinh, va loai canh cua `bench` phuc vu no ------------------
Y_NGHIA = {
    "dong_thoi":     ("KHI NÀO — hai việc chồng thời gian", "gantt"),
    "theo_quy_mo":   ("BAO NHIÊU Ở MỖI MỨC — theo cỡ/tham số", "cot"),
    "so_huu":        ("AI THẤY GÌ — ranh giới, phạm vi", "— CHƯA CÓ"),
    "luong":         ("Ở ĐÂU — đi qua tầng nào, dừng ở đâu", "topology"),
    "ban_sao":       ("MỖI BẢN SAO GIỮ GÌ — N instance", "ban_sao"),
    "phu_thuoc":     ("CÁI NÀO CHỜ CÁI NÀO — bậc thang", "thac"),
    "danh_doi":      ("HAI VẾ — chọn cái nào, mất gì", "compare"),
    "tich_tu":       ("DỒN Ứ — vào nhiều hơn ra", "queue"),
    "trung_nhau":    ("NHIỀU CÁI RA MỘT — trùng, đè", "gop"),
    "doi_trang_thai": ("ĐỔI TỪ GÌ SANG GÌ — v1 → v2", "gantt readout / counters"),
    "thoi_gian":     ("SỐNG BAO LÂU — hết hạn, TTL", "counters / — CHƯA ĐỦ"),
    "nhan_ban":      ("MỘT THÀNH N — bung ra", "multiply"),
    "bien_doi":      ("VÀO RA KHÁC KIỂU — encode, chuẩn hoá", "— CHƯA CÓ"),
    "that_bai":      ("HỎNG MỘT NỬA — mất giữa đường", "— CHƯA CÓ"),
    "nguong":        ("CHẠM TRẦN — giới hạn, hạn mức", "cot + nguong"),
    "khong_mo_phong": ("(trượt Cửa 2 — không có gì đang đổi)", "—"),
}

# --- Ban xep 292 de tai ----------------------------------------------------
XEP = {
    "so_huu": [1, 9, 14, 21, 36, 96, 99, 100, 110, 119, 126, 129, 130, 133,
               236, 242, 252, 255, 256, 261, 264, 269, 270, 271, 284],
    "dong_thoi": [2, 26, 33, 37, 41, 68, 74, 75, 76, 77, 82, 87, 134, 135,
                  147, 148, 169, 184, 212, 225, 226, 229, 232],
    "thoi_gian": [3, 5, 6, 13, 45, 54, 80, 94, 98, 136, 144, 193, 238, 268],
    "danh_doi": [4, 18, 25, 38, 44, 47, 55, 57, 58, 65, 70, 101, 111, 115,
                 117, 150, 159, 161, 183, 188, 192, 239, 246, 253, 254, 263,
                 265, 272],
    "luong": [7, 10, 16, 22, 48, 56, 93, 102, 114, 120, 127, 128, 132, 152,
              154, 164, 165, 199, 205, 237, 243, 244, 245, 247, 248, 250,
              262, 279],
    "ban_sao": [8, 20, 49, 64, 67, 84, 103, 109, 138, 153, 166, 171, 197,
                207, 223, 227, 228, 233, 257, 260, 278, 289],
    "theo_quy_mo": [11, 24, 50, 51, 53, 62, 69, 107, 116, 121, 158, 162, 177,
                    179, 182, 186, 194, 196, 200, 209, 210, 211, 214, 216,
                    219, 234, 249, 276],
    "nguong": [15, 34, 88, 113, 122, 181, 187, 195, 217, 290],
    "trung_nhau": [17, 29, 86, 91, 141, 142, 145, 146, 178, 180, 230, 258],
    "doi_trang_thai": [19, 27, 39, 40, 106, 139, 140, 163, 170, 191, 266, 275],
    "tich_tu": [23, 61, 72, 81, 89, 95, 112, 124, 143, 215, 220, 224, 274, 285],
    "nhan_ban": [12, 31, 42, 43, 52, 60, 125, 131, 190, 206, 222],
    "that_bai": [32, 46, 78, 79, 85, 90, 97, 104, 105, 118, 173, 259, 283],
    "phu_thuoc": [73, 83, 92, 108, 137, 155, 157, 168, 174, 185, 189, 213,
                  218, 221, 231, 240, 241, 251, 273],
    "bien_doi": [63, 71, 277, 280, 281, 282, 288, 292],
    "khong_mo_phong": [28, 30, 35, 59, 66, 123, 149, 151, 156, 160, 167, 172,
                       175, 176, 198, 201, 202, 203, 204, 208, 235, 267, 286,
                       287, 291],
}

# So da lam roi, de biet nhom nao da co kinh nghiem thuc te
DA_LAM = {177: 91, 178: 92, 179: 93, 180: 94, 181: 95, 182: 96, 184: 97,
          185: 98, 186: 99}


def kiem():
    """Moi de tai xep dung MOT lan, va khong sot de tai nao."""
    het = [n for ds in XEP.values() for n in ds]
    d = Counter(het)
    trung = {k: v for k, v in d.items() if v > 1}
    thieu = [n for n in range(1, 293) if n not in d]
    la = [n for n in d if not 1 <= n <= 292]
    return trung, thieu, la


def main():
    trung, thieu, la = kiem()
    if trung or thieu or la:
        print("!! BAN XEP CHUA KHOP")
        if trung:
            print(f"   xep hai lan: {sorted(trung)}")
        if thieu:
            print(f"   chua xep ({len(thieu)}): {sorted(thieu)}")
        if la:
            print(f"   so la: {sorted(la)}")
        return 1

    tong = sum(len(v) for v in XEP.values())
    mp = tong - len(XEP["khong_mo_phong"])
    print(f"BAN DO PHU HINH ANH — {tong} chủ đề, {mp} mô phỏng được "
          f"({mp / tong:.0%})\n")
    print(f"{'ý nghĩa hình':17} {'số':>4} {'%':>5}  {'câu hỏi của cảnh':46} "
          f"loại cảnh")
    print("-" * 112)
    for ten, ds in sorted(XEP.items(), key=lambda kv: -len(kv[1])):
        hoi, canh = Y_NGHIA[ten]
        n = len(ds)
        da = sum(1 for x in ds if x in DA_LAM)
        ghi = f"  ({da} đã làm)" if da else ""
        print(f"{ten:17} {n:>4} {n / tong:>5.0%}  {hoi:46} {canh}{ghi}")

    print("\n--- CHỖ RENDERER CÒN THIẾU, xếp theo số chủ đề ---")
    for ten, ds in sorted(XEP.items(), key=lambda kv: -len(kv[1])):
        hoi, canh = Y_NGHIA[ten]
        if "CHƯA" in canh:
            print(f"  {len(ds):>3} chủ đề   {ten:16} {hoi}")

    if "--chi-tiet" in sys.argv:
        with open(os.path.join(ROOT, "build", "de_tai.json"),
                  encoding="utf-8") as f:
            ten_de = {int(r[0]): r[1] for r in json.load(f)}
        for ten, ds in sorted(XEP.items(), key=lambda kv: -len(kv[1])):
            print(f"\n=== {ten}  ({len(ds)}) — {Y_NGHIA[ten][0]}")
            for n in sorted(ds):
                so = f"  [số {DA_LAM[n]}]" if n in DA_LAM else ""
                print(f"   {n:>3}  {ten_de.get(n, '?')[:74]}{so}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
