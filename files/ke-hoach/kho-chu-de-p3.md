# Kho chủ đề content IT — Phần 3 (bài 209-292)

Tiếp nối phần 1 và phần 2. Bổ sung 84 đề tài, tổng cộng 292.

## Hai lăng kính chẩn đoán (nhóm S và T)

Hai nhóm đầu của file này khác về bản chất với mọi nhóm trước đó. Chúng không phân loại theo *công nghệ* mà theo *nguyên nhân bug xuất hiện*:

- **Nhóm S** — bug chỉ xuất hiện khi dữ liệu nhiều
- **Nhóm T** — bug chỉ xuất hiện khi nhiều người dùng đồng thời

Đây là hai lý do lớn nhất khiến code "chạy ổn ở local" chết trên production. Local luôn có ít dữ liệu và một người dùng — nên hai loại bug này *không thể* xuất hiện ở đó.

**Gợi ý dùng làm series có tên.** Hai nhóm này thích hợp để đóng thành series nhận diện được, ví dụ "Chạy ổn ở local, chết ở production". Series có tên thì người đọc theo dõi được và các bài bổ trợ nhau, khác với bài rời rạc.

## Lưu ý riêng cho nhóm U (mạng)

Mạng là nhóm nhiều tầng, và người đọc phát hiện rất nhanh khi người viết chỉ hiểu nửa vời. Nếu bạn chưa vững phần này, viết ở giọng **"mình đang học, đây là những gì đã hiểu"** thay vì giọng hướng dẫn. Trung thực hơn, và không ai bắt lỗi bạn được.

Nguồn nên đọc trước khi viết: RFC tương ứng cho giao thức, tài liệu của Cloudflare Learning Center (viết tốt và chính xác), và `man` page cho công cụ. Đừng lấy blog tổng hợp làm nguồn chính.

Ký hiệu: 🟢 dễ demo rủi ro thấp — 🟡 cần chuẩn bị — 🔴 rủi ro cao nếu viết sai.

---

# S. Bug chỉ xuất hiện khi dữ liệu nhiều (14 bài)

Đặc điểm chung của nhóm này: **test ở local với 10 dòng luôn pass**. Cách viết hiệu quả nhất là mở bài bằng con số — "với 100 dòng mất 8ms, với 1 triệu dòng mất 42 giây" — vì con số đó là điều người đọc chưa từng tự đo.

**209. Load toàn bộ bảng vào memory** 🟢
Naive → gãy: `const users = await User.findAll()` rồi lọc bằng JavaScript. Với 500 dòng thì mượt; với 2 triệu dòng thì process hết RAM và bị OOM kill — không có stack trace hữu ích nào.
Đánh đổi: đẩy điều kiện xuống DB thì đúng nhưng cần biết SQL và không lọc được bằng logic phức tạp trong ngôn ngữ → stream/cursor xử lý được tập lớn với memory phẳng, đổi lại không random access và code phức tạp hơn → xử lý theo lô là dung hòa thực dụng nhất.
Demo: seed 2 triệu dòng, `findAll()`, quan sát RSS của process tăng tới đâu.

**210. Query không index: từ 5ms lên 40 giây** 🟢
Naive → gãy: `WHERE email = ?` không index. 1000 dòng thì 2ms nên không ai để ý; 5 triệu dòng thì full scan.
Đánh đổi: thêm index thì đọc nhanh nhưng chậm đường ghi (xem bài 57) → cái đáng nói ở đây là *cách phát hiện sớm*: `pg_stat_statements` để tìm query tốn tổng thời gian nhiều nhất, và cảnh báo khi có query vượt ngưỡng — rẻ hơn nhiều so với chờ sự cố.
Demo: cùng một query trên bảng 1 nghìn và 5 triệu dòng, không index; so sánh thời gian.

**211. `SELECT *` khi bảng có cột lớn** 🟢
Naive → gãy: `SELECT *` từ bảng có cột `content TEXT` chứa vài trăm KB mỗi dòng. Danh sách 50 bài viết chỉ cần tiêu đề nhưng kéo về 30MB.
Đánh đổi: chọn cột cụ thể thì nhanh và nhẹ nhưng phải sửa khi thêm nhu cầu → `SELECT *` tiện và không vỡ khi thêm cột nhưng kéo theo mọi thứ, phá covering index, và làm ORM tạo object nặng → tách cột lớn sang bảng riêng là giải pháp schema, đổi lại thêm join.
Demo: so sánh thời gian và dung lượng truyền của `SELECT *` và `SELECT id, title` trên bảng có cột TEXT lớn.

**212. Migration chạy 3 giây ở local, khóa bảng 8 phút ở production** 🔴
Naive → gãy: `ALTER TABLE ADD COLUMN ... DEFAULT ...` trên bảng 20 triệu dòng. Local 10 nghìn dòng nên xong tức thì; production khóa bảng và mọi request treo.
Đánh đổi: xem bài 68 cho chuỗi đầy đủ. Điểm riêng của bài này: **cách tự phát hiện trước khi deploy** — chạy migration trên bản copy của production, hoặc ít nhất trên staging có cùng số dòng. Đây là lý do dữ liệu staging phải đủ lớn.
Demo: cùng một migration trên bảng 10 nghìn và 20 triệu dòng, đo thời gian khóa bằng `pg_locks`.

**213. Vòng lặp gọi API bên ngoài** 🟢
Naive → gãy: 5 sản phẩm thì gọi 5 lần API tính phí vận chuyển, mất 1 giây. 200 sản phẩm thì 200 lần, mất 40 giây và request timeout.
Đánh đổi: batch API (nếu nhà cung cấp có) là tốt nhất nhưng không phải lúc nào cũng có → gọi song song có giới hạn concurrency thì nhanh hơn nhiều nhưng có thể vượt rate limit của họ → đẩy sang job nền thì không timeout nhưng user không có kết quả ngay.
Demo: vòng lặp 200 lời gọi tuần tự so với song song 10 luồng, đo tổng thời gian.

**214. JSON response 50MB** 🟢
Naive → gãy: endpoint export trả toàn bộ dữ liệu dạng JSON. Server phải serialize hết vào memory, client phải parse hết — cả hai đầu đều đứng.
Đánh đổi: phân trang bắt buộc thì an toàn nhưng client phải gọi nhiều lần → streaming JSON (NDJSON) cho memory phẳng ở cả hai đầu, đổi lại client phải xử lý dòng-theo-dòng và mất khả năng dùng `JSON.parse` một lần → nén (gzip/brotli) giảm băng thông đáng kể nhưng không giảm memory khi serialize.
Demo: trả về 100 nghìn bản ghi dạng JSON một lần và dạng NDJSON stream, đo memory hai bên.

**215. Bảng log không có kế hoạch xóa** 🟡
Naive → gãy: bảng `activity_logs` ghi mọi hành động. Sau hai năm nó là 80% dung lượng DB, backup mất 4 giờ, và mọi query trên nó chậm.
Đánh đổi: partition theo thời gian cho phép xóa cả partition tức thì (nhanh hơn DELETE hàng triệu dòng rất nhiều), đổi lại phức tạp hơn khi thiết lập → job xóa định kỳ đơn giản nhưng DELETE lớn tạo bloat và cần VACUUM → chuyển log ra khỏi DB quan hệ hoàn toàn (sang hệ thống log riêng) là đúng nhất về lâu dài.
Demo: đo thời gian `DELETE` 5 triệu dòng so với `DROP` một partition.

**216. Đếm và tổng hợp theo thời gian thực** 🟡
Naive → gãy: dashboard hiện "tổng đơn hàng", "doanh thu tháng" bằng cách tính trực tiếp mỗi lần tải trang. Với 10 triệu đơn, mỗi lần vào dashboard là một query nặng.
Đánh đổi: materialized view làm sẵn kết quả, đọc tức thì, đổi lại dữ liệu cũ tới lần refresh gần nhất → bảng tổng hợp cập nhật theo event thì tươi nhưng phải đảm bảo không sót đường ghi nào → tính trực tiếp thì luôn đúng nhưng không scale. Xem thêm bài 69 về `COUNT(*)`.
Demo: dashboard với 5 chỉ số tính trực tiếp trên 10 triệu dòng, đo thời gian tải trang.

**217. Sắp xếp trong bộ nhớ khi vượt work_mem** 🟡
Naive → gãy: `ORDER BY` trên cột không index với tập kết quả lớn. Postgres sắp xếp trong RAM nếu vừa `work_mem`, còn không thì ghi ra disk — chậm gấp nhiều lần và không có cảnh báo nào ở tầng app.
Đánh đổi: index đúng thứ tự cho phép đọc theo thứ tự sẵn có, bỏ hẳn bước sort → tăng `work_mem` giúp nhưng nhân với số connection đồng thời có thể làm hết RAM server → giới hạn tập kết quả trước khi sort là cách rẻ nhất.
Demo: `EXPLAIN ANALYZE` một câu ORDER BY lớn, tìm dòng `Sort Method: external merge Disk`.

**218. Import file người dùng tải lên: 100 dòng và 100 nghìn dòng** 🟡
Naive → gãy: parse CSV rồi insert từng dòng trong vòng lặp, mỗi dòng một round trip. 100 dòng thì 2 giây; 100 nghìn dòng thì 40 phút và request đã timeout từ lâu.
Đánh đổi: bulk insert theo lô 1000 dòng nhanh hơn hàng chục lần, đổi lại xử lý lỗi phức tạp hơn (lô nào lỗi, dòng nào trong lô) → `COPY` của Postgres nhanh nhất nhưng bỏ qua nhiều logic ứng dụng → xử lý nền với báo cáo tiến độ là bắt buộc từ một ngưỡng nào đó.
Demo: import 100 nghìn dòng theo ba cách, đo thời gian và cách báo lỗi.

**219. Tìm kiếm `LIKE '%keyword%'`** 🟢
Naive → gãy: hoạt động hoàn hảo ở local. Trên 3 triệu dòng thì mỗi lần user gõ là một full scan — và ô search gọi liên tục.
Đánh đổi: xem bài 70 và 71 cho chuỗi đầy đủ. Điểm riêng: `LIKE 'prefix%'` dùng được index còn `'%text%'` thì không — khác biệt một ký tự nhưng khác biệt hàng nghìn lần về tốc độ. `pg_trgm` cho phép index cả trường hợp giữa chuỗi, đổi lại index lớn.
Demo: `EXPLAIN` cho `LIKE 'abc%'` và `LIKE '%abc%'` trên cột có index, so sánh.

**220. Sinh file PDF/Excel hàng loạt** 🟡
Naive → gãy: nút "in tất cả hóa đơn" sinh 5000 PDF trong một request. Mỗi PDF tốn 200ms CPU, tổng 17 phút, và process chiếm hết CPU khiến mọi user khác chậm theo.
Đánh đổi: job nền với giới hạn concurrency bảo vệ hệ thống nhưng user phải chờ và cần cách thông báo khi xong → sinh theo yêu cầu từng cái thì không bao giờ nghẽn nhưng không đáp ứng nhu cầu hàng loạt → tách sang worker riêng (máy khác) cách ly hoàn toàn, đổi lại thêm hạ tầng.
Demo: sinh 500 PDF đồng thời, quan sát latency của các request khác trong lúc đó.

**221. Cây phân cấp sâu: truy vấn đệ quy** 🟡
Naive → gãy: cây danh mục, lấy toàn bộ con cháu bằng đệ quy trong code — mỗi tầng một query. 3 tầng thì ổn; 8 tầng với nhiều nhánh thì hàng nghìn query.
Đánh đổi: recursive CTE làm trong một query, nhanh hơn rất nhiều, đổi lại SQL khó đọc và dễ vô hạn nếu dữ liệu có vòng → materialized path (lưu đường dẫn dạng chuỗi) đọc cực nhanh nhưng cập nhật khi di chuyển nhánh thì đắt → closure table nhanh cả đọc và truy vấn tổ tiên nhưng tốn dung lượng lớn.
Demo: dựng cây 8 tầng, so sánh đệ quy trong code và recursive CTE.

**222. Cache key bùng nổ khi tham số nhiều** 🟡
Naive → gãy: cache theo toàn bộ query string. Với 5 filter mỗi cái 10 giá trị, số tổ hợp là 100 nghìn key — hit rate gần bằng 0 và Redis đầy.
Đánh đổi: chuẩn hóa key (sắp xếp tham số, bỏ tham số không ảnh hưởng kết quả) tăng hit rate đáng kể với chi phí thấp → chỉ cache tổ hợp phổ biến thì hiệu quả nhưng cần đo để biết cái nào phổ biến → cache ở tầng thấp hơn (từng entity thay vì cả kết quả) thì hit rate cao nhưng phải ghép ở tầng app.
Demo: log các cache key thật trong một ngày, đếm số key duy nhất và hit rate.

---

# T. Bug chỉ xuất hiện khi nhiều người dùng đồng thời (12 bài)

Đặc điểm chung: **không tái hiện được bằng cách bấm chuột**. Bạn phải dựng công cụ bắn tải, và đó chính là thứ làm bài viết của bạn khác biệt — vì hầu hết người viết không làm bước này.

Công cụ tối thiểu cần biết: `autocannon` hoặc `k6` để bắn tải, và cách mở nhiều session DB thủ công để điều khiển thứ tự.

**223. Biến toàn cục hoặc state trong module** 🔴
Naive → gãy: lưu thông tin user hiện tại vào một biến ở tầng module cho tiện. Một người dùng thì đúng; hai request đồng thời thì user A thấy dữ liệu của user B.
Đánh đổi: truyền context tường minh qua tham số thì an toàn tuyệt đối nhưng phải xuyên qua nhiều tầng hàm → `AsyncLocalStorage` cho context ngầm mà vẫn cô lập theo request, đổi lại khó debug khi nó không hoạt động → dependency injection theo phạm vi request (NestJS `Scope.REQUEST`) sạch nhưng có chi phí hiệu năng.
Demo: đặt một biến module ghi userId, bắn 50 request đồng thời từ hai token khác nhau, đếm số lần nhầm.

**224. Kết nối DB cạn khi tải tăng** 🔴
Naive → gãy: một người dùng thì pool 10 connection quá dư. 200 người đồng thời thì mọi request xếp hàng chờ connection, và timeout hàng loạt — log báo lỗi DB nhưng DB hoàn toàn khỏe.
Đánh đổi: xem bài 72. Điểm riêng của bài này: **connection leak** — không release connection khi có exception là nguyên nhân phổ biến nhất, và nó chỉ lộ ra khi có tải. Kiểm tra bằng cách theo dõi số connection đang dùng theo thời gian.
Demo: cố tình không release connection trong một nhánh lỗi, bắn tải và xem pool cạn sau bao nhiêu request.

**225. Race condition ở luồng đăng ký: hai tài khoản cùng email** 🔴
Naive → gãy: `if (await findByEmail(email)) throw` rồi `create(...)`. Hai request đồng thời đều thấy chưa tồn tại, cả hai tạo thành công.
Đánh đổi: unique constraint ở DB là lớp duy nhất thật sự chặn được, đổi lại phải bắt lỗi constraint và dịch thành thông báo tử tế → kiểm tra trước vẫn nên có vì cho thông báo đẹp hơn trong trường hợp thường → chỉ dựa vào kiểm tra trước là sai về bản chất, dù test tay không bao giờ phát hiện.
Demo: bắn 20 request đăng ký cùng email đồng thời, đếm số tài khoản được tạo.

**226. Cron chạy chồng nhau khi lần trước chưa xong** 🟡
Naive → gãy: cron mỗi 5 phút, xử lý mất 7 phút. Lần thứ hai chạy khi lần đầu chưa xong, cùng xử lý một tập bản ghi.
Đánh đổi: khóa với TTL chặn được chồng lấn nhưng nếu process chết khi giữ khóa thì job đứng tới khi khóa hết hạn → đánh dấu bản ghi đang xử lý (`SELECT FOR UPDATE SKIP LOCKED`) cho phép nhiều instance chạy song song mà không trùng — mẫu rất hữu ích và ít người biết → tăng chu kỳ cron thì đơn giản nhưng chỉ giảm xác suất.
Demo: cron 10 giây với xử lý 30 giây, log bản ghi được xử lý và tìm bản ghi trùng.

**227. Rate limit đếm sai khi có nhiều instance** 🟡
Naive → gãy: đếm request trong memory của mỗi instance. Ba instance nghĩa là giới hạn thực tế gấp ba lần khai báo — và lệch không đoán được vì phụ thuộc load balancer.
Đánh đổi: đếm ở Redis thì chính xác nhưng thêm một round trip mỗi request và Redis thành phụ thuộc bắt buộc → chia hạn mức cho số instance thì không cần state chung nhưng lệch khi scale thay đổi → đếm ở gateway thì tập trung và rẻ nhưng không biết ngữ cảnh nghiệp vụ.
Demo: chạy 3 instance với rate limit in-memory 10 req/phút, bắn tải và đếm số request thật được cho qua.

**228. Session hoặc cache trong memory khi có nhiều instance** 🔴
Naive → gãy: lưu session trong memory. Một instance thì hoàn hảo. Hai instance thì user đăng nhập rồi request tiếp rơi vào instance khác — bị đăng xuất ngẫu nhiên.
Đánh đổi: session store dùng chung (Redis) là lời giải chuẩn, đổi lại thêm phụ thuộc và mỗi request tốn một lookup → sticky session giữ user ở một instance nhưng vỡ khi instance restart và làm lệch tải → token stateless không cần store nhưng mang theo mọi đánh đổi ở bài 3 và 4.
Demo: chạy 2 instance sau load balancer với session in-memory, refresh liên tục và đếm số lần bị đăng xuất.

**229. Deadlock chỉ xuất hiện dưới tải** 🟡
Naive → gãy: hai đường code khóa hai bản ghi theo thứ tự ngược nhau. Chạy tuần tự không bao giờ deadlock; chạy đồng thời thì deadlock ngẫu nhiên vài lần một giờ trên production.
Đánh đổi: xem bài 82 cho cách phòng. Điểm riêng: **cách tái hiện có kiểm soát** — dùng hai session psql và thêm `pg_sleep` giữa hai lệnh khóa để mở rộng cửa sổ, deadlock xuất hiện 100% số lần. Đây là kỹ thuật đáng viết riêng.
Demo: tái hiện deadlock xác định bằng hai session, đọc log Postgres để thấy nó báo gì.

**230. Số thứ tự tự tăng do app tự sinh** 🔴
Naive → gãy: sinh mã hóa đơn bằng `SELECT MAX(number) + 1`. Một người dùng thì đúng; hai người cùng lúc thì trùng mã.
Đánh đổi: sequence của DB an toàn tuyệt đối nhưng có khoảng trống khi transaction rollback (kế toán có thể không chấp nhận số nhảy) → bảng counter với `SELECT FOR UPDATE` cho số liên tục nhưng tuần tự hóa và thành điểm nghẽn → sinh trước theo lô giảm tranh chấp nhưng vẫn có khoảng trống khi khởi động lại.
Demo: bắn 50 request tạo hóa đơn đồng thời bằng cách `MAX + 1`, đếm số mã trùng.

**231. Timeout theo tầng: chuỗi timeout không khớp nhau** 🟡
Naive → gãy: proxy timeout 60s, app timeout 30s, DB không timeout. Dưới tải, query chậm 90 giây vẫn chạy trong DB sau khi client đã bỏ đi từ lâu — DB tiếp tục làm việc vô nghĩa và chiếm tài nguyên.
Đánh đổi: timeout giảm dần từ ngoài vào trong (proxy > app > DB) là nguyên tắc đúng, đổi lại phải cấu hình ở nhiều nơi và dễ lệch khi ai đó sửa một chỗ → statement timeout ở DB bảo vệ tuyệt đối nhưng có thể cắt query hợp lệ chỉ chậm → cancel request khi client ngắt kết nối là đúng nhất nhưng ít framework làm sẵn.
Demo: gửi request rồi ngắt client, kiểm tra `pg_stat_activity` xem query còn chạy không.

**232. Webhook nhận đồng thời nhiều event cho cùng một đơn** 🔴
Naive → gãy: cổng thanh toán gửi hai event gần nhau (`authorized` rồi `captured`). Hai webhook xử lý song song, cả hai đọc trạng thái cũ, kết quả cuối phụ thuộc cái nào ghi sau.
Đánh đổi: khóa theo ID đơn khi xử lý webhook đảm bảo thứ tự trong phạm vi cần thiết, đổi lại giảm throughput → xử lý tuần tự theo hàng đợi có partition theo đơn thì đúng và vẫn song song giữa các đơn khác nhau → dùng số thứ tự event và bỏ event cũ hơn thì bền nhất nhưng cần nhà cung cấp có cung cấp số thứ tự.
Demo: gửi hai webhook cho cùng một đơn cách nhau 5ms, xem trạng thái cuối.

**233. Blue-green và canary: hai phiên bản cùng chạy** 🔴
Naive → gãy: blue-green tưởng là chuyển tức thì nên không nghĩ tới việc hai phiên bản cùng sống. Nhưng trong lúc chuyển, hai phiên bản cùng đọc ghi *một database* — và nếu phiên bản mới ghi format mới, phiên bản cũ đọc không hiểu.
Đánh đổi: blue-green cho rollback tức thì (chỉ chuyển traffic lại) và không có trạng thái nửa vời trên mỗi instance, đổi lại cần gấp đôi tài nguyên và **migration phải tương thích cả hai chiều** → rolling update tiết kiệm tài nguyên nhưng thời gian hai phiên bản cùng chạy dài hơn → canary phát hiện lỗi với ít user bị ảnh hưởng nhất nhưng phức tạp nhất và cần metric đủ tốt để so sánh hai nhóm.
Demo: deploy blue-green với một migration đổi tên cột, giữ traffic ở cả hai phiên bản và xem cái nào vỡ.

**234. Dựng môi trường test tải: công cụ và cách đọc kết quả** 🟡
Naive → gãy: bắn 10 nghìn request rồi xem "chịu được không". Không có baseline, không biết điểm nghẽn ở đâu, và bắn từ laptop qua WiFi nên chính mạng của bạn là điểm nghẽn.
Đánh đổi: `autocannon` cài trong một phút, đủ cho kiểm tra nhanh, đổi lại ít khả năng mô tả kịch bản phức tạp → `k6` viết được kịch bản thật (đăng nhập rồi mới gọi API) và có metric tốt, đổi lại phải học → điều quan trọng hơn cả công cụ: tăng tải dần và quan sát **điểm mà p95 bắt đầu xấu đi**, không phải tìm điểm sập.
Demo: bắn tải tăng dần lên một endpoint, vẽ đồ thị p95 theo số connection, tìm điểm gấp khúc.

---

# U. Mạng & kết nối (18 bài)

Nhóm bạn nói chưa vững. Đọc lại lưu ý ở đầu file: viết ở giọng đang học, và kiểm chứng từ nguồn gốc.

Điều tốt về nhóm này: **gần như mọi bài đều demo được bằng công cụ có sẵn** — `ping`, `traceroute`, `dig`, `ss`, `tcpdump`, DevTools. Không cần hạ tầng đặc biệt.

**235. LAN, WAN, và tại sao khái niệm này vẫn quan trọng với dev** 🟢
Cách hoạt động: LAN là mạng nội bộ, thiết bị nói trực tiếp với nhau qua switch, độ trễ dưới 1ms. WAN là kết nối qua internet, đi qua nhiều router, độ trễ hàng chục tới hàng trăm ms.
Vì sao dev cần biết: app gọi DB trong cùng LAN mất 0.5ms; cùng logic mà DB ở vùng khác thì mất 80ms — và nếu code có N+1 với 100 query thì đó là 8 giây thay vì 50ms. Vị trí vật lý của service là quyết định kiến trúc, không phải chi tiết vận hành.
Chỗ hay sai: giả định độ trễ không đáng kể vì local test luôn dưới 1ms; đặt DB ở vùng khác với app để "tiết kiệm".
Demo: `ping` một server cùng khu vực và một server ở châu lục khác, nhân số đó với số query trong một request.

**236. IP, subnet, CIDR: đọc được `10.0.1.0/24`** 🟢
Cách hoạt động: IP chia thành phần mạng và phần host; `/24` nghĩa là 24 bit đầu là mạng, còn 8 bit cho host (254 địa chỉ dùng được).
Vì sao dev cần biết: cấu hình security group, whitelist IP, VPC subnet, và `docker network` đều dùng ký hiệu này. Không đọc được CIDR thì mọi cấu hình mạng trở thành copy-paste mù.
Chỗ hay sai: whitelist `0.0.0.0/0` (nghĩa là toàn bộ internet) rồi tưởng đã giới hạn; nhầm dải private (10.x, 172.16-31.x, 192.168.x) với public; tạo subnet chồng lấn nhau khi peering.
Demo: tính số host trong `/24`, `/28`, `/16`; kiểm tra bằng `ipcalc`.

**237. NAT: tại sao máy bạn không có IP public** 🟡
Cách hoạt động: router thay địa chỉ nguồn của gói đi ra bằng IP public của nó, ghi lại bảng mapping để trả lời về đúng máy.
Vì sao dev cần biết: đây là lý do bạn không thể để người khác truy cập trực tiếp server local; lý do rate limit theo IP chặn cả văn phòng (mọi người chung một IP public); và lý do WebRTC cần STUN/TURN.
Chỗ hay sai: tin rằng IP trong log là IP thật của user (sau NAT và proxy thì không); dùng IP làm khóa nhận dạng người dùng.
Demo: so sánh IP thấy trong `ip addr` với IP mà một trang "what is my IP" báo.

**238. DNS: chuỗi phân giải và tại sao đổi record không có hiệu lực ngay** 🟢
Cách hoạt động: resolver hỏi root → TLD → nameserver của domain, rồi cache kết quả theo TTL. Mỗi tầng cache độc lập.
Vì sao dev cần biết: đây là nguyên nhân "tôi đã đổi DNS mà vẫn vào site cũ" — và cũng là lý do phải giảm TTL *trước* khi định chuyển server, không phải lúc chuyển.
Chỗ hay sai: nhầm A record với CNAME; dùng CNAME cho apex domain; đổi record rồi flush DNS local và tưởng thế là xong (ISP và resolver khác vẫn cache); TTL 86400 rồi cần chuyển server gấp.
Demo: `dig +trace example.com` để thấy toàn bộ chuỗi; `dig` từ nhiều resolver khác nhau (`@8.8.8.8`, `@1.1.1.1`) và so sánh.

**239. TCP và UDP: chọn theo cái gì** 🟢
Cách hoạt động: TCP thiết lập kết nối, đảm bảo thứ tự và gửi lại gói mất. UDP gửi và không quan tâm gì thêm.
Dùng cho bài toán nào: TCP cho gần như mọi thứ trong web (HTTP, DB, SSH). UDP cho DNS, video call, game realtime — nơi một gói mất tốt hơn một gói tới muộn.
Chỗ hay sai: nghĩ TCP "đáng tin nên chậm" mà không hiểu vì sao (đảm bảo thứ tự nghĩa là một gói mất làm mọi gói sau phải chờ — head-of-line blocking); dùng UDP vì "nhanh hơn" mà không xử lý mất gói.
Demo: `tcpdump` một request HTTP, tìm handshake ba bước và ACK.

**240. Handshake và tại sao kết nối mới đắt** 🟡
Cách hoạt động: TCP cần một vòng đi về để thiết lập; TLS cần thêm một tới hai vòng nữa. Với độ trễ 100ms, một kết nối mới tốn 200-400ms trước khi gửi được byte dữ liệu đầu tiên.
Vì sao dev cần biết: đây là lý do keep-alive và connection pool tồn tại, và lý do gọi 50 API tuần tự tới domain khác nhau chậm khủng khiếp.
Chỗ hay sai: tạo HTTP client mới cho mỗi request (mất keep-alive); tắt keep-alive ở proxy mà không biết; đo hiệu năng API bằng công cụ tạo kết nối mới mỗi lần.
Demo: gọi 100 request với và không có keep-alive, so sánh tổng thời gian.

**241. HTTP/1.1, HTTP/2, HTTP/3: khác biệt có ý nghĩa với dev** 🟡
Cách hoạt động: HTTP/1.1 một request một lúc trên mỗi kết nối (nên browser mở 6 kết nối). HTTP/2 ghép nhiều stream trên một kết nối. HTTP/3 chuyển sang UDP/QUIC để bỏ head-of-line blocking ở tầng TCP.
Vì sao dev cần biết: nhiều lời khuyên tối ưu cũ (gộp file, sprite ảnh, domain sharding) sinh ra vì giới hạn HTTP/1.1 — với HTTP/2 chúng có thể phản tác dụng.
Chỗ hay sai: vẫn gộp mọi JS thành một file khổng lồ vì "giảm số request"; tin rằng bật HTTP/2 là tự nhanh hơn (nếu điểm nghẽn là server chậm thì không đổi gì).
Demo: mở DevTools Network, cột Protocol, xem site nào dùng h2/h3.

**242. Cổng, listen, và `ss -tlnp`** 🟢
Cách hoạt động: một process bind một cổng trên một địa chỉ. Bind `127.0.0.1` chỉ nghe từ máy đó; bind `0.0.0.0` nghe từ mọi giao diện — nghĩa là từ internet nếu không có firewall.
Vì sao dev cần biết: đây là khác biệt giữa "DB chỉ app truy cập được" và "DB cả internet truy cập được" — một chuỗi cấu hình.
Chỗ hay sai: Postgres/Redis bind `0.0.0.0` không mật khẩu (Redis bị chiếm trong vài giờ); nghĩ container không expose port là an toàn mà quên `network_mode: host`; nhầm `EXPOSE` trong Dockerfile với publish port.
Demo: chạy `ss -tlnp` trên server, đối chiếu từng dòng với ý định của bạn.

**243. Firewall: security group, iptables, và thứ tự quy tắc** 🟡
Cách hoạt động: quy tắc được đánh giá theo thứ tự, thường có luật mặc định ở cuối. Stateful firewall tự cho phép gói trả về của kết nối đã thiết lập.
Vì sao dev cần biết: phần lớn sự cố "không kết nối được" là firewall, và cách chẩn đoán khác hẳn với lỗi ứng dụng.
Chỗ hay sai: mở cổng ở security group nhưng quên firewall trong OS (hoặc ngược lại); thêm luật allow sau luật deny nên không có hiệu lực; mở cổng ra `0.0.0.0/0` cho tiện rồi quên đóng.
Demo: chặn một cổng rồi thử kết nối; phân biệt "connection refused" (không ai nghe) với "timeout" (bị firewall chặn im lặng) — khác biệt này là kỹ năng chẩn đoán quan trọng.

**244. VPN: giải quyết vấn đề gì và không giải quyết gì** 🟡
Cách hoạt động: tạo đường hầm mã hóa giữa máy bạn và một mạng, rồi định tuyến traffic qua đó — máy bạn hành xử như đang ở trong mạng đó.
Dùng cho bài toán nào: truy cập tài nguyên nội bộ (DB, dashboard admin) mà không phơi ra internet; nối hai mạng của hai văn phòng; ẩn traffic khỏi mạng WiFi không tin cậy.
Cái nó KHÔNG giải quyết: không làm bạn ẩn danh (nhà cung cấp VPN thấy hết); không thay thế xác thực (vào được VPN không có nghĩa là được truy cập mọi thứ — cần zero trust); và trở thành điểm lỗi cùng điểm nghẽn băng thông.
Demo: dựng WireGuard giữa hai máy, truy cập một service chỉ bind trên IP nội bộ.

**245. SSH tunnel và port forwarding: công cụ ít người dùng đúng** 🟡
Cách hoạt động: `ssh -L 5432:localhost:5432 user@server` tạo cổng local chuyển tiếp qua SSH tới cổng trên server — bạn nối tới DB production như thể nó ở máy bạn, mà DB không cần mở ra internet.
Dùng cho bài toán nào: truy cập DB hoặc dashboard nội bộ tạm thời; thay thế VPN cho nhu cầu đơn giản; reverse tunnel (`-R`) để phơi service local ra ngoài khi debug webhook.
Chỗ hay sai: nhầm `-L` với `-R`; để tunnel mở vô thời hạn; dùng tunnel làm giải pháp lâu dài thay vì VPN (không quản lý được, không audit được).
Demo: forward cổng Postgres của một server, kết nối bằng client local, rồi thử `-R` để nhận webhook về máy.

**246. Load balancer tầng 4 và tầng 7** 🟡
Cách hoạt động: L4 phân phối theo IP và cổng, không đọc nội dung — nhanh và không phụ thuộc giao thức. L7 đọc HTTP nên route được theo đường dẫn, header, cookie.
Dùng cho bài toán nào: L4 cho throughput cao và giao thức không phải HTTP (DB, TCP thuần); L7 cho routing theo nghiệp vụ, TLS termination, và sticky session theo cookie.
Chỗ hay sai: cần route theo đường dẫn nhưng dùng L4; TLS termination ở L7 rồi quên rằng traffic phía sau là HTTP thô (cần mã hóa nội bộ nếu qua mạng không tin cậy); mất IP thật của client vì không đọc `X-Forwarded-For`.
Demo: cấu hình Nginx route hai đường dẫn tới hai backend, kiểm tra header client nhận được.

**247. WebSocket qua proxy: những chỗ nó vỡ** 🟡
Cách hoạt động: WebSocket bắt đầu bằng HTTP request có header `Upgrade`, sau đó kết nối chuyển sang giao thức khác trên cùng TCP connection.
Vì sao dev cần biết: nhiều proxy mặc định không chuyển tiếp header `Upgrade`, hoặc đóng kết nối idle sau 60 giây — WebSocket chạy ở local nhưng chết sau proxy.
Chỗ hay sai: quên `proxy_set_header Upgrade` trong Nginx; `proxy_read_timeout` mặc định làm kết nối rơi mỗi phút; không có ping/pong nên không phát hiện kết nối đã chết.
Demo: đặt WebSocket sau Nginx cấu hình mặc định, xem nó vỡ; thêm header Upgrade và tăng timeout, so sánh.

**248. Proxy, reverse proxy, và `X-Forwarded-For`** 🟢
Cách hoạt động: forward proxy đứng trước client (client biết), reverse proxy đứng trước server (client không biết). Reverse proxy thêm header ghi IP gốc của client.
Vì sao dev cần biết: sau khi thêm proxy, `req.ip` trong app là IP của proxy — nên rate limit theo IP chặn tất cả cùng lúc, và log ghi sai.
Chỗ hay sai: tin `X-Forwarded-For` một cách vô điều kiện (client giả được — chỉ tin khi request đến từ proxy bạn kiểm soát); quên bật `trust proxy` trong framework; nhầm thứ tự IP trong chuỗi khi có nhiều proxy.
Demo: gửi request kèm header `X-Forwarded-For` giả, xem app ghi log IP nào.

**249. Timeout và MTU: hai nguyên nhân "lỗi ngẫu nhiên"** 🟡
Cách hoạt động: mỗi tầng có timeout riêng (xem bài 231). MTU là kích thước gói tối đa; gói lớn hơn phải phân mảnh, và nếu phân mảnh bị chặn thì kết nối treo với gói lớn nhưng ping vẫn thông.
Vì sao dev cần biết: "ping được nhưng tải file lớn thì treo" là dấu hiệu MTU điển hình, thường gặp qua VPN — và gần như không ai nghĩ tới nó.
Chỗ hay sai: đổ lỗi cho ứng dụng khi vấn đề ở tầng mạng; không phân biệt "chậm" với "treo hoàn toàn ở một ngưỡng kích thước".
Demo: `ping -s 1472 -M do` để tìm MTU thực tế của đường truyền, rồi thử qua VPN.

**250. Chẩn đoán "không kết nối được": trình tự loại trừ** 🟢
Cách hoạt động: đi từ dưới lên — DNS phân giải được không (`dig`) → tới được host không (`ping`, nhưng ICMP có thể bị chặn) → cổng có mở không (`nc -zv`) → TLS handshake được không (`openssl s_client`) → app trả lời gì (`curl -v`).
Vì sao dev cần biết: đây là quy trình thay cho đoán mò, và tiết kiệm hàng giờ.
Chỗ hay sai: nhảy thẳng vào đọc code app khi vấn đề ở DNS; kết luận "server chết" khi chỉ ICMP bị chặn; không phân biệt refused, timeout, và reset.
Demo: cố tình gây từng loại lỗi (DNS sai, cổng đóng, cert sai) và ghi lại thông báo đặc trưng của mỗi loại.

**251. Đọc DevTools Network: waterfall nói gì** 🟢
Cách hoạt động: mỗi request có các pha — queueing, DNS, initial connection, TLS, TTFB, content download. Pha nào dài chỉ ra nguyên nhân khác nhau.
Vì sao dev cần biết: TTFB dài là server chậm; connection dài là vấn đề mạng; download dài là file lớn. Ba nguyên nhân hoàn toàn khác nhau mà nhiều người gộp chung thành "app chậm".
Chỗ hay sai: tối ưu kích thước file khi vấn đề là TTFB; không để ý cột waterfall để thấy request nào chặn request nào; test với cache còn nóng.
Demo: mở một site nặng, đọc waterfall, xác định pha nào chiếm nhiều nhất và tại sao.

**252. Mạng nội bộ trong Docker: tại sao `localhost` không hoạt động** 🟢
Cách hoạt động: mỗi container có network namespace riêng — `localhost` trong container là chính container đó, không phải host. Container trong cùng network gọi nhau bằng tên service.
Vì sao dev cần biết: đây là lỗi phổ biến nhất khi bắt đầu dùng Docker Compose, và thông báo lỗi (`ECONNREFUSED 127.0.0.1:5432`) không gợi ý gì về nguyên nhân.
Chỗ hay sai: dùng `localhost` để gọi container khác; nhầm cổng bên trong với cổng publish; cần gọi service trên host thì không biết `host.docker.internal`.
Demo: hai container trong Compose, thử gọi nhau bằng `localhost` rồi bằng tên service.

---

# V. Identity, SSO & Keycloak (10 bài)

Bạn nhắc tới Keycloak — đúng là một mảng riêng đáng viết. Đây là nhóm mà nhiều dev Việt gặp khi vào dự án doanh nghiệp nhưng ít tài liệu tiếng Việt tử tế.

Toàn nhóm 🔴 hoặc 🟡: sai ở đây ảnh hưởng toàn bộ hệ thống xác thực.

**253. Khi nào tự làm auth, khi nào dùng identity provider** 🟡
Naive → gãy: tự viết auth cho mọi dự án. Với một app đơn giản thì hợp lý; với 5 app cần đăng nhập một lần, cần SSO doanh nghiệp, cần MFA và audit — tự làm là nhiều tháng công việc và nhiều lỗ hổng.
Đánh đổi: tự làm cho kiểm soát hoàn toàn, không phụ thuộc, phù hợp app đơn lẻ → IdP (Keycloak, Auth0, Cognito) cho SSO, MFA, social login, quản lý user sẵn sàng, đổi lại phải học một hệ thống lớn, thêm một thứ phải vận hành, và tùy biến luồng bị giới hạn → self-host (Keycloak) rẻ và giữ dữ liệu nhưng bạn chịu trách nhiệm vận hành; SaaS đắt hơn nhưng hết đau đầu.
Demo: liệt kê yêu cầu auth thật của dự án và ước lượng thời gian tự làm từng cái.

**254. OIDC và OAuth2: hai thứ hay bị gọi lẫn** 🔴
Naive → gãy: dùng OAuth2 access token để xác định "user này là ai". OAuth2 là *authorization* (cho phép truy cập tài nguyên), không phải *authentication* (chứng minh danh tính).
Đánh đổi: OIDC bổ sung `id_token` mang danh tính đã được xác thực — đây mới là thứ dùng để đăng nhập → dùng access token để lấy thông tin user qua `/userinfo` cũng được nhưng thêm một lời gọi và không có tính chứng minh như id_token → nhầm hai cái là gốc của nhiều lỗ hổng thực tế (token thay thế được giữa các client).
Demo: đăng nhập qua một IdP, decode cả `access_token` và `id_token`, so sánh nội dung.

**255. Keycloak: realm, client, role, group — mô hình khái niệm** 🟡
Naive → gãy: vào Keycloak, thấy hàng chục tab, cấu hình theo tutorial mà không hiểu mô hình. Sau đó không sửa được gì khi có yêu cầu mới.
Đánh đổi: realm là biên giới cô lập (một realm cho mỗi tổ chức tách biệt, hay dùng chung với client khác nhau — quyết định này khó đảo ngược) → client đại diện cho một ứng dụng; public client (SPA) không giữ được secret nên phải dùng PKCE, confidential client (backend) thì giữ được → role ở cấp realm dùng chung, ở cấp client thì riêng — dùng sai cấp làm phân quyền rối về sau.
Demo: dựng Keycloak bằng Docker, tạo một realm với hai client (SPA và backend), đăng nhập thử.

**256. Public client và confidential client: PKCE bắt buộc ở đâu** 🔴
Naive → gãy: SPA dùng client secret vì tutorial backend nói vậy. Secret nằm trong bundle JS — ai cũng đọc được, nghĩa là không còn là secret.
Đánh đổi: public client + PKCE là cách đúng cho SPA và mobile, đổi lại phức tạp hơn một chút ở client → BFF (backend giữ token, browser chỉ có cookie) an toàn nhất vì token không tới browser, đổi lại thêm một tầng server → dùng confidential client cho SPA là sai về bản chất bất kể tutorial nói gì.
Demo: tìm client secret trong bundle production của một SPA cấu hình sai.

**257. Đăng xuất trong SSO: khó hơn đăng nhập** 🔴
Naive → gãy: xóa token ở app A và gọi đó là đăng xuất. User vẫn đăng nhập ở app B, C, và ở chính IdP — bấm đăng nhập lại là vào ngay không cần mật khẩu.
Đánh đổi: back-channel logout (IdP thông báo cho từng app) là đúng nhất nhưng mọi app phải hiện thực endpoint và xử lý được → front-channel logout (redirect qua từng app) đơn giản hơn nhưng phụ thuộc browser và vỡ khi third-party cookie bị chặn → chỉ đăng xuất local thì đơn giản nhưng gây bất ngờ nguy hiểm cho user ở máy công cộng.
Demo: đăng nhập hai app qua cùng IdP, đăng xuất một app, thử vào app kia.

**258. Social login: những chỗ hay hở** 🔴
Naive → gãy: nhận email từ Google rồi tìm user theo email và đăng nhập. Nếu có nhà cung cấp không xác minh email (hoặc cho user tự đặt email), kẻ tấn công đăng ký email của người khác ở đó rồi chiếm tài khoản.
Đánh đổi: chỉ tin email khi `email_verified` là true và nhà cung cấp đáng tin → liên kết theo `sub` (ID của nhà cung cấp) thay vì email thì an toàn nhưng user đổi nhà cung cấp là mất tài khoản → cho phép liên kết nhiều nhà cung cấp vào một tài khoản là UX tốt nhưng luồng liên kết phải yêu cầu xác thực lại, nếu không thành lỗ hổng chiếm tài khoản.
Demo: đọc kỹ payload id_token từ hai nhà cung cấp, so sánh field nào có và field nào đáng tin.

**259. MFA: TOTP, SMS, passkey — và recovery** 🔴
Naive → gãy: bật MFA bằng SMS và coi như xong. SIM swap là kỹ thuật tấn công thật và phổ biến; SMS cũng không tới được khi user ra nước ngoài.
Đánh đổi: TOTP (app authenticator) an toàn hơn SMS nhiều và miễn phí, đổi lại user mất điện thoại là mất truy cập — nên **recovery code là phần bắt buộc, không phải tùy chọn** → passkey/WebAuthn an toàn nhất và chống phishing thật sự, đổi lại hỗ trợ và hiểu biết của user còn hạn chế → luồng recovery chính là chỗ yếu nhất của mọi hệ thống MFA: nếu reset qua email thì bảo mật rút về bằng email.
Demo: bật MFA rồi thử toàn bộ luồng mất thiết bị, xem có lối vào nào yếu hơn MFA không.

**260. Đồng bộ user giữa IdP và database của app** 🟡
Naive → gãy: chỉ lưu user ở IdP. Rồi cần join dữ liệu theo user, cần khóa ngoại, cần query "đơn hàng của user có tên chứa X" — không làm được vì user ở hệ thống khác.
Đánh đổi: lưu bản sao user trong DB app (chỉ ID và vài field cần thiết) cho phép join và query, đổi lại phải đồng bộ và xử lý lệch → tạo bản ghi user lúc đăng nhập đầu tiên (JIT provisioning) là mẫu thực dụng nhất → dùng IdP làm nguồn duy nhất thì sạch về nguyên tắc nhưng mọi query cần thông tin user thành lời gọi mạng.
Demo: viết luồng JIT provisioning và thử trường hợp user đổi email ở IdP.

**261. Multi-tenant: một realm hay nhiều realm** 🟡
Naive → gãy: chọn một realm cho tất cả tenant vì đơn giản. Sau đó khách hàng doanh nghiệp yêu cầu SSO riêng bằng Azure AD của họ — và cấu hình đó là cấp realm.
Đánh đổi: một realm thì quản lý đơn giản, chia tenant bằng group/attribute, đổi lại không tùy biến được luồng đăng nhập theo tenant và có nguy cơ rò rỉ giữa tenant nếu phân quyền sai → mỗi tenant một realm thì cô lập tốt và tùy biến tự do, đổi lại số realm bùng nổ và vận hành nặng → mô hình hybrid (realm chung cho tenant nhỏ, realm riêng cho khách lớn) là thực tế nhất nhưng phức tạp về code.
Demo: dựng hai realm với hai cách đăng nhập khác nhau, viết logic app chọn realm theo domain.

**262. Token trong kiến trúc nhiều service: verify ở đâu** 🟡
Naive → gãy: mỗi service gọi IdP để verify token mỗi request. IdP thành điểm nghẽn và điểm lỗi cho toàn hệ thống.
Đánh đổi: verify local bằng public key (JWKS) thì nhanh và không phụ thuộc IdP lúc chạy, đổi lại không biết token đã bị revoke → token introspection cho trạng thái chính xác nhưng tốn một lời gọi mỗi request → verify local + token sống ngắn là dung hòa phổ biến nhất. Nhớ cache JWKS và xử lý key rotation, nếu không thì rotation làm sập tất cả.
Demo: verify một token bằng JWKS local, rồi revoke nó ở IdP và verify lại — xem nó vẫn pass.

---

# W. Git, GitHub & GitLab (14 bài)

Bài 163 (mô hình dữ liệu của Git) ở phần 2 là nền tảng cho nhóm này — nên đọc trước.

Đa số 🟢: demo chỉ cần một repo thử nghiệm, hỏng thì xóa đi làm lại.

**263. Clone bằng HTTPS hay SSH: khác biệt thật sự** 🟢
Naive → gãy: chọn ngẫu nhiên, rồi mỗi lần push phải nhập mật khẩu, hoặc gặp lỗi permission không hiểu.
Đánh đổi: HTTPS đi qua mọi firewall (cổng 443 luôn mở), dễ bắt đầu, nhưng cần credential helper để không nhập lại — và GitHub đã bỏ mật khẩu tài khoản, phải dùng PAT → SSH không phải nhập gì sau khi cài key, phù hợp máy cá nhân, đổi lại cổng 22 có thể bị chặn ở mạng công ty (có thể dùng SSH qua 443) và phải quản lý key. Với CI thì cả hai đều không phù hợp — dùng deploy key hoặc token có phạm vi hẹp.
Demo: clone cùng một repo bằng cả hai cách, xem `git remote -v` và thử push.

**264. PAT, deploy key, SSH key, GitHub App: cái nào cho việc gì** 🔴
Naive → gãy: dùng PAT cá nhân với quyền đầy đủ cho CI. Người đó nghỉ việc là pipeline chết; token rò rỉ là mất toàn bộ repo của cá nhân đó.
Đánh đổi: PAT tiện nhưng gắn với một người và thường quá quyền → deploy key gắn với một repo cụ thể, quyền hẹp, không gắn với người — đúng cho CI đọc một repo → GitHub App/service account cho quyền chi tiết và audit tốt, đổi lại setup phức tạp hơn → fine-grained PAT là dung hòa hiện đại nếu có sẵn.
Demo: tạo deploy key chỉ đọc cho một repo, thử push và xem nó bị từ chối.

**265. Branching strategy: Git Flow, GitHub Flow, trunk-based** 🟡
Naive → gãy: copy Git Flow từ bài viết 2010 cho một team 3 người deploy mỗi ngày. Năm loại nhánh, merge phức tạp, và phần lớn quy trình không phục vụ gì.
Đánh đổi: Git Flow hợp cho phần mềm có version phát hành (desktop app, thư viện) nhưng nặng cho web deploy liên tục → GitHub Flow (một nhánh chính, feature branch ngắn) đơn giản và đủ cho hầu hết web app → trunk-based với feature flag cho tốc độ cao nhất và ít conflict nhất, đổi lại đòi hỏi test tự động tốt và kỷ luật cao.
Demo: nhìn lại lịch sử một dự án thật, đếm số lần thật sự cần hotfix branch.

**266. Merge, rebase, squash: chọn theo mục đích lịch sử** 🟢
Naive → gãy: rebase nhánh đã push và người khác đã pull. Lịch sử của họ và của bạn khác nhau, và lần merge sau tạo mớ hỗn độn.
Đánh đổi: merge giữ lịch sử thật, an toàn tuyệt đối, đổi lại đồ thị rối với nhiều nhánh → rebase cho lịch sử tuyến tính dễ đọc và dễ `bisect`, đổi lại viết lại hash nên **không rebase nhánh chia sẻ** → squash cho mỗi PR một commit sạch, tốt cho lịch sử tổng thể, đổi lại mất chi tiết quá trình và làm cherry-pick khó hơn.
Demo: dựng ba nhánh giống nhau, merge/rebase/squash mỗi cái, so sánh `git log --graph`.

**267. Commit: viết gì trong message và chia commit thế nào** 🟢
Naive → gãy: `git commit -m "fix"` × 50. Sáu tháng sau cần biết vì sao một dòng code tồn tại, `git blame` chỉ ra "fix".
Đánh đổi: commit nhỏ theo ý nghĩa cho `bisect` và review hiệu quả, đổi lại tốn kỷ luật khi đang tập trung code → conventional commits cho phép sinh changelog tự động, đổi lại thêm ràng buộc hình thức → điều quan trọng nhất mà ít người làm: **message nên nói *tại sao*, không phải *cái gì*** — cái gì đã có trong diff.
Demo: chạy `git log --oneline` trên dự án của bạn, đếm bao nhiêu commit message giúp bạn hiểu được điều gì.

**268. `.gitignore` và secret đã lỡ commit** 🔴
Naive → gãy: thêm `.env` vào `.gitignore` sau khi đã commit — file vẫn được theo dõi và vẫn nằm trong history.
Đánh đổi: xem bài 130. Điểm riêng của bài này là **quy trình xử lý**: rotate secret ngay (bắt buộc, làm đầu tiên) → `git rm --cached` để ngừng theo dõi → cân nhắc rewrite history bằng `git filter-repo` (phá mọi clone, và fork/cache của nền tảng có thể vẫn giữ) → cài `gitleaks` ở pre-commit để không tái diễn.
Demo: commit một file secret vào repo thử, thử xóa và tìm lại bằng `git log --all --full-history`.

**269. Protected branch, CODEOWNERS, required review** 🟡
Naive → gãy: ai cũng push thẳng vào `main`. Một lần push sai làm hỏng production, và không có bản ghi ai duyệt gì.
Đánh đổi: bắt buộc review tăng chất lượng và chia sẻ hiểu biết, đổi lại chậm hơn và với team 2 người có thể thành hình thức → CODEOWNERS đảm bảo người đúng chuyên môn xem code của mình, đổi lại tạo điểm nghẽn nếu người đó bận → required status check chặn merge khi CI đỏ, gần như không có nhược điểm.
Demo: bật protected branch trên một repo thử, thử push thẳng và xem nó bị từ chối.

**270. Phân quyền trong GitHub và GitLab: mô hình khác nhau** 🟡
Naive → gãy: cho cả team quyền Maintainer/Admin cho tiện. Ai cũng xóa được branch, đổi được setting, và thấy được secret.
Đánh đổi: GitHub dùng role trên repo/org (Read, Triage, Write, Maintain, Admin) và team lồng nhau → GitLab dùng cấp bậc trên group và kế thừa xuống project (Guest, Reporter, Developer, Maintainer, Owner) — mô hình group của GitLab mạnh hơn cho tổ chức nhiều dự án, đổi lại dễ cấp quyền rộng hơn ý định qua kế thừa. Nguyên tắc chung: quyền tối thiểu, và review định kỳ ai có quyền gì.
Demo: tạo một group lồng nhau trong GitLab, cấp quyền ở cấp trên và kiểm tra người dùng thấy được gì ở dưới.

**271. Secret và biến trong CI: chỗ nó rò rỉ** 🔴
Naive → gãy: `echo $API_KEY` để debug pipeline. Giá trị hiện trong log, và log của repo public thì ai cũng đọc được.
Đánh đổi: masked variable che giá trị trong log nhưng chỉ khi khớp chính xác (biến đổi một chút là lộ) → protected variable chỉ có ở nhánh được bảo vệ, ngăn PR từ fork đọc secret — đây là lỗ hổng phổ biến và nghiêm trọng → environment với required approval cho secret production, đổi lại thêm bước thủ công.
Demo: in một biến đã mask theo nhiều cách (base64, tách chuỗi), xem cách nào lọt qua.

**272. Monorepo hay nhiều repo** 🟡
Naive → gãy: tách repo cho mọi service từ đầu. Một thay đổi API phải mở 3 PR ở 3 repo, và không có cách nào đảm bảo chúng vào cùng lúc.
Đánh đổi: monorepo cho thay đổi nguyên tử xuyên service, chia sẻ code dễ, một chỗ để tìm — đổi lại CI phải biết chỉ chạy phần thay đổi (nếu không thì mọi commit chạy toàn bộ), repo lớn dần, và phân quyền theo thư mục khó hơn → nhiều repo cho biên giới rõ và CI đơn giản, đổi lại phối hợp thay đổi xuyên repo là công việc thật.
Demo: đo thời gian CI của monorepo có và không có tối ưu chạy theo thay đổi.

**273. Submodule và subtree: hai cách chia sẻ code và bẫy của chúng** 🟡
Naive → gãy: thêm submodule rồi clone bình thường — thư mục rỗng, vì submodule cần `--recursive`. Sau đó team liên tục quên cập nhật submodule pointer.
Đánh đổi: submodule giữ repo con độc lập và không phình repo cha, đổi lại quy trình phức tạp và rất nhiều người dùng sai → subtree gộp code vào repo cha nên clone bình thường là đủ, đổi lại lịch sử lẫn vào nhau và đẩy ngược thay đổi thì khó → package registry riêng (npm private, GitLab package) thường là câu trả lời tốt hơn cả hai.
Demo: thêm một submodule, clone lại không có `--recursive`, xem chuyện gì xảy ra.

**274. File lớn trong Git và Git LFS** 🟡
Naive → gãy: commit file thiết kế 200MB, sau đó xóa. Repo vẫn nặng 200MB vĩnh viễn vì Git lưu mọi phiên bản; clone mất 10 phút cho mọi người mãi về sau.
Đánh đổi: Git LFS lưu con trỏ trong repo và file thật ở nơi khác — repo nhẹ, đổi lại cần cài LFS ở mọi máy, và nhiều nền tảng tính phí băng thông LFS → không đưa file lớn vào Git (dùng object storage và tham chiếu bằng URL) là đơn giản nhất → đã lỡ commit thì phải rewrite history, không có cách nhẹ nhàng.
Demo: commit một file 100MB, xóa nó, rồi kiểm tra `.git` còn nặng bao nhiêu.

**275. Cứu tình huống: reflog, cherry-pick, revert, reset** 🟢
Naive → gãy: `git reset --hard` nhầm, mất commit của cả buổi sáng, tưởng mất vĩnh viễn.
Đánh đổi: `git reflog` giữ mọi vị trí HEAD đã đi qua trong 90 ngày — gần như mọi thứ "đã mất" đều lấy lại được, và đây là kiến thức cứu người → `revert` tạo commit mới đảo ngược, an toàn cho nhánh chia sẻ → `reset` viết lại lịch sử, chỉ dùng cho nhánh riêng. Phân biệt `--soft`, `--mixed`, `--hard` là chỗ hay nhầm nhất.
Demo: `reset --hard` xóa 3 commit rồi khôi phục bằng reflog.

**276. `git bisect`: tìm commit gây bug trong 10 bước thay vì 1000** 🟢
Naive → gãy: bug xuất hiện "gần đây", đọc thủ công 200 commit gần nhất để đoán.
Đánh đổi: bisect chia đôi lịch sử nên 1000 commit chỉ cần 10 lần kiểm tra, và tự động hóa được bằng script → đổi lại đòi hỏi mỗi commit đều build và chạy được (đây là lý do commit nhỏ và không commit code hỏng đáng giá), và cần cách kiểm tra bug xác định → nếu lịch sử là những commit squash lớn thì bisect chỉ ra một PR khổng lồ, không giúp được nhiều.
Demo: tạo repo với 100 commit, cài bug ở commit 37, tìm nó bằng `git bisect run`.

---

# X. Web application: những mảng còn thiếu (16 bài)

Trả lời câu hỏi "còn gì nữa không" của bạn. Đây là những mảng mọi web app thật đều cần nhưng gần như không có trong tutorial — vì tutorial dừng ở CRUD.

Nhiều bài trong nhóm này **có đặc thù Việt Nam**, nghĩa là bài tiếng Anh không thay thế được. Đó là lợi thế cạnh tranh rõ ràng nhất bạn có.

**277. Đa ngôn ngữ: khó hơn thay chuỗi văn bản** 🟡
Naive → gãy: tách chuỗi ra file JSON và coi như xong. Rồi gặp số nhiều ("1 sản phẩm" / "2 sản phẩm" — tiếng Việt dễ, nhiều ngôn ngữ khác có 6 dạng), thứ tự từ trong câu ghép, định dạng ngày và số khác nhau, và văn bản dài ra 40% làm vỡ layout.
Đánh đổi: nối chuỗi (`"Có " + n + " sản phẩm"`) dịch được sang ngôn ngữ tương tự nhưng vỡ với ngôn ngữ khác trật tự → ICU message format xử lý đúng mọi trường hợp, đổi lại cú pháp phải học → dịch bằng AI nhanh và rẻ nhưng cần người bản ngữ rà thuật ngữ chuyên ngành.
Demo: dịch giao diện sang một ngôn ngữ có từ dài (tiếng Đức), tìm chỗ vỡ layout.

**278. Hiển thị thời gian cho người dùng: lưu UTC rồi sao nữa** 🟡
Naive → gãy: lưu UTC đúng chuẩn (bài 64) rồi hiển thị luôn giờ UTC. User Việt Nam thấy đơn hàng đặt lúc "2 giờ sáng" trong khi họ đặt lúc 9 giờ.
Đánh đổi: chuyển sang timezone của browser thì tự động đúng cho hầu hết trường hợp, đổi lại SSR không biết timezone của user (gây hydration mismatch — bài 49) → cho user chọn timezone trong cài đặt thì chính xác cho người hay đi lại, đổi lại thêm cài đặt → hiển thị thời gian tương đối ("2 giờ trước") né được vấn đề nhưng mất thông tin chính xác và cần cập nhật liên tục.
Demo: đổi timezone hệ thống rồi tải lại trang, xem thời gian hiển thị và cảnh báo hydration.

**279. Gửi email vào inbox chứ không vào spam: SPF, DKIM, DMARC** 🔴
Naive → gãy: gửi email từ server bằng SMTP thô. Toàn bộ vào spam, và không hiểu vì sao — không có lỗi nào cả.
Đánh đổi: SPF khai server nào được gửi thay domain bạn; DKIM ký để chứng minh không bị sửa; DMARC nói cho người nhận biết làm gì khi hai cái kia thất bại. Cần cả ba → tự chạy mail server thì kiểm soát hoàn toàn nhưng IP mới không có danh tiếng và mất hàng tháng để được tin cậy → dịch vụ gửi email (SES, Resend, Postmark) có sẵn danh tiếng và báo cáo bounce, đổi lại chi phí và phụ thuộc.
Demo: gửi thử tới Gmail, xem "Show original" để đọc kết quả SPF/DKIM/DMARC.

**280. Xuất hóa đơn, báo cáo PDF từ dữ liệu** 🟡
Naive → gãy: dùng thư viện PDF vẽ từng dòng bằng tọa độ. Đổi layout là viết lại; và tiếng Việt có dấu hiện thành ô vuông vì font mặc định không có glyph.
Đánh đổi: HTML → PDF (Puppeteer) cho phép dùng CSS quen thuộc và dễ sửa, đổi lại nặng (mỗi lần render là một browser) và tốn RAM → thư viện vẽ trực tiếp nhẹ và nhanh nhưng layout phức tạp thì cực khổ → template engine chuyên dụng dung hòa. Riêng tiếng Việt: **luôn phải nhúng font có dấu**, đây là lỗi kinh điển.
Demo: sinh PDF có chữ tiếng Việt bằng font mặc định, xem nó hỏng thế nào.

**281. Nhập liệu hàng loạt từ file người dùng cung cấp** 🟡
Naive → gãy: nhận CSV và tin dữ liệu sạch. Thực tế: encoding không phải UTF-8 (Excel Việt Nam hay xuất ra ANSI, tiếng Việt thành ký tự lạ), dấu phân cách là chấm phẩy, số điện thoại mất số 0 đầu vì Excel coi là số, ngày tháng lẫn lộn định dạng.
Đánh đổi: validate nghiêm và từ chối file sai thì dữ liệu sạch nhưng user bực và bỏ cuộc → tự sửa lỗi phổ biến thì thân thiện nhưng có thể sửa sai âm thầm → **xem trước và cho user xác nhận trước khi ghi** là mẫu tốt nhất, đổi lại thêm một bước và cần lưu trạng thái tạm.
Demo: xuất một file Excel tiếng Việt từ Excel bản Việt, import và xem có bao nhiêu vấn đề.

**282. Số điện thoại và địa chỉ Việt Nam** 🟢
Naive → gãy: validate số điện thoại bằng regex tự nghĩ. Rồi gặp `+84`, `84`, `0`, số có dấu chấm, đầu số mới, và số cố định có mã vùng.
Đánh đổi: chuẩn hóa về E.164 (`+84...`) khi lưu là đúng nhất cho gửi SMS và so trùng, đổi lại phải chuyển đổi khi hiển thị → lưu nguyên bản người dùng nhập thì không mất thông tin nhưng không so sánh được → riêng địa chỉ: đơn vị hành chính Việt Nam đã thay đổi (sáp nhập tỉnh, bỏ cấp huyện) nên dữ liệu tỉnh/huyện/xã cũ không còn đúng — cần nguồn cập nhật và kế hoạch cho địa chỉ lịch sử.
Demo: thu thập 20 cách người Việt viết số điện thoại và thử chuẩn hóa tất cả về một dạng.

**283. Tích hợp thanh toán Việt Nam: VNPay, Momo, ZaloPay** 🔴
Naive → gãy: làm theo tài liệu tích hợp, thấy chạy được ở sandbox nên đóng. Chưa xử lý IPN trùng, chưa đối soát, chưa xử lý trường hợp user đóng trình duyệt sau khi trả tiền nhưng trước khi redirect về.
Đánh đổi: xem bài 137, 138, 146 cho nguyên lý. Đặc thù ở đây: mỗi cổng Việt Nam có cách ký chữ ký khác nhau và tài liệu chất lượng không đồng đều — nên **luôn tin IPN/webhook, không tin kết quả trên URL redirect** (URL sửa được). Và bắt buộc có đối soát vì IPN có mất.
Demo: hoàn tất thanh toán sandbox rồi đóng tab trước khi redirect, xem hệ thống có biết đơn đã trả tiền không.

**284. Multi-tenancy: cô lập dữ liệu giữa khách hàng** 🔴
Naive → gãy: thêm cột `tenant_id` và nhớ lọc theo nó ở mọi query. Một query quên lọc là khách hàng A thấy dữ liệu khách hàng B — sự cố nghiêm trọng nhất một SaaS có thể gặp.
Đánh đổi: cột `tenant_id` + lọc ở tầng app thì rẻ và đơn giản nhưng phụ thuộc kỷ luật con người → row-level security ở DB thì không thể quên, đổi lại khó test và khó debug → schema riêng cho mỗi tenant cô lập tốt hơn nhưng migration nhân lên theo số tenant → database riêng cô lập tuyệt đối nhưng chi phí và vận hành nặng nhất. Bất kể chọn gì, **phải có test tự động kiểm tra rò rỉ chéo**.
Demo: viết test tạo dữ liệu cho hai tenant và gọi mọi endpoint bằng token của tenant A tìm dữ liệu của B.

**285. Xóa tài khoản và dữ liệu người dùng** 🔴
Naive → gãy: nút "xóa tài khoản" chỉ set `deleted_at`. Người dùng yêu cầu xóa thật theo quy định thì không đáp ứng được; và dữ liệu của họ vẫn nằm trong backup, log, cache, dịch vụ analytics.
Đánh đổi: xóa thật thì tuân thủ nhưng vỡ khóa ngoại và mất dữ liệu nghiệp vụ cần giữ (hóa đơn có nghĩa vụ lưu trữ) → ẩn danh hóa (giữ bản ghi, xóa thông tin định danh) dung hòa tốt nhất cho hầu hết trường hợp → phải liệt kê **mọi nơi** dữ liệu tồn tại, không chỉ bảng chính. Backup là vấn đề riêng chưa ai có lời giải đẹp.
Demo: liệt kê mọi nơi dữ liệu một user tồn tại trong hệ thống bạn — thường nhiều hơn dự đoán.

**286. Cài đặt thông báo: cho user kiểm soát** 🟡
Naive → gãy: gửi mọi thông báo qua mọi kênh. User tắt hết hoặc đánh dấu spam, và sau đó không nhận được cả thông báo quan trọng.
Đánh đổi: cài đặt chi tiết theo từng loại và từng kênh cho user kiểm soát tốt nhưng giao diện phức tạp và ít người vào chỉnh → mặc định hợp lý (chỉ thông báo quan trọng, gộp thông báo tương tự) thường hiệu quả hơn nhiều cài đặt → phân biệt thông báo giao dịch (bắt buộc, không cho tắt) và tiếp thị (phải cho tắt, có yêu cầu pháp lý ở nhiều nơi) là ranh giới cần rõ ràng.
Demo: đếm số thông báo hệ thống bạn gửi cho một user tích cực trong một tuần.

**287. Admin panel: tự viết, dùng công cụ, hay truy cập DB trực tiếp** 🟡
Naive → gãy: nhân viên vận hành sửa dữ liệu trực tiếp bằng DBeaver. Không audit, không validate, và một câu UPDATE thiếu WHERE là mất dữ liệu.
Đánh đổi: tự viết admin cho kiểm soát và audit đầy đủ, đổi lại tốn nhiều thời gian phát triển cho tính năng không phải sản phẩm chính → công cụ có sẵn (Retool, Directus, admin của framework) nhanh và đủ dùng, đổi lại tùy biến giới hạn và thêm phụ thuộc → truy cập DB trực tiếp chỉ nên dành cho dev với quyền hạn chế và bắt buộc có log.
Demo: đếm số thao tác vận hành hàng ngày cần làm và ước lượng thời gian tự viết cho từng cái.

**288. Trải nghiệm tìm kiếm: gõ sai chính tả, gợi ý, kết quả rỗng** 🟡
Naive → gãy: tìm chính xác chuỗi. User gõ thiếu dấu, sai chính tả, hoặc dùng từ khác — nhận về "không có kết quả" dù sản phẩm có tồn tại.
Đánh đổi: fuzzy matching bắt được lỗi gõ nhưng tạo kết quả nhiễu nếu ngưỡng quá lỏng → từ đồng nghĩa (điện thoại/smartphone/dt) hiệu quả cho tiếng Việt nhưng phải xây thủ công → màn hình không có kết quả là cơ hội bị bỏ phí lớn nhất: gợi ý từ khóa gần đúng, sản phẩm phổ biến, hoặc bộ lọc nới lỏng — thay vì một dòng chữ trống.
Demo: thử 20 truy vấn có lỗi chính tả trên site của bạn, đếm bao nhiêu ra kết quả rỗng.

**289. Tung tính năng dần: feature flag, A/B test, rollout theo phần trăm** 🟡
Naive → gãy: bật tính năng mới cho 100% user cùng lúc. Có bug thì toàn bộ người dùng gặp, và rollback thì phải deploy lại.
Đánh đổi: xem bài 124 cho nợ kỹ thuật của flag. Điểm riêng: rollout theo phần trăm cần **phân nhóm ổn định** (cùng một user luôn thuộc cùng nhóm — dùng hash của userId, không dùng random) nếu không thì user thấy giao diện nhảy qua lại → A/B test cần đủ mẫu và kỷ luật thống kê, nếu không thì kết luận sai còn tệ hơn không đo.
Demo: hiện thực rollout 10% bằng hash userId, kiểm tra một user luôn nhận cùng kết quả.

**290. Giới hạn sử dụng và hạn mức: cho user biết trước khi chặn** 🟡
Naive → gãy: user gọi API vượt hạn mức, nhận `429` không kèm thông tin gì. Không biết hạn mức bao nhiêu, còn lại bao nhiêu, khi nào reset.
Đánh đổi: trả header `RateLimit-*` cho client tự điều tiết là chuẩn và rẻ, gần như không có nhược điểm → cảnh báo trước khi chạm hạn mức (80%) giảm bất ngờ, đổi lại thêm logic thông báo → chặn cứng thì bảo vệ hệ thống nhưng phá luồng nghiệp vụ của khách hàng; cho vượt tạm rồi tính phí thì thân thiện nhưng cần theo dõi chặt.
Demo: gọi vượt hạn mức một API công khai (GitHub chẳng hạn), đọc header trả về và học cách họ làm.

**291. Onboarding trong sản phẩm: trạng thái rỗng và bước đầu tiên** 🟢
Naive → gãy: user đăng ký xong thấy dashboard trống trơn. Không biết làm gì tiếp, thoát ra và không quay lại.
Đánh đổi: dữ liệu mẫu cho user thấy ngay giá trị, đổi lại có thể gây nhầm lẫn với dữ liệu thật và phải dọn → checklist hướng dẫn rõ ràng nhưng thêm ma sát → tour giao diện thì nhiều người bấm bỏ qua ngay. Empty state được thiết kế tốt (giải thích + một hành động rõ ràng) thường hiệu quả hơn cả ba, và rẻ nhất.
Demo: đăng ký tài khoản mới trên chính sản phẩm của bạn và ghi lại cảm giác 60 giây đầu.

**292. Xử lý lỗi hướng tới người dùng: nói gì khi hệ thống hỏng** 🟡
Naive → gãy: hiện `Error: ECONNREFUSED 127.0.0.1:5432` cho người dùng cuối. Vừa vô nghĩa với họ, vừa tiết lộ cấu trúc nội bộ.
Đánh đổi: thông báo chung chung thì an toàn nhưng người dùng không biết nên làm gì và support không có thông tin → mã lỗi kèm thông báo thân thiện (hiện mã ngắn để người dùng đọc cho support, chi tiết chỉ trong log) là dung hòa tốt nhất → phân biệt lỗi user sửa được (nhập sai, hết hạn mức) với lỗi hệ thống là ranh giới quan trọng: cái đầu cần hướng dẫn cụ thể, cái sau cần trấn an và cách liên hệ.
Demo: đi qua mọi luồng lỗi trong app và tự hỏi "nếu là người dùng, tôi biết phải làm gì tiếp không".

---

# Toàn bộ 292 đề tài: bản đồ nhóm

| Phần | Nhóm | Bài |
|---|---|---|
| 1 | A. Xác thực & phiên | 1-14 |
| 1 | B. Upload & media | 15-24 |
| 1 | C. Thiết kế API | 25-36 |
| 1 | D. FE dữ liệu & state | 37-46 |
| 1 | E. FE render & hiệu năng | 47-56 |
| 1 | F. Database | 57-72 |
| 1 | G. Transaction | 73-82 |
| 1 | H. Job & queue | 83-92 |
| 1 | I. Caching | 93-100 |
| 1 | J. Realtime | 101-106 |
| 1 | K. Hạ tầng & deploy | 107-118 |
| 1 | L. Quan sát & debug | 119-125 |
| 1 | M. Bảo mật | 126-133 |
| 2 | G+. Transaction & tiền | 134-148 |
| 2 | N. Tại sao ra đời | 149-163 |
| 2 | O. Quy trình & vận hành | 164-176 |
| 2 | P. Hash & mã hóa | 177-186 |
| 2 | Q. Giao diện mượt | 187-198 |
| 2 | R. SEO kỹ thuật | 199-208 |
| 3 | **S. Bug do dữ liệu nhiều** | **209-222** |
| 3 | **T. Bug do nhiều người đồng thời** | **223-234** |
| 3 | U. Mạng & kết nối | 235-252 |
| 3 | V. Identity & SSO | 253-262 |
| 3 | W. Git & nền tảng | 263-276 |
| 3 | X. Web app: mảng còn thiếu | 277-292 |

## Đề xuất cuối cùng về thứ tự

Sau ba file, mình vẫn giữ khuyến nghị cũ nhưng thêm một điều chỉnh:

**Bắt đầu bằng nhóm S và T, không phải Q.** Mình đã đổi ý so với lần trước, vì hai nhóm này có ba lợi thế mà nhóm khác không có: chúng đóng được thành series có tên; chúng dạy bạn kỹ năng dựng demo (seed dữ liệu lớn, bắn tải song song) mà mọi nhóm sau đều cần; và chúng chạm đúng nỗi đau của dev 1-5 năm — nhóm đối tượng bạn nhắm tới.

Làm xong S và T là bạn có 26 bài, một series nhận diện được, và bộ công cụ để viết mọi nhóm còn lại.

**Nhóm Q vẫn là lựa chọn thứ hai** (demo dễ nhất, ít người viết nhất), rồi F, B.

**Nhóm U (mạng) để sau cùng trong nhóm dễ.** Không phải vì khó viết, mà vì bạn tự nói chưa vững — và nhóm này người đọc phát hiện chỗ hiểu nửa vời rất nhanh. Học trước, viết sau.
