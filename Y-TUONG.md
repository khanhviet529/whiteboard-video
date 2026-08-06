# Kho ý tưởng nội dung

Bảng chọn chủ đề. Xem [CONG-THUC.md](CONG-THUC.md) để biết khung nhịp và quy tắc viết.

## Bốn tuyến nội dung

Định dạng HIỆN TRƯỜNG VỤ ÁN mở bằng một triệu chứng production, nhưng đó không phải
tuyến duy nhất. Mỗi tuyến có **hình dạng hook riêng**, vì "triệu chứng vô lý" chỉ hợp
với tuyến đầu.

| Tuyến | Hook mở bằng gì | Căng thẳng đến từ đâu |
|---|---|---|
| **1. Sự cố production** | Một triệu chứng cụ thể, nghe vô lý | "tao cũng từng dính vụ này" |
| **2. Hiểu nhầm phổ biến** | "Bạn tin X. Đúng trong chín phần mười trường hợp. Đây là phần còn lại." | "tôi tưởng tôi biết" |
| **3. Hai cách làm** | Hai đoạn code gần y hệt, đếm ba giây cho người xem chọn | người xem đã trót chọn trong đầu |
| **4. Cơ chế bên dưới** | "Bạn gọi hàm này mỗi ngày. Đây là những gì xảy ra sau đó." | tò mò, yếu nhất — cần một chỗ bất ngờ thật |

Tuyến 3 chính là "Định dạng phụ: HAI ĐOẠN CODE" đã ghi trong `CONG-THUC.md`.

Tuyến 4 yếu nhất và dễ thành bài giảng. Chỉ dùng khi bên trong cơ chế có một điều
trái trực giác, và điều đó mô phỏng được.

## Hai cửa lọc

### Cửa 1 — Số liệu lấy từ đâu

`CONG-THUC.md` viết: *"chỉ dùng sự cố thật **hoặc dựng lại được**"*. Hai vế đó khác
nhau, và vế sau mạnh hơn người ta tưởng. Ba mức, xếp từ tốt nhất:

| Mức | Nghĩa | Ví dụ |
|---|---|---|
| **đo được** | Viết script trong [repro/](repro/), chạy ra số thật rồi dùng đúng số đó | [phan_trang_bo_sot.py](repro/phan_trang_bo_sot.py) chạy ra: 3 bản ghi bị bỏ sót, 3 bản hiện hai lần |
| **suy ra** | Triệu chứng là hệ quả tất yếu của cơ chế, không cần đo | Thiếu `await` thì log ghi thành công mà dữ liệu không có — đó là định nghĩa của việc không chờ |
| **cần cấp** | Phải có sự cố thật, không dựng lại được | "Cache giữ giá cũ suốt một tuần rồi khách phát hiện" — thời gian và bối cảnh là chuyện thật |

**Bịa** thì khác cả ba: số không đo, không suy ra được, không có nguồn. Cấm, vì
`CONG-THUC.md` ghi hậu quả là mất uy tín cả kênh.

Điều quan trọng: **tuyến 1 không bắt buộc phải là sự cố đã xảy ra với ai đó.** Thiết
kế một tình huống rồi chạy thật để đo cũng là "dựng lại được", và số đo còn chắc hơn
ký ức. Cột `repro` trong bảng dưới ghi việc đó làm được hay không.

### Cửa 2 — Mô phỏng được không

Lợi thế duy nhất của tool này so với người dựng tay là các cảnh mô phỏng. Cửa này áp
cho **cả bốn tuyến**, không riêng tuyến 1.

| Cảnh | Mô phỏng được cái gì |
|---|---|
| `gantt` | hai luồng chồng lấn theo thời gian, ô số đổi giá trị, bộ đếm hậu quả |
| `counters` | một giá trị **không đổi** qua nhiều mốc thời gian |
| `probe` | ba dòng shell, dòng cuối vô lý |

Ý tưởng không lên được cảnh nào trong đây thì làm ở tool này cũng không hơn một video
người nói. Ví dụ "10 lệnh git nên biết" trượt cửa này.

Trường `domain:` (`fe` `be` `database` `infra`) không phải cửa lọc, chỉ để soát phủ
đều. Ba screenplay hiện có đều `be`/`database`.

---

## Đã viết

| Screenplay | Tuyến | Mảng | Triệu chứng | Mô phỏng |
|---|---|---|---|---|
| [cache-stale.yaml](screenplays/cache-stale.yaml) | 1 | database | Xoá cache xong, API vẫn trả giá cũ | `gantt` ×2 (sai / đúng thứ tự) |
| [n-plus-one.yaml](screenplays/n-plus-one.yaml) | 1 | database | 20 dòng dữ liệu, API mất 4,2 giây | `gantt` + bộ đếm câu SQL |
| [double-charge.yaml](screenplays/double-charge.yaml) | 1 | be | Khách bấm một lần, trừ tiền hai lần | `topology` + `race` (theme `phongtoi`) |

---

## Ứng viên

Cột **số liệu** dùng ký hiệu ở Cửa 1. Cột **repro** ghi có viết được script đo hay
không — nếu có thì ý tưởng đó không cần chờ ai cấp gì.

### database

| Ý tưởng | Cơ chế | Số liệu | repro | Mô phỏng |
|---|---|---|---|---|
| Phân trang bỏ sót bản ghi | `LIMIT/OFFSET` tính offset trên tập đã dịch vì có insert đồng thời | **đo được** — 3 bỏ sót, 3 lặp | ✅ [đã có](repro/phan_trang_bo_sot.py) | `gantt` lane đọc + lane insert, bộ đếm bản ghi mất |
| Lost update | Hai transaction đọc rồi ghi cùng bản ghi, không khoá lạc quan | đo được | sqlite, dễ | `gantt` hai lane + ô số giá trị cuối |
| Index bị bỏ qua | Bọc hàm quanh cột hoặc lệch kiểu làm index vô dụng | đo được | sqlite `EXPLAIN QUERY PLAN` | `probe` hai lần `EXPLAIN` |
| Transaction giữ khoá quá lâu | Gọi API bên ngoài **bên trong** transaction | đo được | sqlite + `sleep` | `gantt` lane dài + lane bị chặn |

### be

| Ý tưởng | Cơ chế | Số liệu | repro | Mô phỏng |
|---|---|---|---|---|
| Connection pool cạn | Pool 10, request thứ 11 xếp hàng; một câu chậm làm dồn cả hàng | đo được | `asyncio.Semaphore` | `gantt` + ô "kết nối rảnh", bộ đếm chờ |
| Tiền tính bằng float | `0.1 + 0.2` trong nhị phân không bằng `0.3` | **đo được** | 5 dòng Python | `probe` ba dòng phép tính |
| Thiếu `await` | Hàm trả về trước khi việc xong, lỗi thành unhandled rejection | **suy ra** | asyncio, dễ | `probe`: log OK + `SELECT` trống |
| Retry bão | Nhiều client retry cùng nhịp, không jitter | đo được | mô phỏng bằng vòng lặp | `gantt` nhiều lane cùng nhịp |
| Múi giờ | `TIMESTAMP` không kèm offset | đo được | `datetime` + `zoneinfo` | `counters`: một mốc, ba múi giờ |

### fe

| Ý tưởng | Cơ chế | Số liệu | repro | Mô phỏng |
|---|---|---|---|---|
| Re-render vô hạn | Object tạo mới mỗi render nằm trong dependency array, so sánh theo tham chiếu | **suy ra** | không (cần React) | `gantt` + bộ đếm số lần render |
| Race hai request search | Gõ nhanh, response về không đúng thứ tự gửi, kết quả cũ ghi đè kết quả mới | **suy ra** | asyncio mô phỏng được | `gantt` hai lane response đảo thứ tự |

### infra

| Ý tưởng | Cơ chế | Số liệu | repro | Mô phỏng |
|---|---|---|---|---|
| DNS TTL giữ endpoint cũ | Client cache bản ghi hết TTL mới đổi | **suy ra** | không | `counters`: sau 1 phút / 5 phút / 1 giờ |
| Health check quá nhạy | Timeout ngắn hơn thời gian xử lý bình thường | **cần cấp** | khó | `gantt` lane request + lane health check |

### Tuyến 2 — hiểu nhầm phổ biến

| Ý tưởng | Chỗ hiểu nhầm | Số liệu | Mô phỏng |
|---|---|---|---|
| `async` không phải song song | Một luồng, các việc **đan** vào nhau chứ không chạy cùng lúc; CPU-bound thì `async` không nhanh hơn | **đo được** | `gantt` một lane đan việc so với hai lane thật song song |
| Index không luôn nhanh hơn | Bảng nhỏ hoặc truy vấn lấy phần lớn số dòng thì quét toàn bảng nhanh hơn | đo được | `counters`: 100 / 10.000 / 1 triệu dòng |
| `SELECT *` không chỉ tốn băng thông | Chặn index-only scan, nên chậm cả ở phía DB | đo được | `probe` hai `EXPLAIN` |

---

## Nguồn cấp chất liệu

`build-your-own-x` (536k sao) **không dùng làm nguồn truyện** — nó index các bài hướng
dẫn *tự xây X từ đầu*, khác trục với *điều tra một sự cố* hay *chỉ ra một hiểu nhầm*.
Nó chỉ dùng để soát phủ mảng: 30 nhóm của nó map được sang `domain:`.

| Nguồn | Vì sao dùng được |
|---|---|
| **Tự viết `repro/` rồi đo** | Không phụ thuộc ai, số liệu chắc nhất, và tôi làm được ngay |
| Mục "gotchas" trong tài liệu chính thức | dẫn được, kiểm chứng được |
| Changelog và breaking change của framework | có phiên bản cụ thể |
| Sự cố người dùng từng gặp | cấp được mức "cần cấp" mà repro không dựng lại nổi |

---

## Cách dùng bảng này

1. Chọn ứng viên qua được Cửa 2 (mô phỏng được).
2. Nếu cột repro là ✅ hoặc "dễ" thì viết script trong `repro/` trước, chạy lấy số.
3. Nếu số liệu là **cần cấp** mà chưa có nguồn thì để đó, đừng viết.
4. Viết screenplay theo hình dạng hook của tuyến tương ứng.
5. `python src/lint.py screenplays/<file>.yaml` trước khi render.
6. Chuyển ý tưởng lên bảng **Đã viết**, kèm số liệu đã đo.
