"""Kiem tra screenplay TRUOC khi render - nham vao canh mo phong `gantt`.

Ly do file nay ton tai: `gantt` khong mo phong gi ca. No ve dung nhung gi bạn
khai trong YAML. Nghia la neu bạn ghi cache doi gia tri o `at: 0.84` nhung buoc
`SET` lai ket thuc o `0.60`, animation van chay tron - va no dang NOI SAI ma
khong ai bao. Voi dinh dang "hien truong vu an" thi mot con so sai o day dat hon
mot loi chinh ta rat nhieu.

Nen o day kiem hai nhom:

  LOI       - chac chan sai, phai sua (thanh chong nhau, tran ra ngoai truc...)
  CANH BAO  - dang ngo, nguoi viet tu quyet (o so doi ma khong buoc nao vua
              xong, nhan buoc khong vua trong thanh, khoang khong co gi xay ra)

Khong tu sua gi. Bo cuc va nhip la quyet dinh cua nguoi viet, tool chi chi ra
cho dang ngo.

    python src/lint.py screenplays/cache-stale.yaml [--engine voicestudio]

    thoat 1 neu co LOI, 0 neu chi co canh bao -> dung duoc trong vong lap kiem
    hang loat. Chot chan luc render (`render.py` goi `lint.report`) chi IN loi
    roi chay tiep, tru khi co `--strict`.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

NGAN = 25         # cau duoi nay bi `speak.pause_after` nhan he so 0,85, va do
                  # duoc la doc don toi 6,9 am tiet/giay (dai tu nhien 4,5-6,0)
TOL = 0.05        # sai so coi la "trung mot moc"
GAP_MAX = 0.14    # khoang dai hon nay ma khong co gi xay ra -> canh bao
LANE_W = 960      # (W - MARGIN) - MARGIN, be rong duong ray trong bench.py
PAD_IN = 28       # le trong thanh, khop voi bench._step_label


def _fit_w(txt):
    """Be rong `w` nho nhat de ten buoc con vua BEN TRONG thanh.

    Do bang chinh font va nguong ma `bench._step_label` dung, khong uoc luong -
    nen ket qua no bao la con so dan duoc thang vao YAML.
    """
    import typo
    f = typo.mono_font(20, 700)     # co nho nhat ma _step_label con thu
    return (typo.track_w(txt, f, 1.2) + PAD_IN) / LANE_W


def _bounds(sp):
    """Cac moc thoi diem 'co viec vua xong' - dung de doi chieu voi o so."""
    out = []
    for lane in sp.get("lanes", []):
        for st in lane.get("steps", []):
            at, w = float(st["at"]), float(st.get("w", 0.16))
            out.append((at, f"{lane.get('label', '?')} / {st.get('text', '?')} bắt đầu"))
            out.append((at + w, f"{lane.get('label', '?')} / {st.get('text', '?')} xong"))
    return out


def check_gantt(sp, idx, out):
    tag = f"cảnh {idx:02d} gantt"
    lanes = sp.get("lanes", [])
    if not lanes:
        out.append(("LOI", tag, "không có `lanes`, cảnh sẽ trống"))
        return
    bounds = _bounds(sp)

    # ---- thanh: tran truc, chong nhau, nhan khong vua
    for lane in lanes:
        label = lane.get("label", "?")
        steps = sorted(lane.get("steps", []), key=lambda s: float(s["at"]))
        prev_end, prev_txt = -1.0, None
        for st in steps:
            at, w = float(st["at"]), float(st.get("w", 0.16))
            txt = st.get("text", "")
            if at < 0 or at + w > 1.0001:
                out.append(("LOI", tag,
                            f"`{txt}` chạy tới {at + w:.2f} — tràn ra ngoài trục "
                            f"(at + w phải ≤ 1.0)"))
            if at < prev_end - 1e-6:
                out.append(("LOI", tag,
                            f"`{txt}` bắt đầu ở {at:.2f} khi `{prev_txt}` chưa "
                            f"xong ({prev_end:.2f}) — hai thanh chồng nhau trong "
                            f"cùng một lane `{label}`"))
            need = _fit_w(txt)
            if w < need:
                out.append(("CANH BAO", tag,
                            f"`{txt}` không vừa trong thanh (w={w:.2f}), sẽ bị "
                            f"đẩy xuống hàng nhãn tràn — đặt w ≥ {need:.2f} "
                            f"hoặc viết ngắn hơn"))
            prev_end, prev_txt = at + w, txt

    # ---- o so: moc doi gia tri co dua vao viec gi khong
    for ro in sp.get("readout", []):
        key = ro.get("key", "?")
        steps = ro.get("steps", [])
        if not steps:
            out.append(("LOI", tag, f"ô số `{key}` không có `steps`"))
            continue
        ats = [float(s.get("at", 0.0)) for s in steps]
        if ats != sorted(ats):
            out.append(("LOI", tag,
                        f"ô số `{key}` có `at` không tăng dần {ats} — giá trị sẽ "
                        f"nhảy sai thứ tự"))
        for st in steps:
            at = float(st.get("at", 0.0))
            if at <= 1e-9:
                continue        # gia tri khoi dau, khong can moc nao
            near = [why for t, why in bounds if abs(t - at) <= TOL]
            if not near:
                out.append(("CANH BAO", tag,
                            f"ô số `{key}` đổi thành `{st.get('value')}` ở "
                            f"{at:.2f} nhưng không có bước nào bắt đầu/xong quanh "
                            f"mốc đó — người xem không thấy VÌ SAO nó đổi"))

    # ---- bo dem
    c = sp.get("counter")
    if c:
        frm = float(c.get("from", 0.0))
        if 0 < frm <= 1.0:
            if not [1 for t, _ in bounds if abs(t - frm) <= TOL]:
                out.append(("CANH BAO", tag,
                            f"bộ đếm `{c.get('key')}` bắt đầu chạy ở {frm:.2f} "
                            f"nhưng không có bước nào xong quanh mốc đó"))
        if frm <= 1.0 and float(c.get("rate", 0)) <= 0:
            out.append(("CANH BAO", tag,
                        f"bộ đếm `{c.get('key')}` có rate=0 nên đứng ở 0 — nếu "
                        f"đó là ý bạn (lần chạy đúng) thì đặt luôn from > 1 cho rõ"))

    # ---- verdict
    va = sp.get("verdict_at")
    if va is not None:
        va = float(va)
        last = max([t for t, _ in bounds], default=0.0)
        if va < last - TOL:
            out.append(("CANH BAO", tag,
                        f"`verdict_at: {va:.2f}` chốt TRƯỚC khi bước cuối xong "
                        f"({last:.2f}) — câu kết hiện ra khi mô phỏng chưa chạy hết"))
        if not sp.get("verdict"):
            out.append(("LOI", tag, "có `verdict_at` nhưng thiếu `verdict`"))

    # ---- khoang khong co gi xay ra (dau doc van chay, nhung khong co THONG TIN)
    changes = [float(s.get("at", 0.0))
               for ro in sp.get("readout", []) for s in ro.get("steps", [])]
    if c and 0 <= float(c.get("from", 9)) <= 1 and float(c.get("rate", 0)) > 0:
        busy_counter = float(c["from"])
    else:
        busy_counter = None
    spans = [(float(st["at"]), float(st["at"]) + float(st.get("w", 0.16)))
             for lane in lanes for st in lane.get("steps", [])]

    def active(p):
        if any(a - 1e-9 <= p <= b + 1e-9 for a, b in spans):
            return True
        if any(abs(p - t) <= 0.04 for t in changes):
            return True
        return busy_counter is not None and p >= busy_counter

    gap_start, worst = None, (0.0, 0.0, 0.0)
    p = 0.0
    while p <= 1.0001:
        if active(p):
            if gap_start is not None:
                if p - gap_start > worst[0]:
                    worst = (p - gap_start, gap_start, p)
                gap_start = None
        elif gap_start is None:
            gap_start = p
        p += 0.01
    if gap_start is not None and 1.0 - gap_start > worst[0]:
        worst = (1.0 - gap_start, gap_start, 1.0)
    if worst[0] > GAP_MAX:
        out.append(("CANH BAO", tag,
                    f"từ {worst[1]:.2f} đến {worst[2]:.2f} ({worst[0]:.0%} thời "
                    f"lượng cảnh) không có bước nào chạy và không ô số nào đổi — "
                    f"mắt người xem rời màn hình đúng lúc đó"))


def check_caption(sp, idx, out):
    """Phu de dai qua thi thẻ tràn - `note()` chi thu nho toi 24px roi chiu."""
    import sketch as sk
    from bench import CONTENT_W, NOTE_MAX_H
    from style import font
    txt = sp.get("caption")
    if not txt:
        return
    for size in (32, 30, 28, 26, 24):
        f = font("grot_med", size)
        lines = sk.wrap(txt, f, CONTENT_W - 96)
        lh = sk.line_height(f, 1.34)
        if lh * len(lines) + 44 <= NOTE_MAX_H:
            return
    out.append(("CANH BAO", f"cảnh {idx:02d} {sp.get('scene')}",
                f"`caption` dài {len(txt)} ký tự, thẻ phụ đề chỉ vừa ~3 dòng ở "
                f"24px — viết `caption` riêng ngắn hơn `narration`"))


# Tag CO THAT trong app nhung chi `longform_parser.py` + `ssml_lite.py` parse
# (Audiobook, Stories). `generation.py` khong import ssml_lite, nen tren duong
# `/generate` chung bi doc thanh tieng. Bao loi rieng vi nguoi doc tai lieu se
# thay chung ton tai va khong hieu vi sao khong chay.
_TAG_LONGFORM = ("slow", "fast", "emphasis", "spell", "voice")


def check_tag(sp, idx, out):
    """Bat tag la trong `narration`. LOI chu khong phai canh bao.

    Ly do phai la LOI: tag khong nam trong bo model biet thi KHONG bi bo di - no
    bi DOC THANH TIENG. Do that: them `[excited]` vao mot cau lam audio dai them
    0,73 giay, vi model doc chu "excited". Khong co dong canh bao nao tu backend.

    Day la bay se gap thuong xuyen khi sinh kich ban bang AI: moi model viet
    script deu quen tay `[excited]` `[whispers]` `[angry]` kieu ElevenLabs. Chan o
    lint la cach duy nhat re - phat hien qua audio thi da mat mot luot render.

    `[[...]]` la ghi de phat am cua VoiceStudio, hop le, nen bo qua truoc khi do.
    """
    n = sp.get("narration") or ""
    if not n or "[" not in n:
        return
    tag = f"cảnh {idx:02d}"
    # bo `[[...]]` truoc de khong bao dong gia
    con = re.sub(r"\[\[.*?\]\]", "", n)
    for m in re.finditer(r"\[([^\[\]]*)\]", con):
        noi_dung = m.group(1).strip().lower()
        if noi_dung in ("laughter", "sigh"):
            continue
        if re.fullmatch(r"pause(\s+\d+(?:\.\d+)?\s*(ms|s)?)?", noi_dung):
            continue
        goc = noi_dung.lstrip("/").split(":")[0]
        if goc in _TAG_LONGFORM:
            out.append(("LOI", tag,
                        f"tag `[{m.group(1)}]` CO THAT nhung chi Audiobook/Stories "
                        f"parse (`/longform/render`); `/generate` khong parse nen "
                        f"no se bi ĐỌC THÀNH TIẾNG. Dùng `speed:` ở cấp cảnh thay thế"))
        else:
            out.append(("LOI", tag,
                        f"tag `[{m.group(1)}]` khong co trong bo model biet - "
                        f"no se bi ĐỌC THÀNH TIẾNG. Chỉ dùng `[laughter]`, `[sigh]`, "
                        f"`[pause 400ms]`; xem VIET-KICH-BAN.md mục tag phi ngôn ngữ"))


def check_narration(sp, idx, out, engine):
    """Bay doc sai cua engine `voicestudio` - CHI kiem khi dung engine do.

    Hai bay nay do bang tai roi do lai bang so tren ban render that:

      viet tat o CUOI cau  `"...vẫn cần TTL."` -> OmniVoice nen `TTL` thanh mot
          manh 0,12s; ba chu cai khong the doc ro trong 120ms. Cuoi cau lai la
          cho cao tan sut manh nhat, nen hai cai cong don.
      cau CUC NGAN co viet tat  `"Luôn đặt TTL."` (13 ky tu) -> do duoc 0,58s cho
          4 am tiet = 6,9 am tiet/giay, vuot dai tu nhien 4,5-6,0.

    Cach sua: doi viet tat vao GIUA cau, va gop cau ngan voi cau ben canh.

    Nguong da phai chinh mot lan. Ban dau toi bao MOI cau duoi 25 ky tu, ket qua
    la 11 canh bao tren mot screenplay nguoi dung DA duyet - linter keu nhieu thi
    bi bo qua, thanh vo dung. Doi chieu voi phan hoi that:

      bi phan nan  `"Quy tắc một."` (12) `"Luôn đặt TTL."` (13)
                   `"Bộ đếm đứng ở không."` (20)  -> deu la cau CUOI cua narration
                   canh 01 co 4/5 cau ngan lien tiep -> nghe "doc tung chu"
      KHONG bi      canh 10 `"Một giờ. Một ngày. Một tuần."` (8/9/9) - nhip ba co y
                   canh 05 `"Bạn xoá cache."` `"Cache rỗng."` - nguoi dung xac nhan
                   doc dung

    Nen cau ngan o GIUA narration khong phai van de. Hai dau hieu that su du doan
    duoc loi:

      1. cau ngan o CUOI narration - `contour_for()` ha he so toc do xuong 0,978
         cho cau cuoi, cong voi vi tri cuoi cum la cho cao tan sut manh nhat
      2. tu 4 cau ngan tro len trong mot canh - moi cau la mot lan goi model kem
         mot khoang nghi, do duoc 1,04 giay im lang trong canh ~8 giay

    Chi bao khi engine la `voicestudio`: edge-tts doc ca doan mot lan nen cau ngan
    khong sinh van de nao.
    """
    if engine not in ("omnivoice", "voicestudio"):
        return
    txt = sp.get("narration")
    if not txt:
        return
    cau = [s.strip() for s in re.split(r"(?<=[.!?…])\s+", txt.strip()) if s.strip()]
    if not cau:
        return
    for s in cau:
        end_abbr = re.search(r"\b([A-Z]{2,})\b[.!?…]*$", s)
        if end_abbr:
            out.append(("CANH BAO", f"cảnh {idx:02d} {sp.get('scene')}",
                        f"`{end_abbr.group(1)}` ở CUỐI câu \"{s[:44]}…\" — "
                        f"voicestudio nén viết tắt cuối câu; đổi vào giữa câu"))
    if len(cau) > 1 and len(cau[-1]) < NGAN:
        out.append(("CANH BAO", f"cảnh {idx:02d} {sp.get('scene')}",
                    f"câu CUỐI chỉ {len(cau[-1])} ký tự: \"{cau[-1]}\" — câu cuối bị "
                    f"contour hạ tốc còn 0,978 và nằm ở chỗ cao tần sụt mạnh nhất; "
                    f"gộp vào câu trước"))
    ngan = sum(1 for s in cau if len(s) < NGAN)
    if ngan >= 4:
        out.append(("CANH BAO", f"cảnh {idx:02d} {sp.get('scene')}",
                    f"{ngan}/{len(cau)} câu dưới {NGAN} ký tự — mỗi câu là một lần "
                    f"gọi model kèm một khoảng nghỉ, cả cảnh sẽ nghe rời rạc"))


def _cau(text):
    """Tach cau y het luc sinh giong, de vi tri cau tinh ra dung."""
    try:
        import vitext   # cung thu muc src/, khong con tro sang repo khac
        return vitext.prepare(text)
    except Exception:
        return [c.strip() for c in re.split(r"(?<=[.!?…])\s+", text) if c.strip()]


# Nguong doi chieu voi phan hoi that, khong chon cho tron:
#   da xac nhan hong  n-plus-one canh 5 (139 ky tu, 5,05x)
#                     pool-can   canh 6 (133 ky tu, 2,11x)
#   nguoi dung DA DUYET, khong phan nan  cache-stale canh 8 (102 ky tu, 2,62x)
# Ty le mot minh khong tach duoc hai nhom (2,62x da duyet > 2,11x bi che), do
# dai mot minh cung khong. Phai dung ca hai.
CUOI_DAI = 125
CUOI_TY_LE = 2.0
LAP_CUM = 3


def check_doc_ro(sp, idx, out, engine):
    """Dau hieu SUY DUOC TU VAN BAN, khong can sinh mot giay audio nao.

    KHONG co kiem tra am tiet dau bi nen o day, du do la loi nguoi dung that su
    da bat duoc. Ly do: so do cua chinh toi khong ung ho gia thuyet ngu am nao.
    "Mot" (am tiet dong, phu am tac) bi nen con 88ms, nhung "Cau" va "Dau" la am
    tiet MO cung bi nen con 125ms va 116ms. Chi "Trang" va "Danh" giu duoc do
    dai, va n=1 moi phuong an. Do bien nen thanh mot luat lint thi no se keu tren
    moi screenplay ma khong dung han - dung kieu canh bao lam nguoi ta bo qua ca
    nhung canh bao that.
    Cho do thuoc ve cong nghiem thu (tang 2), noi do TRUC TIEP audio da sinh.
    """
    if engine not in ("omnivoice", "voicestudio"):
        return
    tag = f"cảnh {idx:02d}"
    n = sp.get("narration", "") or ""
    if not n.strip():
        return
    cau = _cau(n)

    # 1. Cau nang nhat nam CUOI. `contour_for()` ha cau cuoi xuong x0,95, nen
    #    cau dai nhat lai la cau chay cham nhat trong ca canh.
    if len(cau) >= 2:
        dai = [len(c) for c in cau]
        con = sorted(dai[:-1])
        tv = con[len(con) // 2] if len(con) % 2 else (con[len(con) // 2 - 1]
                                                     + con[len(con) // 2]) / 2
        ty = dai[-1] / (tv or 1)
        if dai[-1] >= CUOI_DAI and ty >= CUOI_TY_LE:
            out.append(("CANH BAO", tag,
                        f"câu cuối dài {dai[-1]} ký tự, gấp {ty:.1f} lần các "
                        f"câu còn lại, mà câu cuối bị `contour_for()` hạ tốc "
                        f"xuống ×0,95 — thêm một câu kết ngắn hơn phía sau"))

    # 2. Cum tu lap. Bay "tu lap" da do duoc: `"tram phan tram"` sinh lo chet
    #    459ms, `"mot cau"` lap 4 lan cho 3,67 khoi/giay (trung vi 4,94).
    for c in cau:
        tu = [w.lower().strip(",.:;") for w in c.split()]
        dem = {}
        for i in range(len(tu) - 1):
            k = tu[i] + " " + tu[i + 1]
            dem[k] = dem.get(k, 0) + 1
        for k, v in sorted(dem.items()):
            if v >= LAP_CUM:
                out.append(("CANH BAO", tag,
                            f"cụm `{k}` lặp {v} lần trong một câu — dạng này "
                            f"đã đo được sinh lỗ chết"))

    # 3. Tu Latin chua khai trong tu dien phien am. Model TU DOAN cach doc, ma
    #    `mode: tach` sinh tung cau doc lap nen moi cau doan mot kieu.
    try:
        import phienam
        la = sorted(set(phienam.tu_la(n)), key=str.lower)
    except Exception:
        la = []
    if la:
        out.append(("CANH BAO", tag,
                    f"từ chưa khai trong `phienam.TU_DIEN`: "
                    f"{', '.join('`' + x + '`' for x in la)} — model tự đoán "
                    f"cách đọc, mỗi câu đoán một kiểu"))


def check_yaml_cat(o, out, path="doc"):
    """Bat gia tri bi dau phay cat doi trong flow style `{ ... }`.

    Trong `{a: 1, b: 2}` thi dau phay la DAU TACH. Nen mot gia tri khong boc nhay
    ma co dau phay se bi cat lam doi, va YAML KHONG BAO LOI:

        { note: nhanh hơn 1,07 lần }  ->  {'note': 'nhanh hơn 1', '07 lần': None}

    Nguy hon bay dau ':' (bay do lam vo file nen thay ngay). Cai nay file van
    parse duoc, van render duoc, chi la mat mot nua cau tren man hinh.

    Dau hieu chac chan: mot khoa co gia tri None. Khong co truong hop hop le nao
    trong schema nay dat khoa rong.

    KHONG dung cach tach chuoi theo dau phay de tim - `at: [0.5, 0.00]` la mang,
    dau phay o do hop le, va cach do bao nham het cac dong nhu vay.
    """
    if isinstance(o, dict):
        for k, v in o.items():
            if v is None:
                out.append(("LOI", path,
                            f"khoá `{k}` không có giá trị — gần như chắc chắn là "
                            f"một giá trị chứa dấu phẩy bị cắt trong `{{ ... }}`; "
                            f"bọc giá trị đó bằng dấu nháy"))
            else:
                check_yaml_cat(v, out, f"{path}.{k}")
    elif isinstance(o, list):
        for i, x in enumerate(o):
            check_yaml_cat(x, out, f"{path}[{i}]")


# Nhung khoa duoc theme ve THANG ra man hinh duoi dang chu. YAML doc `504` ra
# int va `2.0` ra float, roi ham do be ngang chu no ngay giua luc render - tuc
# la sau khi da tra tien cho ca vong tong hop giong noi.
KHOA_CHU = ("status", "value", "text", "head", "verdict", "vs", "tag", "n",
            "cap_label", "depth_key", "counter_key", "chip", "miss_tag",
            # Them sau khi vap: `label: 23:30` bi PyYAML doc thanh SO 1410 theo
            # he luc thap phan cua YAML 1.1 (23*60+30). Khong bao loi gi, chi no
            # giua luc render. `06:30` thanh 390, `1:2:3` thanh 3723.
            "label", "top", "note", "sub", "small", "body", "hint", "kicker",
            "ten", "nhan", "nut", "url", "so", "packet", "heading", "lenh",
            "nguon", "title", "brand", "footer", "hoi",
            # Bon loai canh mo phong them sau (`cot` `thac` `ban_sao` `gop`).
            # `dv` la don vi cua dong ho `thac` (" s", " ms") - de tran thi
            # YAML doc `dv: 5` ra int va `track_w()` no giua luc render.
            "key", "truc", "ghi", "con", "nhan_chung", "qua", "dv")


def check_kieu_chu(sp, idx, out):
    def soi(o, path):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in KHOA_CHU and isinstance(v, (int, float, bool)):
                    out.append(("LOI", f"canh {idx}",
                                f"`{path}{k}: {v}` bị YAML đọc thành số chứ "
                                f"không phải chữ, render sẽ dừng giữa chừng — "
                                f"bọc nháy: `{k}: \"{v}\"`"))
                elif isinstance(v, (dict, list)):
                    soi(v, f"{path}{k}.")
        elif isinstance(o, list):
            for i, x in enumerate(o):
                soi(x, f"{path}[{i}].")
    soi(sp, "")


def check_queue(sp, idx, out):
    """Duong cong phai DI THEO MOT HUONG va phai cat qua nguong.

    Ca canh nay chi noi duoc mot dieu: hang doi day len va khong rut xuong. Neu
    duong cong co doan di xuong thi hinh anh dang phu dinh chinh loi doc.
    """
    c = [float(x) for x in sp.get("curve") or []]
    if len(c) < 3:
        out.append(("LOI", f"canh {idx}", "`queue` can `curve` it nhat 3 mốc"))
        return
    xuong = [i for i in range(1, len(c)) if c[i] < c[i - 1] - 1e-9]
    if xuong and not sp.get("cho_phep_xuong"):
        out.append(("CANH BAO", f"canh {idx}",
                    f"`curve` đi xuống ở mốc {xuong[0]} ({c[xuong[0] - 1]:g} → "
                    f"{c[xuong[0]]:g}). Cảnh `queue` để kể chuyện dồn ứ; muốn "
                    f"vẽ đường có lên có xuống thì đặt `cho_phep_xuong: true`"))
    cap = sp.get("capacity")
    if cap and max(c) <= float(cap):
        out.append(("CANH BAO", f"canh {idx}",
                    f"`capacity` {cap} cao hơn đỉnh đường cong {max(c):g} — "
                    f"ngưỡng không bao giờ bị vượt nên mất khoảnh khắc đáng "
                    f"nhớ duy nhất của cảnh"))
    ymax = sp.get("ymax")
    if ymax and max(c) > float(ymax):
        out.append(("LOI", f"canh {idx}",
                    f"`ymax` {ymax} nhỏ hơn đỉnh đường cong {max(c):g} — đỉnh "
                    f"sẽ bị cắt cụt ở mép trên biểu đồ"))
    marks = sp.get("marks") or []
    if len(marks) == 1:
        out.append(("CANH BAO", f"canh {idx}",
                    "`marks` chỉ có một mốc nên trục thời gian không nói gì"))


def check_topology(sp, idx, out):
    """`from`/`to` phai nam trong danh sach, va phai co tang KHONG toi duoc."""
    nodes = sp.get("nodes") or []
    n = len(nodes)
    if n < 2:
        out.append(("LOI", f"canh {idx}", "`topology` cần ít nhất 2 `nodes`"))
        return
    if n > 6:
        out.append(("CANH BAO", f"canh {idx}",
                    f"{n} tầng trên sân diễn cao 826px — mỗi thẻ còn dưới 110px, "
                    f"tên tầng sẽ dính vào dòng phụ. Gộp bớt hoặc tách hai cảnh"))
    i_from = int(sp.get("from", 0))
    i_to = int(sp.get("to", n - 1))
    for ten, v in (("from", i_from), ("to", i_to)):
        if not 0 <= v < n:
            out.append(("LOI", f"canh {idx}",
                        f"`{ten}: {v}` nằm ngoài danh sách {n} tầng (0..{n - 1})"))
    if i_from == i_to:
        out.append(("LOI", f"canh {idx}",
                    "`from` trùng `to` nên gói tin không đi đâu cả"))
    for k, nd in enumerate(nodes):
        if not nd.get("name"):
            out.append(("LOI", f"canh {idx}", f"tầng {k} thiếu `name`"))
    if 0 <= i_from < n and 0 <= i_to < n:
        ngoai = n - (abs(i_to - i_from) + 1)
        if ngoai == 0 and sp.get("miss_tag"):
            out.append(("CANH BAO", f"canh {idx}",
                        "gói tin đi qua hết mọi tầng nên `miss_tag` không bao "
                        "giờ hiện — bỏ nó đi hoặc thu hẹp `from`/`to`"))


# Loai canh chiem HET san dien - gan dao cu vao la de len noi dung.
def check_cot(sp, idx, out):
    """`cot` khong tinh gi - no ve dung con so bạn khai, y nhu `gantt`.

    Hai phep kiem o day deu la loi DA THAY khi dung canh nay lan dau:

      thang tuyen tinh voi du lieu lech nhau hang tram lan -> cot nho nhat cao
      duoi mot pixel, tuc bien mat. Nguoi xem chi thay MOT cot va khong hieu
      canh dang so sanh cai gi.

      moi cot mot mau tuy y -> mat het nghia. Trong theme nay mau la NGON NGU:
      `hot` la cai sai, `ok` la cai dung. Hai cot deu `hot` thi khong con doi
      chieu, ba mau khac nhau thi khong con tieu diem.
    """
    tag = f"cảnh {idx:02d} cot"
    cot = sp.get("cot") or []
    if len(cot) < 2:
        out.append(("LOI", tag, "cần ít nhất 2 `cot`, một cột thì không so gì"))
        return
    if len(cot) > 5:
        out.append(("CANH BAO", tag,
                    f"{len(cot)} cột trên sân diễn rộng 960px — nhãn cột sẽ "
                    f"dính nhau. Gộp bớt hoặc tách hai cảnh"))
    gia = []
    for i, c in enumerate(cot):
        if "gia" not in c:
            out.append(("LOI", tag, f"cột {i} thiếu `gia` (số, để tính chiều cao)"))
            gia.append(0.0)
            continue
        try:
            gia.append(float(c["gia"]))
        except (TypeError, ValueError):
            out.append(("LOI", tag,
                        f"cột {i} có `gia: {c['gia']!r}` không phải số"))
            gia.append(0.0)
        if not c.get("nhan"):
            out.append(("CANH BAO", tag, f"cột {i} thiếu `nhan`, người xem "
                                         f"không biết cột đó là gì"))
    duong = [g for g in gia if g > 0]
    kieu = str(sp.get("thang", "tuyen")).lower()
    if kieu == "log" and any(g <= 0 for g in gia):
        out.append(("LOI", tag,
                    "`thang: log` mà có cột `gia` bằng 0 hoặc âm — log không "
                    "biểu diễn được, cột đó sẽ cao 0"))
    if duong:
        ty = max(duong) / min(duong)
        if ty > 60 and kieu != "log":
            out.append(("CANH BAO", tag,
                        f"cột lớn nhất gấp {ty:,.0f} lần cột nhỏ nhất mà trục "
                        f"tuyến tính — cột nhỏ sẽ cao dưới một pixel, tức biến "
                        f"mất. Đặt `thang: log`".replace(",", ".")))
        if ty < 1.25 and len(duong) > 1:
            out.append(("CANH BAO", tag,
                        f"cột cao nhất chỉ hơn cột thấp nhất {ty:.2f} lần — "
                        f"mắt không đọc ra chênh lệch, cảnh này không nói gì"))
    tl = sp.get("ty_le")
    if tl:
        for ten in ("a", "b"):
            v = tl.get(ten)
            if v is None or not 0 <= int(v) < len(cot):
                out.append(("LOI", tag,
                            f"`ty_le.{ten}: {v}` nằm ngoài danh sách "
                            f"{len(cot)} cột (0..{len(cot) - 1})"))
        if not tl.get("nhan"):
            out.append(("CANH BAO", tag,
                        "`ty_le` không có `nhan` nên vẽ một cái ngoặc trống"))
    # `cool` KHONG tinh vao so mau: trong bang mau cua theme no la "luong
    # chinh", tuc vai tro TRUNG TINH - dung cho cot MOC, cai cot khong phai
    # dung cung khong phai sai. So 96 co dung ba mau va ca ba deu dung viec:
    # cool cho moc, hot cho cau hinh yeu hon, ok cho cau hinh chac hon. Dem ca
    # `cool` vao thi luat nay bao tren mot canh viet dung, va mot luat bao nham
    # deu deu thi nguoi ta bo qua luon nhung lan bao dung.
    mau = {str(c.get("color", "")).lower() for c in cot}
    mau.discard("")
    mau.discard("cool")
    if len(mau) > 2:
        out.append(("CANH BAO", tag,
                    f"{len(mau)} màu khác nhau (chưa tính `cool` là màu mốc) — "
                    f"trong theme này màu là ngôn ngữ (`hot` sai, `ok` đúng), "
                    f"quá hai màu là mất tiêu điểm"))


def check_thac(sp, idx, out):
    """`thac` ke chuyen BAC THANG: moi hang cho hang tren xong moi chay.

    Nen phep kiem chinh la kiem tinh bac thang. Neu cac hang chay chong lan
    nhau thi hinh dang tro thanh mot khoi dac, va khoi dac thi noi dieu NGUOC
    lai: rang chung chay song song, tuc khong ai phai cho ai.
    """
    tag = f"cảnh {idx:02d} thac"
    hang = sp.get("hang") or []
    if len(hang) < 3:
        out.append(("LOI", tag,
                    f"chỉ {len(hang)} hàng — dưới ba bậc thì không thành bậc "
                    f"thang, dùng `gantt` hai lane cho rõ hơn"))
    if len(hang) > 14:
        out.append(("CANH BAO", tag,
                    f"{len(hang)} hàng nhưng chỉ 14 hàng đầu được vẽ — phần "
                    f"còn lại nên gộp thành một hàng kèm `con:`"))
    truoc_end, truoc_ten = None, None
    for i, h in enumerate(hang[:14]):
        try:
            at, w = float(h.get("at", 0.0)), float(h.get("w", 0.08))
        except (TypeError, ValueError):
            out.append(("LOI", tag, f"hàng {i} có `at`/`w` không phải số"))
            continue
        ten = str(h.get("nhan", "?"))
        if at < 0 or at + w > 1.0001:
            out.append(("LOI", tag,
                        f"`{ten}` chạy tới {at + w:.2f} — tràn ra ngoài trục "
                        f"(at + w phải ≤ 1.0)"))
        if len(ten) > 30:
            out.append(("CANH BAO", tag,
                        f"`nhan` của hàng {i} dài {len(ten)} ký tự, máng trái "
                        f"chỉ vẽ 30 ký tự đầu — viết ngắn hơn"))
        if truoc_end is not None and at < truoc_end - 0.02 \
                and not sp.get("chong_lan"):
            out.append(("CANH BAO", tag,
                        f"`{ten}` bắt đầu ở {at:.2f} khi `{truoc_ten}` chưa "
                        f"xong ({truoc_end:.2f}) — hai hàng chồng lấn thì hình "
                        f"nói NGƯỢC lời đọc: chúng đang chạy song song, không "
                        f"ai chờ ai. Đúng ý thì đặt `chong_lan: true`"))
        truoc_end, truoc_ten = at + w, ten
    xau = [i for i, h in enumerate(hang[:14]) if h.get("bad")]
    if len(xau) > 1:
        out.append(("CANH BAO", tag,
                    f"{len(xau)} hàng đánh `bad` — mỗi cảnh chỉ nên một hàng "
                    f"đỏ, không thì mất tiêu điểm"))
    tong = sp.get("tong")
    if tong:
        try:
            float(tong.get("gia", 0))
        except (TypeError, ValueError):
            out.append(("LOI", tag,
                        f"`tong.gia: {tong.get('gia')!r}` không phải số — đồng "
                        f"hồ không đếm lên được"))
    else:
        out.append(("CANH BAO", tag,
                    "không có `tong` nên cảnh mô phỏng này không có con số nào "
                    "đang đổi — xem docstring đầu bench.py"))


def check_ban_sao(sp, idx, out):
    """`ban_sao` song nho O SU THAT. Bo no di thi canh chi la `counters` dong.

    Phep kiem quan trong nhat o day: co `that` hay khong. Ba o cung dem len ma
    khong co con so su that ben canh thi nguoi xem thay ba con so nho nho va
    khong thay chuyen gi sai - dung cai bay ma canh nay sinh ra de chua.
    """
    tag = f"cảnh {idx:02d} ban_sao"
    o = sp.get("o") or []
    if len(o) < 2:
        out.append(("LOI", tag, "cần ít nhất 2 `o`, một bản sao thì không có "
                                "chuyện gì để kể"))
    if len(o) > 4:
        out.append(("CANH BAO", tag,
                    f"{len(o)} ô nhưng chỉ 4 ô đầu được vẽ — bốn ô đã là mức "
                    f"mà mỗi ô còn đọc được số"))
    for i, oo in enumerate(o[:4]):
        buoc = oo.get("buoc") or []
        if not buoc:
            out.append(("LOI", tag, f"ô {i} không có `buoc`, giá trị sẽ trống"))
            continue
        ats = [float(x.get("at", 0.0)) for x in buoc]
        if ats != sorted(ats):
            out.append(("LOI", tag,
                        f"ô {i} có `at` không tăng dần {ats} — giá trị sẽ nhảy "
                        f"sai thứ tự"))
        if not oo.get("nhan"):
            out.append(("CANH BAO", tag, f"ô {i} thiếu `nhan`"))
    if not sp.get("that"):
        out.append(("CANH BAO", tag,
                    "thiếu ô `that` — không có con số sự thật bên cạnh thì ba "
                    "bộ đếm nhỏ không nói lên điều gì sai, và cảnh này thành "
                    "một `counters` biết chạy"))
    if not sp.get("ruler"):
        out.append(("CANH BAO", tag,
                    "thiếu `ruler` nên các ô đổi số mà người xem không biết "
                    "đang ở giây thứ bao nhiêu"))


def check_gop(sp, idx, out):
    """`gop`: hai dau vao KHAC NHAU ra mot ket qua. Chu KHAC NHAU la ban le.

    Bay da thay ngay o ban thu dau tien: hai the dau vao deu ghi
    `d131dd02c5e6eec4...` vi cat cung mot so ky tu dau. Tren man hinh chung
    GIONG HET nhau, nen ca canh mat sach y - nguoi xem thay hai the giong nhau
    ra mot ket qua, chuyen do hoan toan binh thuong.
    """
    tag = f"cảnh {idx:02d} gop"
    vao = sp.get("vao") or []
    if len(vao) < 2:
        out.append(("LOI", tag, "cần ít nhất 2 `vao`, một đầu vào thì không "
                                "có gì trùng nhau"))
        return
    if len(vao) > 3:
        out.append(("CANH BAO", tag,
                    f"{len(vao)} đầu vào nhưng chỉ 3 cái đầu được vẽ"))
    if not sp.get("ra"):
        out.append(("LOI", tag, "thiếu `ra`, không có kết quả để gộp về"))
    val = [str(v.get("value", "")) for v in vao[:3]]
    if len(set(val)) == 1:
        out.append(("LOI", tag,
                    f"mọi `vao.value` hiện y hệt nhau trên màn hình "
                    f"(`{val[0]}`) — cả cảnh nói rằng hai đầu vào KHÁC nhau mà "
                    f"cho ra một kết quả, nên phải cho thấy chỗ chúng khác. "
                    f"Cắt đoạn chứa byte khác nhau, hoặc bôi đậm phần lệch"))
    if not sp.get("khac"):
        out.append(("CANH BAO", tag,
                    "không có thẻ `khac` (đối chứng) — nó là chỗ cho thấy lỗi "
                    "không nằm ở đầu vào mà ở phép biến đổi"))


CANH_KIN = {"probe", "gantt", "queue", "topology", "multiply", "code",
            "cot", "thac", "ban_sao", "gop"}


def check_prop(sp, idx, out):
    """Dao cu ve DE LEN canh, nen canh nao chiem het san thi no cham vao chu.

    Da thay: dao cu `trinh_duyet` gan vao canh `probe`, nhan cua no de len chu
    `status` o goc tren phai cua khung console.
    """
    if not sp.get("prop"):
        return
    if sp.get("scene") in CANH_KIN:
        out.append(("CANH BAO", f"cảnh {idx:02d}",
                    f"gắn đạo cụ vào cảnh `{sp['scene']}` — loại cảnh này chiếm "
                    f"hết sân diễn nên đạo cụ sẽ đè lên nội dung. Chuyển sang "
                    f"cảnh `statement`, `list` hoặc `ask`"))


def check_chua_xong(doc, out):
    """Chan khung tu sinh khong cho lot vao ban render.

    `research/sinh_khung.py` sinh khung cho ca 90 so, moi khung deu co
    `chua_xong: true` va mot loat o trong `{{SO}}` o dung nhung cho can so do.
    Hai dau hieu do la LOI chu khong phai canh bao: mot khung ma render duoc thi
    no se ra mot video doc "hai ngoac nhon SO hai ngoac nhon" suot bay canh.
    """
    if doc.get("chua_xong"):
        out.append(("LOI", "doc",
                    "screenplay còn `chua_xong: true` — đây là khung tự sinh, "
                    "chưa có số đo và chưa có lời đọc. Làm xong rồi xoá dòng đó"))
    n = 0

    def dem(o):
        nonlocal n
        if isinstance(o, str):
            n += o.count("{{SO}}")
        elif isinstance(o, dict):
            for v in o.values():
                dem(v)
        elif isinstance(o, list):
            for v in o:
                dem(v)
    dem(doc)
    if n:
        out.append(("LOI", "doc",
                    f"còn {n} chỗ `{{{{SO}}}}` chưa thay bằng số đo được"))


# --- CONG KE CHUYEN -------------------------------------------------------
#
# Muoi hai phep kiem duoi day khong soi mot canh, chung soi CA CHUOI CANH: thu
# tu nhip, cho dat thu pham, ty le mo phong, cau hoi cuoi. Tuc chung kiem cai ma
# `CONG-THUC.md` goi la khung nhip, con moi phep kiem le o tren thi kiem bo cuc.
#
# Vi sao tach thanh mot nhom rieng: mot screenplay co the SACH het moi phep kiem
# bo cuc ma van la mot bai giang chia thanh slide - khong co gi gay, khong co gi
# tran, va cung khong co gi de nguoi xem to mo. Cai do khong phep kiem le nao
# bat duoc, vi no nam o QUAN HE giua cac canh.
#
# BA phep la LOI, va ca ba deu chi ma hoa lai dieu `CONG-THUC.md` da ghi la
# tuyet doi tu truoc, khong phai luat moi:
#   "Mo bang loi chao        -> mat 4 giay dat nhat cua video"
#   "Noi ten benh o nhip 1   -> mat sach cang thang, con lai la bai giang"
#   "Cau hoi cuoi chung chung -> khong ai tra loi"
# Phan con lai la CANH BAO, vi chung phu thuoc dinh dang: dinh dang HAI DOAN
# CODE (mua 3) co y khong co canh mo phong dong va khong co nhip thu pham.

# Canh mo phong DONG: co thu gi dang chay theo thoi gian (dau doc, bo dem,
# duong cong, goi tin). `probe` `compare` `counters` KHONG nam day - chung la
# bang chung TINH, va nhip RECONSTRUCTION doi mot thu dang chuyen dong.
CANH_DONG = {"gantt", "thac", "multiply", "queue", "cot", "topology",
             "ban_sao", "gop",           # theme bench
             "race", "decay", "flow", "timeline"}   # ba theme cu

# Cum mo dau bi cam. Do bang chinh loi doc cua canh dau tien.
MO_CAM = ("bạn có biết", "trong video này", "hôm nay chúng ta",
          "hôm nay mình", "có bao giờ bạn tự hỏi", "xin chào",
          "chào mọi người", "chào các bạn", "mình sẽ giới thiệu",
          "chúng ta sẽ tìm hiểu", "chúng ta sẽ học")

# Cum ket bi cam: cau hoi khong ve he thong cua nguoi xem thi khong ai tra loi.
KET_CAM = ("bạn nghĩ sao", "các bạn nghĩ sao", "ý kiến của bạn",
           "comment bên dưới", "để lại bình luận", "đừng quên like")


def _canh_thu_pham(scenes):
    """Chi so canh goi ten thu pham, hoac None. Doc theo `chapter` va `label`."""
    for i, sp in enumerate(scenes):
        for k in ("chapter", "label"):
            if "THỦ PHẠM" in str(sp.get(k, "")).upper():
                return i
    return None


def check_cong(doc, out):
    scenes = doc.get("scenes") or []
    if doc.get("chua_xong") or len(scenes) < 3:
        return
    kinds = [sp.get("scene") for sp in scenes]
    n = len(scenes)
    tag = "cổng kể chuyện"

    # 1. Mo dau. LOI - xem CONG-THUC.md bang "Loi thuong gap".
    n1 = (scenes[0].get("narration") or "").lower()
    for cum in MO_CAM:
        if cum in n1:
            out.append(("LOI", tag,
                        f"cảnh 01 mở bằng `{cum}` — bốn giây đắt nhất của video "
                        f"thành lời dẫn. Nhịp 1 phải là chính cái LỖI"))

    # 2. Cau hoi cuoi. LOI neu chung chung, CANH BAO neu khong ve nguoi xem.
    hoi = [sp for sp in scenes if sp.get("scene") in ("ask", "qa")]
    if not hoi:
        out.append(("CANH BAO", tag,
                    "không có cảnh `ask` chốt — mất nhịp 7, tức mất chỗ đẩy "
                    "người xem về bình luận"))
    else:
        cuoi = hoi[-1]
        txt = ((cuoi.get("narration") or "") + " "
               + str(cuoi.get("text") or "")).lower()
        for cum in KET_CAM:
            if cum in txt:
                out.append(("LOI", tag,
                            f"câu hỏi cuối dùng `{cum}` — câu hỏi chung chung "
                            f"thì không ai trả lời. Hỏi về hệ thống CỦA CHÍNH "
                            f"người xem"))
        if "của bạn" not in txt and "của mình" not in txt:
            out.append(("CANH BAO", tag,
                        "câu hỏi cuối không nhắc tới hệ thống của người xem "
                        "(`của bạn`) — nó đang hỏi về chủ đề, không hỏi về họ"))
        if kinds[-1] not in ("ask", "qa"):
            out.append(("CANH BAO", tag,
                        f"cảnh cuối là `{kinds[-1]}` chứ không phải `ask` — "
                        f"câu hỏi chốt nên là thứ cuối cùng người xem thấy"))

    # 3. Thu pham phai goi SAU mo phong. LOI.
    dong = [i for i, k in enumerate(kinds) if k in CANH_DONG]
    thu = _canh_thu_pham(scenes)
    if thu is not None and dong and thu < dong[0]:
        out.append(("LOI", tag,
                    f"gọi tên thủ phạm ở cảnh {thu + 1} nhưng mô phỏng mới ở "
                    f"cảnh {dong[0] + 1} — đặt tên trước khi cho xem là mất "
                    f"sạch căng thẳng, phần còn lại thành bài giảng"))

    # 4. Nhip RECONSTRUCTION. Canh bao chu khong loi: dinh dang HAI DOAN CODE
    #    (mua 3) co y khong co canh mo phong dong, no dung `code` + `probe`.
    if not dong:
        thay_the = "code" in kinds or "probe" in kinds
        out.append(("CANH BAO", tag,
                    "không có cảnh mô phỏng ĐỘNG nào (gantt, thac, multiply, "
                    "queue, cot, topology, ban_sao, gop) — nhịp dựng lại hiện "
                    "trường đang được KỂ chứ không được CHO XEM"
                    + (". Nếu đây là định dạng HAI ĐOẠN CODE thì bỏ qua"
                       if thay_the else "")))
    else:
        # Do theo DO DAI LOI DOC, khong theo so canh. Ly do: `CONG-THUC.md` nham
        # 35-40% THOI LUONG, ma thoi luong canh do pipeline tinh tu do dai audio,
        # con do dai audio thi ty le voi so ky tu. Dem so canh la do sai don vi.
        #
        # Do doi chieu tren `cache-stale` cho thay proxy nay dung: 2/13 canh la
        # 15% neu dem canh, nhung 25% neu dem ky tu - va so do THAT tu log render
        # la 23% thoi luong. Dem canh thi lech 8 diem, dem ky tu thi lech 2.
        #
        # Nguong 20%: duoi muc cua MOI file da duyet co canh mo phong
        # (cache-stale 25%, n-plus-one 24%, async 25%, pool-can 32%).
        tong = sum(len(sp.get("narration") or "") for sp in scenes)
        chu = sum(len(scenes[i].get("narration") or "") for i in dong)
        if tong and chu / tong < 0.20:
            out.append(("CANH BAO", tag,
                        f"nhịp mô phỏng chỉ chiếm {chu / tong:.0%} lời đọc "
                        f"({len(dong)}/{n} cảnh) — thấp hơn mọi bản đã duyệt "
                        f"(`cache-stale` 25%, `pool-can` 32%), và công thức nhắm "
                        f"35–40%. Cách sửa là VIẾT THÊM lời đọc cho cảnh mô "
                        f"phỏng, đừng đóng cứng `min_duration`"))

    # 5. Bao nhieu quy tac la nhieu. Nguong la BA, khong phai HAI - va cho nay
    #    chinh la mot bay: `CONG-THUC.md` nhip 6 viet "dung MOT quy tac", nhung
    #    mau dien cua bien the HOOK 5 NHIP o cuoi CHINH FILE DO lai co `rule 01`
    #    (quy tac chan) va `rule 02` (luoi cuoi). Hai canh la cau truc DA DUYET
    #    cua `cache-stale`, nen bao o muc hai la bao tren mot file dung.
    #    Ban dau toi dat nguong 1 va no keu ngay tren file tham chieu.
    n_rule = kinds.count("rule") + kinds.count("sticky")
    if n_rule >= 3:
        out.append(("CANH BAO", tag,
                    f"{n_rule} cảnh quy tắc — CONG-THUC.md nhịp 6: đúng MỘT "
                    f"quy tắc chặn, cộng tối đa một `lưới cuối`. Ba quy tắc thì "
                    f"người xem không nhớ nổi cái nào"))

    # 6. Ve "phat hien som". Day la nua bi bo quen nhieu nhat cua nhip 6, va la
    #    ly do mid-level luu video lai.
    if n_rule and not any(
            "phát hiện sớm" in str(sp.get("small") or "").lower()
            for sp in scenes if sp.get("scene") in ("rule", "sticky")):
        out.append(("CANH BAO", tag,
                    "cảnh quy tắc không có vế `phát hiện sớm` trong `small` — "
                    "một quy tắc chặn mà không có chỉ số nào để theo dõi thì "
                    "người xem không biết mình đang dính hay không"))

    # 7. Don dieu. Hai phep kiem duoi day dem DANG BONG, khong dem TEN LOAI
    #    CANH - va do la mot phan biet phai giu cho dung.
    #
    #    Ly do: `research/do_don_dieu.py` do dang bong cua tung khung hinh (blur
    #    test) va cho thay hai canh `statement` trong cung mot video cach nhau
    #    0,042 tren thang 0..1, tuc gan nhu trung. Nguyen nhan la mot dong code:
    #    khoi chu luon can giua san dien. Sau khi them `neo: tren|duoi`, cung
    #    hai canh do cach nhau 0,112 - gap gan ba lan. Cung mot LOAI canh, cung
    #    mot noi dung, nhung khac dang bong.
    #
    #    Nen (loai, neo) moi la don vi dung. Dem theo `scene` khong thi phep
    #    kiem se bat mot van de da duoc chua, va bo qua hai canh khac loai ma
    #    van cung mot cuc chu o giua.
    def bong(sp):
        k = sp.get("scene")
        if k in ("statement", "bigstat", "ask", "rule", "sticky"):
            return f"{k}/{str(sp.get('neo', 'giua')).lower()}"
        return k

    dang = [bong(sp) for sp in scenes]

    #    Hai canh LIEN TIEP cung dang bong. Nguong la HAI, khong phai ba - nhung
    #    CHI ap cho canh khong phai mo phong. Hai canh mo phong lien tiep giu Y
    #    NGUYEN bo cuc la ky thuat manh nhat cua repo (`cache-stale` va
    #    `async-song-song` deu dung), nen bao o do la bao tren mot file dung.
    for i in range(1, n):
        if dang[i] == dang[i - 1] and kinds[i] not in CANH_DONG:
            out.append(("CANH BAO", tag,
                        f"cảnh {i} và {i + 1} cùng một dạng bóng "
                        f"(`{dang[i]}`) — hai khung hình liên tiếp trông như "
                        f"nhau. Đổi loại cảnh, hoặc đổi `neo` của một trong hai"))
    #    Mot dang bong chiem qua mot phan tu tong so canh.
    from collections import Counter
    for d, c in Counter(dang).items():
        if n and c / n > 0.25 and c >= 3:
            out.append(("CANH BAO", tag,
                        f"dạng bóng `{d}` chiếm {c}/{n} cảnh ({c / n:.0%}) — "
                        f"nhắm một phần tư. Đổi `neo` cho một hai cảnh, hoặc "
                        f"hỏi lại xem cảnh đó có phải một `compare` bị nén không"))


def check(doc):
    out = []
    check_cong(doc, out)
    check_chua_xong(doc, out)
    check_cau_dai(doc, out)
    check_tu_la(doc, out)
    check_yaml_cat(doc, out)
    engine = doc.get("engine", "voicestudio")
    # Ten canh KHONG duy nhat giua cac theme: `phongtoi` cung co `topology` va
    # `compare` nhung schema khac han (nodes co toa do `at`, co `packets`). Chay
    # kiem tra cua bench len file phongtoi thi bao loi hang loat va sai het.
    bench = doc.get("theme") == "bench"
    for i, sp in enumerate(doc.get("scenes", []), 1):
        if bench and sp.get("scene") == "gantt":
            check_gantt(sp, i, out)
        elif bench and sp.get("scene") == "queue":
            check_queue(sp, i, out)
        elif bench and sp.get("scene") == "topology":
            check_topology(sp, i, out)
        elif bench and sp.get("scene") == "cot":
            check_cot(sp, i, out)
        elif bench and sp.get("scene") == "thac":
            check_thac(sp, i, out)
        elif bench and sp.get("scene") == "ban_sao":
            check_ban_sao(sp, i, out)
        elif bench and sp.get("scene") == "gop":
            check_gop(sp, i, out)
        if bench:
            check_kieu_chu(sp, i, out)
        check_caption(sp, i, out)
        check_tag(sp, i, out)
        check_narration(sp, i, out, engine)
        check_doc_ro(sp, i, out, engine)
        if bench:
            check_prop(sp, i, out)
    return out


def report(doc, prefix="  "):
    """In ket qua. Tra ve so LOI (de goi y co nen dung lai hay khong)."""
    found = check(doc)
    if not found:
        print(f"{prefix}kiểm tra screenplay: không thấy gì đáng ngờ")
        return 0
    nerr = sum(1 for k, _, _ in found if k == "LOI")
    print(f"{prefix}kiểm tra screenplay: {nerr} lỗi, "
          f"{len(found) - nerr} cảnh báo")
    for kind, where, msg in found:
        print(f"{prefix}  [{kind:8s}] {where}: {msg}")
    return nerr


# --- do dai MOT LAN SINH, va tu la chua phien am -----------------------------
#
# Ca hai loi duoi day do NGUOI XEM nghe ra o so 72, khong phai tu suy dien:
#
#   canh 2  "khong mot dong log do"   -> `log` chua co trong TU_DIEN, model tu
#           doan cach doc mot tu ngan va la nam giua dong chay tieng Viet.
#   canh 5  "...duoi dang chuoi ky tu, nhung thu vien..."  -> cau do 132 ky tu.
#
# CAU_DAI = 110 lay tu du lieu chu khong dat bua: trong 38 loi doc cua
# cache-stale ma nguoi xem DA DUYET, cau dai nhat la 107 ky tu. Mode `tach` sinh
# MOI CAU bang mot lan goi model rieng, nen do dai mot cau CHINH LA do dai mot
# lan sinh - vuot khoi khoang da duoc duyet thi chat luong troi ve cuoi cau.
CAU_DAI = 110


def _cac_cau(t):
    """Cat loi doc Y HET cach speak.py cat, de dem dung do dai mot lan sinh."""
    try:
        import vitext   # cung thu muc src/, khong con tro sang repo khac
        return vitext.prepare(t)
    except Exception:
        return [c.strip() for c in re.split(r"(?<=[.!?])\s+", t) if c.strip()]


def _sau_phien_am(doc, n):
    if not doc.get("phien_am"):
        return n
    try:
        import phienam
        return phienam.phien_am(n)
    except Exception:
        return n


def check_cau_dai(doc, out):
    if doc.get("theme") != "bench":
        return
    for i, sp in enumerate(doc.get("scenes") or [], 1):
        n = sp.get("narration")
        if not n:
            continue
        for c in _cac_cau(_sau_phien_am(doc, n)):
            if len(c) > CAU_DAI:
                out.append(("LOI", f"canh {i}",
                            f"mot cau dai {len(c)} ky tu (nguong {CAU_DAI}, "
                            f"dai nhat trong ban da duyet la 107). Mode tach "
                            f"sinh moi cau mot lan goi model, cau dai thi chat "
                            f"luong troi ve cuoi. Cat lam hai: {c[:55]}..."))


def check_tu_la(doc, out):
    """Tu khong phai am tiet Viet va CHUA duoc quyet dinh trong phienam.py.

    GOI THANG `phienam.tu_la()` chu khong tu do lai. Ban truoc do lai bang mot
    vong lap rieng va no SAI: no ha chu ve chu thuong (`w.lower()`) roi tra
    trong `TU_DIEN`, nhung khoa cua `TU_DIEN` viet HOA cho moi viet tat (`API`
    `TTL` `SQL` `MD5`...). Nen moi viet tat DA khai trong tu dien deu bi bao la
    "chua khai", con `tu_la()` thi so bang chu hoa nen khong bao.

    Loi nay im lang tu dau vi ba screenplay duyet dau tien chua bat `phien_am`,
    va 70 khung tu sinh thi `narration` con la `{{SO}}`. No lo ra o so 91 - file
    dau tien vua bat `phien_am` vua co viet tat trong loi doc.

    Bai hoc chung: co MOT cho quyet dinh mot tu la la hay khong. Hai cho thi
    truoc sau gi cung lech, va cho lech se lech ve phia bao nham - tuc phia lam
    nguoi viet bo qua ca nhung canh bao that.
    """
    if doc.get("theme") != "bench" or not doc.get("phien_am"):
        return
    try:
        import phienam
    except Exception:
        return
    for i, sp in enumerate(doc.get("scenes") or [], 1):
        n = sp.get("narration")
        if not n:
            continue
        for w in sorted(set(phienam.tu_la(n)), key=str.lower):
            out.append(("NGO", f"canh {i}",
                        f"{w!r} chua co trong TU_DIEN cung chua trong "
                        f"GIU_GOC - model se tu doan cach doc. Quyet dinh "
                        f"trong src/phienam.py truoc khi render."))


def main():
    import yaml
    if len(sys.argv) < 2:
        raise SystemExit("dùng: python src/lint.py screenplays/<file>.yaml "
                         "[--engine voicestudio]")
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    # Phep kiem narration chi ap cho engine voicestudio, nen phai ghi de duoc tu
    # dong lenh - khong thi khong test duoc ma cung khong soi truoc duoc.
    if "--engine" in sys.argv:
        doc["engine"] = sys.argv[sys.argv.index("--engine") + 1]
    sys.exit(1 if report(doc, prefix="") else 0)


if __name__ == "__main__":
    main()


def main():
    """CLI. PHAI ton tai va PHAI thoat khac 0 khi co LOI.

    Truoc do file nay khong con `main()`: `python src/lint.py <file>` chi nap
    module roi thoat 0, khong kiem gi ca. Nguy hiem hon la khong co CLI, vi day
    la lenh dau tien trong quy trinh o VIET-KICH-BAN.md - no bao "sach" cho moi
    thu, ke ca 70 khung tu sinh con nguyen `{{SO}}`. Da mot lan dung chinh no de
    "xac minh" 20 so da xong, va ket qua do vo nghia.

    Chot chan luc render (`render.py` goi `lint.report`) van song, nhung no chi
    IN ra loi roi chay tiep tru khi co `--strict`.
    """
    import yaml
    args = [x for x in sys.argv[1:] if not x.startswith("-")]
    if not args:
        raise SystemExit(
            "dung: python src/lint.py screenplays/<file>.yaml [--engine voicestudio]\n"
            "      thoat 1 neu co LOI, 0 neu chi co canh bao")
    with open(args[0], "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    # Phep kiem narration chi ap cho engine voicestudio nen phai ghi de duoc tu
    # dong lenh, khong thi khong soi truoc duoc ma cung khong test duoc.
    if "--engine" in sys.argv:
        doc["engine"] = sys.argv[sys.argv.index("--engine") + 1]
    sys.exit(1 if report(doc, prefix="") else 0)


if __name__ == "__main__":
    main()
