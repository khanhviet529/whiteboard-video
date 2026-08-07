"""Sinh KHUNG screenplay cho ca 90 so tu bang trong KE-HOACH-90.md.

    py research/sinh_khung.py            # sinh nhung file chua co
    py research/sinh_khung.py --lai      # ghi de tat ca (mat cong da viet!)

## Vi sao co file nay, va vi sao no KHONG viet noi dung

82 kich ban con lai, moi cai chung 45 phut viet va soi, la khoang 60 gio. Viet
mot mach cho du thi phan lon se phai dien SO BIA, vi so do cua chung chua ton
tai. Ma so bia thi dung thu quy tac goc cua kenh cam, va trong mot buoi da co
hai lan so sai lot vao kich ban that:

  - bo do Python chay luc may dang render -> lech 5 lan
  - bo do postgres dao 23-90 lan qua nam luot, khong du on dinh de cong bo

File nay lam phan CO CHE: khung canh, ten file, brand, cau hinh giong, va mot
o trong `{{SO}}` o dung nhung cho can so do. Phan CON NGUOI - loi doc, cach ke,
cho lat bai - van phai viet tay.

## Cai chan

Moi khung sinh ra deu co `chua_xong: true`. `lint.py` bao LOI neu thay khoa do
hoac thay `{{SO}}` con sot, nen mot khung khong the lot vao ban render duoc.
Xoa `chua_xong` la viec cuoi cung nguoi viet lam, sau khi da co so that.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KE_HOACH = os.path.join(ROOT, "KE-HOACH-90.md")
RA = os.path.join(ROOT, "screenplays")

# Mua -> (ten hien thi, he nhan dien, khung canh mac dinh)
MUA = {
    1: ("HIỆN TRƯỜNG · HỒ SƠ", "hien_truong",
        ["probe", "statement", "compare", "list", "gantt", "statement",
         "rule", "ask"]),
    2: ("TÔI TƯỞNG TÔI BIẾT · SỐ", "giang_duong",
        ["statement", "probe", "compare", "list", "gantt", "statement",
         "rule", "ask"]),
    3: ("HAI ĐOẠN CODE · SỐ", "hien_truong",
        ["code", "probe", "compare", "statement", "rule", "ask"]),
    4: ("CƠ CHẾ BÊN DƯỚI · SỐ", "hien_truong",
        ["intro", "probe", "topology", "compare", "statement", "rule", "ask"]),
    5: ("FRONTEND · SỐ", "giang_duong",
        ["probe", "statement", "compare", "list", "multiply", "rule", "ask"]),
    6: ("CÔNG CỤ · SỐ", "hien_truong",
        ["probe", "statement", "compare", "rule", "ask"]),
}
RANH = {1: (1, 20), 2: (21, 35), 3: (36, 50), 4: (51, 65), 5: (66, 80),
        6: (81, 90)}

# Chuong theo tung mua - dat ten khac nhau de mua doc khac nhau
CHUONG = {
    1: ["HIỆN TRƯỜNG", "HIỆN TRƯỜNG", "HIỆN TRƯỜNG", "HIỆN TRƯỜNG",
        "QUAY CHẬM", "THỦ PHẠM", "CHẶN", "CÒN LẠI"],
    2: ["BẠN TIN GÌ", "PHẦN CÒN LẠI", "PHẦN CÒN LẠI", "PHẦN CÒN LẠI",
        "QUAY CHẬM", "RANH GIỚI", "CHẶN", "CÒN LẠI"],
    3: ["CHỌN ĐI", "CHẠY THẬT", "VÌ SAO", "VÌ SAO", "CHẶN", "CÒN LẠI"],
    4: ["MỞ MÀN", "CHẠY THẬT", "BÊN TRONG", "VÌ SAO", "CHỖ LẠ", "DÙNG ĐƯỢC GÌ",
        "CÒN LẠI"],
    5: ["HIỆN TRƯỜNG", "HIỆN TRƯỜNG", "VÌ SAO", "HIỆN TRƯỜNG", "QUAY CHẬM",
        "CHẶN", "CÒN LẠI"],
    6: ["HIỆN TRƯỜNG", "VÌ SAO", "VÌ SAO", "CHẶN", "CÒN LẠI"],
}


def doc_ke_hoach():
    """Doc bang 90 dong. Tra ve [(so, chu_de, ghi_chu, do_bang)]."""
    s = io.open(KE_HOACH, encoding="utf-8").read()
    ra = []
    for m in re.finditer(r"^\| (\d{2}) \| (.+?) \| (.+?) \| (.+?) \| (.+?) \|",
                         s, re.M):
        so, chu_de, ghi, so_lieu, do_bang = (x.strip() for x in m.groups())
        ra.append((int(so), chu_de, ghi, so_lieu, do_bang.strip("` ")))
    return ra


def ten_file(so, chu_de):
    t = re.sub(r"[`*~]", "", chu_de).lower()
    t = re.sub(r"[^a-z0-9à-ỹ ]+", " ", t)
    import unicodedata
    t = "".join(c for c in unicodedata.normalize("NFD", t)
                if not unicodedata.combining(c)).replace("đ", "d")
    t = "-".join(t.split())[:34].strip("-")
    return f"{so:02d}-{t}.yaml"


def mua_cua(so):
    for m, (a, b) in RANH.items():
        if a <= so <= b:
            return m
    return 1


def khung(so, chu_de, ghi, so_lieu, do_bang):
    m = mua_cua(so)
    ten_mua, he, canh = MUA[m]
    ch = CHUONG[m]
    d = []
    d.append(f"# SO {so:02d} - MUA {m}. Xem KE-HOACH-90.md.")
    d.append(f"#   chu de   : {chu_de[:96]}")
    d.append(f"#   ghi chu  : {ghi[:96]}")
    d.append(f"#   do bang  : {do_bang}   (muc: {so_lieu})")
    d.append("#")
    d.append("# KHUNG TU SINH boi research/sinh_khung.py. Chua viet loi doc,")
    d.append("# chua co so do. `chua_xong: true` chan khong cho render.")
    d.append("#")
    d.append("# Viec phai lam, theo thu tu:")
    d.append(f"#   1. chay bo do `{do_bang}`, lay so THAT (may phai ranh)")
    d.append("#   2. thay moi `{{SO}}` bang so do duoc")
    d.append("#   3. viet `narration` va `caption` cho tung canh")
    d.append("#   4. doi chuoi canh neu co che nay hop loai khac (xem README)")
    d.append("#   5. xoa dong `chua_xong` o duoi")
    d.append("")
    d.append("chua_xong: true       # XOA dong nay khi da co so that")
    d.append("")
    # Bat buoc boc nhay: chu de trong ke hoach co dau backtick va dau hai
    # cham (`COUNT(*)` la thu cham nhat trang), ca hai deu vo YAML.
    def nhay(t):
        return "'" + str(t).replace("'", "''") + "'"
    d.append(f"title: {nhay(chu_de)}")
    d.append("theme: bench")
    if he != "hien_truong":
        d.append(f"he: {he}")
    d.append("accent: hot")
    d.append(f"brand: {nhay(f'{ten_mua} {so:02d}')}")
    d.append(f"tag: {nhay(do_bang + ' · chưa xong')}")
    d.append("footer: '{{SO}}'")
    d.append("voice: female")
    d.append('rate: "+16%"')
    d.append("")
    d.append("omni_voice: namtre_v3")
    d.append("style: camhung")
    d.append("mode: tach")
    d.append("phien_am: true")
    d.append("")
    d.append("pause_scale: 0.70")
    d.append("speed: 1.03")
    d.append("pre_pad: 0.35")
    d.append("post_pad: 0.55")
    d.append("")
    d.append("scenes:")
    for i, c in enumerate(canh):
        d.append(f"  - scene: {c}")
        d.append(f"    chapter: {ch[i] if i < len(ch) else 'CÒN LẠI'}")
        d.append("    head: '{{SO}}'")
        d.append("    narration: '{{SO}}'")
        d.append("    caption: '{{SO}}'")
        d.append("")
    return "\n".join(d) + "\n"


def main():
    lai = "--lai" in sys.argv
    rows = doc_ke_hoach()
    moi = bo = 0
    for so, chu_de, ghi, so_lieu, do_bang in rows:
        p = os.path.join(RA, ten_file(so, chu_de))
        # da co kich ban that cho so nay thi khong dung toi
        if any(f"SO {so:02d} -" in io.open(os.path.join(RA, f),
                                           encoding="utf-8").read()[:200]
               for f in os.listdir(RA) if f.endswith(".yaml")) and not lai:
            pass
        if os.path.exists(p) and not lai:
            bo += 1
            continue
        io.open(p, "w", encoding="utf-8").write(
            khung(so, chu_de, ghi, so_lieu, do_bang))
        moi += 1
    print(f"sinh {moi} khung moi, bo qua {bo} file da co")
    print(f"tat ca deu co `chua_xong: true` nen lint.py chan khong cho render")


if __name__ == "__main__":
    main()
