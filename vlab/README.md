# Visual Lab — vòng R&D 01

Nhánh thí nghiệm, **không phải production**. `src/bench.py` và 102 screenplay
không bị chạm tới. Ở đây tương thích ngược không phải mục tiêu, và một prototype
bỏ đi vẫn có giá.

```bash
python src/vlab/dung.py vlab/129-idor-huong-c.vlab.yaml          # 1 khung/nhịp
python src/vlab/dung.py vlab/129-idor-huong-c.vlab.yaml --dai 6  # 6 khung/nhịp
python research/do_don_dieu.py 129-idor-huong-c                  # đo
```

---

## 1. GIẢ ĐỊNH BỊ THỬ THÁCH

> **`scene` là đơn vị bố cục.** Mỗi cảnh gọi `build()` với một `B(dur)` mới, vẽ
> lại từ đầu trên một hình chữ nhật sân diễn cố định (470..1296), rồi tan đi.

Hai hệ quả đo được, không phải suy diễn:

- `research/do_don_dieu.py`: khung cố định làm phẳng **21–39%** độ đa dạng
- hai cảnh cùng loại cách nhau **0,036–0,042** trên thang 0..1, tức gần như trùng

Và một hệ quả nặng hơn, không đo được nhưng quyết định hơn: **không thể hé lộ
thông tin bằng cách di chuyển máy quay.** Muốn người xem *phát hiện ra* một thứ
thì phải vẽ thêm nó vào một cảnh khác — tức nói cho họ, không phải để họ tự thấy.

## 2. BA HƯỚNG

| | Mô hình tư duy | Đơn vị | Hé lộ bằng gì |
|---|---|---|---|
| **A** — dấu vết thực thi | các tầng hệ thống, gói tin đi qua | cảnh | vẽ thêm một cảnh |
| **B** — tập hợp và thành viên | hai tập, một phần tử thuộc tập nào | cảnh | tô màu phần tử |
| **C** — không gian bền vững | một thế giới liên tục, ống kính di chuyển trong đó | nhịp | **ống kính** |

Hướng A là đúng cái production sẽ làm — đã dựng thật bằng `bench` để so sánh
ngang hàng: [`129-idor-huong-a.yaml`](129-idor-huong-a.yaml). Hướng C dựng bằng
engine mới: [`129-idor-huong-c.vlab.yaml`](129-idor-huong-c.vlab.yaml). Hướng B
không dựng — nó là hướng A với một primitive khác, cùng một mô hình "cảnh vẽ
lại từ đầu", nên không trả lời được câu hỏi của vòng này.

Đề tài benchmark: **129 (IDOR)**, thuộc `so_huu` — nhóm 25 chủ đề lớn nhất
chưa có hình nào, theo `research/ban_do_hinh.py`.

## 3. PROTOTYPE

`src/vlab/` — 3 module, ~700 dòng:

| | Là gì |
|---|---|
| `the_gioi.py` | `DoiTuong` sống xuyên suốt, `Cam` (viewport trong thế giới), `Nhip` = ống kính + đổi trạng thái, `kiem()` = lint ở **tầng ngữ nghĩa** |
| `ve.py` | 6 primitive vẽ trong **toạ độ thế giới**: `vung` `hang` `the` `cong` `goi` `nhan` |
| `dung.py` | ba chế độ khung (`day` / `toi_gian` / `khong`), dựng still |

Ba thứ engine này làm được mà `bench` không:

1. **Hé lộ bằng ống kính.** Nhịp 3 không thêm đối tượng nào ngoài vùng thứ hai —
   nó chỉ lui ống kính, và vùng đó *đã luôn ở đó*, chỉ nằm ngoài khung.
2. **Khung là tham số của nhịp.** Nhịp cao trào chạy `khung: khong` — không rail,
   không tiêu đề. Luật duy nhất giữ lại: nhịp đầu và nhịp cuối phải `day`.
3. **Lint ở tầng ngữ nghĩa.** `kiem()` bắt được *"`chu_y` trỏ vào đối tượng có
   tâm nằm ngoài khung nhìn"* — tức "đang bảo người xem chú ý vào thứ họ không
   thấy". `lint.py` của production không thể có phép kiểm này: nó chỉ kiểm được
   hình học, vì ở đó hình học *chính là* nội dung.

Nó bắt lỗi thật ngay lần đầu chạy: nhịp 3 khai `chu_y: [r1043, api]` trong khi
thẻ `api` đã trôi khỏi cạnh trên.

## 4. TRƯỚC / SAU

Cùng câu chuyện, cùng 6 nhịp, ánh xạ một-đối-một.

| | khác biệt trung bình | cặp giống nhau nhất |
|---|---|---|
| **A** production `bench` | 0,127 | **0,041** `statement`↔`statement` |
| **C** visual lab | **0,141** (+11%) | **0,067** (+63%) |

Còn ba biến thể trung gian, để thấy con số **không** đi một chiều:

| biến thể | đo được | mắt nhìn |
|---|---|---|
| C1 — ống kính viết tay, tiêu điểm nhị phân | **0,174** (+37%) | nhịp 4–5 **xấu hơn** bản A |
| C2 — ống kính suy từ tiêu điểm | 0,163 | **tệ nhất cả ba** |
| C3 — ống kính viết tay, ba tầng nhấn mạnh | 0,141 | nhịp 1–2 và 6 **hơn A**, nhịp 4–5 vẫn kém A |

## 5. CÁI GÌ THẤT BẠI

**a. Thế giới nằm ngang trong khung dọc.** Bản đầu xếp hai vùng cạnh nhau theo
chiều ngang. Khung 9:16 cao gấp 1,78 lần bề rộng, nên nó để lại 40% diện tích
trống ở trên và dưới, còn chữ tụt xuống sàn 17px. **Bài học:** trong khung dọc,
đường biên phải nằm ngang và cú hé lộ phải là một cú lui theo chiều dọc.
"Ngoài khung" ở định dạng này nghĩa là *ở trên* hoặc *ở dưới*.

**b. Ống kính suy từ tiêu điểm — thất bại hoàn toàn.** Ý tưởng: đừng để người
viết đặt toạ độ, chỉ khai tiêu điểm rồi engine tính khung nhìn sao cho tiêu điểm
chiếm `muc` phần bề rộng. Kết quả tệ hơn cả hai bản còn lại, và số đo cũng giảm.
**Lý do:** một hình chữ nhật bao quanh tập tiêu điểm **không phải** một khung
hình tốt. Khung hình tốt cần biết *bối cảnh nào phải còn nhìn thấy để tiêu điểm
có nghĩa* — và thông tin đó không nằm trong bounding box. Hàm
`cam_tu_tieu_diem()` giữ lại trong code kèm chú thích, không xoá: nó là bằng
chứng cho một hướng đã đóng.

**c. Dùng `p` của `ttext` như độ mờ.** `p` là *tiến độ hé chữ* (mask trượt lên),
không phải opacity. Nên mọi đối tượng bị làm mờ 0,42 lại được vẽ với chữ **cắt
mất một nửa** — nhìn như chữ vỡ, không nhìn như chữ nhạt đi. Đây là lỗi làm hỏng
nhiều nhất, và nó chỉ lộ ra khi nhìn still ở cỡ thật.

**d. Tiêu điểm nhị phân.** Chia "tiêu điểm / phần còn lại" rồi mờ phần còn lại
xuống 0,20 làm nhịp **hé lộ** mất nghĩa — vì nghĩa của nhịp đó *chính là* phép so
sánh giữa hai vùng, mờ cả hai đi là bỏ mất nội dung. Phải ba tầng: tiêu điểm 1,00
/ bối cảnh cần đọc 0,55 / chỉ cần có mặt 0,18.

**e. Nhãn neo vào góc đối tượng.** Ống kính cắt qua một vùng thì góc trái của nó
trôi ra ngoài màn hình, và nhãn "ĐƠN CỦA NGƯỜI KHÁC" biến mất trong khi chính
vùng đó đang là nội dung. Lỗi này **không tồn tại** ở sân diễn cố định, vì ở đó
góc của một khối luôn nằm trong khung. Đã sửa: nhãn dính, ép vào phần còn thấy.

## 6. NGUYÊN TẮC HỌC ĐƯỢC

**Nguyên tắc 1 — Ống kính là một kênh kể chuyện, không phải một hiệu ứng.**
Trong khung dọc, "chưa thấy" và "nằm ngoài khung" là hai thứ khác nhau, và cái
thứ hai mạnh hơn hẳn: người xem tự phát hiện thay vì được thông báo. Đây là điều
kiến trúc `scene` **không thể** làm, không phải làm kém hơn.

**Nguyên tắc 2 — Bỏ khung cố định là bỏ luôn một đảm bảo, và phải trả nó lại ở
chỗ khác.** `chrome()` + sân diễn cố định *đảm bảo* mỗi khung có đúng một khối
chính. Bỏ nó đi thì không gì đảm bảo điều đó nữa. Trả lại bằng **nhấn mạnh ba
tầng** thì được một phần; trả lại bằng **ống kính tự tính** thì thất bại.

**Nguyên tắc 3 — Đa dạng và rõ ràng đánh đổi nhau, và `do_don_dieu.py` chỉ thấy
một phía.** Bản vô kỷ luật nhất đo cao nhất (0,174) và nhìn tệ nhất ở hai nhịp.
Áp kỷ luật tiêu điểm làm số **tụt** xuống 0,141 trong khi mắt thì tốt lên. Nên
số đó là *cảnh báo trần*, không phải hàm mục tiêu: nó phát hiện được video một
màu, nhưng không phát hiện được video rối.

**Nguyên tắc 4 — Thế giới bền vững không có anh hùng chữ.** Sức mạnh lớn nhất
của `bench` là `statement`/`rule`: một câu slab khổng lồ chiếm cả khung. Trong mô
hình thế giới, chữ là *một đối tượng giữa các đối tượng*, nên nó không bao giờ áp
đảo được khung hình. Đó là lý do nhịp 4–5 của C vẫn kém A.

## 7. HỆ QUẢ VỀ KIẾN TRÚC

Nếu bốn nguyên tắc trên đúng thì source cần đổi ở ba tầng, theo thứ tự này:

| Tầng | Đổi gì | Vì nguyên tắc |
|---|---|---|
| **Nhịp** | `cam` do người viết đặt, **không** suy tự động. `chu_y` + `boi_canh` là bắt buộc. | 2, và thất bại (b) |
| **Primitive** | `nhan_manh` phải là thuộc tính **liên tục** ảnh hưởng cả **cỡ chữ**, không chỉ độ mờ. Một đối tượng chữ ở nhấn mạnh 1,0 phải to gấp 4–5 lần mọi thứ khác. | 4 |
| **Kiểm** | Lint dời lên tầng ngữ nghĩa: quan hệ, tiêu điểm, khung nhìn. Hình học tự suy ra và không cần kiểm. | 3 |

## KẾT LUẬN CỦA VÒNG NÀY

**Chưa phải một bước nhảy thế hệ. Tiếp tục R&D.**

Ba trên sáu nhịp hơn hẳn bản production, hai nhịp kém hơn, và mức tăng đo được
tụt từ +37% xuống +11% ngay khi áp kỷ luật tiêu điểm. Theo đúng điều kiện thành
công đã đặt ra, kết quả này là *"bench nhưng khác đi"*, chưa phải *"production
nhìn rõ ràng là thế hệ trước"*.

Vòng 02 phải giải đúng một việc: **`nhan_manh` liên tục ảnh hưởng cỡ chữ** —
nguyên tắc 4. Đó là thứ duy nhất còn giữ `bench` ở trên, và nó không cần thêm
một loại cảnh nào.
