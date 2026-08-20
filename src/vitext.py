"""
Chuan bi van ban tieng Viet truoc khi dua vao TTS.

Dau cau la don bay manh nhat cho nhip ngat nghi va duong ngu dieu - manh hon
moi tham so cua model. Module nay lam ba viec:

  1. Doc so, viet tat, ky hieu thanh chu (model doc "40%" khong dung)
  2. Chuan hoa dau cau, chen dau phay o ranh gioi menh de de co cho nghi
  3. Tach van ban dai thanh tung cau -> sinh rieng roi noi lai, giu duoc nhip

Khong dung thu vien ngoai: WeTextProcessing khong ho tro tieng Viet.
"""
import re

# --- 1. So sang chu -------------------------------------------------------

DV = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]


def _under_thousand(n, full=False):
    """full=True khi con so nay dung sau mot nhom khac (phai doc du 'khong tram')."""
    out = []
    tram, du = divmod(n, 100)
    chuc, dv = divmod(du, 10)

    if tram or full:
        out += [DV[tram], "trăm"]
    if chuc == 0:
        if dv and (tram or full):
            out += ["lẻ", DV[dv]]
        elif dv:
            out += [DV[dv]]
    elif chuc == 1:
        out += ["mười"]
        if dv == 5:
            out += ["lăm"]
        elif dv:
            out += [DV[dv]]
    else:
        out += [DV[chuc], "mươi"]
        if dv == 1:
            out += ["mốt"]
        elif dv == 4:
            out += ["tư"]
        elif dv == 5:
            out += ["lăm"]
        elif dv:
            out += [DV[dv]]
    return " ".join(out)


def num_to_words(n):
    n = int(n)
    if n == 0:
        return "không"
    if n < 0:
        return "âm " + num_to_words(-n)

    groups = []  # (gia tri, ten don vi) tu lon xuong nho
    for div, name in ((10**9, "tỷ"), (10**6, "triệu"), (10**3, "nghìn")):
        q, n = divmod(n, div)
        groups.append((q, name))
    groups.append((n, ""))

    # Nhom rong bo han: 1.500.000.000 -> "mot ty nam tram trieu", KHONG doc
    # "khong tram nghin". Trong mot nhom khac 0 thi van doc du ("mot nghin
    # khong tram nam muoi") nen can biet da co nhom nao dung truoc chua.
    parts, started = [], False
    for val, name in groups:
        if val == 0:
            continue
        parts.append((_under_thousand(val, full=started) + " " + name).strip())
        started = True
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def _decimal(m):
    whole, frac = m.group(1), m.group(2)
    w = num_to_words(whole.replace(".", "").replace(",", ""))
    f = " ".join(DV[int(c)] for c in frac)
    return f"{w} phẩy {f}"


# --- 2. Viet tat / ky hieu ------------------------------------------------

ABBR = {
    "%": " phần trăm",
    "&": " và ",
    "+": " cộng ",
    "=": " bằng ",
    "@": " a còng ",
    "₫": " đồng",
    "$": " đô la",
    "°C": " độ C",
    "km/h": " ki lô mét trên giờ",
    "km": " ki lô mét",
    "kg": " ki lô gam",
    "cm": " xen ti mét",
    "mm": " mi li mét",
    "ml": " mi li lít",
    "mg": " mi li gam",
    "TP.": "thành phố ",
    "TP ": "thành phố ",
    "Q.": "quận ",
    "P.": "phường ",
    "vd:": "ví dụ:",
    "VD:": "ví dụ:",
    "v.v.": "vân vân.",
    "vv.": "vân vân.",
}


def expand(text):
    for k, v in ABBR.items():
        text = text.replace(k, v)

    # 1.234.567 hoac 1,234,567 -> bo dau phan cach nhom
    text = re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", text)
    # thap phan: 3,5 hoac 3.5
    text = re.sub(r"\b(\d+)[.,](\d+)\b", _decimal, text)
    # so nguyen con lai
    text = re.sub(r"\b\d+\b", lambda m: num_to_words(m.group()), text)
    return text


# --- 3. Dau cau va ranh gioi menh de --------------------------------------

# Cac tu mo dau menh de: chen dau phay TRUOC chung de co cho lay hoi.
# CHI dua vao day nhung tu gan nhu LUON la lien tu. Cac tu vua la lien tu vua la
# tu thuong ("mà", "còn", "hay") bi loai - chung gay cat vun sai cho:
# "chỉ còn ba ngày" khong duoc thanh "chỉ, còn ba ngày".
#
# DA LOAI THEM (2026-08-04), deu vi la mot phan cua CUM TU CO DINH:
#   "đồng thời"   -> "khả năng xử lý đồng thời" bi cat thanh "xử lý, đồng thời";
#                    "gần như đồng thời" thanh "gần như, đồng thời". SAI NGHIA.
#   "nhất là"     -> "quan trọng nhất là X" thanh "quan trọng nhất, là X"
#   "kết quả là"  -> "kết quả là 70" thanh "kết quả, là 70"
#   "đặc biệt là" -> "món đặc biệt là X" thanh "món đặc biệt, là X"
CONNECTIVES = [
    "nhưng", "tuy nhiên", "thế nhưng", "vì vậy", "vì thế", "do đó",
    "cho nên", "bởi vậy", "ngoài ra", "bên cạnh đó", "trong khi đó",
    "thậm chí",
]

# Cac tu mo dau cau -> them dau phay SAU chung.
OPENERS = [
    "vì vậy", "vì thế", "do đó", "tuy nhiên", "ngoài ra", "bên cạnh đó",
    "trước tiên", "đầu tiên", "cuối cùng", "thật ra", "thực tế",
    "nói cách khác", "đặc biệt", "hơn nữa", "tất nhiên",
]


# Do dai toi thieu cua ve truoc thi moi chen dau phay - tranh cat vun cau ngan.
MIN_CLAUSE = 14

_OPENER_RE = re.compile(
    r"(^|(?<=[.!?…])\s+)(" + "|".join(re.escape(w) for w in sorted(OPENERS, key=len, reverse=True)) + r")\s+(?![,])",
    re.IGNORECASE,
)
_CONN_RE = re.compile(
    r"\s+(" + "|".join(re.escape(w) for w in sorted(CONNECTIVES, key=len, reverse=True)) + r")\s+",
    re.IGNORECASE,
)


def punctuate(text):
    """Chen dau phay o ranh gioi menh de de model co cho ngat nghi."""
    t = re.sub(r"\s+", " ", text.strip())

    # Sau tu mo dau cau. Giu nguyen chu hoa/thuong cua ban goc.
    t = _OPENER_RE.sub(lambda m: f"{m.group(1)}{m.group(2)}, ", t)

    # Truoc lien tu noi hai menh de - chi chen khi ve truoc du dai, tinh tu
    # dau cau hoac dau phay gan nhat chu khong phai tu mot tu don le.
    def conn(m):
        head = t[: m.start()]
        clause = re.split(r"[.!?…,]", head)[-1].strip()
        if len(clause) < MIN_CLAUSE:
            return m.group(0)
        return f", {m.group(1)} "

    t = _CONN_RE.sub(conn, t)

    t = re.sub(r"\s*,\s*", ", ", t)
    t = re.sub(r",\s*(?=[,.!?…])", "", t)
    t = re.sub(r",\s*,+", ", ", t)
    t = re.sub(r"\s+([.!?…:;])", r"\1", t)
    t = re.sub(r"([.!?…])(?=[^\s])", r"\1 ", t)
    return re.sub(r"\s+", " ", t).strip()


# --- 4. Tach cau ----------------------------------------------------------

def split_sentences(text, max_chars=180):
    """Tach thanh tung cau. Cau qua dai thi cat tiep o dau phay."""
    parts = re.split(r"(?<=[.!?…])\s+", text.strip())
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        if len(p) <= max_chars:
            out.append(p)
            continue
        # Cat o dau phay, gom lai cho gan max_chars
        buf = ""
        for seg in re.split(r"(?<=,)\s+", p):
            if buf and len(buf) + len(seg) + 1 > max_chars:
                out.append(buf.strip())
                buf = seg
            else:
                buf = f"{buf} {seg}".strip()
        if buf:
            out.append(buf.strip())
    # Viet hoa chu dau moi cau cho nhat quan.
    return [s[0].upper() + s[1:] if s else s for s in out]


def prepare(text, do_expand=True, do_punctuate=True):
    """Pipeline day du: so->chu, chen dau phay, tra ve danh sach cau."""
    t = expand(text) if do_expand else text
    t = punctuate(t) if do_punctuate else t
    return split_sentences(t)


if __name__ == "__main__":
    demo = (
        "Giảm 40% hôm nay! Sản phẩm chứa 2,5 ml tinh chất và 1.200 mg vitamin C "
        "nhưng giá chỉ 199.000₫. Vì vậy bạn đừng bỏ lỡ vd: ưu đãi này chỉ còn 3 ngày."
    )
    print("GOC:\n ", demo, "\n")
    print("SAU XU LY:")
    for i, s in enumerate(prepare(demo), 1):
        print(f"  {i}. {s}")
