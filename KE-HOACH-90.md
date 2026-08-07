# 90 video, 6 mùa

Bảng chọn chủ đề cho 90 số, mỗi ngày một số. Xem [Y-TUONG.md](Y-TUONG.md) để biết
bốn tuyến nội dung và hai cửa lọc, [VIET-KICH-BAN.md](VIET-KICH-BAN.md) để biết bẫy
khi viết, [CONG-THUC.md](CONG-THUC.md) để biết khung nhịp.

Đối tượng: **dev 1–4 năm kinh nghiệm**. Người đã đi làm, đã gặp bug production
nhưng chưa gọi tên được cơ chế. Chủ đề nào chỉ junior mới chưa biết thì loại;
chủ đề nào phải là tech lead mới gặp thì để dành.

## Vì sao chia mùa

Ở 90 số, ý tưởng không phải thứ khan hiếm. Ba thứ khan hiếm là số liệu bảo vệ
được, sức chịu đựng của người xem với một format, và thông lượng làm việc.

Chia mùa giải cả ba cùng lúc. Mỗi mùa dùng chung một bộ đo, nên script đo thứ hai
trong mùa gần như miễn phí. Mỗi mùa có một dạng hook riêng, nên người xem không
thấy số 40 giống hệt số 5. Và mỗi mùa có nhận diện hình riêng, nên kênh trông như
có mùa thật chứ không phải một khuôn lặp 90 lần.

| Mùa | Số | Tuyến | Hook mở bằng | Bộ đo |
|---|---|---|---|---|
| 1. Hiện trường vụ án | 20 | sự cố production | triệu chứng nghe vô lý | sqlite, asyncio, postgres |
| 2. Tôi tưởng tôi biết | 15 | hiểu nhầm phổ biến | "đúng chín phần mười trường hợp" | dùng lại mùa 1 |
| 3. Hai đoạn code | 15 | hai cách làm | hai đoạn gần y hệt, đếm ba giây | benchmark vi mô |
| 4. Cơ chế bên dưới | 15 | cơ chế | "bạn gọi hàm này mỗi ngày" | dựng lại cấu trúc |
| 5. Frontend | 15 | trộn | tuỳ số | node, react |
| 6. Công cụ và vận hành | 10 | trộn | tuỳ số | git thật, shell, docker |

## Phải làm trước khi viết

| Việc | Vì sao chặn | Chặn mùa nào |
|---|---|---|
| Cài postgres + redis trong WSL2 → [CAI-DAT-WSL.md](CAI-DAT-WSL.md) | sqlite không có MVCC, không có gap lock, không có autovacuum, không có eviction policy. 15 chủ đề mạnh nhất nằm ở đó | 1, 2, 4 |
| Cài docker trong WSL2 | OOMKilled, cgroup throttling, SIGTERM đều không dựng lại được bằng process thường | 6 |
| `npm install react react-test-renderer` | đếm số lần render là cách duy nhất đo được bug re-render | 5 |
| Loại cảnh `code` cho theme `bench` | mùa 3 không có cảnh nào để chiếu hai đoạn code | 3 |
| Nhận diện hình thứ hai | mùa 2 và 5 dùng chung `bench` thì người xem không phân biệt được mùa | 2, 5 |
| Vòng sinh YAML tự động + `lint.py` soi | ở 3 video thì viết tay hợp lý, ở 90 thì đây là đường tới hạn | tất cả |

Đã có sẵn trên máy: Python 3.14, sqlite3, `node v24`, `npm 11`, WSL2 Ubuntu (đang
chạy omnivoice), git.

## Cách đọc bảng

Cột **số liệu** dùng ký hiệu ở [Y-TUONG.md](Y-TUONG.md) Cửa 1: `đo` (viết script
trong `repro/`), `suy` (hệ quả tất yếu của cơ chế), `cấp` (phải có sự cố thật).
Bảng này **không ghi con số kết quả** — con số chỉ được ghi vào kịch bản sau khi
script chạy ra. Ghi trước là bịa.

Cột **mô phỏng** là loại cảnh dự kiến. Nó có thể đổi khi viết, nhưng ý tưởng nào
để trống cột này thì trượt Cửa 2 và bị loại.

---

## Mùa 1 — HIỆN TRƯỜNG VỤ ÁN (20 số)

Tuyến 1. Mở bằng một triệu chứng cụ thể nghe vô lý, đóng bằng một quy tắc. Đây là
mùa mạnh nhất và nên chạy trước để dựng nhận diện kênh.

| # | Chủ đề | Triệu chứng mở đầu | Số liệu | Đo bằng | Mô phỏng |
|---|---|---|---|---|---|
| 01 | Cache giữ giá cũ | Xoá cache xong, API vẫn trả giá cũ | ✅ đo | sqlite | `gantt` ×2 |
| 02 | N+1 query | 20 đơn hàng, API mất gần 4 giây | ✅ đo | sqlite | `multiply` |
| 03 | Pool kết nối cạn | 1/3 request lỗi, database dùng 1% sức | ✅ đo | asyncio | `topology` + `queue` |
| 04 | Phân trang bỏ sót | Xuất báo cáo ba lần ra ba số khác nhau | ✅ đo | sqlite | `gantt` |
| 05 | Lost update | Trừ kho 100 lần, kho giảm ít hơn 100 | đo | sqlite | `gantt` hai lane |
| 06 | Index bị bỏ qua | ✅ **ĐÃ VIẾT** [index-bi-bo-qua](screenplays/index-bi-bo-qua.yaml) — 81,23ms so với 903µs, **90×**; EXPLAIN: quét song song so với Index Scan | ✅ đo | postgres | `probe` ×2 + `compare` |
| 07 | Transaction giữ khoá quá lâu | Một request chậm làm cả bảng đứng | đo | postgres | `gantt` lane bị chặn |
| 08 | Deadlock do thứ tự khoá | Job chạy 300 ngày không sao, ngày 301 chết | đo | postgres | `gantt` hai lane chéo nhau |
| 09 | `COUNT(*)` là thứ chậm nhất trang | ĐÃ ĐO: 39,28ms so với `LIMIT 20` 763µs, **51×** trên bảng 500.000 dòng | ✅ đo | postgres | `compare` |
| 10 | Cache stampede | Cứ đúng năm phút một lần API sập vài giây | đo | asyncio | `queue` + `gantt` |
| 11 | Retry bão không jitter | Thêm retry cho ổn định hơn, hệ thống sập hẳn | đo | asyncio | `multiply` + `queue` |
| 12 | Hàng đợi không giới hạn | Container bị giết mà không để lại log nào | đo | asyncio + docker | `queue` |
| 13 | Thiếu timeout | Một dịch vụ ngoài treo, cả hệ thống treo theo | đo | asyncio | `topology` + `queue` |
| 14 | Trừ tiền hai lần | Khách bấm một lần, trừ tiền hai lần | đo | asyncio | `gantt` hai lane |
| 15 | Tiền tính bằng float | ✅ **ĐÃ VIẾT** [15-tien-tinh-bang-float](screenplays/15-tien-tinh-bang-float.yaml). **Triệu chứng ghi ở đây ban đầu SAI**: cộng 50.000 giao dịch thật chỉ lệch 0,00000038 đồng/ngày. Cơ chế thật là PHÉP SO SÁNH — 21,52% đơn báo "chưa trả đủ" dù tiền đủ | ✅ đo | python | `probe` ba dòng |
| 16 | Timestamp không có offset | ✅ **ĐÃ VIẾT** [16-timestamp-khong-co-offset](screenplays/16-timestamp-khong-co-offset.yaml) — mốc `28/02 23:30` rơi vào 28/02 hoặc 01/03 tuỳ nơi đọc | ✅ đo | python `zoneinfo` | `counters` ba múi giờ |
| 17 | UUID v4 làm khoá chính | ĐÃ ĐO: chèn 300.000 dòng mất 5,04s so với 1,19s, **4,3×**. Index 11,6MB so với 6,8MB | ✅ đo | postgres | `queue` |
| 18 | Regex quay lui thảm hoạ | Một dòng log làm treo cả service | đo | python | `queue` theo độ dài chuỗi |
| 19 | Soft delete làm index vô dụng | Bảng có index mà query vẫn quét toàn bảng | đo | postgres | `probe` `EXPLAIN` |
| 20 | Bảng phình vì UPDATE | ĐÃ ĐO: 200.000 dòng, UPDATE toàn bảng 5 lần → 11,8MB thành 55,0MB, **gấp 4,7 lần**, 200.070 bản chết nằm lại | ✅ đo | postgres | `queue` dung lượng |

Đã có video: 01 [cache-stale](screenplays/cache-stale.yaml), 02 [n-plus-one](screenplays/n-plus-one.yaml), 03 [pool-can](screenplays/pool-can.yaml). Số 04 đã có script đo
([phan_trang_bo_sot.py](repro/phan_trang_bo_sot.py)) nhưng chưa có kịch bản.

## Mùa 2 — TÔI TƯỞNG TÔI BIẾT (15 số)

Tuyến 2. Hook mở bằng "bạn tin X, đúng chín phần mười trường hợp, đây là phần còn
lại". Căng thẳng đến từ cảm giác tự mình sai chứ không phải từ sự cố.

Mùa này cần **nhận diện hình riêng**, vì nếu vẫn là HIỆN TRƯỜNG · HỒ SƠ thì người
xem đọc nó như mùa 1 và hook mất tác dụng.

| # | Niềm tin bị lật | Phần còn lại | Số liệu | Đo bằng | Mô phỏng |
|---|---|---|---|---|---|
| 21 | async là chạy song song | ✅ đã viết | ✅ đo | asyncio | `gantt` ×2 |
| 22 | Index luôn làm query nhanh hơn | Cột ít giá trị phân biệt thì quét bảng còn nhanh hơn | đo | postgres | `compare` |
| 23 | Cache luôn làm hệ thống nhanh hơn | Tỷ lệ trúng thấp thì cache là chi phí thuần | đo | asyncio | `queue` |
| 24 | GIL làm Python vô dụng với đa luồng | ✅ **ĐÃ VIẾT** [gil-va-viec-cho](screenplays/gil-va-viec-cho.yaml) — 8 việc chờ: 1204ms so với 158,84ms, **7,6×** | ✅ đo | python | `gantt` |
| 25 | Thêm server thì chịu tải gấp đôi | Nút thắt chỉ dời chỗ, không biến mất | đo | asyncio | `topology` |
| 26 | Nhiều index thì đọc nhanh hơn | Mỗi index là một lần ghi thêm | đo | postgres | `compare` |
| 27 | `try/except` chậm nên phải tránh | Không có lỗi thì nó gần như miễn phí | đo | python | `compare` |
| 28 | `SELECT *` chậm vì lấy nhiều cột | Chậm vì mất covering index, không vì số cột | đo | postgres | `probe` `EXPLAIN` |
| 29 | Transaction là đủ để an toàn | Read committed vẫn cho lost update | đo | postgres | `gantt` |
| 30 | HTTPS làm chậm đáng kể | TLS 1.3 cộng keep-alive gần như không tốn gì | đo | node | `compare` |
| 31 | Thêm `LIMIT 1` thì luôn nhanh | Không có index phù hợp thì vẫn quét hết | đo | postgres | `probe` |
| 32 | Đọc cả file nhanh hơn đọc từng dòng | Bộ đệm đã lo phần đó rồi | đo | python | `compare` |
| 33 | List comprehension luôn nhanh hơn | Không đúng khi thân vòng lặp gọi hàm | đo | python | `compare` |
| 34 | Redis nhanh nên không cần nghĩ | Một lệnh chậm chặn cả server đơn luồng | đo | redis | `gantt` |
| 35 | ORM là thứ làm code chậm | Chậm là do cách dùng, và đo được chỗ nào | đo | sqlite | `multiply` |

Đã có video: 21 [async-song-song](screenplays/async-song-song.yaml).

## Mùa 3 — HAI ĐOẠN CODE (15 số)

Tuyến 3. Format: chiếu hai đoạn gần y hệt, đếm ba giây cho người xem chọn, rồi
chạy thật. Đây là mùa có tỷ lệ bình luận cao nhất, vì người xem đã trót chọn trong
đầu và vào bình luận để bảo vệ lựa chọn đó.

Điều kiện: một trong hai đoạn phải **có bug thật hoặc chậm hơn đo được**. Hai đoạn
chỉ khác nhau ở chỗ đẹp xấu thì bỏ.

Cần loại cảnh `code` cho theme `bench`, hiện chưa có.

| # | Hai đoạn khác nhau ở | Đoạn sai sai ở đâu | Số liệu | Đo bằng |
|---|---|---|---|---|
| 36 | `x in list` với `x in set` | ✅ **ĐÃ VIẾT** [tim-trong-set](screenplays/tim-trong-set.yaml) — 159,75ms so với 1,01ms, 158× | ✅ đo | python |
| 37 | Tham số mặc định là `[]` | ✅ **ĐÃ VIẾT** [gio-dung-chung](screenplays/gio-dung-chung.yaml) — gọi 3 lần ra `[[0],[0,1],[0,1,2]]` so với `[[0],[1],[2]]` | ✅ đo | python |
| 38 | Nối chuỗi trong vòng lặp | ĐÃ ĐO: chỉ **2×** chứ không bình phương — CPython sửa tại chỗ khi refcount bằng 1. Kể theo hướng đó, nối với số 53 | đo | python |
| 39 | `datetime.now()` không có múi giờ | So sánh với mốc có múi giờ thì nổ | đo | python |
| 40 | ~~`float` với `Decimal` cho tiền~~ | **TRÙNG, nên đổi chủ đề.** Số 15 đã kể tiền + Decimal ở mùa 1, số 49 đã kể so sánh float ở mùa 3. Làm thêm số này là ba video cùng một cơ chế. Đề nghị thay bằng một ứng viên khác trong Y-TUONG.md | — | — |
| 41 | `dict[k]` với `dict.get(k)` | ĐÃ ĐO: `try/except` 2,44ms so với `dict.get` 3,02ms — **try/except nhanh hơn** khi khoá luôn có | đo | python |
| 42 | Có `FOR UPDATE` và không | Lost update dưới tải | đo | postgres |
| 43 | Thứ tự cột trong index ghép | `(a,b)` dùng được, `(b,a)` thì không | đo | postgres |
| 44 | `LIMIT` không kèm `ORDER BY` | ✅ **ĐÃ VIẾT** [44-limit-khong-kem-order-by](screenplays/44-limit-khong-kem-order-by.yaml) — `[1,2,3,4,5]` rồi `[20001,…]` sau một UPDATE bình thường | ✅ đo | postgres |
| 45 | `copy()` với `deepcopy()` | ✅ **ĐÃ VIẾT** [45-copy-voi-deepcopy](screenplays/45-copy-voi-deepcopy.yaml) — sửa bản sao làm gốc đổi theo; tốc độ dao 822–1226× nên kịch bản nói "hàng trăm lần" | ✅ đo | python |
| 46 | `await` trong vòng lặp với `gather` | Tuần tự so với cùng lúc | đo | asyncio |
| 47 | `except Exception` với bắt cụ thể | Nuốt luôn cả bug của chính mình | suy | python |
| 48 | `open()` với `with open()` | Exception giữa chừng làm rò file | đo | python |
| 49 | So sánh float bằng `==` | ✅ **ĐÃ VIẾT** [49-so-sanh-float-bang](screenplays/49-so-sanh-float-bang.yaml) — chia 1 thành k phần rồi cộng lại: `==` đúng 50%, `isclose` đúng 100% | ✅ đo | python |
| 50 | ~~`sort(key=)` với tính trước~~ | ĐÃ ĐO: **giả thuyết SAI** — `sorted(key=)` nhanh hơn 2× vì key chỉ gọi một lần mỗi phần tử. Chuyển sang mùa 2 làm một niềm tin bị lật | đo | python |

## Mùa 4 — CƠ CHẾ BÊN DƯỚI (15 số)

Tuyến 4. Đây là tuyến yếu nhất và dễ thành bài giảng nhất, nên mỗi số phải có
**một chỗ trái trực giác đo được**. Không có chỗ đó thì loại, không tiếc.

| # | Cơ chế | Chỗ trái trực giác | Số liệu | Đo bằng |
|---|---|---|---|---|
| 51 | `dict` hoạt động thế nào | Vì sao thứ tự chèn được giữ mà không tốn gì thêm | đo | python |
| 52 | `list.append` | Thỉnh thoảng nó copy cả mảng, và đo được lúc nào | đo | python `getsizeof` |
| 53 | Chuỗi bất biến mà `+=` vẫn nhanh | CPython sửa tại chỗ khi chỉ còn một tham chiếu | đo | python |
| 54 | Số nguyên nhỏ dùng chung | `a is b` đúng với 256 và sai với 257 | đo | python |
| 55 | Event loop chỉ có một vòng lặp | Một `time.sleep` giết sạch mọi thứ đang chờ | đo | asyncio |
| 56 | B-tree index | Tìm một dòng trong 10 triệu chỉ đọc vài trang | đo | postgres |
| 57 | WAL | Ghi vào hai chỗ mà lại nhanh hơn ghi một chỗ | đo | postgres |
| 58 | MVCC | Đọc không chặn ghi, và cái giá phải trả là gì | đo | postgres |
| 59 | Planner đổi ý | Cùng câu query, thêm dữ liệu thì đổi hẳn cách chạy | đo | postgres |
| 60 | TCP bắt tay | Request đầu tiên luôn chậm hơn hẳn phần còn lại | đo | node |
| 61 | DNS TTL | Đổi IP xong, nửa tiếng sau vẫn có request vào máy cũ | đo | node |
| 62 | HTTP keep-alive | 100 request trên một kết nối so với 100 kết nối | đo | node |
| 63 | UTF-8 | `len()` của chuỗi tiếng Việt khác số chữ bạn nhìn thấy | đo | python |
| 64 | LRU cache | Thêm bộ nhớ có lúc làm tỷ lệ trúng giảm | đo | python |
| 65 | Bloom filter | Nói "không có" thì chắc đúng, nói "có" thì có thể sai | đo | python |

## Mùa 5 — FRONTEND (15 số)

Tệp khán giả khác hẳn năm mùa kia. Nếu muốn kênh tập trung một tệp thì cắt mùa
này và chia 15 số cho mùa 1 và mùa 3.

Cách đo: đếm số lần render bằng `react-test-renderer`, đo thời gian bằng node.
Vài số cần trình duyệt thật (`puppeteer`) vì jsdom không có layout engine.

| # | Chủ đề | Triệu chứng | Số liệu | Đo bằng |
|---|---|---|---|---|
| 66 | Re-render vô hạn | Object tạo mới mỗi render nằm trong dependency array | đo | react |
| 67 | `key={index}` | Xoá một phần tử giữa danh sách, state nhảy sang dòng khác | đo | react |
| 68 | Stale closure | `setInterval` đọc mãi giá trị của lần render đầu | đo | react |
| 69 | `useMemo` không có tác dụng | Dependency đổi mỗi render nên nó tính lại mỗi lần | đo | react |
| 70 | `await` trong vòng lặp | 20 request tuần tự thay vì cùng lúc | đo | node |
| 71 | `Array.sort` mặc định so chuỗi | `[10, 9, 1].sort()` ra `[1, 10, 9]` | đo | node |
| 72 | Số nguyên lớn trong JS | ID từ backend vượt `MAX_SAFE_INTEGER` và đổi giá trị | đo | node |
| 73 | `==` và bảng ép kiểu | `[] == ![]` là `true` | đo | node |
| 74 | Nối mảng bằng spread trong vòng lặp | Bình phương theo số phần tử | đo | node |
| 75 | `JSON.parse` chuỗi lớn | Chặn main thread bao lâu, đo được | đo | node |
| 76 | `localStorage` là đồng bộ | Mỗi lần ghi là một lần dừng main thread | đo | puppeteer |
| 77 | Event listener không gỡ | Rò bộ nhớ tăng tuyến tính theo số lần vào trang | đo | puppeteer |
| 78 | Layout thrashing | Đọc `offsetHeight` xen kẽ ghi style trong vòng lặp | đo | puppeteer |
| 79 | `debounce` và `throttle` | Hai cái làm hai việc khác nhau, gõ thử thì rõ | đo | node |
| 80 | Import cả thư viện để dùng một hàm | Kích thước bundle trước và sau | đo | esbuild |

## Mùa 6 — CÔNG CỤ VÀ VẬN HÀNH (10 số)

Mùa rẻ nhất để làm và cũng dễ đụng hàng nhất. Nó chỉ sống được nếu mỗi số vẫn có
một cú lật, chứ "10 lệnh git nên biết" thì trượt Cửa 2.

| # | Chủ đề | Cú lật | Số liệu | Đo bằng |
|---|---|---|---|---|
| 81 | `.gitignore` không có tác dụng | File đã track thì thêm vào `.gitignore` chẳng làm gì | đo | git thật |
| 82 | `git reflog` | `reset --hard` không xoá commit, chỉ thả tay ra | đo | git thật |
| 83 | `git bisect` | 100 commit tìm ra thủ phạm trong 7 bước | đo | git thật |
| 84 | `rm -rf "$DIR/"` | Biến rỗng biến nó thành `rm -rf /` | đo | shell trong thư mục tạm |
| 85 | Exit code trong pipe | Lệnh đầu hỏng mà pipeline vẫn báo thành công | đo | shell |
| 86 | CRLF | Diff đỏ toàn file mà không ai sửa dòng nào | đo | git thật |
| 87 | BOM | File JSON hợp lệ mà parser vẫn từ chối | đo | python |
| 88 | Log không rotate | Đĩa đầy trước khi ai kịp nhìn bảng đo | đo | shell |
| 89 | OOMKilled | Container chết không để lại log ứng dụng nào | đo | docker |
| 90 | `SIGTERM` và tắt êm | Rolling update cắt ngang request đang chạy | đo | docker |

---

## Thứ tự phát đề xuất

Không chạy hết mùa 1 rồi mới sang mùa 2. Người xem cần thấy kênh có nhiều dạng
ngay trong hai tuần đầu, nhưng cũng cần thấy mùa 1 đủ dày để nhớ nhận diện.

| Tuần | Nội dung |
|---|---|
| 1–2 | 10 số mùa 1 liên tiếp, dựng nhận diện |
| 3 | 5 số mùa 3, đổi không khí, kéo bình luận |
| 4–5 | 10 số mùa 1 còn lại |
| 6 | 5 số mùa 2 |
| 7 trở đi | trộn theo tỷ lệ 2 mùa 1 hoặc 2 : 1 mùa 3 : 1 mùa 4 : 1 mùa 5 |

Mùa 6 rải đều làm số đệm cho những ngày không kịp đo.

## Rủi ro đã biết

Số 12, 89, 90 cần docker. Số 76, 77, 78 cần puppeteer. Nếu không cài được thì ba
số đầu chuyển sang mô phỏng bằng process thường và mất phần "container", còn ba số
sau phải bỏ hoặc hạ xuống mức `suy`.

Mùa 4 có nguy cơ thành bài giảng cao nhất. Kiểm bằng một câu hỏi: sau khi xem
xong, người xem có sửa được dòng code nào không? Không thì viết lại hoặc bỏ.

Mùa 3 có nguy cơ ngược lại: quá giống các kênh đố mẹo. Chống bằng cách luôn chạy
thật ở cuối và cho thấy con số, chứ không dừng ở "đáp án là B".
