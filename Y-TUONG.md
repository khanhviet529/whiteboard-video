# Kho ý tưởng nội dung

> Lịch 90 số đã chốt nằm ở [KE-HOACH-90.md](KE-HOACH-90.md). File này giữ
> phần **lý lẽ**: bốn tuyến nội dung, hai cửa lọc, và vì sao một ý tưởng bị
> loại. Chọn chủ đề mới thì đọc file này trước, rồi thêm dòng vào kế hoạch.

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

> **Có một loại thứ tư, và nhận ra nó tiết kiệm rất nhiều công.** `[10,9,1].sort()`
> trả về `[1,10,9]` vì **đặc tả** JavaScript quy định vậy — đúng trên mọi máy, mọi
> phiên bản, không dao động, không phụ thuộc tải. Dựng bộ đo có hiệu chuẩn và lấy
> trung vị cho một sự thật như thế là thừa. Vẫn nên **chạy một lần** cho chắc, vì
> trong một buổi đã ba lần nhớ sai code làm gì, và vì dòng `nguon:` trong video chỉ
> có nghĩa khi file đó chạy được. Xem `bench-js/su-that.mjs` — 40 dòng, không đo gì.

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

| Cảnh | Trả lời câu | Mô phỏng được cái gì |
|---|---|---|
| `gantt` | KHI NÀO | hai luồng chồng lấn theo thời gian, ô số đổi giá trị, bộ đếm hậu quả |
| `multiply` | BAO NHIÊU CÁI | một câu thành N câu, một render thành N render — lưới ô đầy dần |
| `queue` | BAO NHIÊU THEO THỜI GIAN | hàng đợi dâng lên và không rút, biểu đồ cắt màu tại ngưỡng |
| `topology` | Ở ĐÂU | tầng nào có, **tầng nào không** — gói tin dừng giữa đường |
| `cot` | BAO NHIÊU Ở MỖI MỨC | một đại lượng theo một biến **không phải thời gian** — cỡ dữ liệu, tham số cấu hình, hàm nào |
| `thac` | CÁI NÀO CHỜ CÁI NÀO | chuỗi việc nối đuôi thành bậc thang, đồng hồ tổng đếm lên |
| `ban_sao` | MỖI BẢN SAO GIỮ GÌ | N instance mỗi cái một giá trị, cộng một ô **sự thật** để đối chiếu |
| `gop` | NHIỀU CÁI RA MỘT | hai đầu vào khác nhau cho ra cùng một kết quả |
| `counters` | — | một giá trị **không đổi** qua nhiều mốc thời gian |
| `compare` | — | hai vế đặt cạnh nhau, con số này bên con số kia |
| `probe` | — | ba dòng shell, dòng cuối vô lý |

Chọn theo **câu hỏi**, đừng chọn theo thói quen. Ba screenplay đầu tiên đều dùng
`gantt` vì lúc đó nó là loại mô phỏng duy nhất, và kết quả là ba video nhìn giống
hệt nhau. Xem [VIET-KICH-BAN.md](VIET-KICH-BAN.md) mục "Bẫy lớn nhất".

Ý tưởng không lên được cảnh nào trong đây thì làm ở tool này cũng không hơn một video
người nói. Ví dụ "10 lệnh git nên biết" trượt cửa này.

Trường `domain:` (`fe` `be` `database` `infra`) không phải cửa lọc, chỉ để soát phủ
đều. Ba screenplay hiện có đều `be`/`database`.

---

## Đã viết

| Screenplay | Tuyến | Mảng | Triệu chứng | Mô phỏng |
|---|---|---|---|---|
| [cache-stale.yaml](screenplays/cache-stale.yaml) | 1 | database | Xoá cache xong, API vẫn trả giá cũ | `gantt` ×2 (sai / đúng thứ tự) |
| [n-plus-one.yaml](screenplays/n-plus-one.yaml) | 1 | database | 20 đơn hàng, API mất 3,73 giây | `multiply` (149 ô, ô đầu xanh) |
| [double-charge.yaml](screenplays/double-charge.yaml) | 1 | be | Khách bấm một lần, trừ tiền hai lần | `topology` + `race` (theme `phongtoi`) |
| [async-song-song.yaml](screenplays/async-song-song.yaml) | 2 | be | Thêm async, nhanh hơn được 0,04 giây | `gantt` ×2 (một luồng / hai tiến trình) |
| [pool-can.yaml](screenplays/pool-can.yaml) | 1 | be | 1/3 request lỗi, database dùng 1,1% sức | `topology` (chết ở POOL) + `queue` (70 chờ, 10 chỗ) |

### Mùa 7 — BĂM VÀ BÍ MẬT (9 số, từ kho 292 chủ đề trong `files/`)

Xem [KE-HOACH-KHO-292.md](KE-HOACH-KHO-292.md). Cả mùa đo bằng một lượt chạy duy
nhất của [repro/bam_va_bi_mat.py](repro/bam_va_bi_mat.py), kết quả lưu ở
[repro/ket-qua/mua-07-bam-va-bi-mat.txt](repro/ket-qua/mua-07-bam-va-bi-mat.txt).

| Screenplay | Tuyến | Triệu chứng | Mô phỏng |
|---|---|---|---|
| [91](screenplays/91-bam-khong-phai-an-danh.yaml) | 2 | Cột số điện thoại đã băm, dò ra số gốc trong 2,3 giây | `multiply` (1.234.568 ô) + `cot` log |
| [92](screenplays/92-md5-vo-nghia-la-gi.yaml) | 4 | Hai tệp lệch 6 bit trên 1024, cùng một mã băm MD5 | `gop` ⭐ |
| [93](screenplays/93-ham-bam-nhanh-la-nhuoc-diem.yaml) | 2 | 804.070 lần mỗi giây so với 3,9 lần mỗi giây | `cot` log + `counters` |
| [94](screenplays/94-muoi-giai-quyet-viec-gi.yaml) | 2 | 2.195 bản ghi trùng hash, nhóm lớn nhất 473 người | `gop` (ba người, một dòng) |
| [95](screenplays/95-bcrypt-72-byte.yaml) | 3 | Hai mật khẩu khác nhau cùng đăng nhập được | `cot` + `nguong` (trần 72) |
| [96](screenplays/96-argon2-ba-tham-so.yaml) | 4 | Hạ bộ nhớ còn 0,20 lần chi phí mà không ai báo | `cot` (5 cột, đổi một tham số một lần) |
| [97](screenplays/97-chu-ky-khong-co-khoa.yaml) | 1 | Đơn 100 nghìn, chữ ký khớp, ghi vào 1 đồng | `gantt` (kẻ chen giữa đường) |
| [98](screenplays/98-so-sanh-chuoi-bi-mat.yaml) | 4 | Vòng lặp tự viết rò 11,67 lần; `==` thì không đo thấy | `thac` ⭐ |
| [99](screenplays/99-token-sinh-bang-ngau-nhien-thuong.yaml) | 1 | 5.469 trên 200.000 token ngắn hơn 9 ký tự | `cot` log |

Bốn loại cảnh mô phỏng mới (`cot` `thac` `ban_sao` `gop`) sinh ra từ mùa này —
xem Cửa 2 phía trên, bảng đã cập nhật đủ tám loại.

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
| ~~Connection pool cạn~~ | đã viết → [pool-can.yaml](screenplays/pool-can.yaml) | **đo được** | ✅ [đã có](repro/pool_ket_noi_can.py) | `topology` + `queue` |
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
