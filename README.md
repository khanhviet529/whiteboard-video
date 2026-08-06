# whiteboard-video

Tool dựng video giải thích kiến thức lập trình bằng tiếng Việt từ một file
screenplay YAML. Ra mp4 dọc 1080×1920 kèm giọng thuyết minh — đăng thẳng
TikTok / Reels / Shorts.

```bash
python src/render.py screenplays/cache-stale.yaml
# -> out/cache-stale.mp4
```

## Bốn theme

| `theme:` | Trông thế nào | Dùng khi |
|---|---|---|
| **`bench`** *(mới nhất)* | "Bàn thí nghiệm": nền gần đen, lưới **chấm**, bloom tím mờ. Khung cố định kín cả frame — rail chữ mono trên cùng, chip chương, tiêu đề cảnh, thẻ phụ đề, dòng chân. Nét mảnh + **ngoặc góc** kiểu khung ngắm. Điểm mạnh riêng: **đồng hồ đo chạy thật** — ô số đổi giá trị theo đầu đọc. Chuyển cảnh bằng cú **tan mềm riêng dải nội dung**, rail và dòng chân đứng yên. | Sản xuất chính. |
| `phongtoi` | Nền xanh đêm ba tầng bề mặt, lưới hairline, hạt nhiễu, chữ căn lề trái tracking âm, vệt sáng quanh phần tử tiêu điểm. Chuyển cảnh bằng bóng tối quét **ngang**. | Vẫn dùng được, đối chiếu. |
| `brutalist` | Khối màu phẳng, viền đen dày, bóng lệch cứng, chữ Phudu cực lớn. | Bản trung gian, giữ để đối chiếu. |
| `whiteboard` | Nét vẽ tay xiêu xiêu, nền giấy kem lưới chấm. | Bản đầu tiên. Tên repo còn sót từ giai đoạn này. |

Ba theme cũ dùng **chung** bộ loại cảnh, nên cùng một screenplay chạy được cả ba:

```bash
python src/render.py screenplays/double-charge.yaml --theme brutalist
```

`bench` thì **không**: nó có bộ loại cảnh riêng (bảng bên dưới), vì bố cục kín
frame cần những trường khác. Chạy screenplay cũ với `--theme bench` sẽ báo lỗi
ngay chứ không render ra hình sai:

```
ValueError: theme bench khong co loai canh 'bigstat'.
            Co: ask, compare, counters, gantt, list, multiply, probe,
                queue, rule, statement, topology
```

### `bench` khác `phongtoi` ở đâu

Không phải khác màu — khác **cách nhìn**:

| | `phongtoi` | `bench` |
|---|---|---|
| Khung hình | để trống ba phần tử khung, mỗi cảnh như một slide rời | rail + chip chương + tiêu đề + thẻ phụ đề + dòng chân, **luôn có** |
| Căn chữ | căn lề trái hết | câu đập vào mặt thì **căn giữa**, danh sách mới căn trái |
| Nền | ke ngang | **lưới chấm** + bloom tím |
| Viền | panel tô đặc | nét mảnh + **ngoặc góc** |
| Mô phỏng | hình minh hoạ tĩnh | **ô số đổi giá trị theo đầu đọc** + bộ đếm |
| Chuyển cảnh | bóng quét ngang cả frame | **tan mềm riêng dải nội dung**; rail + dòng chân đứng yên suốt video |

Ý tưởng dẫn dắt của `bench`: người xem không đọc biểu đồ, họ **đọc số**. Một con
số đang nhảy giữ mắt lâu hơn bất kỳ mũi tên nào — nên mọi cảnh mô phỏng đều phải
có ít nhất một ô số liên tục đổi giá trị.

## Mã màu theo mảng

> Áp dụng cho `phongtoi` / `brutalist` / `whiteboard`. Theme `bench` không dùng
> `domain:` — nó lấy màu nhấn từ `accent:` (`hot` `ok` `cool` `violet` `gold`) khai
> ở đầu screenplay hoặc trên từng cảnh, và nhận diện video bằng `brand:` + `tag:`
> trên rail chữ mono chứ không bằng badge mảng.

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

`bench` theo cùng tinh thần: dòng có `focus: true` trong `list` được tô số bằng
màu nhấn, các dòng còn lại chữ xám. Trong `gantt` thì `bad: true` trên một bước
tô thanh đó thành đỏ và thêm vệt sáng — mỗi cảnh chỉ nên có **một** bước `bad`.

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
python src/render.py screenplays/cache-stale.yaml

# xuất 1 PNG mỗi cảnh để soi bố cục — dùng cái này khi chỉnh style
python src/render.py screenplays/cache-stale.yaml --stills

# chỉ 1 cảnh
python src/render.py screenplays/cache-stale.yaml --stills --scene 7

# render nhanh không gọi TTS (thời lượng lấy từ `duration:` trong YAML)
python src/render.py screenplays/cache-stale.yaml --no-audio

# ghép bảng tổng tất cả cảnh vào 1 ảnh để soi toàn cục
python research/contact_sheet.py

# dải 6 mốc thời gian của MỘT cảnh mô phỏng — bắt buộc soi cái này
# (ảnh tĩnh không đánh giá được cảnh động: phải xem đầu đọc đi tới đâu,
#  ô số đổi lúc nào, có giây nào không có gì chuyển động hay không)
python research/sim_strip.py gantt cache-stale.yaml 1   # cảnh gantt thứ nhất
python research/sim_strip.py gantt cache-stale.yaml 2   # cảnh gantt thứ hai
python research/sim_strip.py multiply n-plus-one.yaml 1 # loại nào cũng soi được

# dải kiểm tra cú chuyển cảnh
python research/wipe_strip.py cache-stale.yaml

# N frame LIÊN TIẾP của một cảnh — dùng để bắt cú "khựng" trong chuyển động.
# sim_strip lấy 6 mốc rải đều nên không bao giờ thấy được: cú khựng chỉ dài
# 2–3 frame. Cột `d=` in ra phải tăng giảm dần đều.
#                              screenplay        cảnh  t_đầu  số_frame
python research/frame_strip.py cache-stale.yaml  10    0.60   18
```

Vòng làm việc nên theo: `--stills` → soi → sửa YAML/style → `--stills` lại →
khi hài lòng mới render full.

---

## Hai engine giọng đọc

Chọn bằng `engine:` ở đầu screenplay, hoặc ghi đè từ CLI.

| | `edge` *(mặc định)* | `omnivoice` |
|---|---|---|
| Nguồn | edge-tts, miễn phí, qua mạng | OmniVoice chạy trong WSL, offline |
| Tốc độ sinh | ~1 giây/câu | **RTF 14–54** — xem bảng dưới |
| Giọng | 2 giọng Microsoft | giọng **clone từ mẫu**, tự nhiên hơn |
| Định dạng ra | mp3 → 48k stereo | 24k **mono** → 48k stereo |
| Giấy phép | dùng được thương mại | ⚠ trọng số **CC-BY-NC, cấm thương mại** |

```bash
# edge (mặc định)
python src/render.py screenplays/cache-stale.yaml

# omnivoice — `--voice` là BẮT BUỘC. Screenplay khai `voice: female` cho
# edge-tts, omnivoice không có tên giọng đó nên không truyền thì dừng ngay
# (kèm dòng lỗi ghi rõ phải gõ gì).
python src/render.py screenplays/cache-stale.yaml \
    --engine omnivoice --voice namtre_v3 --style camhung --tts-mode lien
# -> out/cache-stale-omnivoice.mp4   (tên có hậu tố để không ghi đè bản edge)
```

Xem giọng và sắc thái có thật: `D:\omnivoice-test\say.ps1 --list`. Tên giọng
**không** tự do — `namtre_va` không tồn tại, có `namtre_v2` / `namtre_v3` /
`nam_tre`.

### `mode: lien` hay `tach` — chênh nhau 2,4 lần

Đo thật trên máy này (i7-1355U, CPU, không GPU), cùng một câu:

| Cấu hình | audio ra | sinh mất | RTF |
|---|---|---|---|
| `camhung` (style tự khai `tach`) | 4,39s | 236s | **53,8** |
| `camhung` + `--tts-mode lien` | 2,64s | 59s | **22,4** |
| `camhung` + `lien` + `--num-step 4` | 2,62s | 37s | 14,1 |

`tach` tách từng câu rồi sinh riêng, nên chi phí cố định nhân với số câu.
`lien` sinh cả đoạn một lần — nhanh hơn **và** audio gọn hơn vì bỏ khoảng nghỉ
dài giữa câu. Đổi lại mất cái ngắt nghỉ đều đặn mà `tach` tạo ra.

### Vì sao phải gom cả video vào một lần gọi

`omnivoice` nạp model ~8 giây, cộng warmup ~14 giây cho câu đầu **mỗi process**.
Gọi từng câu là 13 lần trả cái phí đó. Nên `tts.prefetch()` gom **tất cả câu còn
thiếu vào một lần gọi** `say.py` (nó nhận nhiều text và ghi ra `_1.wav`,
`_2.wav`… theo đúng thứ tự tham số), rồi mới convert từng file sang 48k stereo.

Cache theo hash của *nội dung + toàn bộ cấu hình giọng*, nên đổi một cảnh thì chỉ
sinh lại đúng câu đó. Đổi `engine`/`voice`/`style` là đổi khoá → sinh lại toàn bộ.

## Công thức kể

Xem [CONG-THUC.md](CONG-THUC.md) — định dạng **HIỆN TRƯỜNG VỤ ÁN**: khung 7 nhịp,
quy tắc từng nhịp, lỗi thường gặp, mẫu điền. Screenplay
[double-charge.yaml](screenplays/double-charge.yaml) là bản mẫu bám đúng công thức.

Biến thể mở đầu **HOOK 5 NHỊP** (lỗi thật → hậu quả → gợi mở nguyên nhân → người
xem được gì → vào demo ngay) ở cùng file đó. Bản mẫu:
[cache-stale.yaml](screenplays/cache-stale.yaml) — mở bằng ba dòng shell chứ không
bằng lời chào, và chạy mô phỏng **hai lần** (sai thứ tự / đúng thứ tự) trên cùng
một bố cục để người xem đối chiếu bằng mắt.

Chọn chủ đề tiếp theo ở [Y-TUONG.md](Y-TUONG.md): bảng ứng viên kèm hai cửa lọc —
số liệu lấy từ đâu, và mô phỏng được không.

**Trước khi viết screenplay mới, đọc [VIET-KICH-BAN.md](VIET-KICH-BAN.md).** Đó là
danh sách bẫy đã va phải, mỗi cái kèm số đo. Ví dụ: câu ngắn đứng cuối `narration`
bị đọc dồn tới 6,9 âm tiết/giây, viết tắt trần bị nén còn 0,12 giây, và sửa
`pause_scale` trong `speak.py` thì không có tác dụng gì vì nó không vào khoá cache.

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

### 12 loại cảnh của theme `bench`

Mọi cảnh nhận thêm ba trường chung: `chapter` (tên chương, tự đánh số theo lần
xuất hiện đầu tiên), `head` (tiêu đề ngắn của cảnh), `accent` (`hot` `ok` `cool`
`violet` `gold`).

| `scene` | Dùng để | Trường chính |
|---|---|---|
| `probe` | Console thật: lệnh bên trái, kết quả bên phải, dòng sai tô đỏ | `heading`, `status`, `lines[{cmd,out,state}]`, `verdict` |
| `statement` | Một câu đập vào mặt, đặt trong ngoặc góc, căn giữa | `label`, `value`, `size`, `sub`, `strike`, `color` |
| `list` | Danh sách có số trong ô vuông nhỏ | `items[{text,focus,color}]` |
| `rule` | Thẻ quy tắc: số lớn trong ngoặc góc + câu quy tắc + ghi chú | `n`, `kicker`, `body`, `small`, `color` |
| `counters` | Dãy ô số cạnh nhau — cho thấy một giá trị **không đổi** qua nhiều mốc | `items[{value,label,top,color}]`, `box_h`, `verdict` |
| `compare` | Hai ô xếp dọc, có gạch nối `vs` ở giữa | `a{}`, `b{}`, `vs`, `bad`, `note` |
| `ask` | Cảnh chốt: câu hỏi về hệ thống của chính người xem | `text`, `size`, `hint` |

### Bốn cảnh mô phỏng ⭐ — chọn theo CÂU HỎI, đừng chọn theo thói quen

Đây là chỗ tool ăn đứt slide, và cũng là chỗ dễ làm video nhìn giống nhau nhất.
Ba screenplay đầu tiên đều mở `probe > statement > statement > list > gantt` chỉ
vì `gantt` là loại mô phỏng duy nhất có sẵn lúc đó. Mỗi loại trả lời **một** câu
hỏi khác nhau — hỏi trước xem cảnh của bạn đang trả lời câu nào:

| `scene` | Trả lời câu | Hình dạng | Trường chính |
|---|---|---|---|
| `gantt` | **KHI NÀO** — hai việc chồng lên nhau theo thời gian | hai đường ray ngang, đầu đọc chạy qua | `lanes`, `readout`, `counter`, `ruler`, `verdict_at` |
| `multiply` | **BAO NHIÊU CÁI** — một thành rất nhiều | ô nguồn + lưới ô đầy dần + bộ đếm | `source{label,text}`, `count`, `cols`, `counter_key`, `chip` |
| `queue` | **BAO NHIÊU THEO THỜI GIAN** — dồn ứ, không rút xuống | biểu đồ miền, cắt màu tại ngưỡng | `curve[]`, `capacity`, `ymax`, `marks[]`, `inbox{}`, `outbox{}` |
| `topology` | **Ở ĐÂU** — tầng nào có, tầng nào không | các tầng xếp dọc, gói tin chạy dọc sống | `nodes[{name,sub,tag,color}]`, `from`, `to`, `miss_tag`, `packet` |

Trong `gantt`:

- `readout[].steps[{at,value,state,note}]` — ô số đổi giá trị khi đầu đọc đi qua
  `at`. `state`: `ok` `bad` `stale` `empty` `warn`. Ô nháy sáng ngay lúc đổi.
- `counter{key,from,rate,label}` — số đếm lên từ mốc `from`. Đặt `from` lớn hơn 1
  thì bộ đếm **đứng ở 0** — đó là cách cho thấy lần chạy đúng không hại ai.
- `lanes[].steps[].w` phải **đủ rộng để chứa tên bước bên trong thanh**. Hẹp hơn
  thì tên bước bị đẩy xuống hàng nhãn tràn, đọc kém hơn nhiều.

Trong `multiply`: ô đầu tiên **luôn xanh**, các ô còn lại đỏ — tỷ lệ 1 trên
N hiện ra mà không cần một lời giải thích nào. Ô tự co lại cho đủ `count`; chỉ
khi co xuống dưới 11px mới cắt và ghi `+N nữa`.

Trong `queue`: `curve` là danh sách số **đo được**, khai thẳng, không nội suy từ
công thức — công thức thì dễ viên số cho đẹp. Phần đường cong nằm dưới `capacity`
tô xanh, phần vượt lên tô đỏ; khoảnh khắc cắt ngưỡng là điểm đáng nhớ duy nhất
của cảnh nên `capacity` phải thấp hơn đỉnh (linter bắt).

Trong `topology`: gói tin chạy từ tầng `from` tới tầng `to`. **Những tầng nó
không tới mới là nội dung** — chúng bị mờ đi và đeo nhãn `miss_tag`. Tối đa 6
tầng; nhiều hơn thì mỗi thẻ hụt dưới 110px và tên tầng dính vào dòng phụ.

> Tên cảnh không duy nhất giữa các theme: `phongtoi` cũng có `topology` và
> `compare` nhưng schema khác hẳn. `lint.py` vì thế chỉ chạy kiểm tra của `bench`
> khi `theme: bench`.

### ⚠ `gantt` KHÔNG mô phỏng gì — nó vẽ đúng cái bạn khai

Đây là điều quan trọng nhất phải biết về cảnh mô phỏng. Không có mô hình thực
thi nào phía sau: từng mốc `at`, từng `w`, từng giá trị `readout` đều do **người
viết khai bằng tay**. Nếu bạn ghi cache đổi giá trị ở `at: 0.84` nhưng bước `SET`
lại kết thúc ở `0.60` thì animation vẫn chạy trơn — và nó đang **nói sai** mà
không có gì gãy để bạn nhận ra.

Vì vậy có `src/lint.py`, chạy **tự động mỗi lần render**:

```bash
python src/lint.py screenplays/cache-stale.yaml     # chạy riêng
python src/render.py <yaml> --strict                # dừng lại nếu có LOI
python src/render.py <yaml> --no-lint               # bỏ qua
```

| Kiểm | Mức |
|---|---|
| Hai thanh chồng nhau trong cùng một lane | LOI |
| `at + w > 1.0` (tràn ra ngoài trục) | LOI |
| `readout` có `at` không tăng dần | LOI |
| Có `verdict_at` mà thiếu `verdict` | LOI |
| Tên bước không vừa trong thanh — **báo luôn `w` tối thiểu** | CẢNH BÁO |
| Ô số đổi giá trị mà **không bước nào bắt đầu/xong quanh mốc đó** | CẢNH BÁO |
| `verdict_at` chốt trước khi bước cuối xong | CẢNH BÁO |
| Khoảng > 14% thời lượng không bước nào chạy, không ô số nào đổi | CẢNH BÁO |
| `caption` dài quá thẻ phụ đề (3 dòng ở 24px) | CẢNH BÁO |

Cảnh báo *"ô số đổi mà không bước nào vừa xong"* là cái đáng giá nhất: nó chính
là kiểu sai làm mô phỏng **nói dối** người xem. Con số phải đổi **vì** một việc
vừa xong, không phải vì người viết đặt mốc cho đẹp.

Linter không tự sửa gì — bố cục và nhịp là quyết định của người viết.

### 11 loại cảnh (ba theme cũ)

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
├── typo.py      chữ có tracking + vệt sáng — dùng chung cho hai theme tối
├── timing.py    bộ đếm nhịp dùng chung: xếp phần tử + chuẩn hoá theo lời nói
├── lint.py      kiểm screenplay trước khi render — nhắm vào cảnh mô phỏng
├── bench.py     THEME chính: bàn thí nghiệm + 12 loại cảnh (4 cảnh mô phỏng)
├── phongtoi.py  THEME nền tối + 13 loại cảnh (kèm 2 mô phỏng)
├── brutal.py    THEME brutalist
├── scenes.py    THEME whiteboard
├── tts.py       edge-tts + đo duration + nối track audio
└── render.py    CLI, chọn theme, vòng lặp frame, encode

research/        công cụ soi bằng mắt — dùng thường xuyên khi chỉnh style
├── contact_sheet.py   ghép tất cả cảnh vào 1 ảnh
├── sim_strip.py       dải 6 mốc thời gian của 1 cảnh mô phỏng
├── frame_strip.py     N frame LIÊN TIẾP + số đo độ sáng, để bắt cú khựng
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
- **Chữ có tracking thì con trỏ phải cộng cả tracking.** `typo.ttext` vẽ từng ký
  tự để làm tracking, nhưng ban đầu con trỏ chỉ cộng `advance` mà bỏ `track`.
  Hậu quả kép: tracking chỉ dịch vị trí khối chữ chứ không đổi khoảng giữa các
  ký tự, và layer được cấp theo bề rộng *đã tính* tracking — nên với tracking âm
  (tiêu đề lớn dùng `-2` đến `-3.5`) layer hẹp hơn chữ thực vẽ và **ký tự cuối bị
  cắt mất**. Câu kết dài 22 ký tự là đủ để lộ ra.
- **Đo chữ và vẽ chữ phải dùng CÙNG một anchor của PIL.** `"t"` (top) chỉ hợp lệ
  với chữ **dọc**; với chữ ngang thì `textbbox(anchor="lt")` trả `b[1] == 0`
  mãi mãi. `typo.tm` đo bằng `"lt"` còn `ttext` vẽ bằng `"la"` (mặc định), nên
  offset luôn ra 0 và phép trừ canh giữa **không bao giờ chạy** — mọi thứ bị đặt
  thấp hơn đúng bằng khoảng từ đỉnh ascender xuống đỉnh mực (22px với Phudu 72,
  15,5px với BeVietnamPro Black 62). Số `01`/`02` trong khung ngoặc của cảnh
  `rule` lệch hẳn xuống dưới là vì thế. Giờ cả hai đều dùng `typo.ANCHOR`.
  `sketch.text_metrics` **giữ nguyên** `"lt"`: theme whiteboard/brutalist đo và
  vẽ cùng bằng `"lt"` nên tự khớp nhau, sửa ở đó mới là làm lệch.
- **Chuyển cảnh: đừng kéo vạch sáng qua vòng mắt.** Bản đầu của `bench` dùng màn
  che trượt dọc có một vạch màu accent kèm glow dẫn đường. Vấn đề: mỗi điểm cắt
  có **hai** vạch (một khi ra cảnh, một khi vào cảnh) lướt hết khung trong
  ~0,56s, lại dùng `expo_out` nên phóng rất nhanh ở đầu — 12 lần trong hai phút
  là nhức mắt thật, mà nó không nói thêm điều gì về nội dung. Giờ chỉ **tan mềm
  dải nội dung** (`ease_in_out`, 0,42s) và **giữ nguyên rail + dòng chân**, nên
  hai cảnh nối nhau như đổi trang trong cùng một bản đồ.
- **Đồ đạc cố định thì không được chạy lại hiệu ứng.** Hệ quả của cú tan trên:
  vì cú tan không tan rail, nếu cảnh sau lại cho rail mờ dần từ 0 thì mỗi điểm
  cắt có một cú sụt sáng của rail — đúng thứ vừa bỏ vạch sáng để tránh. Rail và
  dòng chân chỉ chạy hiệu ứng ở cảnh **đầu tiên** (so sánh định danh
  `scenes[0] is sp`), từ cảnh hai vẽ đặc ngay. Và phải xếp từ **mốc 0**: vẽ đặc
  thôi chưa đủ, vì phần tử nào chưa tới `at` thì `render.py` bỏ qua hẳn
  (`p <= 0`) nên dòng chân sẽ biến mất 0,46s đầu mỗi cảnh.
- **Chữ không dùng easing của panel.** `expo_out` dồn 87% chuyển động vào 30%
  thời gian đầu rồi kéo một cái đuôi rất dài. Với panel thì đẹp, nhưng với chữ —
  cộng thêm alpha nhân `1.6` nên đạt độ đặc ngay ở 14% đầu — thì chữ hiện gần
  như tức thì rồi còn bò lên vài pixel rất lâu: mắt đọc thấy **một cú khựng**.
  Chữ giờ dùng `ease_out_cubic`, và alpha đi cùng một đường cong với cú trượt.
  Kiểm bằng `research/frame_strip.py`: độ sáng dải chữ phải tăng giảm dần đều,
  không được nhảy một bậc lớn rồi đứng yên.
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

Theme `bench` tự khai bố cục riêng (hằng số ở đầu `bench.py`), kín cả frame:

| Dải | y |
|---|---|
| Rail chữ mono + ke ngang | 62 – 116 |
| Chip chương | 150 – 198 |
| Tiêu đề cảnh | 244 – 434 |
| Sân diễn | 470 – 1296 |
| Thẻ phụ đề | 1332 – ~1500 |
| Dòng chân | 1524 |

---

## Giới hạn hiện tại

- Mỗi theme có đúng một kiểu chuyển cảnh, cứng trong code: `whiteboard` mờ dần,
  `phongtoi` quét ngang, `bench` tan mềm dải nội dung. Chưa chọn được từ screenplay.
- Chưa có nhạc nền. Muốn thêm thì mix vào bước ghép audio trong `render.py`.
- **`rate:` quyết định độ dài video nhiều hơn bạn tưởng.** Giọng
  `vi-VN-HoaiMyNeural` đọc khoảng 13–15 ký tự/giây ở `+16%`; nhiều câu ngắn thì
  chậm hơn vì thêm khoảng nghỉ. Cộng thêm `PRE_PAD + POST_PAD` = 1,3 giây **mỗi
  cảnh** (render.py) — 13 cảnh là 17 giây chỉ để im lặng. `cache-stale.yaml` từng
  ra gần 3 phút ở `+6%`; phải rút chữ và nâng `rate` mới về ~2 phút.
- **Chú ý dấu `:` trong scalar YAML.** `narration: Quy tắc một: ghi trước` làm vỡ
  file. Bỏ dấu hai chấm hoặc bọc nháy.
- **`engine: omnivoice` không dùng được cho mục đích thương mại.** Code OmniVoice
  là Apache 2.0 nhưng **trọng số là CC-BY-NC**. Kênh có bật kiếm tiền, hoặc video
  làm cho công ty, đều là dùng thương mại. Kênh dev cá nhân không kiếm tiền thì
  được. Muốn giọng clone mà vẫn dùng thương mại được thì `D:\omnivoice-test\CLAUDE.md`
  đã khảo sát sẵn hai hướng: VieNeu-TTS (Apache 2.0 cả trọng số) hoặc Azure Speech
  free tier (500k ký tự/tháng). Engine `edge` mặc định không vướng.
- **`omnivoice` chậm và chỉ chạy CPU trên máy này.** Sinh giọng cho một video 2
  phút mất khoảng nửa tiếng. Nó là bước một-lần (có cache), nhưng đừng dùng khi
  đang thử nghiệm nội dung — dùng `edge` để chốt kịch bản, xong mới đổi engine.
- Phụ đề bám theo cả câu, chưa highlight theo từng từ. edge-tts có trả
  `WordBoundary` với offset từng từ nên làm được, chỉ là chưa dùng.
- Nội dung do người viết, tool không tự sinh screenplay. Muốn tự sinh thì bọc
  thêm một lớp gọi Claude API xuất ra YAML đúng schema trên.

## Tham chiếu

`reference/` giữ video gốc đã phân tích và 21 keyframe trích ra làm chuẩn style
(bảng màu trong `style.py` đọc trực tiếp từ các frame đó). Xem `HANDOFF.md` để
biết bối cảnh và các quyết định ban đầu.
