"""Phien am tu viet tat va tu tieng Anh TRUOC khi gui cho model doc.

Van de: `mode: tach` sinh TUNG CAU mot lan goi model rieng, nen cung mot tu nam
o hai cau khac nhau la hai lan model tu quyet cach doc doc lap. Dem tren bon
screenplay hien co: "database" xuat hien 12 lan, "request" 11 lan, "cache" 9
lan. Dau video doc khac cuoi video, va khong co gi bao.

Truoc day phai viet phien am THANG vao `narration` roi giu chu goc o `caption` -
chep tay hai lan va rat de quen. File nay bo cai do: screenplay viet "API" nhu
binh thuong, con doan doc duoc chuyen thanh "ây pi ai" ngay truoc khi goi model.

## Ba dieu phai nho

1. Phien am ap TRUOC KHI TINH KHOA CACHE. Neu ap sau thi sua tu dien ma khoa
   khong doi, render sau dung lai audio cu va thay doi khong co tac dung nao -
   dung cai bay ma `speed` trong speak.py da vap.

2. Bat theo TUNG SCREENPLAY (`phien_am: true`). Ba screenplay da duyet dang
   chua san "ây pi ai" nen khong con chu "API" nao de luat khop; nhung "database"
   thi dang nam tran, bat lop nay len se doi khoa va sinh lai audio DA DUYET.

3. Chi them mot tu vao `TU_DIEN` SAU KHI NGHE NO HONG. Viet tat thi model chac
   chan doc sai nen phien am manh tay. Tu tieng Anh thuong nhu "cache", "log",
   "request" thi model doc tam duoc, ep phien am vao co khi nghe gia hon. Cac
   ung vien chua kiem nam o `TU_DIEN_THU` va KHONG duoc ap.
"""
import re
import unicodedata

# Ten chu cai tieng Anh viet theo chinh ta tieng Viet. Bang nay KHONG duoc dung
# de tu dong bung moi viet tat - no chi de suy ra muc moi cho `TU_DIEN` cho nhat
# quan. Suy tu ba muc da co san trong du an:
#   HTTP = "hát ti ti pi"   ORM = "ô a em"   API = "ây pi ai"   TTL = "ti ti eo"
CHU_CAI = {
    "A": "ây", "B": "bi", "C": "xi", "D": "đi", "E": "i", "F": "ép",
    "G": "gi", "H": "hát", "I": "ai", "J": "giây", "K": "kê", "L": "eo",
    "M": "em", "N": "en", "O": "ô", "P": "pi", "Q": "kiu", "R": "a",
    "S": "ét", "T": "ti", "U": "diu", "V": "vi", "W": "đắp liu",
    "X": "ích", "Y": "quai", "Z": "dét",
}


def danh_van(tu):
    """Bung mot viet tat thanh ten tung chu cai. Dung khi THEM muc moi, khong
    dung luc chay - moi muc trong TU_DIEN phai la mot lua chon co y thuc."""
    return " ".join(CHU_CAI.get(c.upper(), c) for c in tu if c.isalnum())


# --- TU DIEN DANG AP -------------------------------------------------------
# Moi muc o day la mot quyet dinh, khong phai suy ra may moc. Viet tat thi model
# doc sai gan nhu chac chan nen vao thang; tu tieng Anh thuong phai nghe hong roi
# moi duoc vao.
TU_DIEN = {
    # --- viet tat: model doc sai gan nhu chac chan
    "API": "ây pi ai",
    "ORM": "ô a em",
    "TTL": "ti ti eo",
    "SQL": "ét kiu eo",
    "CPU": "xi pi diu",
    "RAM": "ram",
    "URL": "diu a eo",
    "HTTP": "hát ti ti pi",
    "HTTPS": "hát ti ti pi ét",
    "JSON": "giây sơn",
    "UUID": "diu diu ai đi",
    "DNS": "đi en ét",
    "TCP": "ti xi pi",
    "SDK": "ét đi kê",
    "CDN": "xi đi en",
    "OK": "ô kê",
    "IO": "ai ô",
    "ID": "ai đi",
    "GIL": "gi ai eo",
    "WAL": "đắp liu ây eo",
    "MVCC": "em vi xi xi",
    "LRU": "eo a diu",
    "CRUD": "cờ rớt",
    # Nhom BAM VA BI MAT (mua 7). Ca nam muc deu la VIET TAT, tuc dung dien
    # nguoi ta noi o dau bang nay: "viet tat thi model doc sai gan nhu chac
    # chan nen phien am manh tay". Suy theo dung bang `CHU_CAI`, kiem lai bang
    # `danh_van()`:
    #   MD5     = em(M) di(D) nam(5)
    #   SHA     = et(S) hat(H) ay(A)
    #   HMAC    = hat(H) em(M) ay(A) xi(C)
    # DAI TRUOC NGAN SAU da duoc `_bien()` lo, nen "SHA-256" khong bi "SHA"
    # nuot mat phan so.
    "MD5": "em đi năm",
    "SHA-256": "ét hát ây hai năm sáu",
    "SHA-1": "ét hát ây một",
    "SHA": "ét hát ây",
    "HMAC": "hát em ây xi",
    # --- ky hieu doc thanh chu
    "N+1": "en cộng một",
    "%": "phần trăm",
    # --- tu tieng Anh DA NGHE va da chot. Chi nhung tu nguoi dung nghe thay
    #     ban phien am RO HON moi nam o day; xem `research/bo_chuan_giong.py`.
    "cache": "két",
    "index": "in đét",
    "pool": "pun",
    "timeout": "tai mao",
    "list": "lít",
    # Nguoi dung nghe ra o so 72 canh 2 ("khong mot dong log do"): tu ngan,
    # la, nam giua dong chay tieng Viet -> model tu doan cach doc.
    "log": "lốc",
    # Sau tu duoi day chi NGHE chu khong hien tren man hinh, nen phien am theo
    # cach dan trong nghe doc. Da nghe kiem mot luot o `out/thu-tu/`. Hai ung
    # vien cua cung luot do bi bac: `javascript` va `production`, xem GIU_GOC.
    "email": "i meo",
    "code": "cốt",
    "python": "pai thon",
    "file": "phai",
    "test": "tét",
    "review": "ri viu",
    # `is` la chu de chinh cua so 54 nen no duoc doc rat nhieu lan. Hai ky tu,
    # tu la -> dung cai bay cua `log`. "ít" la cach dan trong noi. CHUA co tai
    # nguoi xac nhan, nghe o bo chuan luot sau truoc khi render so 54.
    "is": "ít",
}

# --- UNG VIEN, CHUA AP -----------------------------------------------------
# `research/bo_chuan_giong.py` sinh ca hai cach doc de nghe doi chieu. Nghe xong
# thay cach phien am ro hon thi chuyen muc do sang TU_DIEN, thay khong hon thi
# xoa han - dung de o day lung lung.
TU_DIEN_THU = {
    # `eager load` chua co khung cau trong bo chuan nen chua duoc nghe. Them
    # khung vao `research/bo_chuan_giong.py` roi chay lai moi quyet dinh duoc.
    "eager load": "i gờ lâu",
    # Nam muc `Python`, `code`, `test`, `file`, `email` tung nam o day da duoc
    # nghe va chuyen han sang TU_DIEN, khong con lap lai o duoi nua.
}

# --- DA NGHE va QUYET DINH GIU NGUYEN CHU GOC ------------------------------
# Ghi lai de nguoi sau khong thu lai: nguoi dung da nghe doi chieu tung cap va
# thay ban goc ro bang hoac ro hon. Ep phien am vao mot tu model von doc dung
# chi lam no nghe gia.
#
# `database` dang chu y: thuoc do noi ban phien am RO HON HAN (5,66 so voi 3,49
# khoi/giay, ban goc con bi gan co DINH-AM), va chinh nguoi dung la nguoi de
# xuat "đa ta bây" luc dau. Nghe that thi ho chon ban goc. Day la lan thu ba
# trong du an nay tai nguoi khong dong y voi thuoc do, va ca ba lan tai deu la
# ben quyet dinh.
GIU_GOC = ("database", "nginx", "query", "redis", "request", "transaction",
           "worker",
           # `set` giu goc con `list` thi phien am, du hai tu doi nhau va deu
           # nam trong cung mot cau. Nguoi dung nghe tung cap va chon nhu vay.
           # Thuoc do cung nghieng ve ban goc cua `set`: ban phien am sinh them
           # mot lo 120ms ma ban goc khong co.
           "set",
           # Ba tu nay HIEN TREN MAN HINH duoi dang code (None, .lower(),
           # EXPLAIN) nen loi doc phai khop voi chu nguoi xem dang nhin.
           "none", "lower", "explain",
           # `javascript` tung duoc phien am thanh "gia va sơ críp" va nguoi
           # xem nghe ra tieng nhieu ngay: `críp` KHONG PHAI am tiet tieng
           # Viet (khong co phu am dau `cr`), nen model phai phat ra mot thu
           # nam ngoai von am cua no - dung cai loi ma tu dien sinh ra de
           # chua. Giu chu goc: canh 3 so 72 tung doc "JavaScript" khong
           # phien am va khong ai keu.
           "javascript",
           # `production` tung duoc phien am thanh "pờ rô đắc sần" - hop le
           # ve am tiet nhung bon am cho mot tu, nghe le the. Nguoi dung chon
           # giu chu goc, cung cach da chon cho `database` va `set`.
           "production",
           # `join` hien tren man hinh trong doan code `"".join(...)` nen loi
           # doc phai khop voi chu nguoi xem dang nhin - cung luat voi `none`.
           "join")

# CHO HO DA BIET: `la_am_tiet_viet` nhan nham vai tu tieng Anh la am tiet Viet
# hop le, vi no chi kiem phu am dau va phu am cuoi chu khong kiem phan van.
# Da thay: `key` va `set`. Ca hai deu doc ra tam duoc nen chua chua; nhung
# `check_tu_la` trong lint.py se KHONG bat duoc nhung tu kieu do.


def _boundary(tu):
    """Bien tu thanh mau khop khong dinh vao tu khac.

    Khong dung `\\b` duoc: `N+1` va `%` co ky tu khong phai chu, `\\b` xu ly
    chung khac han va cho ket qua sai o hai dau.
    """
    lo = re.escape(tu)
    dau = r"(?<![0-9A-Za-z])" if tu[0].isalnum() else ""
    cuoi = r"(?![0-9A-Za-z])" if tu[-1].isalnum() else ""
    return dau + lo + cuoi


def _bien(tu_dien):
    # DAI TRUOC NGAN SAU: khong thi "SQL" nuot mat "MySQL", "HTTP" nuot "HTTPS".
    khoa = sorted(tu_dien, key=len, reverse=True)
    return re.compile("|".join(_boundary(k) for k in khoa), re.IGNORECASE)


_RE = _bien(TU_DIEN) if TU_DIEN else None
_TRA = {k.lower(): v for k, v in TU_DIEN.items()}


def phien_am(text, tu_dien=None):
    """Doi tu viet tat va tu tieng Anh sang cach doc. Mot luot, khong lap lai.

    Mot luot la co y: neu ap lai luot hai thi chu trong ban phien am co the lai
    khop mot luat khac va bien dang tiep.
    """
    if not text:
        return text
    rg, tra = (_RE, _TRA)
    if tu_dien is not None:
        rg = _bien(tu_dien) if tu_dien else None
        tra = {k.lower(): v for k, v in tu_dien.items()}
    if rg is None:
        return text

    def thay(m):
        ra = tra[m.group(0).lower()]
        # Viet hoa neu no dung dau cau, de ban phien am con doc duoc khi in ra.
        t = text[:m.start()].rstrip()
        if not t or t[-1] in ".!?…:":
            ra = ra[0].upper() + ra[1:]
        # Chen dau cach neu ky tu ke ben la chu hoac so. Bat buoc cho nhung muc
        # khong phai chu nhu `%`: "32%" ma noi thang thanh "32phần trăm" thi
        # model doc lien mot cuc.
        truoc = text[m.start() - 1] if m.start() else ""
        sau = text[m.end()] if m.end() < len(text) else ""
        if truoc.isalnum() and ra[0].isalnum():
            ra = " " + ra
        if sau.isalnum() and ra[-1].isalnum():
            ra = ra + " "
        return ra
    return rg.sub(thay, text)


# --- cho lint: tim tu Latin chua duoc khai -----------------------------------
#
# Cach lam DAU TIEN la mot danh sach trang cac am tiet tieng Viet khong dau. No
# hong ngay: `do` `di` `dang` `chia` `thanh` `khe` `chen` deu bi bao la tieng
# Anh, 8-16 canh bao moi screenplay ke ca ban da duyet. Linter keu nhieu thi bi
# bo qua, thanh vo dung - da vap dung loi do mot lan voi nguong cau ngan.
#
# Cach nay dung CAU TRUC AM TIET. Am tiet tieng Viet co dang: phu am dau (tap
# dong) + nguyen am + phu am cuoi (tap dong). Tu nao khong phan tich duoc theo
# khuon do thi chac chan khong phai tieng Viet.

DAU = ["ngh", "ng", "nh", "ch", "gh", "gi", "kh", "ph", "qu", "th", "tr",
       "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s",
       "t", "v", "x"]
CUOI = ["ngh", "ng", "nh", "ch", "c", "m", "n", "p", "t"]
NGUYEN_AM = set("aeiouy")


# Tu muon DA Viet hoa, model doc dung. Danh sach nay chi dai ra khi mot tu duoc
# XAC NHAN doc dung, khong them theo cam tinh.
DA_QUEN = {"mili", "kilo", "mega", "giga", "tera", "micro", "nano", "pico",
           "gam", "met", "lit"}


def la_am_tiet_viet(tu):
    """Tu nay co the la mot am tiet tieng Viet khong dau khong?

    Thu MOI phu am dau co the, ke ca khong co. Chi thu cai dai nhat thi hong:
    "gi" bi coi la phu am dau cua chinh no, con lai rong -> bao nham "gì" la
    tieng Anh. Trong "gì" thi `i` vua la mot phan phu am dau vua la nguyen am.

    Khong can dung 100%: mot vai tu tieng Anh lot qua ("can", "ban") thi linter
    im lang, chap nhan duoc. Cai KHONG chap nhan duoc la bao nham tu tieng Viet,
    vi no lam nguoi viet bo qua ca nhung canh bao that.
    """
    t = _khong_dau(tu)
    if not t or any(c in "fjwz" for c in t):
        return False
    if t in DA_QUEN:
        return True
    for d in [""] + DAU:
        if d and not t.startswith(d):
            continue
        r = t[len(d):]
        if not r or r[0] not in NGUYEN_AM:
            continue
        i = 0
        while i < len(r) and r[i] in NGUYEN_AM:
            i += 1
        if r[i:] == "" or r[i:] in CUOI:
            return True
    return False


def _khong_dau(tu):
    t = unicodedata.normalize("NFD", tu.lower())
    t = "".join(c for c in t if not unicodedata.combining(c))
    return t.replace("đ", "d")


def tu_la(text):
    """Tra ve cac tu KHONG phan tich duoc thanh am tiet tieng Viet va cung chua
    nam trong tu dien phien am.

    Day la nhung tu model se TU DOAN cach doc, ma `mode: tach` sinh tung cau doc
    lap nen moi cau doan mot kieu. Linter bao de nguoi viet ra quyet dinh: hoac
    them vao TU_DIEN, hoac chap nhan va ghi ro la chap nhan.
    """
    # GIU_GOC cung tinh la "da khai": nguoi dung da nghe va quyet dinh giu chu
    # goc, nen linter con bao nua la bao mot viec da xong.
    co = ({k.upper() for k in TU_DIEN} | {k.upper() for k in TU_DIEN_THU}
          | {k.upper() for k in GIU_GOC})
    ra = []
    for m in re.finditer(r"[A-Za-zÀ-ỹĐđ][A-Za-zÀ-ỹĐđ0-9_+]*", text):
        tu = m.group(0)
        if len(tu) < 2 or tu.upper() in co:
            continue
        if all(la_am_tiet_viet(x) for x in re.split(r"[-_]", tu) if x):
            continue
        ra.append(tu)
    return ra


# --- tu kiem: ban phien am phai la tieng Viet doc duoc -----------------------
#
# Ly do co ham nay: toi tung phien am `javascript` thanh "gia va so crip" va
# nguoi xem nghe ra tieng nhieu trong vong mot phut. `crip` khong phai am tiet
# tieng Viet - tieng Viet khong co phu am dau `cr`. Ban phien am cua toi tao ra
# DUNG CAI LOI ma tu dien nay sinh ra de chua: mot chuoi nam ngoai von am cua
# model, buoc no phai doan.
#
# Chay ngay luc nap module chu khong de trong lint, vi mot muc hong trong
# TU_DIEN lam hong MOI kich ban chua tu do - phai chet som chu khong canh bao.
def _tu_kiem():
    hong = []
    for goc, pa in TU_DIEN.items():
        xau = [w for w in pa.split() if not la_am_tiet_viet(w)]
        if xau:
            hong.append(f"{goc!r} -> {pa!r}: {xau} khong phai am tiet tieng Viet")
    if hong:
        raise ValueError(
            "TU_DIEN co ban phien am khong doc duoc bang tieng Viet:\n  "
            + "\n  ".join(hong)
            + "\nDoi ban phien am, hoac dua tu do vao GIU_GOC.")


_tu_kiem()
