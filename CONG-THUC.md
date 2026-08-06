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

---

## Biến thể mở đầu: HOOK 5 NHỊP

Khung 7 nhịp ở trên mở bằng *triệu chứng* rồi đi luôn vào loại nghi phạm. Biến
thể này thay ba nhịp đầu bằng **năm nhịp mở đầu** — cùng tinh thần điều tra,
nhưng nói thẳng với người xem rằng họ sẽ nhận được gì, trước khi vào mô phỏng.
Dùng khi muốn tăng lượt lưu chứ không chỉ lượt xem hết.

Screenplay mẫu: [cache-stale.yaml](screenplays/cache-stale.yaml) (theme `bench`).

| Nhịp | Nhiệm vụ | Loại cảnh | Ví dụ |
|---|---|---|---|
| 1 | **Tình huống quen** — một lỗi thật, cụ thể, nghe vô lý | `probe` | ba dòng shell: `DEL` OK, `UPDATE` 1 row, `GET` → vẫn số cũ |
| 2 | **Hậu quả / chỗ khó chịu** — vì sao nó *không* được sửa | `statement` | "xoá lần hai thì đúng" → nên không ai điều tra tiếp |
| 3 | **Gợi mở nguyên nhân thật** — chỉ ra chỗ ít ai soi, **chưa đặt tên** | `statement` | "ba mili giây giữa hai lệnh, không log nào ghi lại" |
| 4 | **Người xem đạt được gì** — đúng hai dòng, không hứa quá | `list` | thứ tự đúng của hai lệnh + vì sao vẫn cần TTL |
| 5 | **Vào demo ngay** — câu cuối của nhịp 4, không thành cảnh riêng | → `gantt` | "giờ quay chậm ba mili giây đó" |

Bốn quy tắc bắt buộc, thiếu một là hỏng:

1. **Không mở bằng lời chào.** "Xin chào mọi người, hôm nay chúng ta sẽ học…"
   là bốn giây chết ở đúng chỗ đắt nhất của video. Nhịp 1 phải là *lỗi*.
2. **Nhịp 1 phải là một lỗi tái dựng được**, không phải một khái niệm. Ba dòng
   shell thật mạnh hơn mọi câu mô tả, vì mid-level đọc chúng nhanh hơn đọc chữ.
3. **Nhịp 3 không được đặt tên bệnh.** Chỉ ra *chỗ* ("ba mili giây giữa hai
   lệnh") chứ không gọi tên ("race condition khi invalidate cache"). Gọi tên ở
   giây thứ mười là mất sạch lý do ở lại.
4. **Nhịp 4 không được hứa sai.** Viết "TTL chặn cái sai sống mãi" thì đúng;
   viết "một dòng config hết bug" thì sai, và mid-level phát hiện ngay. Video
   này còn dành riêng một cảnh để **thừa nhận chưa đạt 100%** — đó là chỗ lấy
   được lòng tin, không phải chỗ mất.

Đo lại sau khi viết: nhịp 1 tới nhịp 3 phải xong trong khoảng **20–25 giây**.
Dài hơn thì cắt chữ, đừng cắt nhịp.

### Hai lần mô phỏng, giữ nguyên bố cục

`cache-stale.yaml` chạy `gantt` **hai lần**: lần một sai thứ tự (bộ đếm "khách
đọc sai" chạy lên 8), lần hai đúng thứ tự (**bộ đếm đứng ở 0**). Hai cảnh dùng y
nguyên bố cục, y nguyên bề rộng thanh, chỉ đổi thứ tự hai lệnh của lane trên.

Đó là toàn bộ mẹo: **giữ nguyên bố cục thì người xem đối chiếu được bằng mắt**,
không cần một câu giải thích nào. Đổi bố cục ở lần hai là mất sạch tác dụng —
lúc đó hai cảnh chỉ còn là hai hình khác nhau.

### Số đo thật của `cache-stale.yaml`

Đo từ log render, không phải ước lượng:

| | Giây | % video |
|---|---|---|
| Tổng | 120,9 | 100% |
| Hook (cảnh 1–4) | 33,1 | 27% |
| *trong đó nhịp 1–3* | *25,0* | — |
| Hai cảnh mô phỏng | 28,4 | **23%** |
| Cảnh dài nhất (`gantt` #1) | 15,4 | — |

Mô phỏng 23% là **dưới** mức 35–40% mà công thức nhắm. Đổi lại, hai cảnh đó vẫn
là hai cảnh dài nhất video (15,4s và 13,0s so với 7–10s của các cảnh khác) và
không có giây chết nào. Muốn kéo lên 35% thì **viết thêm lời đọc** cho hai cảnh
đó — đừng nâng `min_duration`, vì nâng thì đầu đọc quét chậm hơn nhưng im lặng.

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
| Mở bằng lời chào | Mất 4 giây đắt nhất của video | Nhịp 1 phải là *lỗi*, xem HOOK 5 NHỊP |
| Hứa "hết bug mãi mãi" | Mất uy tín, và không đúng | Nói rõ giới hạn, dành hẳn 1 cảnh thừa nhận chưa 100% |
| Mô phỏng lần hai đổi bố cục | Người xem không đối chiếu được | Giữ y nguyên bố cục, chỉ đổi biến số |

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

Mẫu điền cho biến thể HOOK 5 NHỊP (theme `bench`):

```yaml
# NHỊP 1 — probe:      lỗi thật, 3 dòng shell, dòng cuối vô lý
# NHỊP 2 — statement:  hậu quả — vì sao lỗi này KHÔNG được sửa
# NHỊP 3 — statement:  chỗ ít ai soi, CHƯA đặt tên bệnh
# NHỊP 4 — list:       đúng 2 dòng người xem sẽ đạt được
# NHỊP 5 —             câu cuối của narration nhịp 4, dẫn thẳng vào gantt
# ---- MÔ PHỎNG 1 — gantt: chạy SAI, bộ đếm hậu quả chạy lên
# ---- statement:    gọi tên thủ phạm, một câu
# ---- rule 01:      quy tắc chặn
# ---- MÔ PHỎNG 2 — gantt: chạy ĐÚNG, cùng bố cục, bộ đếm đứng ở 0
# ---- probe:        đường hỏng còn lại (lệnh mất trong im lặng)
# ---- counters:     cái sai không tự hết qua 1 giờ / 1 ngày / 1 tuần
# ---- rule 02:      lưới cuối
# ---- statement:    thừa nhận chưa 100%
# ---- ask:          câu hỏi về hệ thống của chính người xem
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

| Scene | Theme | Trả lời câu | Cho thấy điều gì | Dùng cho mảng |
|---|---|---|---|---|
| `gantt` ✅ | `bench` | **KHI NÀO + ĐANG GIỮ GÌ** | Hai luồng theo thời gian **cộng ô số đổi giá trị theo đầu đọc** và bộ đếm hậu quả | BE, Database |
| `counters` ✅ | `bench` | BAO LÂU | Dãy ô số cạnh nhau: cùng một giá trị sai qua nhiều mốc thời gian | Database, BE |
| `topology` ✅ | `phongtoi` | **Ở ĐÂU** | Các tầng hệ thống thành khối, request là chấm tròn bay giữa chúng | Tất cả |
| `race` ✅ | `phongtoi` | **KHI NÀO** | Hai luồng song song, đan và chồng lấn theo thời gian | BE, Database |
| `queue` | — | BAO NHIÊU | Hàng đợi đầy lên rồi rút xuống | Hạ tầng, BE |
| `multiply` | — | BAO NHIÊU | Bộ đếm nhân lên ngoài tầm kiểm soát | Database (N+1), FE (re-render) |

✅ = đã dựng xong.

**`gantt` hơn `race` ở đúng một điểm, và đó là điểm quyết định:** nó có hàng ô số
phía trên, giá trị trong đó đổi theo đầu đọc. Người xem không phải tự suy ra "vậy
lúc này cache đang giữ gì" — nó hiện ra thành chữ. Chính chỗ đó biến một biểu đồ
thành một thí nghiệm. Thêm bộ đếm hậu quả ("khách đọc sai: 8") thì người xem có
một con số để nhớ và để kể lại.

**Hai scene mô phỏng đầu bổ sung cho nhau, không thay thế nhau.** `topology` cho
thấy đường đi và ai sinh ra lỗi; `race` cho thấy hai việc chồng lấn thời gian ra
sao. Với race condition thì thời gian chính là bản chất, nên bỏ `race` là mất
mất thông tin. Screenplay `double-charge.yaml` dùng **cả hai nối tiếp** ở nhịp 4.

**Quy tắc khi xếp lịch mô phỏng: không được để khoảng chết.** Nếu có một giây nào
không có gì chuyển động, mắt người xem rời màn hình đúng lúc đó. Kiểm tra bằng
`python research/sim_strip.py topology` — nó xuất dải ảnh 6 mốc thời gian, nhìn
là thấy ngay chỗ hở.
