"""Bo do dung chung cho MUA 7 - BAM VA BI MAT (nhom P cua kho chu de).

    py repro/bam_va_bi_mat.py              # chay het, in bang
    py repro/bam_va_bi_mat.py toc_do_bam   # chay mot ca

Vi sao mot bo do chung: cung ly do nhu `bench_python.py` - 10 script roi thi 10
cach do khac nhau va khong so sanh duoc voi nhau. O day moi ca khai mot ham
`ca_*` tra ve dict, phan in bang la chung.

Ba loai ca:

  TOC DO    hai cach lam, khac thoi gian
  DUNG SAI  hai cach lam, khac KET QUA - in ca hai de thay cai nao sai
  MOT VE    mot phep do khong co doi chung (so lan bam moi giay, do trung lap)

Cai gi KHONG do o day: khong co ca nao "pha" duoc SHA-256 hay bcrypt. Nhung con
so o day la SO LAN BAM MOI GIAY tren dung may nay, va no du de noi len dieu can
noi - phan con lai la nhan len bang phep chia, va phep chia thi nguoi xem tu
kiem duoc.
"""
import gc
import hashlib
import hmac
import os
import secrets
import statistics as st
import string
import sys
import time

LAP = 7

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _hieu_chuan import canh_bao, in_moc, kiem_may  # noqa: E402


def _vi(v):
    """1234567 -> "1.234.567".

    Ham rieng chu khong viet thang `f"{v:,}".replace(",", ".")` tai cho: cach do
    lam hong moi so co phan thap phan, vi no doi luon dau cham thap phan thanh
    dau nghin - "931,843.6" ra "931.843.6". Da in ra dung cai so do mot lan.
    """
    return f"{int(round(v)):,}".replace(",", ".")


def _do(ham, lap=LAP):
    ra = []
    gc.disable()
    try:
        for _ in range(lap):
            t0 = time.perf_counter()
            ham()
            ra.append(time.perf_counter() - t0)
    finally:
        gc.enable()
    return st.median(ra)


# ===================================================== 178. MD5 va SHA-1 vo
# Cap khoi 128 byte noi tieng cua Wang & Yu (2004). KHONG phai so bia: script
# tu kiem lai bang chinh hashlib, va neu hai md5 khong trung thi ca nay bao
# hong chu khong im lang tra ve so dep.
_MD5_A = bytes.fromhex(
    "d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89"
    "55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b"
    "d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0"
    "e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70")
_MD5_B = bytes.fromhex(
    "d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89"
    "55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b"
    "d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0"
    "e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70")


def ca_md5_trung():
    a, b = hashlib.md5(_MD5_A).hexdigest(), hashlib.md5(_MD5_B).hexdigest()
    lech = [i for i, (x, y) in enumerate(zip(_MD5_A, _MD5_B)) if x != y]
    bit = sum(bin(_MD5_A[i] ^ _MD5_B[i]).count("1") for i in lech)
    return dict(loai="dung sai",
                hoi="Hai tep 128 byte KHAC nhau, bam MD5 ra gi",
                a="md5(tệp A)", b="md5(tệp B)", ka=a, kb=b,
                them=[f"hai tep khac nhau o {len(lech)} byte, vi tri {lech}",
                      f"tong so BIT khac nhau: {bit} tren {len(_MD5_A) * 8}",
                      f"doan lech dau tien  A: {_MD5_A[16:24].hex()}",
                      f"                    B: {_MD5_B[16:24].hex()}",
                      f"md5 TRUNG NHAU: {a == b}",
                      f"sha256 trung nhau: {hashlib.sha256(_MD5_A).hexdigest() == hashlib.sha256(_MD5_B).hexdigest()}",
                      f"sha256(A) = {hashlib.sha256(_MD5_A).hexdigest()[:24]}...",
                      f"sha256(B) = {hashlib.sha256(_MD5_B).hexdigest()[:24]}..."])


# ===================================================== 179. nhanh la nhuoc diem
def ca_toc_do_bam():
    """So lan bam MOI GIAY cua tung ham, tren dung may nay.

    Day la con so quyet dinh ca mua: mot ham bam nhanh nghia la ke do mat khau
    thu duoc nhieu lan moi giay. Bam mat khau la cho duy nhat ma NHANH la xau.
    """
    import bcrypt
    mk = b"matkhau-cua-nguoi-dung-1"
    n_sha = 200_000

    def sha():
        for _ in range(n_sha):
            hashlib.sha256(mk).digest()

    t_sha = _do(sha, 3) / n_sha
    muoi = bcrypt.gensalt(rounds=12)
    t_bc = _do(lambda: bcrypt.hashpw(mk, muoi), 3)
    try:
        from argon2.low_level import Type, hash_secret_raw
        t_ar = _do(lambda: hash_secret_raw(
            mk, b"muoi-16-byte-abc", time_cost=3, memory_cost=65536,
            parallelism=4, hash_len=32, type=Type.ID), 3)
    except Exception as e:      # noqa: BLE001
        t_ar = None
        print(f"  (bo qua argon2: {e})")
    them = [f"sha256    {_vi(1 / t_sha):>15} lan/giay  ({t_sha * 1e9:.0f} ns moi lan)",
            f"bcrypt 12 {1 / t_bc:>15.1f} lan/giay  ({t_bc * 1000:.0f} ms moi lan)"]
    if t_ar:
        them.append(f"argon2id  {1 / t_ar:>15.1f} lan/giay  ({t_ar * 1000:.0f} ms moi lan)")
        them.append(f"sha256 nhanh hon argon2id {_vi(t_ar / t_sha)} lan")
    them.append(f"sha256 nhanh hon bcrypt12 {_vi(t_bc / t_sha)} lan")
    return dict(loai="mot ve", hoi="Bam mot mat khau bao nhieu lan moi giay",
                them=them)


# ===================================================== 180. muoi
def ca_muoi():
    """Ba nguoi dung dat CUNG mot mat khau. Khong muoi thi ba ban ghi giong het.

    Con so dang gia hon: trong mot bang 10.000 nguoi ma mat khau lay theo phan
    phoi thuc te (mot nhom nho dung mat khau pho bien), dem xem bao nhieu ban
    ghi co the gom nhom chi bang mat thuong.
    """
    pho_bien = ["123456", "password", "123456789", "12345", "qwerty"]
    rng = secrets.SystemRandom()
    mk = []
    for i in range(10_000):
        # 22% dung mat khau pho bien - ty le nay chi de dung MO PHONG, nen no
        # duoc in ra thanh mot dong rieng chu khong lan vao ket qua.
        mk.append(rng.choice(pho_bien) if i % 100 < 22
                  else f"mk-rieng-{i}-{rng.randrange(10**9)}")
    khong_muoi = [hashlib.sha256(p.encode()).hexdigest() for p in mk]
    co_muoi = [hashlib.sha256(secrets.token_bytes(16) + p.encode()).hexdigest()
               for p in mk]
    d1, d2 = len(mk) - len(set(khong_muoi)), len(mk) - len(set(co_muoi))
    nhom = max(khong_muoi.count(h) for h in set(khong_muoi))
    return dict(loai="dung sai",
                hoi="10.000 ban ghi, 22% dung mat khau pho bien",
                a="sha256(mat khau)", b="sha256(muoi + mat khau)",
                ka=f"{d1} ban ghi trung hash", kb=f"{d2} ban ghi trung hash",
                them=[f"nhom trung lon nhat khong muoi: {nhom} nguoi cung mot hash",
                      "gia tri 22% la tham so mo phong, khong phai so do"])


# ===================================================== 181. bcrypt 72 byte
def ca_bcrypt_72():
    """Gioi han 72 byte cua bcrypt, va HAI cach thu vien xu ly no.

    Ban `bcrypt` moi NEM ValueError thay vi cat am tham. Do la tin tot, nhung
    no doi cho hong: khong con la "hai mat khau khac nhau cung vao duoc" ma
    thanh "nguoi dat mat khau dai khong dang nhap noi".

    Cach cat tay - dung `mk[:72]` truoc khi bam - la cach nhieu doan code that
    dang dung de tranh exception do, va no dung lai cai loi cu.
    """
    import bcrypt
    a = "MatKhauRatDaiCuaToi-" + "x" * 60          # 80 byte
    b = a[:72] + "PHAN-KHAC-HAN"                    # 72 byte dau Y HET a
    h = bcrypt.hashpw(a[:72].encode(), bcrypt.gensalt(rounds=10))
    nem = ""
    try:
        bcrypt.checkpw(a.encode(), h)
    except ValueError as e:
        nem = type(e).__name__ + ": " + str(e)[:52]
    return dict(loai="dung sai",
                hoi=f"Hai mat khau khac nhau, 72 byte dau giong het ({len(a)} va {len(b)} byte)",
                a="checkpw(mat khau A[:72])", b="checkpw(mat khau B[:72])",
                ka=str(bcrypt.checkpw(a[:72].encode(), h)),
                kb=str(bcrypt.checkpw(b[:72].encode(), h)),
                them=[f"A = {a[:30]}...",
                      f"B = {b[:30]}...",
                      f"hai chuoi khac nhau tu byte thu {next(i for i, (x, y) in enumerate(zip(a, b)) if x != y) + 1}",
                      f"khong cat tay ma dua ca {len(a)} byte vao: {nem}",
                      "ban bcrypt nay NEM loi thay vi cat am tham"])


# ===================================================== 182. argon2 ba tham so
def ca_argon2_tham_so():
    """Ba tham so, va cai nao that su lam ke tan cong ton kem."""
    try:
        from argon2.low_level import Type, hash_secret_raw
    except Exception as e:      # noqa: BLE001
        return dict(loai="mot ve", hoi="argon2 khong nap duoc",
                    them=[str(e)])
    mk, muoi = b"mat-khau", b"muoi-16-byte-abc"

    def chay(t, m, p):
        return _do(lambda: hash_secret_raw(mk, muoi, time_cost=t,
                                           memory_cost=m, parallelism=p,
                                           hash_len=32, type=Type.ID), 3)
    goc = chay(3, 65536, 4)
    them = [f"t=3  m=64MB  p=4   {goc * 1000:>8.1f} ms   (moc)"]
    for ten, r in (("t=1  m=64MB  p=4  ", chay(1, 65536, 4)),
                   ("t=3  m=8MB   p=4  ", chay(3, 8192, 4)),
                   ("t=3  m=256MB p=4  ", chay(3, 262144, 4)),
                   ("t=3  m=64MB  p=1  ", chay(3, 65536, 1))):
        them.append(f"{ten} {r * 1000:>8.1f} ms   ({r / goc:.2f}x moc)")
    return dict(loai="mot ve", hoi="Doi tung tham so, thoi gian bam doi bao nhieu",
                them=them)


# ===================================================== 184. HMAC
def ca_hmac_webhook():
    """Chu ky kieu sha256(payload) thi AI CUNG ky lai duoc sau khi sua.

    Day la loi that trong nhieu doan code nhan webhook: ky bang hash cua noi
    dung ma khong co khoa nao trong do.
    """
    khoa = b"khoa-bi-mat-chi-hai-ben-biet"
    that = b'{"don":"A-1","so_tien":100000}'
    gia = b'{"don":"A-1","so_tien":1}'

    def ky_sai(p):
        return hashlib.sha256(p).hexdigest()

    def ky_dung(p):
        return hmac.new(khoa, p, hashlib.sha256).hexdigest()
    return dict(loai="dung sai",
                hoi="Ke tan cong sua so tien roi tu ky lai. Server nhan khong",
                a="chu ky = sha256(payload)",
                b="chu ky = HMAC(khoa, payload)",
                ka=f"server nhan: {ky_sai(gia) == ky_sai(gia)}",
                kb=f"server nhan: {hmac.compare_digest(ky_dung(gia), ky_sai(gia))}",
                them=[f"payload that: {that.decode()}",
                      f"payload da sua: {gia.decode()}",
                      "cach A: ke tan cong bam lai payload moi la co chu ky hop le",
                      "cach B: khong co khoa thi khong ky lai duoc"])


# ===================================================== 185. timing attack
def ca_timing():
    """Ba cach so sanh token, xem cach nao ro ri do dai tien to trung khop.

    KET LUAN DA DO (dung nguyen van, dung lam tron cho dep): `==` cua CPython
    KHONG ro ri o co 64 byte - no goi memcmp cua he dieu hanh, chay mot hai lenh
    SIMD, va nhieu cua may lon hon chenh lech can do. Chinh vong lap TU VIET moi
    ro ri, va no ro ri tuyen tinh.

    Do la ly do ca nay ton tai: neu chi do `==` roi khong thay gi, nguoi viet se
    ket luan "timing attack la chuyen ly thuyet" - va ket luan do sai.
    """
    token = "a" * 64
    n = 120_000

    def so_tay(x, y):
        """Cach nhieu doan code that viet, va cach moi nguoi tu viet khi so
        sanh tung phan tu: tra ve NGAY khi thay khac."""
        if len(x) != len(y):
            return False
        for i in range(len(x)):
            if x[i] != y[i]:
                return False
        return True

    # Do DU SAU MUC, khong do ba muc roi noi suy ba muc con lai. So 98 dung
    # tung con so nay lam be rong mot hang trong canh `thac`, va noi suy o day
    # nghia la ba hang trong video la so bia.
    MUC = (0, 8, 16, 32, 48, 63)
    them = ["cach 1 - `==` cua CPython (goi memcmp):"]
    goc = {}
    for k in MUC:
        doan = "a" * k + "b" * (64 - k)

        def viec(d=doan):
            for _ in range(n):
                _ = token == d
        t = _do(viec, 5) / n
        goc[k] = t
        them.append(f"   trung {k:>2} ky tu dau  {t * 1e9:>8.1f} ns"
                    f"  ({t / goc[0]:.2f}x)")
    them.append("cach 2 - vong lap tu viet, tra ve ngay khi khac:")
    tay = {}
    for k in MUC:
        doan = "a" * k + "b" * (64 - k)

        def viec2(d=doan):
            for _ in range(n):
                so_tay(token, d)
        t = _do(viec2, 5) / n
        tay[k] = t
        them.append(f"   trung {k:>2} ky tu dau  {t * 1e9:>8.1f} ns"
                    f"  ({t / tay[0]:.2f}x)")

    def an_toan():
        for _ in range(n):
            hmac.compare_digest(token, "b" * 64)
    ta = _do(an_toan, 5) / n
    them.append(f"cach 3 - compare_digest  {ta * 1e9:>8.1f} ns  (thiet ke de khong doi)")
    them.append(f"vong lap tu viet: trung 63 ky tu ton {tay[63] / tay[0]:.1f}x so voi trung 0")
    them.append(f"`==`            : trung 63 ky tu ton {goc[63] / goc[0]:.2f}x so voi trung 0")
    return dict(loai="mot ve",
                hoi="So sanh token 64 ky tu, cach nao ro ri qua dong ho",
                them=them)


# ===================================================== 186. Math.random
def ca_token_36():
    """Ban Python cua doan mot dong pho bien nhat de sinh token.

    `Math.random().toString(36).substr(2, 9)` - do dai KHONG on dinh, va do la
    cho hong that su. O day dung `secrets` cho phan ngau nhien de con so trung
    lap chi noi ve DO DAI chu khong noi ve chat luong bo sinh.
    """
    rng = secrets.SystemRandom()

    def kieu_36():
        # Mo phong toString(36) cua mot so thuc trong [0,1) roi cat 9 ky tu
        x = rng.random()
        s = ""
        for _ in range(13):
            x *= 36
            d = int(x)
            s += string.digits[d] if d < 10 else string.ascii_lowercase[d - 10]
            x -= d
        return s[:9].rstrip("0")

    n = 200_000
    ra = [kieu_36() for _ in range(n)]
    dai = {}
    for t in ra:
        dai[len(t)] = dai.get(len(t), 0) + 1
    trung = n - len(set(ra))
    them = [f"sinh {n:,} token".replace(",", "."),
            f"token trung nhau: {trung}",
            f"ngan nhat {min(dai)} ky tu, dai nhat {max(dai)} ky tu"]
    for k in sorted(dai):
        them.append(f"  dai {k} ky tu: {dai[k]:>7,} token".replace(",", "."))
    return dict(loai="mot ve", hoi="Token tu toString(36).substr(2,9) dai bao nhieu",
                them=them)


# ===================================================== 177. hash khac ma hoa
def ca_hash_mot_chieu():
    """Bam roi thi khong lay lai duoc - do bang so kha nang phai thu."""
    pin = "4271"
    h = hashlib.sha256(pin.encode()).hexdigest()
    t0 = time.perf_counter()
    tim = None
    for i in range(10_000):
        if hashlib.sha256(f"{i:04d}".encode()).hexdigest() == h:
            tim = f"{i:04d}"
            break
    dt = time.perf_counter() - t0
    return dict(loai="mot ve",
                hoi="Bam mot chieu, nhung khong gian nho thi do het duoc",
                them=[f"sha256('{pin}') = {h[:32]}...",
                      f"do het 10.000 pin: tim ra '{tim}' sau {dt * 1000:.1f} ms",
                      "mot chieu KHONG co nghia la an toan khi dau vao it kha nang"])


# ===================================================== 177. do het khong gian
def ca_khong_gian():
    """Bao lau thi do het mot khong gian mat khau, o toc do DO DUOC o tren.

    Hai phan phai tach ro:
      SO DO   toc do bam - do bang chinh may nay, in o `toc_do_bam`
      SUY RA  thoi gian = so kha nang / toc do. Phep chia, nguoi xem tu kiem.

    Khong dam bam that het khong gian tam ky tu - do la hang tram nam bang
    Python. Nen o day bam that MOT khong gian nho (pin bon so) roi suy phan con
    lai, va in ro cai nao la do cai nao la suy.
    """
    mk = b"mat-khau"
    n = 200_000
    t0 = time.perf_counter()
    for _ in range(n):
        hashlib.sha256(mk).digest()
    toc = n / (time.perf_counter() - t0)

    pin = "4271"
    h = hashlib.sha256(pin.encode()).hexdigest()
    t1 = time.perf_counter()
    for i in range(10_000):
        if hashlib.sha256(f"{i:04d}".encode()).hexdigest() == h:
            break
    dt = time.perf_counter() - t1

    them = [f"SO DO   toc do sha256 tren may nay: {toc:,.0f} lan/giay"
            .replace(",", "."),
            f"SO DO   do het 10.000 pin bon so: {dt * 1000:.1f} ms",
            "SUY RA  cac dong duoi = so kha nang / toc do do duoc:"]
    for ten, kg in (("pin 4 số", 10 ** 4), ("pin 6 số", 10 ** 6),
                    ("6 chữ thường", 26 ** 6),
                    ("8 chữ thường", 26 ** 8),
                    ("8 chữ + số + ký tự", 72 ** 8)):
        gy = kg / toc
        if gy < 90:
            dv = f"{gy:.1f} giay"
        elif gy < 5400:
            dv = f"{gy / 60:.1f} phut"
        elif gy < 129600:
            dv = f"{gy / 3600:.1f} gio"
        elif gy < 3.15e7:
            dv = f"{gy / 86400:.1f} ngay"
        else:
            dv = f"{gy / 3.15e7:.1f} nam"
        them.append(f"        {ten:<20} {kg:>22,} kha nang  ->  {dv}"
                    .replace(",", "."))
    them.append("        (mot GPU that nhanh hon Python nay hang nghin lan)")
    return dict(loai="mot ve", hoi="Bam mot chieu thi do het mat bao lau",
                them=them)


# ============================== 177b. bam so dien thoai de "an danh" du lieu
def ca_so_dien_thoai():
    """Bam so dien thoai KHONG an danh duoc gi. Do that, khong suy.

    Day la cho bang "khong gian mat khau" tro thanh chuyen cua nguoi Viet: so
    di dong Viet Nam co 10 chu so va dau so dau la mot tap dong. Cho truoc mot
    dau so, chi con BAY chu so tu do - tuc 10 trieu kha nang, va 10 trieu thi
    do het duoc bang mot vong for.

    Chay that ca vong do va do thoi gian, khong nhan chia gi.
    """
    dau_so = "090"
    that = dau_so + "1234567"
    h = hashlib.sha256(that.encode()).hexdigest()
    t0 = time.perf_counter()
    tim, dem = None, 0
    for i in range(10 ** 7):
        dem += 1
        if hashlib.sha256(f"{dau_so}{i:07d}".encode()).hexdigest() == h:
            tim = f"{dau_so}{i:07d}"
            break
    dt = time.perf_counter() - t0
    return dict(loai="mot ve",
                hoi="Bam so dien thoai roi coi la da an danh - do het mat bao lau",
                them=[f"so that:  {that}",
                      f"sha256:   {h[:40]}...",
                      f"tim ra:   {tim} sau {dt:.1f} giay, thu {dem:,} lan"
                      .replace(",", "."),
                      f"ca dau so {dau_so} chi co 10.000.000 kha nang",
                      "khong can bang tra cuu, khong can GPU, mot vong for la xong"])


# ==================================== 179b. do het mat khau 8 ky tu, ba ham
def ca_do_het_8_ky_tu():
    """Cung mot khong gian mat khau, ba ham bam thi ton bao lau.

    Toc do do THAT bang chinh ba ham do (khong lay lai so cu cua `toc_do_bam`,
    de moi lan chay la mot bo so tu nhat quan). Phan con lai la phep chia, va
    con so kha nang thi ai cung tu nhan ra duoc: 26 luy thua 8.
    """
    import bcrypt
    mk = b"matkhau8"
    n_sha = 200_000
    t0 = time.perf_counter()
    for _ in range(n_sha):
        hashlib.sha256(mk).digest()
    r_sha = n_sha / (time.perf_counter() - t0)
    muoi = bcrypt.gensalt(rounds=12)
    r_bc = 1.0 / _do(lambda: bcrypt.hashpw(mk, muoi), 3)
    try:
        from argon2.low_level import Type, hash_secret_raw
        r_ar = 1.0 / _do(lambda: hash_secret_raw(
            mk, b"muoi-16-byte-abc", time_cost=3, memory_cost=65536,
            parallelism=4, hash_len=32, type=Type.ID), 3)
    except Exception:       # noqa: BLE001
        r_ar = None

    kg = 26 ** 8
    them = [f"khong gian: 8 chu thuong = 26^8 = {_vi(kg)} kha nang"]
    for ten, r in (("sha256", r_sha), ("argon2id t3 m64MB p4", r_ar),
                   ("bcrypt cost 12", r_bc)):
        if not r:
            continue
        gy = kg / r
        nam = gy / 3.15e7
        dv = f"{gy / 86400:.1f} ngay" if nam < 1 else f"{_vi(nam)} nam"
        toc = _vi(r) if r >= 1000 else f"{r:.1f}"
        them.append(f"  {ten:<24} {toc:>15} lan/giay  ->  {dv}")
    return dict(loai="mot ve",
                hoi="Do het mat khau 8 chu thuong mat bao lau, theo tung ham",
                them=them)


CA = {
    "khong_gian": ca_khong_gian,
    "do_het_8_ky_tu": ca_do_het_8_ky_tu,
    "so_dien_thoai": ca_so_dien_thoai,
    "md5_trung": ca_md5_trung,
    "toc_do_bam": ca_toc_do_bam,
    "muoi": ca_muoi,
    "bcrypt_72": ca_bcrypt_72,
    "argon2_tham_so": ca_argon2_tham_so,
    "hmac_webhook": ca_hmac_webhook,
    "timing": ca_timing,
    "token_36": ca_token_36,
    "hash_mot_chieu": ca_hash_mot_chieu,
}


def main():
    in_moc()
    ten = sys.argv[1:] or list(CA)
    ban = []
    for k in ten:
        if k not in CA:
            print(f"khong co ca {k!r}. Co: {', '.join(CA)}")
            continue
        r = CA[k]()
        ranh, ty = (kiem_may(im=True) if r["loai"] in ("toc do", "mot ve")
                    else (True, 1.0))
        if not ranh:
            ban.append(f"{k} ({ty:.2f}x)")
        print(f"\n=== {k} ===")
        print(f"  {r['hoi']}")
        if r["loai"] == "toc do":
            ta, tb = r["ta"], r["tb"]
            print(f"  A  {r['a']:30} {ta * 1000:>10.2f} ms")
            print(f"  B  {r['b']:30} {tb * 1000:>10.2f} ms")
            print(f"  -> chenh {max(ta, tb) / min(ta, tb):.0f} lan")
        elif r["loai"] == "dung sai":
            print(f"  A  {r['a']:30} -> {r['ka']}")
            print(f"  B  {r['b']:30} -> {r['kb']}")
        for d in r.get("them", []):
            print(f"     {d}")
    if ban:
        print("\n!! MAY BAN luc do: " + ", ".join(ban))
        print("   Dung nhung so nay cho kich ban la SAI. Chay lai luc may ranh.")


if __name__ == "__main__":
    main()
