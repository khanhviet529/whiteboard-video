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


def check(doc):
    out = []
    engine = doc.get("engine", "edge")
    for i, sp in enumerate(doc.get("scenes", []), 1):
        if sp.get("scene") == "gantt":
            check_gantt(sp, i, out)
        check_caption(sp, i, out)
        check_narration(sp, i, out, engine)
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
