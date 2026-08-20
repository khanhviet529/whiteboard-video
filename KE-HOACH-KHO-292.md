# Thiết kế lại toàn bộ kịch bản từ kho 292 chủ đề

[KE-HOACH-90.md](KE-HOACH-90.md) là lịch **đã chốt** cho số 01–90, dựng từ ý
tưởng tự sinh. File này là bản thiết kế lại, dựng từ kho chủ đề trong
[files/](files/) — 292 đề tài trong ba tệp `kho-chu-de-content-it*.md`, cộng
`SKILL.md` và hai tệp tham chiếu về định dạng và giọng văn.

Đọc [Y-TUONG.md](Y-TUONG.md) để biết hai cửa lọc, [CONG-THUC.md](CONG-THUC.md)
để biết khung nhịp, [VIET-KICH-BAN.md](VIET-KICH-BAN.md) để biết bẫy khi viết.

---

## Kho 292 chủ đề khác kho cũ ở đâu

Đây là lý do phải thiết kế lại chứ không chỉ thêm dòng vào kế hoạch cũ.

| | KE-HOACH-90 | Kho 292 trong `files/` |
|---|---|---|
| Cách nghĩ ra đề tài | tự nghĩ theo mảng công nghệ | mỗi đề là **một bài toán có đánh đổi**, không có lời giải hoàn hảo |
| Trục phân nhóm | theo công nghệ (python, postgres, git…) | theo **nguyên nhân bug xuất hiện** ở nhóm S và T |
| Cột riêng | *mô phỏng* | *naive → gãy → chuỗi đánh đổi → demo* |
| Phủ | nặng backend và database | có cả xác thực, upload, SEO, hiệu năng cảm nhận, Keycloak, Git |

Ba thứ trong kho mới **dùng được ngay** cho định dạng HIỆN TRƯỜNG VỤ ÁN:

1. **Cột "naive → gãy" chính là nhịp 1 và 2.** Nó viết sẵn triệu chứng cụ thể
   và cách hỏng, tức đúng thứ hai nhịp mở đầu cần.
2. **Cột "đánh đổi" chính là nhịp 3.** Cách giải thích mà 90% người xem đang
   nghĩ trong đầu thường là vế đầu của chuỗi đánh đổi.
3. **Cột "Demo" chính là cửa 1.** Nó nói luôn phải dựng gì để có số thật.

Còn một thứ trong kho **không** dùng được trực tiếp: nhóm N ("tại sao công nghệ
này ra đời") và nhóm R (SEO) phần lớn trượt Cửa 2 — xem mục "Đề tài bị loại".

---

## Cách xếp: gán CÂU HỎI cho từng đề tài trước khi chọn loại cảnh

Đây là bước quyết định, và nó là hệ quả trực tiếp của cái bẫy đã ghi ở
[VIET-KICH-BAN.md](VIET-KICH-BAN.md) mục *"Bẫy lớn nhất: ba video nhìn giống hệt
nhau"*. Với 292 đề tài thì bẫy đó không còn là nguy cơ thẩm mỹ nữa — nó là
đường tới hạn của cả kênh.

Nên quy trình xếp là: **đọc đề tài, viết ra câu hỏi mà cảnh mô phỏng phải trả
lời, rồi mới tra bảng chọn loại cảnh.** Không đi ngược lại.

Rà cả 292 đề tài theo cách đó thì lộ ra bốn câu hỏi mà **không loại cảnh nào có
sẵn** trả lời được. Bốn loại cảnh dưới đây sinh ra từ phép đếm đó, không phải từ
cảm giác "hình này đẹp":

| Câu hỏi | Số đề tài hỏi câu này | Loại cảnh mới | Vì sao loại cũ không làm được |
|---|---|---|---|
| **BAO NHIÊU Ở MỖI MỨC** — một đại lượng theo một biến *không phải thời gian* | ~40 | `cot` | `queue` có trục x là thời gian và bắt buộc đi lên |
| **CÁI NÀO CHỜ CÁI NÀO** — một chuỗi việc nối đuôi, bậc thang | ~25 | `thac` | `gantt` chỉ vẽ **hai** lane và đặt nhãn *bên trong* thanh |
| **MỖI BẢN SAO GIỮ GÌ** — N instance, mỗi cái một giá trị | ~12 | `ban_sao` | `counters` là số **tĩnh**; `gantt` hai lane là hai *việc*, không phải hai *bản sao* |
| **NHIỀU CÁI RA MỘT** — hai đầu vào khác nhau, một kết quả | ~6 | `gop` | ngược chiều `multiply`, không có gì vẽ được |

Cả bốn đã dựng xong, có kiểm tra riêng trong `lint.py`, và đã chạy trong kịch
bản thật (mùa 7). Xem README mục *"Tám cảnh mô phỏng"*.

### Bảng chọn loại cảnh, bản đầy đủ

| Câu hỏi của cảnh | Loại cảnh | Ép sai vào chỗ khác thì mất gì |
|---|---|---|
| KHI NÀO — hai việc chồng lấn thời gian | `gantt` | — |
| CÁI NÀO CHỜ CÁI NÀO — bậc thang tuần tự | `thac` | ép vào `gantt` thì mất chiều cao bậc thang |
| BAO NHIÊU CÁI — một thành rất nhiều | `multiply` | ép vào `gantt` thì người xem phải **đọc** con số thay vì **nhìn** |
| BAO NHIÊU THEO THỜI GIAN — dồn ứ không rút | `queue` | ép vào `gantt` thì hai thanh ngang không kể được "lên mà không xuống" |
| BAO NHIÊU Ở MỖI MỨC — theo một biến rời rạc | `cot` | ép vào `queue` thì trục thời gian nói sai bản chất |
| Ở ĐÂU — tầng nào có, tầng nào không | `topology` | ép vào `gantt` thì mất phần quan trọng nhất: tầng gói tin **không** tới |
| MỖI BẢN SAO GIỮ GÌ — N instance | `ban_sao` | ép vào `counters` thì mất chuyển động, mất ô sự thật |
| NHIỀU CÁI RA MỘT — trùng nhau | `gop` | không loại nào thay được |

---

## Mười mùa mới, 133 số

Mỗi mùa dùng **một bộ đo dùng chung**, nên script đo thứ hai trong mùa gần như
miễn phí — đúng lý lẽ đã dùng cho sáu mùa đầu. Mỗi mùa có nhận diện hình riêng
(`brand` + `he`) để người xem không đọc số 120 như số 5.

| Mùa | Tên | Số | Nhóm trong kho | Bộ đo | Nhận diện |
|---|---|---|---|---|---|
| 7 | **BĂM VÀ BÍ MẬT** | 91–99 | P (10 bài) | `repro/bam_va_bi_mat.py` | `giang_duong` · BĂM VÀ BÍ MẬT |
| 8 | **CHẠY Ổ LOCAL, CHẾT Ở PRODUCTION** | 100–113 | S (14 bài) | python + sqlite, seed lớn | `hien_truong` · DỮ LIỆU NHIỀU |
| 9 | **MỘT NGƯỜI THÌ ĐÚNG** | 114–125 | T (12 bài) | threads/asyncio + sqlite | `hien_truong` · ĐỒNG THỜI |
| 10 | **TIỀN KHÔNG THA AI** | 126–140 | G+ (15 bài) | sqlite + mô phỏng cổng | `hien_truong` · SỔ SÁCH |
| 11 | **CỬA KHOÁ** | 141–154 | A (14 bài) | node + cookie/CORS thật | `giang_duong` · PHIÊN VÀ QUYỀN |
| 12 | **ĐƯỜNG TRUYỀN** | 155–172 | U (18 bài) | node, `ss`, `dig`, curl | `hien_truong` · MẠNG |
| 13 | **GIT THẬT** | 173–186 | W (14 bài) | git trong thư mục tạm | `giang_duong` · GIT |
| 14 | **16 MILI GIÂY** | 187–198 | Q (12 bài) | node + puppeteer | `giang_duong` · MƯỢT |
| 15 | **HỢP ĐỒNG API** | 199–210 | C (12 bài) | node + curl | `hien_truong` · API |
| 16 | **HÀNG ĐỢI VÀ VIỆC NỀN** | 211–223 | H (10) + I (8) | asyncio + redis | `hien_truong` · VIỆC NỀN |

Còn lại trong kho — nhóm B, D, E, F, G, J, K, L, M, N, O, R, V, X — nằm ở mục
"Đề tài chưa xếp số" và "Đề tài bị loại" phía dưới.

### Thứ tự làm đề xuất

Không làm hết một mùa rồi mới sang mùa khác, cùng lý do như sáu mùa đầu. Nhưng
có một ràng buộc **cứng** mới: mùa 8, 9, 10 dùng chung một bộ seed dữ liệu lớn,
nên phải dựng bộ seed đó **trước** cả ba, và ba mùa đó nên chạy gần nhau để
không phải seed lại.

| Việc chặn | Chặn mùa nào | Vì sao |
|---|---|---|
| Bộ seed 2 triệu dòng + môi trường test đồng thời | 8, 9, 10 | không có nó thì cả ba mùa chỉ là lý thuyết đọc lại |
| postgres + redis trong WSL2 | 10, 16 | sqlite không có MVCC, không có eviction policy |
| `npm i puppeteer` | 14 | jsdom không có layout engine nên không đo được CLS hay layout thrashing |
| Nhận diện hình cho từng mùa | tất cả | mười mùa mà cùng một `brand` thì người xem không phân biệt được |

---

## Mùa 7 — BĂM VÀ BÍ MẬT (9 số, ĐÃ XONG)

Nhóm P của kho. Chọn làm mùa đầu vì đây là nhóm **đo được hết bằng Python thuần**
— `hashlib`, `hmac`, `secrets` có sẵn, `bcrypt` và `argon2` đã cài — nên không
chờ hạ tầng nào. Toàn bộ số liệu nằm trong một lượt chạy duy nhất, lưu ở
[repro/ket-qua/mua-07-bam-va-bi-mat.txt](repro/ket-qua/mua-07-bam-va-bi-mat.txt).

| # | Chủ đề | Kho | Mô phỏng | Số liệu | Kịch bản |
|---|---|---|---|---|---|
| 91 | Băm không phải ẩn danh | 177 | `multiply` + `cot` | đo · 2,3 giây dò ra số điện thoại | [91](screenplays/91-bam-khong-phai-an-danh.yaml) |
| 92 | "MD5 vỡ" nghĩa là gì | 178 | `gop` | đo · 6 bit trên 1024, cùng mã băm | [92](screenplays/92-md5-vo-nghia-la-gi.yaml) |
| 93 | Băm nhanh là nhược điểm | 179 | `cot` log + `counters` | đo · 804.070 so 3,9 lần mỗi giây | [93](screenplays/93-ham-bam-nhanh-la-nhuoc-diem.yaml) |
| 94 | Muối giải quyết việc gì | 180 | `gop` | đo · 2.195 bản ghi trùng, nhóm lớn nhất 473 | [94](screenplays/94-muoi-giai-quyet-viec-gi.yaml) |
| 95 | Giới hạn 72 byte của bcrypt | 181 | `cot` + `nguong` | đo · hai mật khẩu khác nhau cùng vào được | [95](screenplays/95-bcrypt-72-byte.yaml) |
| 96 | Ba tham số của Argon2 | 182 | `cot` | đo · 22,9 đến 409,4 ms theo tham số | [96](screenplays/96-argon2-ba-tham-so.yaml) |
| 97 | Chữ ký không có khoá | 184 | `gantt` | đo · payload sửa rồi tự ký, server nhận | [97](screenplays/97-chu-ky-khong-co-khoa.yaml) |
| 98 | So sánh chuỗi bí mật | 185 | `thac` | đo · vòng lặp rò 11,67 lần, `==` thì không | [98](screenplays/98-so-sanh-chuoi-bi-mat.yaml) |
| 99 | Token sinh bằng ngẫu nhiên thường | 186 | `cot` log | đo · 5.469 trên 200.000 token ngắn hơn 9 ký tự | [99](screenplays/99-token-sinh-bang-ngau-nhien-thuong.yaml) |

Bài 183 của kho ("chọn bcrypt, argon2 hay scrypt") **gộp vào số 93** — nó là
đúng cùng một câu hỏi, và làm riêng thì hai video cùng một bảng số.

### Ba điều mùa 7 để lại cho các mùa sau

**1. `cot` xuất hiện ở 5 trên 9 số, và đó là mức cao nhất chấp nhận được.**
Nguyên nhân là bản chất mùa này: nó nói về *tốc độ và kích cỡ*, tức đúng câu hỏi
BAO NHIÊU Ở MỖI MỨC. Ép sang loại khác cho đỡ lặp là vi phạm chính quy tắc chọn
theo câu hỏi. Nhưng năm số dùng chung một hình dạng là ngưỡng — **mùa 8 trở đi
phải nghiêng về `thac`, `ban_sao`, `topology`**, và mỗi mùa nên tự đếm phân bố
loại cảnh trước khi viết số thứ tư.

**2. Lời đọc phải là tiếng Việt gần như thuần.** `lint.check_tu_la` chỉ soi
`narration`, và nó bắt mọi từ Latin chưa khai trong `phienam.TU_DIEN`. Rà thử 90
thuật ngữ IT thì chỉ 26 từ đi qua được. Nên cách viết đã chốt:

- **Viết tắt** (`MD5`, `SHA-256`, `HMAC`, `API`, `TTL`) → khai vào `TU_DIEN`,
  suy phiên âm theo bảng `CHU_CAI`. Đây là chính sách có sẵn của `phienam.py`:
  *"viết tắt thì model đọc sai gần như chắc chắn nên phiên âm mạnh tay"*.
- **Tên riêng** (`bcrypt`, `argon2`, `token`, `cron`, `webhook`) → **không đưa
  vào lời đọc**. Gọi bằng tiếng Việt (*hàm băm mật khẩu*, *chuỗi mã*, *cú gọi
  ngược*) và để chữ gốc trên màn hình ở `caption`, `head`, `value`. Không tự
  quyết phiên âm cho chúng khi chưa nghe thử — đúng luật của `TU_DIEN`.
- Tiếng Việt có sẵn từ cho gần hết: *khoá chết*, *sổ cái*, *số dư*, *luồng*,
  *tiến trình*, *bộ nhớ*, *phiên*, *muối*, *mã băm*, *bản sao*.

**3. Mỗi mùa một lượt đo, lưu ra `repro/ket-qua/`.** Tốc độ băm dao động
804.070–966.181 lần mỗi giây giữa các lượt trong cùng một buổi. Lấy tốc độ của
lượt này ghép với bảng thời gian của lượt kia thì **hai con số trên màn hình
không chia ra nhau được** — mà người xem làm phép chia đó thật. Nên: một lượt
chạy, lưu ra tệp, mọi số trong mùa trích từ đúng tệp đó.

---

## Mùa 8 — CHẠY Ổ LOCAL, CHẾT Ở PRODUCTION (14 số)

Nhóm S. Đặc điểm chung: **test ở local với 10 dòng luôn pass**. Kho gợi ý đóng
thành series có tên, và tên đó dùng luôn làm tên mùa.

Cần trước: một bộ seed dùng chung (`repro/seed_lon.py`) sinh sqlite 2 triệu
dòng, có cột TEXT lớn, có bảng log không xoá. Mọi số trong mùa đo trên cùng bộ
đó nên so sánh được với nhau.

| # | Chủ đề | Kho | Câu hỏi của cảnh | Mô phỏng | Số liệu |
|---|---|---|---|---|---|
| 100 | Load toàn bộ bảng vào memory | 209 | BAO NHIÊU Ở MỖI MỨC | `cot` (RSS theo số dòng) | đo · `psutil` |
| 101 | Query không index, 5ms lên 40 giây | 210 | BAO NHIÊU Ở MỖI MỨC | `cot` log | đo |
| 102 | `SELECT *` khi bảng có cột lớn | 211 | — | `compare` + `probe` | đo · byte truyền |
| 103 | Migration khoá bảng 8 phút | 212 | KHI NÀO | `gantt` (lane migration chặn lane đọc) | đo · postgres |
| 104 | Vòng lặp gọi API bên ngoài | 213 | CÁI NÀO CHỜ CÁI NÀO | `thac` ⭐ | đo |
| 105 | JSON response 50MB | 214 | BAO NHIÊU Ở MỖI MỨC | `cot` (bộ nhớ hai đầu) | đo |
| 106 | Bảng log không có kế hoạch xoá | 215 | BAO NHIÊU THEO THỜI GIAN | `queue` (dung lượng) | đo |
| 107 | Đếm và tổng hợp theo thời gian thực | 216 | BAO NHIÊU Ở MỖI MỨC | `cot` | đo |
| 108 | Sắp xếp vượt `work_mem` | 217 | BAO NHIÊU Ở MỖI MỨC | `cot` (đổ ra đĩa) | đo · postgres |
| 109 | Import file người dùng tải lên | 218 | CÁI NÀO CHỜ CÁI NÀO | `thac` | đo |
| 110 | `LIKE '%keyword%'` | 219 | BAO NHIÊU Ở MỖI MỨC | `cot` log | đo |
| 111 | Sinh PDF/Excel hàng loạt | 220 | BAO NHIÊU THEO THỜI GIAN | `queue` | đo |
| 112 | Cây phân cấp sâu, truy vấn đệ quy | 221 | CÁI NÀO CHỜ CÁI NÀO | `thac` (mỗi mức một hàng) | đo |
| 113 | Cache key bùng nổ khi tham số nhiều | 222 | BAO NHIÊU CÁI | `multiply` ⭐ | đo |

---

## Mùa 9 — MỘT NGƯỜI THÌ ĐÚNG (12 số)

Nhóm T. Đây là mùa mà `ban_sao` sinh ra để phục vụ: bảy trên mười hai số nói về
"chạy đúng với một bản, sai ngay khi có hai".

Cần trước: `repro/dong_thoi.py` — bắn N request song song và đo kết quả. Kho ghi
rõ đây là điều kiện tiên quyết, và nó đúng.

| # | Chủ đề | Kho | Câu hỏi của cảnh | Mô phỏng | Số liệu |
|---|---|---|---|---|---|
| 114 | Biến toàn cục hoặc state trong module | 223 | MỖI BẢN SAO GIỮ GÌ | `ban_sao` ⭐ | đo |
| 115 | Kết nối DB cạn khi tải tăng | 224 | Ở ĐÂU + BAO NHIÊU THEO THỜI GIAN | `topology` + `queue` | đo (đã có mẫu ở số 03) |
| 116 | Hai tài khoản cùng email | 225 | KHI NÀO | `gantt` hai lane | đo |
| 117 | Cron chạy chồng nhau | 226 | KHI NÀO | `gantt` (lần trước chưa xong) | đo |
| 118 | Rate limit đếm sai khi nhiều instance | 227 | MỖI BẢN SAO GIỮ GÌ | `ban_sao` ⭐ | đo |
| 119 | Session hoặc cache trong memory | 228 | MỖI BẢN SAO GIỮ GÌ | `ban_sao` ⭐ | đo |
| 120 | Deadlock chỉ xuất hiện dưới tải | 229 | KHI NÀO | `gantt` hai lane chéo nhau | đo · postgres |
| 121 | Số thứ tự tự tăng do app tự sinh | 230 | MỖI BẢN SAO GIỮ GÌ | `ban_sao` + `gop` | đo |
| 122 | Timeout theo tầng không khớp nhau | 231 | CÁI NÀO CHỜ CÁI NÀO | `thac` ⭐ | đo |
| 123 | Webhook nhận nhiều event cùng đơn | 232 | KHI NÀO | `gantt` | đo |
| 124 | Blue-green: hai phiên bản cùng chạy | 233 | MỖI BẢN SAO GIỮ GÌ | `ban_sao` | suy |
| 125 | Dựng môi trường test tải | 234 | BAO NHIÊU Ở MỖI MỨC | `cot` | đo |

---

## Mùa 10 — TIỀN KHÔNG THA AI (15 số)

Nhóm G+. Kho khuyên nhắm nhóm này lâu dài: toàn 🔴 hoặc 🟡, và là nhóm trống
nhất trong tiếng Việt. Đồng ý, và thêm một lý do nữa: **mọi số ở đây đều có một
con số người xem đếm được** (số dư, số đơn, số bút toán), tức luôn có cái để đặt
vào ô số đang chạy.

| # | Chủ đề | Kho | Câu hỏi của cảnh | Mô phỏng |
|---|---|---|---|---|
| 126 | Lost update — ba cách mất dữ liệu | 134 | KHI NÀO | `gantt` hai lane |
| 127 | Write skew — cả hai đều "đúng" | 135 | KHI NÀO | `gantt` hai lane |
| 128 | Giữ hàng khác trừ hàng | 136 | BAO NHIÊU THEO THỜI GIAN | `queue` (hàng bị giam) |
| 129 | Transaction của bạn dừng ở đâu | 137 | Ở ĐÂU | `topology` |
| 130 | Đối soát — hai hệ thống sẽ lệch | 138 | MỖI BẢN SAO GIỮ GÌ | `ban_sao` ⭐ (DB so cổng) |
| 131 | Hoàn tiền một phần | 139 | Ở ĐÂU | `topology` (trạng thái) |
| 132 | Ledger — vì sao không UPDATE số dư | 140 | BAO NHIÊU Ở MỖI MỨC | `cot` (chi phí tính số dư) |
| 133 | Double-entry | 141 | NHIỀU CÁI RA MỘT | `gop` (hai vế về không) |
| 134 | Idempotency ở tầng nghiệp vụ | 142 | KHI NÀO | `gantt` |
| 135 | Audit trail không phá hiệu năng | 143 | BAO NHIÊU Ở MỖI MỨC | `cot` |
| 136 | Job nửa đêm bắc qua hai ngày | 144 | KHI NÀO | `gantt` + `counters` ba múi giờ |
| 137 | ID phân tán | 145 | NHIỀU CÁI RA MỘT | `gop` (hai nơi cùng một ID) |
| 138 | Retry với thanh toán | 146 | CÁI NÀO CHỜ CÁI NÀO | `thac` |
| 139 | Số dư âm khi hai lần trừ song song | 147 | KHI NÀO | `gantt` + ô số dư |
| 140 | Test tính đồng thời | 148 | BAO NHIÊU Ở MỖI MỨC | `cot` (số lần lặp so số bug bắt được) |

---

## Mùa 11 đến 16 — khung đã xếp, chưa chi tiết hoá

Mỗi mùa dưới đây đã qua Cửa 2 (mọi số đều gán được một loại cảnh), nhưng chưa
tách thành bảng từng số. Làm tới mùa nào thì chi tiết hoá mùa đó — chi tiết hoá
sớm mười mùa thì phần lớn sẽ phải sửa lại sau khi đo.

| Mùa | Số | Nhóm | Ba số mạnh nhất của mùa (theo mức đo được + độ trái trực giác) |
|---|---|---|---|
| 11 CỬA KHOÁ | 141–154 | A | 2 (refresh token race → `gantt`), 3 (JWT không revoke được → `counters` qua các mốc), 12 (chống brute force không tiết lộ tài khoản → `thac`) |
| 12 ĐƯỜNG TRUYỀN | 155–172 | U | 240 (handshake, kết nối mới đắt → `thac`), 238 (DNS TTL → `counters`), 249 (MTU và "lỗi ngẫu nhiên" → `cot` theo kích thước gói) |
| 13 GIT THẬT | 173–186 | W | 268 (`.gitignore` với secret đã commit → `probe` ×2), 276 (`bisect` 10 bước thay vì 1000 → `cot` log), 274 (file lớn và LFS → `cot` dung lượng repo) |
| 14 16 MILI GIÂY | 187–198 | Q | 187 (16ms mỗi frame → `cot`), 189 (layout thrashing → `thac`), 191 (CLS từng nguyên nhân → `cot`) |
| 15 HỢP ĐỒNG API | 199–210 | C | 26 (offset so cursor → `gantt` lane đọc + lane insert), 33 (idempotency key → `gantt`), 32 (bulk 100 item lỗi 1 → `ban_sao`) |
| 16 HÀNG ĐỢI VÀ VIỆC NỀN | 211–223 | H + I | 95 (cache stampede → `queue` + `gantt`), 89 (dồn 100 nghìn job → `queue`), 86 (at-least-once → `gop`) |

---

## Đề tài chưa xếp số

Qua được cả hai cửa nhưng chưa vào mùa nào, vì mùa của chúng chưa mở hoặc vì
trùng cơ chế với một số đã xếp. Giữ lại làm nguồn thay thế cho những ngày bộ đo
không chạy được.

| Nhóm | Số bài | Ghi chú khi xếp |
|---|---|---|
| B — upload và media | 10 | Bài 17 (magic byte), 24 (export vài trăm nghìn dòng) mạnh nhất; phần còn lại nặng về lựa chọn kiến trúc, khó mô phỏng |
| D — FE dữ liệu và trạng thái | 10 | Bài 41 (race ở ô tìm kiếm → `gantt`) và 39 (invalidate cache FE) qua cửa; số còn lại là bài so sánh thư viện |
| E — FE render và hiệu năng | 10 | Trùng nhiều với mùa 5 (số 66–80) đã xếp ở kế hoạch cũ. Chỉ lấy bài 53 (danh sách 10 nghìn dòng) và 49 (hydration mismatch) |
| F — database schema | 16 | Trùng dày với mùa 1 và 4. Lấy thêm bài 71 (tìm kiếm tiếng Việt có dấu, không dấu, telex) — đề tài này **không kênh nào làm** và đo được |
| G — transaction | 10 | Đã bị mùa 10 (nhóm G+) bao gần hết |
| J — realtime | 6 | Bài 103 (scale WebSocket nhiều instance → `ban_sao`) và 106 (trạng thái online luôn sai một chút) qua cửa |
| K — hạ tầng | 12 | Bài 107 (image 1,2GB xuống 80MB → `cot`), 108 (layer cache → `thac`), 113 (413 và 504 → `topology`) |
| L — quan sát và gỡ lỗi | 7 | Bài 121 (**vì sao trung bình luôn nói dối** → `cot` phân vị) là số mạnh nhất của cả nhóm này |
| M — bảo mật ngoài xác thực | 8 | Bài 126 (CORS thật ra làm gì), 129 (IDOR), 133 (mass assignment) đều mô phỏng được bằng `topology` hoặc `probe` |
| V — Keycloak và SSO | 10 | Cần dựng Keycloak thật. Bài 257 (đăng xuất trong SSO khó hơn đăng nhập → `topology`) là số đáng làm nhất |
| X — mảng còn thiếu | 16 | Bài 282 (số điện thoại và địa chỉ Việt Nam), 283 (VNPay, Momo, ZaloPay) là hai đề tài **riêng của thị trường Việt**, không có bản tiếng Anh để đối chiếu — nên làm |

---

## Đề tài bị loại, và vì sao

Ghi lại để người sau không xếp lại rồi mới phát hiện. Cả ba nhóm dưới đây trượt
**Cửa 2**: không có con số nào đang đổi, nên làm ở tool này cũng không hơn một
video người nói.

| Nhóm | Số bài | Vì sao trượt |
|---|---|---|
| N — "tại sao công nghệ này ra đời" | 15 | Định dạng của nhóm này là *bối cảnh → vấn đề → cách giải → cái nó KHÔNG giải*. Đó là một bài đọc, không có đại lượng nào đo được theo thời gian. Vài bài cứu được bằng cách đổi trục sang một phép đo (149 Docker → `cot` thời gian dựng môi trường; 158 Redis → `cot` độ trễ), còn lại loại |
| O — quy trình và vận hành | 13 | *Mục tiêu → các bước → chỗ hay sai → mức tối thiểu*. Mô phỏng được cái gì? Không. Ba bài cứu được: 169 (deploy không downtime → `gantt`), 170 (rollback → `gantt`), 174 (15 phút đầu xử lý sự cố → `thac`) |
| R — SEO kỹ thuật | 10 | Không có phép đo nào chạy được trên máy mình, và mọi con số phụ thuộc vào hành vi của một hệ thống bên ngoài mà không ai kiểm chứng lại được. Đây là nhóm dễ vi phạm Cửa 1 nhất trong cả kho |

Ngoài ra loại theo từng bài: mọi đề tài mà cột "Demo" của kho ghi kiểu *"viết ra
10 kịch bản rồi thử biểu diễn"* hoặc *"đọc tài liệu X"* đều trượt Cửa 1 mức
đo-được, và trượt Cửa 2 luôn.

---

## Ba việc phải làm trước khi viết mùa 8

1. **`repro/seed_lon.py`** — sinh sqlite 2 triệu dòng dùng chung cho mùa 8, 9,
   10. Có cột `content TEXT` vài trăm KB, có bảng log không xoá, có bảng đơn
   hàng nhiều cấp. Seed một lần, mọi số đo trên cùng bộ đó.
2. **`repro/dong_thoi.py`** — khung bắn N việc song song rồi đếm kết quả, dùng
   chung cho mùa 9 và 10. Không có nó thì hai mùa đó chỉ là lý thuyết.
3. **Đếm phân bố loại cảnh của mùa trước khi viết số thứ tư.** Mùa 7 đi tới 5
   trên 9 số dùng `cot` mà chỉ nhận ra khi đã viết xong. Đếm sớm thì còn kịp
   chọn lại — và chọn lại phải bằng cách **đổi câu hỏi của cảnh**, không phải
   bằng cách đổi hình cho khác đi.
