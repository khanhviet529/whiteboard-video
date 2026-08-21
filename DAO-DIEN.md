# Đạo diễn: ba vai, và cổng lọc trước khi viết

[CONG-THUC.md](CONG-THUC.md) cho khung nhịp. [VIET-KICH-BAN.md](VIET-KICH-BAN.md)
cho bẫy khi viết. File này cho thứ nằm giữa hai cái đó: **quyết định người xem
đang nghĩ gì ở từng giây, và mỗi giây trên màn hình đang chứng minh điều gì.**

Câu hỏi sai khi viết một cảnh:

> Làm sao minh hoạ lời narration này?

Câu hỏi đúng:

> **Người xem cần NHÌN THẤY điều gì để tự hiểu cơ chế trước khi tôi gọi tên nó?**

Toàn bộ file này là hệ quả của một câu đó.

---

## Ba vai, và mỗi vai quyết định cái gì

Viết một số là làm ba việc khác nhau. Trộn chúng lại thì ra một bài giảng chia
thành slide — đúng thứ mà [CONG-THUC.md](CONG-THUC.md) gọi là hỏng.

| Vai | Quyết định | Sai thì ra cái gì |
|---|---|---|
| **Content strategist** | Người xem đang tin gì, thông tin nào bị **giấu**, giấu tới giây thứ mấy | Tiết lộ thủ phạm ở giây thứ mười → còn lại là bài giảng |
| **Technical storyteller** | Cơ chế thật là gì, chỗ nào phải nêu giả định, số nào có quyền xuất hiện | Kịch bản nghe hay mà mid-level bắt lỗi trong ba giây → mất uy tín cả kênh |
| **Motion director** | Mắt người xem đang ở đâu, cái gì hiện ra **lúc nào**, cái gì mờ đi | Bốn thứ tranh nhau attention → người xem đọc trước câu chuyện năm giây |

Ba vai này không chạy tuần tự. Strategist chọn giấu gì, thì director phải biết
**thứ tự hé ra**; storyteller nói cơ chế cần gì, thì strategist phải biết nhịp
nào đủ chỗ cho nó.

---

## ⚠ Từ vựng cảnh: bộ tiêu chí gốc gọi tên SAI so với renderer

Đây là chỗ phải lọc trước khi làm bất cứ gì khác.

Bộ tiêu chí kể chuyện (bản gốc) gợi ý chọn cảnh theo *loại thông tin*, và nó
liệt kê: `bigstat` `compare` `flow` `timeline` `topology` `race` `code`
`checklist` `sticky` `decay`. Danh sách đó viết cho **ba theme cũ**
(`phongtoi`, `brutal`, `scenes.py`).

Theme đang dùng cho toàn bộ 93 screenplay là `bench`, và **7 trong 10 tên đó
không tồn tại ở đây**. Gõ chúng vào một file `theme: bench` thì render dừng ngay:

```
ValueError: theme bench khong co loai canh 'timeline'.
```

Bảng đổi tên, dùng cái này chứ không dùng danh sách gốc:

| Bộ tiêu chí gốc gọi | `bench` dùng | Ghi chú |
|---|---|---|
| `bigstat` | `statement` | cùng việc: một câu đập vào mặt |
| `compare` | `compare` ✅ | tên trùng, schema khác — `items[]` chứ không `a{}`/`b{}` |
| `flow` | `topology` hoặc `thac` | `topology` nếu câu hỏi là Ở ĐÂU, `thac` nếu là CÁI NÀO CHỜ CÁI NÀO |
| `timeline` | `gantt` | `gantt` mạnh hơn: có hàng ô số đổi theo đầu đọc |
| `topology` | `topology` ✅ | tên trùng, schema khác — `nodes[{name,sub,tag}]`, không có toạ độ `at` |
| `race` | `gantt` | `race` chỉ có ở `phongtoi` |
| `code` | `code` ✅ | |
| `checklist` | `list` (nhịp 4) hoặc `rule` (nhịp 6) | hai việc khác nhau, đừng gộp |
| `sticky` | `rule` | |
| `decay` | `counters` | dãy ô số cạnh nhau: cùng một giá trị sai qua nhiều mốc |

Và bốn loại `bench` **không có trong bộ tiêu chí gốc** — chúng sinh ra từ lần rà
292 chủ đề, xem [KE-HOACH-KHO-292.md](KE-HOACH-KHO-292.md):

`thac` `cot` `ban_sao` `gop`

Danh sách đầy đủ 17 loại của `bench` nằm ở README. Trước khi khai một loại cảnh,
kiểm bằng:

```bash
PYTHONIOENCODING=utf-8 python -c "import sys; sys.path.insert(0,'src'); import bench; print(sorted(bench.BUILDERS))"
```

---

## Năm câu hỏi phải trả lời cho TỪNG cảnh

Đây là phần đáng giá nhất của bộ tiêu chí, và nó không có trong CONG-THUC.md.
Trước khi viết một cảnh, viết ra năm dòng này:

1. **Người xem đang NHÌN thấy gì?**
2. **Người xem đang TIN gì?** (trước cảnh này)
3. **Bằng chứng MỚI nào xuất hiện?**
4. **Giả định nào bị phá?**
5. **Câu hỏi nào được sinh ra?** (dẫn vào cảnh sau)

**Cảnh nào không làm thay đổi ít nhất một trong năm thứ đó thì xoá.** Không sửa,
xoá — vì một cảnh không đổi gì trong đầu người xem là một cảnh họ dùng để trượt
ngón tay.

Cách dùng thực dụng: viết năm dòng này vào **comment YAML ngay trên cảnh**. Chín
screenplay của mùa 7 làm vậy, và hai lần nó lôi ra được chỗ hai cảnh liền nhau
đang trả lời cùng một câu — tức phải gộp.

### Một cảnh, một câu hỏi hình ảnh

Nếu một cảnh đang trả lời hai ba câu thì **tách cảnh**. Bảng chọn theo câu hỏi
nằm ở [KE-HOACH-KHO-292.md](KE-HOACH-KHO-292.md) mục *"Bảng chọn loại cảnh"* —
tám loại mô phỏng, mỗi loại một câu hỏi.

---

## Narration ≠ chữ trên màn hình

Người xem **nghe** phần diễn giải. Người xem **nhìn** bằng chứng. Hai đường đó
bổ sung nhau, không lặp lại nhau.

Sai:

```yaml
narration: Hai request cùng đọc số dư trước khi request nào kịp ghi.
caption:   Hai request cùng đọc số dư.        # lặp lại y nguyên lời đọc
```

Đúng — `caption` nói phần *hệ quả*, còn *bằng chứng* nằm ở hình:

```yaml
narration: Hai request cùng đọc số dư trước khi request nào kịp ghi.
caption:   Cả hai đọc được 100. Cả hai ghi 80.
# và cảnh `gantt` vẽ hai lane có vùng chồng lấn được tô đỏ
```

`lint.py` không bắt được lỗi này — nó là việc của người viết. Cách tự kiểm nhanh:
**che phần hình đi, đọc `caption` một mình. Nếu nó vẫn đủ nghĩa thì hình đang là
đồ trang trí.**

---

## Thứ tự hé ra

Đừng đưa cả sơ đồ lên một lượt. Hé theo đúng thứ tự suy nghĩ, mỗi lần hé khớp
với câu narration đang đọc.

Trong `bench` thì thứ tự hé **không phải tuỳ chọn** — nó đã nằm trong code:
`timing.B` xếp phần tử tuần tự và `finish()` chuẩn hoá nhịp theo độ dài giọng
đọc. Nên việc của người viết là **thứ tự khai trong YAML**, và với cảnh mô phỏng
là các mốc `at`.

Đúng một luật cứng ở đây, và `lint.py` bắt nó: **ô số phải đổi VÌ một việc vừa
xong**, không phải vì người viết đặt mốc cho đẹp. Xem README mục *"`gantt` KHÔNG
mô phỏng gì"*.

---

## Liên tục giữa các cảnh

Hai cảnh liền nhau nói về cùng một cơ chế thì giữ lại **mỏ neo hình ảnh**. Đừng
reset canvas nếu câu chuyện vẫn ở cùng một hiện trường.

Chuyển cảnh phải có lý do, và chỉ có năm lý do hợp lệ:

- zoom sâu vào một thành phần;
- tách riêng một thành phần ra;
- đổi câu hỏi (Ở ĐÂU → KHI NÀO);
- so sánh trước/sau;
- hé ra một state đang bị giấu.

Đổi layout chỉ để "cho khác đi" là mất khả năng đối chiếu bằng mắt. Đây chính là
mẹo của `cache-stale`: hai cảnh `gantt` giữ **y nguyên** bố cục, chỉ đổi thứ tự
hai lệnh — nên người xem đối chiếu được mà không cần một câu giải thích nào.

Và một cảnh báo ngược lại, đã ghi ở [VIET-KICH-BAN.md](VIET-KICH-BAN.md): hai
cảnh mô phỏng trong cùng một video thì hoặc **giống hệt bố cục**, hoặc **khác hẳn
loại**. Giống lờ mờ là tệ nhất.

---

## Màu là ngôn ngữ, không phải trang trí

Bảng màu của `bench` (xem `src/bench.py` mục `HE`) đã gán nghĩa cố định. Giữ đúng
nghĩa đó xuyên suốt cả kênh:

| Tên | Nghĩa | Không được dùng cho |
|---|---|---|
| `hot` | cái sai, vùng xung đột, state nguy hiểm | nhấn mạnh chung |
| `ok` | cái đúng, đã chặn được | bất cứ gì còn hỏng |
| `gold` | cần chú ý, đang chuyển, chỗ thừa nhận chưa 100% | lỗi |
| `cool` / `violet` | thực thể hệ thống, luồng chính / luồng phụ | kết luận |
| `muted` / `dim` | bối cảnh, thông tin đã nguội | tiêu điểm |

**Mỗi thời điểm đúng MỘT tiêu điểm.** `lint.check_cot` bắt trường hợp quá hai
màu trong một cảnh cột; các loại cảnh khác thì người viết tự giữ.

---

## Đo độ đơn điệu, thay vì tranh luận về nó

Câu "video đang một màu" là một cảm nhận, và cả dự án này dựng trên luật *đo được
hoặc bỏ*. Nên có [research/do_don_dieu.py](research/do_don_dieu.py):

```bash
python src/render.py screenplays/<f>.yaml --stills
python research/do_don_dieu.py <f> [--hinh]
```

Phép đo là **blur test**: thu mỗi khung hình xuống lưới 12×21, trừ nền đi, rồi so
từng cặp. Blur mạnh thì chữ biến mất, màu nhoè, chỉ còn lại **dạng bóng** — đúng
cái mà mắt người dùng để nhận ra "cảnh này giống cảnh kia" *trước khi* đọc được
bất kỳ chữ nào.

Số đo trên ba video, thang 0..1, càng cao càng đa dạng:

| Video | Cả khung | Sân diễn | Khung cố định làm phẳng |
|---|---|---|---|
| `cache-stale` (13 cảnh) | 0,109 | 0,139 | **21%** |
| `93-ham-bam-nhanh` (9 cảnh) | 0,101 | 0,161 | **37%** |
| `91-bam-khong-phai-an-danh` (9 cảnh) | 0,120 | 0,197 | **39%** |

Cột cuối là cột đáng đọc nhất, và nó chỉ ra một nguyên nhân mà "thư viện cảnh quá
ít" không giải thích được: `chrome()` vẽ rail ở y=62, chip chương ở y=150, tiêu đề
ở y=244, sân diễn 470–1296, thẻ phụ đề ở y=1332, dòng chân ở y=1524 — **giống hệt
nhau ở cả 17 loại cảnh, trong mọi video**. Nên hai cảnh khác hẳn nội dung vẫn chia
nhau một khung xương giống nhau, và khung đó ăn mất 21–39% độ đa dạng.

### Chỗ đơn điệu nhất, và nó là một dòng code

Ba cặp cảnh giống nhau nhất, đo trên `cache-stale`:

```
0,036   probe      <-> probe
0,042   statement  <-> statement
0,071   statement  <-> statement
```

Cùng một loại cảnh thì dạng bóng gần như **trùng khớp**. Với `statement` `ask`
`rule` thì nguyên nhân là đúng một dòng, giống nhau ở cả ba hàm:

```python
y0 = STAGE_CY - blk / 2      # khối chữ LUÔN căn giữa sân diễn
```

Nên mọi cảnh chữ của cả kênh là một cục chữ ở đúng một chỗ. Đã thêm trường `neo`
(`tren` / `giua` / `duoi`) cho ba loại đó, mặc định `giua` nên không file cũ nào
đổi. Đo lại số 91 sau khi neo hai cảnh:

| | trước | sau |
|---|---|---|
| khác biệt sân diễn | 0,185 | **0,197** |
| cặp giống nhau nhất | 0,068 `statement`↔`statement` | **0,112** `compare`↔`rule` |

Cặp `statement`↔`statement` rời khỏi top ba. Hai dòng YAML, không thêm một loại
cảnh nào, không sửa một pixel nào của thư viện.

### Vì sao CHƯA viết lại renderer thành primitive + composition

Đề xuất thay `sc_bigstat` / `sc_compare` / `sc_flow`… bằng một tầng
*primitives → compositions → motions* đúng hướng nhưng **sai thứ tự**, và nó đánh
đổi mất đúng thứ tài sản duy nhất của kênh này.

`gantt` có hình học cố định **vì** `lint.py` kiểm được nó: hai thanh chồng nhau,
ô số đổi mà không việc nào vừa xong, khoảng chết quá 14%, `verdict_at` chốt trước
khi mô phỏng chạy hết. Với composition tự do thì **không phép kiểm nào trong số
đó còn tồn tại** — không lint được "bố cục này có đang nói thật hay không" khi bố
cục là tuỳ ý. Xem README mục *"`gantt` KHÔNG mô phỏng gì"*: mô phỏng ở đây không
có model thực thi phía sau, nó vẽ đúng cái người viết khai, nên phần *kiểm* chính
là phần giữ cho nó không nói dối.

Và một điểm nữa: `composition: shared-state` cộng `motions: [pull_snapshot,
overwrite]` **cũng là một template**, chỉ chi tiết hơn. Mười tám composition thì
người viết vẫn sẽ trôi về ba cái quen. Vấn đề đơn điệu không giải được bằng cách
làm template nhỏ hơn — nó giải được bằng cách **bắt buộc đa dạng** và **đo được**
đa dạng, tức đúng hai thứ vừa dựng ở trên.

Thứ tự nên làm, xếp theo lợi ích trên chi phí (đo bằng chính `do_don_dieu.py`):

| # | Việc | Trạng thái | Lợi ích đo được |
|---|---|---|---|
| 1 | `neo` cho `statement` `ask` `rule` | ✅ xong | cặp giống nhất 0,068 → 0,112 |
| 2 | Cổng đếm **dạng bóng**, không đếm tên loại cảnh | ✅ xong | bắt được cả hai cảnh khác loại mà cùng một cục chữ |
| 3 | `head` thành tuỳ chọn, sân diễn giãn lên khi vắng nó | chưa | thu lại phần lớn của 21–39% kia, và cho nhịp mô phỏng thêm 190px |
| 4 | Thang biểu diễn — bắt mỗi video đi qua ≥3 tầng | chưa | đa dạng ở tầng *nội dung*, không chỉ tầng bố cục |
| 5 | Thư viện primitive + composition | chưa | chỉ làm sau khi 1–4 đã cạn, và phải mang theo cách lint mới |

### Thang biểu diễn

Một cơ chế biểu diễn được ở năm tầng, và video hay thì **di chuyển giữa các tầng**
thay vì nằm nguyên ở một tầng:

| Tầng | Là gì | Loại cảnh của `bench` |
|---|---|---|
| 1 — vật thể | người, hộp, két, đồng hồ, ổ khoá | đạo cụ (`prop`) |
| 2 — ẩn dụ gọn | request là gói tin, cache là bản copy | `topology`, `gop` |
| 3 — sơ đồ hệ thống | trình duyệt → API → Redis → database | `topology`, `thac` |
| 4 — trạng thái | `cache = 100`, `db = 120` | `gantt` (ô số), `counters`, `ban_sao` |
| 5 — code | `value = cache.get(key)` | `code`, `probe` |

Mùa 7 nằm gần hết ở tầng 4 và 5 — đó là lý do nó chính xác nhưng khô. Ẩn dụ ở
tầng 2 phải dùng có giới hạn: khán giả là dev đã đi làm, và `files/skill/` ghi
đúng nguyên tắc *"dùng một phép so sánh đời thường rồi lập tức quay lại thuật ngữ
chính xác — đừng dừng ở phép so sánh, vì so sánh nào cũng có chỗ sai"*.

---

## Cổng chất lượng: cái nào máy chạy, cái nào người phải đọc

### Máy chạy — `lint.check_cong`

Mười hai phép kiểm soi **cả chuỗi cảnh**, không soi từng cảnh. Chạy tự động mỗi
lần lint hoặc render:

```bash
PYTHONIOENCODING=utf-8 python src/lint.py screenplays/<f>.yaml --engine voicestudio
```

Ba cái là **LỖI**, và cả ba chỉ mã hoá lại điều CONG-THUC.md đã ghi là tuyệt đối:

| Kiểm | Vì sao là lỗi |
|---|---|
| Cảnh 01 mở bằng lời chào hoặc lời dẫn | mất bốn giây đắt nhất của video |
| Gọi tên thủ phạm TRƯỚC cảnh mô phỏng | mất sạch căng thẳng, phần còn lại thành bài giảng |
| Câu hỏi cuối là `bạn nghĩ sao` / `comment bên dưới` | câu hỏi chung chung thì không ai trả lời |

Phần còn lại là **cảnh báo**, vì chúng phụ thuộc định dạng: thiếu cảnh `ask`;
câu hỏi cuối không nhắc `của bạn`; không có cảnh mô phỏng động; mô phỏng dưới
15% số cảnh; ba cảnh quy tắc; thiếu vế *phát hiện sớm*; ba cảnh cùng loại liên
tiếp; `statement` quá 25%.

### Người phải đọc — bảy câu không tự động hoá được

Đọc lại kịch bản và trả lời thật. Một câu NO là viết lại, không phải chỉnh sửa:

1. **Hook** — đọc to câu mở. Người nghe có buột miệng hỏi *"ủa sao vậy?"* không?
2. **Dự đoán** — nhịp 3 có đá đúng cách giải thích mà mid-level đang nghĩ không?
   Đoán sai chỗ này là video thành nhạt, và không thước đo nào bắt được.
3. **Nhân quả** — người xem có chỉ được vào một khung hình và nói *"lỗi xảy ra
   chính xác ở đây"* không?
4. **Dư thừa** — `caption` có chỉ lặp lại `narration` không?
5. **Liên tục** — chín cảnh có cảm giác thuộc cùng một cuộc điều tra, hay là
   chín slide rời?
6. **Chính xác** — có câu nào khẳng định tuyệt đối trong khi nó phụ thuộc bản
   cài đặt không? Nếu có thì nêu giả định ra: *"giả sử hai worker cùng xử lý
   một bản ghi mà không có khoá"*.
7. **Giá trị** — xem xong, người xem có biết đủ ba thứ: lỗi xảy ra thế nào,
   chặn ở đâu, phát hiện bằng gì?

---

## Trạng thái hiện tại của source, đo bằng chính cổng này

Chạy cổng lên 32 screenplay đã xong (không tính 70 khung tự sinh):

| Phát hiện | Số file | Đánh giá |
|---|---|---|
| **0 lỗi** | 32/32 | không file nào vi phạm ba luật tuyệt đối |
| **Mùa 7 sạch hoàn toàn** | 9/9 | sau khi sửa: không cảnh báo nào, mô phỏng 21–25% lời đọc, `statement` 22% |
| Thiếu vế *phát hiện sớm* trong cảnh quy tắc | ~15 | **món nợ thật.** CONG-THUC.md nhịp 6 gọi đây là *"chỗ hầu hết nội dung khác bỏ quên, và là lý do mid-level lưu video lại"* — kể cả `cache-stale` cũng thiếu |
| Không có cảnh mô phỏng **động** | 14 | phần lớn là định dạng HAI ĐOẠN CODE (mùa 3) — có chủ ý. Nhưng `ho-so-mat`, `hom-nao-di-an`, `cache-invalidation` thì trượt Cửa 2 thật |
| Nhịp mô phỏng dưới 20% lời đọc | 3 | **đã sửa 8 số của mùa 7**: viết thêm 2–3 câu cho cảnh mô phỏng, nâng từ 11–13% lên 21–25%. Còn `gil-va-viec-cho` (14%) và hai file cũ |
| `statement` quá 25% | 6 | **đã sửa số 96 và 98** bằng cách đổi `statement` thành `compare` — cả hai đúng là một `compare` bị nén. Cao nhất còn lại: `54-so-nguyen-nho-dung-chung` 50%, ba cảnh `statement` liên tiếp |
| Câu hỏi cuối không nhắc `của bạn` | 12 | rẻ nhất để sửa, nhưng **sửa `narration` là đổi khoá cache**, nên chỉ sửa file chưa render |
| Thiếu cảnh `ask` chốt | 4 | `double-charge`, `ho-so-mat`, `hom-nao-di-an`, `cache-invalidation` — bốn file cũ nhất, viết trước khi có nhịp 7 |

**Không sửa hàng loạt.** Sửa `narration` của một file đã render là đổi khoá cache
của toàn bộ cảnh đó, tức trả tiền sinh giọng lại. Ưu tiên:

1. File **chưa render bao giờ** thì sửa ngay (mùa 7 và 70 khung tự sinh).
2. File đã render thì chỉ sửa khi có việc khác buộc phải render lại nó.
3. Bốn file cũ nhất (`ho-so-mat`, `hom-nao-di-an`, `cache-invalidation`,
   `double-charge`) nên **viết lại từ đầu** theo `bench`, không vá — chúng dùng
   theme cũ và thiếu tới hai nhịp.
