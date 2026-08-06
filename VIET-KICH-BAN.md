# Viết kịch bản: những bẫy đã va phải

Mỗi mục dưới đây là một lỗi có thật, đã tốn ít nhất một lượt render (10–45 phút) để
phát hiện. Ghi kèm bằng chứng đo được, để người sau tin mà tránh chứ không phải tin
vì có người bảo thế.

Xem [CONG-THUC.md](CONG-THUC.md) để biết khung nhịp, [Y-TUONG.md](Y-TUONG.md) để chọn
chủ đề, và README để biết các loại cảnh.

## Quy trình nên theo

Đừng render cả video để thử một câu. Vòng lặp đúng:

| Bước | Lệnh | Thời gian |
|---|---|---|
| Soi lỗi kịch bản | `python src/lint.py screenplays/<f>.yaml --engine omnivoice` | tức thì |
| Soi bố cục | `python src/render.py <f> --stills` rồi `python research/contact_sheet.py` | ~1 phút |
| Soi cảnh mô phỏng | `python research/sim_strip.py gantt <f> 1` | ~1 phút |
| **Nghe thử một cảnh** | `python src/render.py <f> ... --audio-only --scenes 8` | 2–7 phút |
| Thử nhiều cách diễn đạt | `python src/thu_cau.py build/thu_cau.txt ...` | ~6 phút cho 5 phương án |
| Render đầy đủ | `python src/render.py <f> ... -j 10` | ~12 phút (edge) / ~40 phút (omnivoice) |
| Dò sạn trong bản đã render | `python D:/omnivoice-test/soi_san.py out/<f>.mp4` | tức thì |

Sau khi render, nghe lại và ghi mốc giây của chỗ nghe cộm. Tai người vẫn bắt được
những lỗi mà thước đo bỏ sót — đã có trường hợp cùng một câu sinh hai lần, chỉ số
lệch 2% mà tai phân biệt rõ.

---

## Bẫy khi viết lời đọc

Toàn bộ mục này chỉ áp cho engine `omnivoice`. Với `edge-tts` thì cả đoạn được đọc
một lần nên không gặp. Lý do gốc: `mode: tach` sinh **từng câu một lần gọi model
riêng**, nên mỗi câu tự quyết mọi thứ và không có ngữ cảnh từ câu bên cạnh.

| Bẫy | Bằng chứng đo được | Cách tránh |
|---|---|---|
| **Câu ngắn ở CUỐI narration** | `"Bộ đếm đứng ở không."` (20 ký tự) cho 2,63 khối âm/giây, thấp nhất trong cảnh; 6 âm tiết chỉ tách được 4 khối | Gộp vào câu trước. `contour_for()` hạ hệ số tốc độ câu cuối xuống 0,978, cộng với vị trí cuối cụm là chỗ cao tần sụt mạnh nhất |
| **Từ 4 câu ngắn trở lên trong một cảnh** | Cảnh 1 có 4/5 câu dưới 25 ký tự, sinh ra 1,04 giây im lặng trong cảnh ~8 giây | Gộp bớt. Mỗi dấu chấm là một lần gọi model kèm một khoảng nghỉ |
| **Viết tắt trần** (`API`, `TTL`) | `TTL` bị nén thành mảnh 0,12 giây; `"Luôn đặt TTL."` cho 0,58s/4 âm tiết = 6,9 âm tiết/giây | Viết phiên âm vào `narration`, giữ chữ gốc ở `caption`. `vitext.ABBR` không có viết tắt IT nào |
| **Viết tắt ở cuối câu** | Cuối câu vừa là chỗ cao tần sụt mạnh nhất vừa là chỗ model nén viết tắt | Đổi viết tắt vào giữa câu |
| **Từ lặp** (`"trăm phần trăm"`) | Sinh lỗ chết 459ms ở v3 và 155ms ở v2, cùng một vị trí văn bản | Diễn đạt khác |
| **Thiếu dấu phẩy ở ranh giới mệnh đề** | `"Sáu mươi giây nghĩa là"` cho một khối âm 848ms liền không có chỗ tụt năng lượng, nghe thành "giây giây" | Thêm phẩy. README của omnivoice-test ghi đây là đòn bẩy mạnh nhất cho nhịp ngắt nghỉ, mạnh hơn mọi tham số |
| **Từ tiếng Anh trần lặp nhiều lần** | `cache` xuất hiện ở 12 câu, mỗi câu model tự quyết cách đọc một lần độc lập, nên đầu video đọc khác cuối video | Hoặc phiên âm nhất quán, hoặc chấp nhận và chỉ sinh lại câu nào đọc sai |

### Phiên âm viết tắt

`lecture.py` có sẵn bảng `TECH_SAY` nhưng nó nằm ở nhánh `giangvien.py`, không với tới
được từ `render.py`. Nên phải viết tay vào `narration`. Suy phiên âm theo đúng quy ước
của bảng đó:

```
HTTP = hát(H) ti(T) ti(T) pi(P)      ->  T = "ti"
URL  = iu(U)  a(R)  eo(L)            ->  L = "eo"
=> TTL = "ti ti eo"        API = "ây pi ai"        OK = "ô kê"
```

Giới thiệu thuật ngữ **một lần** ở chỗ nó xuất hiện đầu tiên, các lần sau dùng thẳng:

```yaml
narration: ... và vì sao ti ti eo, tức thời gian sống của cache, vẫn là thứ phải có.
caption:   ...                       # caption giữ nguyên chữ TTL
```

---

## Bẫy về cấu hình và cache

| Bẫy | Hậu quả | Cách tránh |
|---|---|---|
| Sửa `speed` / `pause_scale` trong `speak.py` | Không có tác dụng gì. `tts.config()` chỉ đưa giá trị khai trong YAML vào **khoá cache**, nên render sau dùng lại audio cũ | Khai trong screenplay: `speed:` `pause_scale:` |
| Tưởng cache lưu theo từng câu | Khoá tính trên **toàn bộ narration của cảnh**. Sửa một chữ là cả cảnh sinh lại | Đã sửa thì gộp câu cho triệt để, giữ nguyên vài câu không bảo toàn được gì |
| `min_duration` canh theo edge-tts | Giọng omnivoice đọc gọn hơn, khung cứng để lại 3,9–4,9 giây im lặng ở cuối cảnh | Bỏ `min_duration`, để thời lượng chạy theo audio |
| Quên `pre_pad` / `post_pad` | Mặc định 0,45 + 0,85 = 1,3 giây **mỗi điểm cắt**. Video 13 cảnh mất 15,6 giây chỉ để im lặng, đo được là 24% thời lượng | Khai `pre_pad: 0.35` và `post_pad: 0.55` |
| `caption` để trống | Nó mặc định lấy luôn `narration`, mà thẻ phụ đề chỉ vừa ~3 dòng ở cỡ 24px | Viết `caption` riêng, ngắn hơn `narration` |
| Dấu `:` theo sau dấu cách trong scalar YAML | Vỡ file, `ScannerError` | Bỏ dấu hai chấm hoặc bọc nháy |

---

## Bẫy khi viết cảnh `gantt`

| Bẫy | Cách tránh |
|---|---|
| `w` của bước quá hẹp | Tên bước bị đẩy xuống hàng nhãn tràn, nhiều nhãn chồng nhau. Nhẩm: `w × 960 − 28 ≥ số_ký_tự × 12` |
| Hai lần mô phỏng khác bố cục | Giữ **y nguyên** bố cục và bề rộng thanh, chỉ đổi biến số. Đổi bố cục là mất khả năng đối chiếu bằng mắt |
| Mốc `at` của `readout` lệch với bước | `lint.py` bắt được. Ô số đổi giá trị mà chưa bước nào vừa xong là animation đang nói sai |
| Nhiều bước `bad` trong một cảnh | Mỗi cảnh chỉ nên một bước `bad`, không thì mất tiêu điểm |

---

## Bẫy về nội dung

| Bẫy | Cách tránh |
|---|---|
| Bịa triệu chứng hoặc số liệu | Ba mức hợp lệ: **đo được** (viết script trong `repro/`), **suy ra** (hệ quả tất yếu của cơ chế), **cần cấp** (sự cố thật). Xem [Y-TUONG.md](Y-TUONG.md) |
| Đặt tên bệnh ở nhịp mở | Mất sạch căng thẳng. Giấu tới nhịp gọi tên thủ phạm |
| Câu hỏi cuối là câu tra cứu | `"DEL nằm trên hay dưới UPDATE?"` chỉ cần mở file ra nhìn. Hỏi câu kiểm tra cơ chế: `"TTL một giây thì còn cần đúng thứ tự không?"` — người trả lời được là người đã hiểu |
| Bộ đếm trong `gantt` nói mạnh hơn sự thật | Script `repro/cache_sai_thu_tu.py` cho thấy đúng thứ tự làm cache không bị nhiễm bẩn (0/200) nhưng người đọc trong khe hở **vẫn** đọc trúng giá cũ. Nhãn bộ đếm phải khớp điều đó |
| Nhịp mô phỏng quá ngắn | Đó là lợi thế duy nhất của tool. Muốn dài ra thì **viết thêm lời đọc**, đừng đóng cứng khung bằng `min_duration` |

---

## Checklist trước khi render

1. `python src/lint.py screenplays/<f>.yaml --engine omnivoice` sạch.
2. Không câu nào dưới 25 ký tự đứng cuối `narration`.
3. Mọi viết tắt trong `narration` đã phiên âm, `caption` giữ chữ gốc.
4. `caption` viết riêng và ngắn hơn `narration`.
5. Không có `min_duration` nếu dùng omnivoice.
6. Đã khai `speed`, `pause_scale`, `pre_pad`, `post_pad` trong YAML.
7. Số liệu trong video đã đo hoặc suy ra được, không có số bịa.
8. Đã nghe thử bằng `--audio-only --scenes N` những cảnh mới viết.
