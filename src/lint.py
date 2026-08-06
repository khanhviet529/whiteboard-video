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

    python src/lint.py screenplays/cache-stale.yaml
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


def check_narration(sp, idx, out, engine):
    """Bay doc sai cua engine `omnivoice` - CHI kiem khi dung engine do.

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

    Chi bao khi engine la `omnivoice`: edge-tts doc ca doan mot lan nen cau ngan
    khong sinh van de nao.
    """
    if engine != "omnivoice":
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
                        f"omnivoice nén viết tắt cuối câu; đổi vào giữa câu"))
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
        sys.path.insert(0, os.path.join("D:", os.sep, "omnivoice-test"))
        import vitext
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
    if engine != "omnivoice":
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
            "cap_label", "depth_key", "counter_key", "chip", "miss_tag")


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


def check(doc):
    out = []
    check_yaml_cat(doc, out)
    engine = doc.get("engine", "edge")
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
        if bench:
            check_kieu_chu(sp, i, out)
        check_caption(sp, i, out)
        check_narration(sp, i, out, engine)
        check_doc_ro(sp, i, out, engine)
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


def main():
    import yaml
    if len(sys.argv) < 2:
        raise SystemExit("dùng: python src/lint.py screenplays/<file>.yaml "
                         "[--engine omnivoice]")
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    # Phep kiem narration chi ap cho engine omnivoice, nen phai ghi de duoc tu
    # dong lenh - khong thi khong test duoc ma cung khong soi truoc duoc.
    if "--engine" in sys.argv:
        doc["engine"] = sys.argv[sys.argv.index("--engine") + 1]
    sys.exit(1 if report(doc, prefix="") else 0)


if __name__ == "__main__":
    main()
