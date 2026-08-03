# Công thức kể: HIỆN TRƯỜNG VỤ ÁN

Định dạng chính của kênh. Người xem mục tiêu: **dev mid-level, 2–5 năm**.

Ý tưởng cốt lõi: không giảng bài, mà **điều tra một vụ việc**. Mở bằng một triệu
chứng production kỳ quặc, loại dần nghi phạm, rồi quay chậm hiện trường cho tới
khi lộ cơ chế. Người xem ở lại vì muốn biết thủ phạm, chứ không phải vì muốn học.

---

## Vì sao chọn công thức này

**Vì mid-level ai cũng từng debug production.** Họ nhận ra mình ngay ở giây đầu,
và cái cảm giác "tao cũng từng dính vụ này" mạnh hơn mọi lời hứa kiến thức.

**Vì nó đặt mô phỏng vào trung tâm.** Nhịp dài nhất của video là đoạn quay chậm
hiện trường — đúng thứ mà tool này làm được còn người dựng tay thì không. Không
ai ngồi animate một race condition trong CapCut cho từng video.

**Vì chưa kênh dev Việt nào làm.** Đa số là người nói cộng ảnh chụp code.

---

## Khung nhịp (~75–95 giây)

| Giây | Nhịp | Nhiệm vụ | Loại cảnh |
|---|---|---|---|
| 0–4 | **Triệu chứng** | Một câu, cụ thể, có số, nghe vô lý | `bigstat` / `compare` |
| 4–12 | **Loại nghi phạm hiển nhiên** | "Log sạch, không exception nào" | `code` (`mark: check`) |
| 12–20 | **Loại nghi phạm số 1** | Đá văng cách giải thích ai cũng nghĩ tới | `compare` |
| 20–52 | **QUAY CHẬM HIỆN TRƯỜNG** | Mô phỏng cơ chế. Nhịp dài nhất. | `race` và các scene mô phỏng |
| 52–64 | **Thủ phạm** | Gọi tên, một câu | `bigstat` |
| 64–80 | **Chặn + phát hiện sớm** | 1 quy tắc + 1 chỉ số cần theo dõi | `checklist` 2 dòng |
| 80–90 | **Câu hỏi về hệ thống của bạn** | Đẩy về bình luận | `code` |

Thời lượng tự tính từ giọng đọc, nên đây là khung tương đối. Điều bắt buộc là
**thứ tự** và **tỉ lệ**: đoạn mô phỏng phải chiếm 35–40% video.

---

## Quy tắc từng nhịp

### Nhịp 1 — Triệu chứng (0–4s)

Đây là nhịp quyết định cả video. Ba điều kiện, thiếu một là hỏng:

1. **Cụ thể, không khái quát.** ✅ "Khách bấm một lần, hệ thống trừ tiền hai lần."
   ❌ "Xử lý concurrency sai gây hậu quả nghiêm trọng."
2. **Nghe vô lý.** Phải có mâu thuẫn nội tại thì người xem mới dừng.
3. **Không tiết lộ nguyên nhân.** Đặt tên bệnh ở giây đầu là mất sạch căng thẳng.

> Kiểm tra nhanh: đọc to câu mở. Nếu người nghe **không** buột miệng hỏi "ủa
> sao vậy?" thì viết lại.

### Nhịp 2 — Loại nghi phạm hiển nhiên (4–12s)

Chặn ngay cách giải thích dễ nhất, thường là "chắc do lỗi/exception". Câu
"log sạch, không có lỗi nào" cực mạnh với mid-level, vì họ biết loại bug im lặng
là loại đáng sợ nhất.

### Nhịp 3 — Loại nghi phạm số 1 (12–20s)

Đá văng cách giải thích mà **90% người xem đang nghĩ trong đầu**. Nhịp này tạo
khoảng hở "tôi tưởng tôi biết". Muốn viết đúng nhịp này thì phải thật sự đoán
được khán giả đang nghĩ gì — sai chỗ này là video thành nhạt.

### Nhịp 4 — Quay chậm hiện trường (20–52s) ⭐

Nhịp quan trọng nhất. Ba nguyên tắc:

- **Cho thấy, đừng kể.** Không dùng câu "hai request chen vào nhau". Chạy hai
  request đó trên màn hình cho người xem tự thấy.
- **Chậm hơn đời thực rất nhiều.** Sự cố xảy ra trong 5ms; ở đây kéo thành 20
  giây. Chính việc kéo giãn mới là thứ giải thích.
- **Một biến số mỗi lần.** Đừng animate ba thứ cùng lúc.

### Nhịp 5 — Thủ phạm (52–64s)

Một câu. Không giải thích thêm, không kèm điều kiện. Nhịp mô phỏng đã giải thích
xong rồi; ở đây chỉ đặt tên.

### Nhịp 6 — Chặn và phát hiện sớm (64–80s)

**Đúng một quy tắc và đúng một chỉ số.** Ba quy tắc thì người xem không nhớ cái
nào. Vế "phát hiện sớm" là chỗ hầu hết nội dung khác bỏ quên, và là lý do
mid-level lưu video lại.

### Nhịp 7 — Câu hỏi (80–90s)

Hỏi về hệ thống của chính họ, không hỏi ý kiến chung chung.
✅ "Endpoint thanh toán của bạn có idempotency key chưa?"
❌ "Bạn nghĩ sao về vấn đề này?"

---

## Lỗi thường gặp

| Lỗi | Hậu quả | Cách sửa |
|---|---|---|
| Nói tên bệnh ở nhịp 1 | Mất sạch căng thẳng, còn lại là bài giảng | Giấu tới nhịp 5 |
| Nhịp mô phỏng dưới 20 giây | Mất luôn lợi thế duy nhất của kênh | Cắt bớt nhịp 2–3 để dồn cho nhịp 4 |
| Nhịp 3 đoán sai suy nghĩ khán giả | Nhạt, không có khoảnh khắc "à hoá ra" | Hỏi vài dev thật xem họ đoán nguyên nhân là gì |
| Ba quy tắc ở nhịp 6 | Không nhớ nổi cái nào | Chọn một, bỏ hai |
| Triệu chứng bịa cho kêu | Mid-level phát hiện ngay, mất uy tín cả kênh | Chỉ dùng sự cố thật hoặc dựng lại được |
| Số liệu bịa | Như trên, nhưng nặng hơn | Đo thật hoặc bỏ số |

---

## Mẫu điền

```yaml
# NHỊP 1 — triệu chứng cụ thể, nghe vô lý, chưa lộ nguyên nhân
# NHỊP 2 — loại nghi phạm hiển nhiên (thường: "log sạch")
# NHỊP 3 — loại cách giải thích mà 90% người xem đang nghĩ
# NHỊP 4 — MÔ PHỎNG: cho thấy cơ chế, kéo chậm, một biến số
# NHỊP 5 — gọi tên thủ phạm, một câu
# NHỊP 6 — một quy tắc chặn + một chỉ số phát hiện sớm
# NHỊP 7 — câu hỏi về hệ thống của người xem
```

---

## Định dạng phụ: HAI ĐOẠN CODE (~45–60s)

Xen giữa các kỳ để đăng dày. Hai đoạn code gần y hệt, một cái hỏng ở production,
đếm ba giây cho người xem chọn, rồi chạy song song cả hai. Rất kích bình luận vì
người xem đã trót chọn trong đầu.

Dùng chung thư viện mô phỏng với định dạng chính nên không tốn thêm công dựng.

---

## Thư viện mô phỏng cần có

Nhịp 4 sống nhờ những scene này. Mỗi cái viết một lần, mọi screenplay sau gọi lại.

| Scene | Trả lời câu | Cho thấy điều gì | Dùng cho mảng |
|---|---|---|---|
| `topology` ✅ | **Ở ĐÂU** | Các tầng hệ thống thành khối, request là chấm tròn bay giữa chúng | Tất cả |
| `race` ✅ | **KHI NÀO** | Hai luồng song song, đan và chồng lấn theo thời gian | BE, Database |
| `queue` | BAO NHIÊU | Hàng đợi đầy lên rồi rút xuống | Hạ tầng, BE |
| `multiply` | BAO NHIÊU | Bộ đếm nhân lên ngoài tầm kiểm soát | Database (N+1), FE (re-render) |
| `expire` | BAO LÂU | Đồng hồ đếm ngược và dữ liệu hỏng khi hết hạn | Database, BE |

✅ = đã dựng xong.

**Hai scene mô phỏng đầu bổ sung cho nhau, không thay thế nhau.** `topology` cho
thấy đường đi và ai sinh ra lỗi; `race` cho thấy hai việc chồng lấn thời gian ra
sao. Với race condition thì thời gian chính là bản chất, nên bỏ `race` là mất
mất thông tin. Screenplay `double-charge.yaml` dùng **cả hai nối tiếp** ở nhịp 4.

**Quy tắc khi xếp lịch mô phỏng: không được để khoảng chết.** Nếu có một giây nào
không có gì chuyển động, mắt người xem rời màn hình đúng lúc đó. Kiểm tra bằng
`python research/sim_strip.py topology` — nó xuất dải ảnh 6 mốc thời gian, nhìn
là thấy ngay chỗ hở.
