# Viết kịch bản: những bẫy đã va phải

Mỗi mục dưới đây là một lỗi có thật, đã tốn ít nhất một lượt render (10–45 phút) để
phát hiện. Ghi kèm bằng chứng đo được, để người sau tin mà tránh chứ không phải tin
vì có người bảo thế.

Xem [CONG-THUC.md](CONG-THUC.md) để biết khung nhịp, [Y-TUONG.md](Y-TUONG.md) để chọn
chủ đề, và README để biết các loại cảnh.

## Khung tự sinh, và vì sao chúng bị chặn

`research/sinh_khung.py` sinh khung cho cả 90 số từ bảng trong
[KE-HOACH-90.md](KE-HOACH-90.md): chuỗi cảnh, tên file, brand, cấu hình giọng.
Nó **không** viết lời đọc và **không** điền số — mọi chỗ cần số đo đều để trống
bằng `{{SO}}`, và file có `chua_xong: true`.

`lint.py` báo **LỖI** khi thấy một trong hai dấu hiệu đó, nên một khung không thể
lọt vào bản render. Quy trình làm một số:

1. chạy bộ đo tương ứng, **máy phải rảnh** (xem `repro/_hieu_chuan.py`)
2. thay mọi `{{SO}}` bằng số đo được
3. viết `narration` và `caption`
4. đổi chuỗi cảnh nếu cơ chế đó hợp loại khác
5. xoá dòng `chua_xong`

Lý do tách hai bước: viết một mạch 82 kịch bản thì phần lớn phải điền số bịa, vì
số đo của chúng chưa tồn tại. Trong một buổi đã có **hai lần** số sai lọt vào
kịch bản thật — bộ đo Python chạy lúc máy render lệch 5 lần, và bộ đo postgres
dao 23–90 lần qua năm lượt.

## Quy trình nên theo

Đừng render cả video để thử một câu. Vòng lặp đúng:

| Bước | Lệnh | Thời gian |
|---|---|---|
| Soi lỗi kịch bản | `python src/lint.py screenplays/<f>.yaml --engine omnivoice` | tức thì |
| Soi bố cục | `python src/render.py <f> --stills` rồi `python research/contact_sheet.py` | ~1 phút |
| Soi cảnh mô phỏng | `python research/sim_strip.py gantt <f> 1` | ~1 phút |
| **Nghe thử một cảnh** | `python src/render.py <f> ... --audio-only --scenes 8` | 2–7 phút |
| Thử nhiều cách diễn đạt | `python src/thu_cau.py build/thu_cau.txt ...` | ~6 phút cho 5 phương án |

Dán **cả lời đọc của cảnh** vào một dòng của `thu_cau.txt`, đừng dán từng câu lẻ.
`contour_for()` áp hệ số theo **vị trí câu**, nên một câu đứng một mình chạy ×0,98
còn chính câu đó nằm cuối lời đọc ba câu thì chạy ×0,95. Đã kết luận sai một lần
vì thử câu lẻ: người dùng báo một câu nghe không rõ trong video, thử riêng thì
thấy ổn, và suýt đổ lỗi cho cách diễn đạt. `thu_cau.py` giờ in sẵn bảng hệ số đó.

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
| **Âm tiết đầu tiên của lời đọc bị nén** | `"Một câu đầu tiên..."` — âm tiết `"Một"` chỉ dài 88ms trong khi trung vị của chính câu đó là 112ms. Đổi sang `"Danh sách này..."` thì âm tiết đầu giữ được 197ms, gấp 2,2 lần. Cả 13 lời đọc của `cache-stale` (bản đã duyệt) đều mở bằng âm tiết kết thúc bằng nguyên âm hoặc phụ âm mũi — `Bạn` `Vấn` `Của` `Thủ` `Quy` `Cũng` `Nhưng` `Nói` `Nếu` — không cái nào kết bằng phụ âm tắc | Đừng mở lời đọc bằng âm tiết kết thúc bằng `-t` `-c` `-p` `-ch`. Đo bằng độ dài khối âm đầu tiên so với trung vị của cả câu; dưới 0,8 lần là bị nén |
| **Câu nặng nhất đặt ở CUỐI narration** | `contour_for()` hạ tốc câu cuối xuống ×0,95 để "kết chắc chắn". Với `speed: 1.03` thì câu cuối chạy 0,978 còn các câu giữa chạy 1,030 — chậm hơn 5,3%, đủ để tai nghe ra là "bị nhấn và chậm". Người dùng đã chỉ ra đúng hai chỗ, và cả hai đều là câu cuối cảnh | Đặt câu mang thông tin nặng nhất ở **giữa**, rồi thêm một câu kết dài trên 25 ký tự để nó nhận hệ số hạ tốc thay |
| **Số đứng trần ở cuối mệnh đề** | `"dâng lên bảy mươi trong khi..."` — số là thông tin mới, đứng cuối mệnh đề chính, không có danh từ đơn vị theo sau. Nó nhận trọng âm tiêu điểm, mà tiếng Việt lại kéo dài âm tiết cuối trước ranh giới ngữ điệu, nên hai hiệu ứng rơi trúng một chỗ. Người nghe còn tự điền tiếp thành "bảy mươi **phần trăm**" vì cảnh trước có nói "phần trăm" | Luôn cho số một đơn vị: `"bảy mươi request"`. Đo được khối dài nhất giảm từ 3,12 xuống 2,74 lần trung vị |
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
| **Giọng, style và mode để trên dòng lệnh** | Đây là bẫy đắt nhất đã gặp. `--style camhung --tts-mode tach` là cả cơ chế kiểm soát chất lượng: `camhung` bật `contour` và `retry=2`, còn nhánh `tach` mới có vòng thử lại — nhánh `lien` sinh một phát rồi lấy nguyên, không kiểm tra gì. Quên hai cờ đó thì video vẫn ra, vẫn nghe được, chỉ là nhiều sạn hơn hẳn và không có gì báo | Khai trong screenplay: `omni_voice:` `style:` `mode:`. Chạy `--engine omnivoice` là đủ |
| Chạy `--engine omnivoice` mà quên `--voice` | `voice: female` trong screenplay là tên giọng của **edge-tts**. Omnivoice không có tên đó nên render dừng ngay | `--voice` là **bắt buộc** khi dùng omnivoice. `tts.config()` chặn sớm và in ra tên giọng nên đọc dòng lỗi là biết phải gõ gì |
| **`label: 23:30` không có nháy** | YAML 1.1 đọc số cách nhau bằng dấu hai chấm theo **hệ lục thập phân**: `23:30` thành `1410`, `1:2:3` thành `3723`. Không báo lỗi gì, chỉ nổ giữa lúc render. Lạ hơn nữa: `06:30` thì lại giữ nguyên là chuỗi vì số 0 đứng đầu | Bọc nháy mọi giờ phút. `lint.py` giờ kiểm 30 khoá được vẽ thẳng ra màn hình |
| `status: 504` không có nháy | YAML trả về `int`, `track_w()` nổ **giữa lúc render** — tức sau khi đã trả tiền cho cả vòng tổng hợp giọng nói | Bọc nháy. `lint.py` bắt được mọi khoá được vẽ thẳng ra màn hình mà bị đọc thành số |
| Dấu `:` theo sau dấu cách trong scalar YAML | Vỡ file, `ScannerError` | Bỏ dấu hai chấm hoặc bọc nháy |
| **Dấu phẩy trong giá trị của flow style `{ ... }`** | **Không báo lỗi.** Dấu phẩy là dấu tách, nên `{ note: nhanh hơn 1,07 lần }` cho ra `{'note': 'nhanh hơn 1', '07 lần': None}` — file vẫn parse, vẫn render, chỉ mất nửa câu trên màn hình | Bọc giá trị bằng nháy. `lint.py` bắt được: bất kỳ khoá nào có giá trị rỗng đều bị báo LỖI |

---

## Bẫy lớn nhất: ba video nhìn giống hệt nhau

Đo trên ba screenplay đầu tiên, trước khi có thêm loại cảnh:

- cả ba mở đúng một chuỗi `probe > statement > statement > list > gantt`
- `statement` chiếm **32%** tổng số cảnh
- ba loại cảnh chiếm **65%** tổng số cảnh

Nguyên nhân không phải lười. Nó là hệ quả của hai thứ: khung HOOK 5 NHỊP được
ánh xạ **máy móc** một nhịp thành một cảnh, và `gantt` từng là loại mô phỏng
**duy nhất** nên mọi cơ chế đều bị ép vào hai đường ray ngang — kể cả những cơ
chế chẳng liên quan gì tới thời gian.

Cách tránh: trước khi chọn loại cảnh, viết ra **câu hỏi** mà cảnh đó trả lời.

| Cảnh đang trả lời câu | Dùng | Ép sai vào `gantt` thì thành |
|---|---|---|
| KHI NÀO — hai việc chồng lên nhau | `gantt` | — |
| BAO NHIÊU CÁI — một thành rất nhiều | `multiply` | người xem phải **đọc** con số "còn 140 câu" thay vì **nhìn thấy** nó |
| BAO NHIÊU THEO THỜI GIAN — dồn ứ | `queue` | hai thanh ngang không kể được "lên mà không xuống" |
| Ở ĐÂU — tầng nào có, tầng nào không | `topology` | mất hẳn phần quan trọng nhất: những tầng gói tin **không** tới |

`n-plus-one.yaml` từng mắc đúng lỗi này: N+1 nói về **số lượng** bung ra, không
phải hai việc chồng thời gian, nhưng vẫn dùng `gantt`. Đổi sang `multiply` thì
149 ô hiện lên hết trên màn hình, ô đầu tiên xanh và 148 ô sau đỏ — tỷ lệ 1 trên
148 đọc được trong nửa giây, không cần một lời giải thích nào.

Lần sửa đó còn lòi ra một chuyện khác: ba con số trong kịch bản không cộng ra
đúng (143 câu × 3ms = 0,43 giây, nhưng kịch bản ghi tổng 4,2 giây). Chạy thật
bằng [repro/n_cong_1_truy_van.py](repro/n_cong_1_truy_van.py) mới thấy phần
thiếu nằm ở số lần đi về qua mạng. **Đổi loại cảnh cho đúng câu hỏi thường lôi
ra luôn chỗ nội dung đang nói sai** — vì hình vẽ đúng thì không giấu được số sai.

Hai điều nữa về sự đơn điệu:

- `statement` là loại dễ viết nhất nên tay tự trôi về đó. Đo hiện tại:
  `async-song-song` 30%, `cache-stale` 31%, `pool-can` 22%, `n-plus-one` 25%
  (hai file sau đã sửa). Nhắm về **một phần tư**, và mỗi lần định viết
  `statement` thứ ba thì hỏi lại xem cảnh đó có phải một `compare` bị nén không.
- Hai cảnh mô phỏng trong cùng một video thì hoặc **giống hệt bố cục** (để đối
  chiếu bằng mắt, như hai `gantt` của `async-song-song.yaml`), hoặc **khác hẳn
  loại**. Giống lờ mờ là tệ nhất — mắt tưởng đang so sánh nhưng không so được.

---

## Bẫy khi viết cảnh mô phỏng mới

| Bẫy | Cách tránh |
|---|---|
| `queue` có đoạn đường cong đi xuống | Cả cảnh chỉ nói được một điều: dồn lên và không rút. Đường có lên có xuống là hình đang phủ định lời đọc. `lint.py` bắt |
| `queue` đặt `capacity` cao hơn đỉnh | Ngưỡng không bao giờ bị vượt nên mất khoảnh khắc đáng nhớ duy nhất của cảnh |
| `queue` khai `curve` bằng công thức | Công thức thì dễ viên số cho đẹp. Khai số **đo được**, viết script trong `repro/` |
| `topology` cho gói tin đi qua hết mọi tầng | Nội dung của cảnh nằm ở những tầng nó **không** tới. Đi hết thì chỉ còn một danh sách |
| `topology` quá 6 tầng | Mỗi thẻ hụt dưới 110px, tên tầng dính vào dòng phụ. Gộp bớt hoặc tách hai cảnh |
| `multiply` đặt `accent: hot` rồi tưởng ô đầu đổi màu theo | Ô đầu **luôn** xanh, cố định trong code — nếu không thì nó trùng màu với 142 ô kia và mất sạch ý |
| Đặt tên cảnh trùng theme khác | `phongtoi` cũng có `topology` và `compare` nhưng schema khác hẳn. `lint.py` chỉ chạy kiểm tra `bench` khi `theme: bench` |

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
| **Nói "số đo thật" mà không cho xem cách đo** | Bảng số tĩnh là lời tuyên bố, không phải bằng chứng. Dùng `lenh:` để dòng lệnh gõ ra trước rồi kết quả chạy theo sau, và `nguon:` để người xem tự chạy lại. Mỗi mùa nên có ít nhất một cảnh `code` chiếu chính vòng đo |
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
