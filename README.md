# whiteboard-video

Tool dựng video giải thích kiến thức lập trình bằng tiếng Việt từ một file
screenplay YAML. Ra mp4 dọc 1080×1920 kèm giọng thuyết minh — đăng thẳng
TikTok / Reels / Shorts.

```bash
python src/render.py screenplays/cache-invalidation.yaml
# -> out/cache-invalidation.mp4
```

## Ba theme

| `theme:` | Trông thế nào | Dùng khi |
|---|---|---|
| **`phongtoi`** *(chính thức của kênh)* | Nền xanh đêm ba tầng bề mặt, lưới hairline, hạt nhiễu, nhãn mono có tracking, chữ căn lề trái tracking âm, vệt sáng quanh phần tử tiêu điểm. Hé lộ bằng mask trượt lên; chuyển cảnh bằng bóng tối quét qua có vạch sáng dẫn đầu. | Sản xuất chính. |
| `brutalist` | Khối màu phẳng, viền đen dày, bóng lệch cứng, chữ Phudu cực lớn. | Bản trung gian, giữ để đối chiếu. |
| `whiteboard` | Nét vẽ tay xiêu xiêu, nền giấy kem lưới chấm. | Bản đầu tiên. Tên repo còn sót từ giai đoạn này. |

Đổi theme không phải sửa nội dung — cùng một screenplay chạy được cả ba:

```bash
python src/render.py screenplays/double-charge.yaml --theme brutalist
```

## Mã màu theo mảng

Khai báo `domain:` ở đầu screenplay (hoặc trên từng cảnh). Badge góc trên trái
tô đúng màu mảng, nên xem 0,5 giây là biết video thuộc mảng nào:

| `domain:` | Badge | Màu |
|---|---|---|
| `fe` | FRONTEND | vàng |
| `be` | BACKEND | xanh lá |
| `database` | DATABASE | xanh dương |
| `infra` | HẠ TẦNG | tím |

Màu đỏ `ALERT` **không** thuộc mảng nào — nó dành riêng cho "đây là chỗ sai",
nên khối lỗi luôn đỏ ở cả bốn mảng. Đó là lý do badge phải tô đầy màu mảng chứ
không chỉ viền: nếu không, bốn mảng nhìn gần như y nhau.

## Một điểm nhấn mỗi cảnh

Theme brutalist tự áp quy tắc: **mỗi cảnh chỉ một khối được tô màu**, mọi khối
còn lại tô trắng và chữ xám nhạt. Screenplay không phải khai báo gì; muốn chỉ
định khối nào là điểm nhấn thì thêm `focus: true` vào item đó.

---

## Cài đặt

**Không cần cài gì.** Toàn bộ phụ thuộc đã có sẵn trong Python trên máy này:
`PIL`, `numpy`, `yaml`, `edge_tts`, `imageio_ffmpeg` (kèm luôn bản ffmpeg riêng
nên không cần ffmpeg trên PATH).

Python ở `D:\Downloads\Python311\python.exe` (không có trên PATH — gọi full path).

Font nằm trong `assets/fonts/`, lấy từ repo `google/fonts`, cả 3 đã kiểm tra
render đủ dấu tiếng Việt:

| Vai trò | Font |
|---|---|
| Tiêu đề, số lớn | Playpen Sans (variable, wght 700/800) |
| Thân chữ, phụ đề, nhãn | Patrick Hand |
| Code | JetBrains Mono |

---

## Cách dùng

```bash
# render full ra mp4 (có giọng đọc)
python src/render.py screenplays/cache-invalidation.yaml

# xuất 1 PNG mỗi cảnh để soi bố cục — dùng cái này khi chỉnh style
python src/render.py screenplays/cache-invalidation.yaml --stills

# chỉ 1 cảnh
python src/render.py screenplays/cache-invalidation.yaml --stills --scene 7

# render nhanh không gọi TTS (thời lượng lấy từ `duration:` trong YAML)
python src/render.py screenplays/cache-invalidation.yaml --no-audio

# ghép bảng tổng tất cả cảnh vào 1 ảnh để soi toàn cục
python research/contact_sheet.py
```

Vòng làm việc nên theo: `--stills` → soi → sửa YAML/style → `--stills` lại →
khi hài lòng mới render full.

---

## Công thức kể

Xem [CONG-THUC.md](CONG-THUC.md) — định dạng **HIỆN TRƯỜNG VỤ ÁN**: khung 7 nhịp,
quy tắc từng nhịp, lỗi thường gặp, mẫu điền. Screenplay
[double-charge.yaml](screenplays/double-charge.yaml) là bản mẫu bám đúng công thức.

Điều quan trọng nhất của công thức: **nhịp mô phỏng phải chiếm 35–40% video**.
Đó là chỗ tool này hơn người dựng tay — không ai animate lại một race condition
trong CapCut cho từng video, còn ở đây nó là code, viết một lần chạy mãi.

## Screenplay

Một file YAML. Mỗi cảnh có `scene` (loại cảnh) và `narration` (lời đọc).
**Thời lượng cảnh tự tính từ độ dài giọng đọc** — không phải canh tay.

```yaml
title: Cache xoá lúc nào?
voice: female        # female = HoaiMy | male = NamMinh
rate: "+6%"          # tốc độ đọc

scenes:
  - scene: timeline
    narration: Giữa hai việc có một khe hở.
    marks:
      - { at: 0.28, label: XOÁ CACHE, color: amber }
      - { at: 0.74, label: GHI DATABASE, color: blue }
    gap: { from: 0.28, to: 0.74, label: KHE HỞ, note: 5MS, color: red }
    intruder: REQUEST KHÁC
```

`caption` (phụ đề dưới) mặc định lấy luôn `narration`; ghi đè nếu muốn khác.
`chips` vẽ dãy nhãn tiến độ ở góc trên phải: `- { label: THỨ TỰ, color: blue, done: true }`

### 11 loại cảnh

| `scene` | Dùng để | Trường chính |
|---|---|---|
| `title` | Tiêu đề chương | `text`, `sub`, `underline`, `strike`, `color` |
| `bigstat` | Một con số / một câu đập vào mặt | `value`, `sub`, `circle` |
| `compare` | Hai hộp giá trị xếp dọc, so sánh | `items[{label,value,color,cross,note}]`, `arrow`, `verdict` |
| `flow` | Chuỗi bước nối bằng mũi tên | `steps[{text,color,arrow_label}]`, `verdict` |
| `timeline` | Trục thời gian, khe hở, request chen ngang | `marks`, `gap`, `intruder` |
| `sticky` | Sticky note ghi quy tắc | `tone` (yellow/blue/green), `heading`, `body`, `small` |
| `code` | Đoạn code mono + dấu ✗/✓ | `heading`, `code`, `mark`, `verdict` |
| `checklist` | Danh sách có số, highlight từ khoá | `items[{text,highlight}]` |
| `figures` | Dãy người que (9/10 người…) | `count`, `lit`, `label` |
| `qa` | Bong bóng thoại + người que | `text`, `thought` |
| `decay` | Cache giữ giá cũ theo thời gian | `value`, `stops`, `verdict`, `customer` |
| `topology` ⭐ | **Mô phỏng "ở đâu"**: các tầng thành khối, request là chấm tròn bay giữa chúng | `nodes[{id,label,at}]`, `packets[{from,to,at,dur,label,bad}]`, `events[{at,node,label}]` |
| `race` ⭐ | **Mô phỏng "khi nào"**: hai luồng song song, đan và chồng lấn | `lanes[{label,color,steps}]`, `collision` |

Màu dùng tên: `ink` `red` `green` `blue` `purple` `amber` `pink` `grey` `grey_dark`.

---

## Kiến trúc

```
src/
├── style.py     khung hình, font, easing — dùng chung mọi theme
├── sketch.py    chữ (ngắt dòng, đo, hiện dần) + primitive nét vẽ tay
├── timing.py    bộ đếm nhịp dùng chung: xếp phần tử + chuẩn hoá theo lời nói
├── phongtoi.py  THEME chính: nền tối + 13 loại cảnh (kèm 2 mô phỏng)
├── brutal.py    THEME brutalist
├── scenes.py    THEME whiteboard
├── tts.py       edge-tts + đo duration + nối track audio
└── render.py    CLI, chọn theme, vòng lặp frame, encode

research/        công cụ soi bằng mắt — dùng thường xuyên khi chỉnh style
├── contact_sheet.py   ghép tất cả cảnh vào 1 ảnh
├── sim_strip.py       dải 6 mốc thời gian của 1 cảnh mô phỏng
├── wipe_strip.py      dải kiểm tra cú chuyển cảnh
└── domain_sheet.py    4 mảng cạnh nhau, kiểm tra mã màu
```

Mỗi theme là một module tự lo `background()`, `build(sp, dur, doc)` và hằng số
`FADE`. `render.py` chọn module theo `theme:` trong screenplay — không có
`if theme == ...` rải rác trong code vẽ.

Vài quyết định đáng biết:

- **Animation là hàm thuần của thời gian.** Mỗi phần tử là
  `(t_bắt_đầu, thời_lượng, hàm_vẽ)`; frame tại `t` được dựng lại từ đầu.
  Không có state tích luỹ nên tua tới đâu cũng ra đúng hình đó.
- **Nhiễu nét vẽ phải tiền định.** Mỗi hình có `seed`, điểm được cache. Nếu sinh
  ngẫu nhiên lại mỗi frame thì hình sẽ rung.
- **Vẽ ở 2× rồi thu nhỏ LANCZOS.** PIL không có anti-alias cho đường thẳng;
  supersample là cách chống răng cưa.
- **Bỏ frame trùng.** Mỗi frame tính một "chữ ký" trạng thái; giống frame trước
  thì dùng lại luôn. Video kiểu này giữ hình rất nhiều nên tiết kiệm đáng kể.
- **Canh giữa theo chiều dọc phải trừ offset font.** PIL đặt *đỉnh khung dòng*
  tại `y`, không phải đỉnh mực. Không trừ thì chữ luôn lệch lên trên
  (xem `sketch.text_metrics`).
- **Câu kết có chốt an toàn.** `verdict()` tự kéo lên nếu sắp tràn xuống dải phụ
  đề, và các loại cảnh chừa sẵn chỗ cho nó trước khi chia phần còn lại.
- **Nhịp vẽ chuẩn hoá HAI CHIỀU.** `timing.B.finish()` không chỉ co timeline khi
  quá dài mà còn **giãn** khi quá ngắn. Thiếu vế giãn thì cảnh có giọng đọc dài
  sẽ vẽ xong ở giây thứ 2 rồi đứng im 4 giây — bug này từng lọt qua vì tưởng
  "62% frame trùng" là tối ưu chạy tốt, thực ra là triệu chứng.
- **Ngắt dòng cân bằng, không dùng ngắt tham lam.** `sk.wrap_balanced` tìm nhị
  phân bề rộng nhỏ nhất mà vẫn ra đúng số dòng, nên không còn chữ mồ côi kiểu
  "TẦNG 1 — THỨ / TỰ". Với chữ tiêu đề khổng lồ thì một chữ trơ trọi rất xấu.
- **Chữ lớn thì ưu tiên ngắt dòng, không co chữ.** `brutal.big_lines` ngược với
  `sk.fit_lines`: hai dòng chữ khổng lồ đẹp hơn một dòng chữ vừa phải.
- **Dấu X phải tương phản với khối bên dưới.** Vẽ X đỏ lên khối đã tô đỏ thì mất
  hút — `cross_out` nhận màu, khối alert truyền màu đen vào.

Bố cục dọc chia 3 dải, khai báo ở `style.py`:

| Dải | y | Ghi chú |
|---|---|---|
| Tiêu đề | 150–430 | |
| Sân diễn | 330–1340 | hộp, mũi tên, timeline |
| Phụ đề | 1250–1410 | |
| — | > 1570 | TikTok phủ UI, không đặt gì quan trọng |

---

## Giới hạn hiện tại

- Chuyển cảnh chỉ có một kiểu: mờ dần về nền (giống video tham chiếu). Chưa có
  hiệu ứng lật/trượt.
- Chưa có nhạc nền. Muốn thêm thì mix vào bước ghép audio trong `render.py`.
- Phụ đề bám theo cả câu, chưa highlight theo từng từ. edge-tts có trả
  `WordBoundary` với offset từng từ nên làm được, chỉ là chưa dùng.
- Nội dung do người viết, tool không tự sinh screenplay. Muốn tự sinh thì bọc
  thêm một lớp gọi Claude API xuất ra YAML đúng schema trên.

## Tham chiếu

`reference/` giữ video gốc đã phân tích và 21 keyframe trích ra làm chuẩn style
(bảng màu trong `style.py` đọc trực tiếp từ các frame đó). Xem `HANDOFF.md` để
biết bối cảnh và các quyết định ban đầu.
