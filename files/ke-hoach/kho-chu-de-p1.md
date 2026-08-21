# Kho chủ đề content IT — 133 bài toán có đánh đổi

Mỗi đề tài dưới đây là một **bài toán ai cũng gặp, không có lời giải hoàn hảo**. Đó là lý do nó viết được thành content có giá trị: người đọc cần hiểu đánh đổi để tự chọn, không cần bạn phán quyết.

## Cách dùng file này

**Đọc theo cột "Demo".** Bạn chưa vận hành production nhiều, nên đây là cột quan trọng nhất — nó là việc bạn cần làm để bài viết có thứ mà bài tổng hợp trên mạng không có. Phần lớn demo dựng được trong 1-2 giờ trên máy local.

**Không viết theo thứ tự.** Chọn đề tài bạn dựng được demo trước. Một bài có số liệu thật hơn năm bài lý thuyết.

**Chuỗi đánh đổi trong file này là bản phác.** Nó cho bạn biết bài sẽ đi hướng nào, không phải nội dung viết sẵn. Khi viết thật, phải đọc nguồn gốc (MDN, OWASP, docs chính thức, RFC) để kiểm chứng lại chi tiết. Kiến thức của mình tới khoảng giữa 2026 và có thể sai ở chi tiết cập nhật gần đây.

**Ký hiệu độ khó:**
- 🟢 Dựng demo dễ, rủi ro viết sai thấp — bắt đầu từ đây
- 🟡 Cần dựng môi trường phức tạp hơn hoặc đọc kỹ trước khi viết
- 🔴 Rủi ro cao nếu viết sai (bảo mật, dữ liệu, tiền) — chỉ viết khi đã kiểm chứng chắc

---

# A. Xác thực & phiên đăng nhập (14 bài)

Nhóm hút người đọc nhất, và cũng là nhóm nhiều bài viết nửa vời nhất. 🔴 gần hết nhóm này.

**1. Lưu access token ở đâu: localStorage, cookie, hay memory** 🔴
Naive → gãy: `localStorage` đơn giản nhưng JS đọc được, XSS là mất token mang ra ngoài dùng.
Đánh đổi: httpOnly cookie chặn XSS đọc token nhưng mở CSRF → `SameSite` chặn CSRF nhưng phá luồng cross-site và link từ email → `SameSite=None` cho cross-site thì CSRF quay lại, phải thêm CSRF token → memory + refresh cookie thì mất token khi F5. Kết luận thật: không lựa chọn nào chặn được XSS, chỉ giới hạn thiệt hại.
Demo: dựng FE và BE trên hai domain khác nhau, thử từng cấu hình `SameSite` xem cookie có được gửi.

**2. Refresh token rotation và race condition khi nhiều request cùng gặp 401** 🔴
Naive → gãy: mỗi request gặp 401 tự gọi refresh. Năm request song song gọi refresh năm lần, rotation làm bốn cái sau invalid, user bị đăng xuất ngẫu nhiên.
Đánh đổi: hàng đợi request chờ một lần refresh (phức tạp hơn nhưng đúng) vs cho phép reuse token trong cửa sổ ngắn (đơn giản hơn nhưng nới lỏng bảo mật) vs không rotation (đơn giản nhất, refresh token bị lấy là dùng được lâu).
Demo: mở 5 tab cùng lúc sau khi token hết hạn, log lại số lần gọi refresh.

**3. Logout thật sự nghĩa là gì — và tại sao JWT không thể revoke** 🔴
Naive → gãy: xóa token ở client và gọi đó là logout. Token vẫn hợp lệ tới lúc hết hạn; ai đã copy được nó vẫn dùng được.
Đánh đổi: blacklist trong Redis (mất tính stateless, mỗi request phải query) vs token sống rất ngắn (giảm cửa sổ, tăng số lần refresh) vs quay về session ID (revoke tức thì, đổi lại phải query DB mỗi request).
Demo: copy JWT ra Postman, logout trên web, gọi API bằng token cũ.

**4. JWT hay session ID trong DB** 🟡
Naive → gãy: chọn JWT vì "hiện đại, stateless, scale tốt", rồi thêm blacklist, thêm quyền động — thành session ID nhưng nặng hơn.
Đánh đổi: JWT không cần query mỗi request nhưng không revoke được và payload phình theo quyền → session ID revoke tức thì và nhỏ gọn nhưng thêm một lần đọc Redis/DB mỗi request. Sự thật hay bị bỏ qua: một lần đọc Redis mất dưới 1ms, "stateless để scale" thường không phải lý do thật.
Demo: đo latency thực tế của một lần lookup Redis so với verify JWT.

**5. Access token nên sống bao lâu** 🟡
Naive → gãy: đặt 7 ngày cho tiện, không ai phải đăng nhập lại. Token bị lộ là kẻ tấn công có 7 ngày.
Đánh đổi: ngắn (5-15 phút) thì cửa sổ tấn công nhỏ nhưng phụ thuộc hoàn toàn vào luồng refresh chạy đúng, và mọi bug refresh thành bug đăng xuất → dài thì mượt nhưng revoke gần như vô nghĩa.
Demo: thử đặt 1 phút và xem app có chỗ nào vỡ.

**6. "Ghi nhớ đăng nhập" cài đặt thế nào cho đúng** 🟡
Naive → gãy: đặt cookie expiry 1 năm. Máy công cộng thành lỗ hổng, và không có cách nào biết thiết bị nào đang giữ phiên.
Đánh đổi: refresh token dài hạn gắn với thiết bị (quản lý được, revoke được, đổi lại phải lưu bảng device) vs cookie persistent đơn giản (dễ làm, mù thông tin).
Demo: đăng nhập trên hai trình duyệt, thử revoke một cái mà không ảnh hưởng cái kia.

**7. OAuth: authorization code + PKCE và tại sao implicit flow bị khai tử** 🔴
Naive → gãy: SPA dùng implicit flow vì "không có backend nên không giữ được secret". Token đi qua URL fragment, lọt vào history, referrer, log.
Đánh đổi: code + PKCE an toàn hơn nhưng thêm một round trip và phải lưu code_verifier → BFF (backend for frontend) an toàn nhất vì token không bao giờ tới browser, đổi lại phải nuôi thêm một tầng server.
Demo: đọc URL sau khi redirect ở cả hai flow, xem cái gì nằm trong đó.

**8. Quản lý phiên trên nhiều thiết bị** 🟡
Naive → gãy: không quản lý gì. User đổi mật khẩu vì nghi bị hack, nhưng phiên trên máy kẻ tấn công vẫn sống.
Đánh đổi: bảng session có device info (làm được tính năng "đăng xuất mọi thiết bị", đổi lại thêm state và phải dọn bản ghi cũ) vs token version trong user record (nhẹ hơn, chỉ revoke được tất cả cùng lúc).
Demo: đổi mật khẩu và kiểm tra phiên cũ còn hoạt động không.

**9. RBAC hay ABAC: phân quyền khi role không đủ diễn tả** 🟡
Naive → gãy: enum role `admin | user`. Ba tháng sau cần "trưởng nhóm chỉ xem được đơn của nhóm mình", enum không diễn tả nổi, sinh ra `if` rải khắp code.
Đánh đổi: RBAC đơn giản dễ hiểu dễ cache nhưng bùng nổ số role khi có ngữ cảnh → ABAC/policy linh hoạt nhưng khó debug, khó trả lời "tại sao user này bị chặn", và khó cache.
Demo: viết ra 5 yêu cầu phân quyền thực tế và thử mô hình hóa bằng cả hai cách.

**10. Kiểm tra quyền ở đâu: FE, gateway, service, hay tận DB** 🔴
Naive → gãy: ẩn nút trên FE là xong. API vẫn gọi được trực tiếp.
Đánh đổi: check ở gateway thì tập trung nhưng gateway không biết ngữ cảnh dữ liệu → check ở service thì đúng ngữ cảnh nhưng dễ sót một endpoint → row-level security ở DB thì không thể sót nhưng khó test và khó nhìn thấy. Nguyên tắc: FE chỉ để UX, không bao giờ là lớp bảo vệ.
Demo: gọi thẳng API bằng curl với token của user thường lên endpoint admin.

**11. Hash mật khẩu: bcrypt, argon2, và cost factor đặt bao nhiêu** 🔴
Naive → gãy: dùng SHA-256 vì "đã hash rồi". SHA-256 nhanh, GPU thử hàng tỷ lần mỗi giây.
Đánh đổi: bcrypt phổ biến, thư viện ổn định, nhưng giới hạn 72 byte đầu vào → argon2 chống GPU tốt hơn nhưng tốn RAM, phải tune ba tham số. Cost factor cao thì an toàn hơn nhưng mỗi lần đăng nhập tốn CPU thật, và trở thành cửa cho DoS.
Demo: đo thời gian hash ở cost 10, 12, 14 trên máy bạn.

**12. Chống brute force login mà không tiết lộ tài khoản nào tồn tại** 🔴
Naive → gãy: báo "email không tồn tại" cho thân thiện. Kẻ tấn công dò được danh sách email có thật.
Đánh đổi: thông báo chung chung thì an toàn nhưng UX tệ hơn → rate limit theo IP dễ vượt bằng proxy, theo account thì mở ra tấn công khóa tài khoản người khác → captcha hiệu quả nhưng thêm ma sát. Thời gian phản hồi cũng rò rỉ thông tin nếu không xử lý.
Demo: đo thời gian phản hồi khi email tồn tại và không tồn tại.

**13. Token xác thực email và đặt lại mật khẩu: những chỗ hay sai** 🔴
Naive → gãy: token là UUID lưu trong DB, không hết hạn, dùng lại được nhiều lần.
Đánh đổi: hết hạn ngắn thì an toàn nhưng user nhận email muộn sẽ thất vọng → dùng một lần thì đúng nhưng phải xử lý trường hợp user bấm hai lần vì mạng chậm → lưu hash của token thay vì token gốc thì DB rò rỉ cũng vô hại, đổi lại không tra cứu trực tiếp được.
Demo: dùng lại link reset lần thứ hai, xem có vào được không.

**14. Cho admin đăng nhập hộ user (impersonation) mà không tạo lỗ hổng** 🔴
Naive → gãy: tạo token của user đó cho admin. Không còn dấu vết ai làm gì, audit log ghi tên user thật.
Đánh đổi: token có cả hai identity (truy vết được, đổi lại mọi chỗ check quyền phải hiểu khái niệm này) vs phiên riêng đánh dấu impersonation (rõ ràng hơn, phải sửa nhiều nơi). Quyết định khó: admin đang mạo danh có được thực hiện hành động ghi không?
Demo: kiểm tra audit log sau một phiên impersonation, xem ghi tên ai.

---

# B. Upload file & xử lý media (10 bài)

Đây là nhóm bạn đã nhắc tới — dễ dựng demo, ai cũng gặp, ít bài viết đủ sâu. 🟢 nhiều.

**15. File nhỏ gửi trực tiếp, file lớn phải chia nhỏ: ngưỡng ở đâu** 🟢
Naive → gãy: một endpoint cho mọi file. File 500MB làm memory server phình, hoặc chết ở giới hạn proxy trước khi tới app.
Đánh đổi: gửi trực tiếp đơn giản nhưng giới hạn bởi timeout, body size limit, và mất hết khi mạng đứt giữa đường → chunked phức tạp hơn nhiều (quản lý session upload, ghép file, dọn chunk mồ côi) nhưng resume được. Ngưỡng thực tế phụ thuộc giới hạn proxy, không phải con số đẹp.
Demo: upload file 100MB, 500MB, 2GB qua Nginx mặc định, ghi lại lỗi chính xác ở từng mốc.

**16. Upload qua backend hay presigned URL lên object storage** 🟢
Naive → gãy: mọi file đi qua BE. Băng thông và CPU của app server phục vụ việc chuyển byte, scale theo lượng upload chứ không theo logic.
Đánh đổi: qua BE thì validate được nội dung trước khi lưu và kiểm soát hoàn toàn, đổi lại tốn tài nguyên và giới hạn kích thước → presigned URL rẻ và nhanh nhưng file vào storage trước khi bạn kiểm tra được nó là gì, phải xử lý hậu kiểm và bản ghi mồ côi khi client upload xong mà không gọi confirm.
Demo: đo CPU/RAM app server khi upload 1GB qua BE so với presigned.

**17. Validate loại file: đuôi file, Content-Type, hay magic byte** 🔴
Naive → gãy: kiểm tra đuôi `.jpg`. Đổi tên `shell.php` thành `shell.jpg` là qua.
Đánh đổi: đuôi file rẻ nhất và vô dụng nhất → Content-Type do client gửi nên cũng giả được → magic byte đáng tin hơn nhưng file có thể vừa là ảnh hợp lệ vừa chứa payload (polyglot) → parse lại và re-encode ảnh là chắc nhất, đổi lại tốn CPU và mất metadata gốc.
Demo: tự tạo file polyglot đơn giản và thử vượt từng lớp kiểm tra.

**18. Resize ảnh lúc upload hay lúc request** 🟢
Naive → gãy: tạo sẵn 5 kích thước lúc upload. Ba tháng sau thiết kế đổi, cần kích thước thứ 6 cho 200 nghìn ảnh cũ.
Đánh đổi: pre-generate thì request nhanh và tải ổn định nhưng cứng nhắc và tốn dung lượng cho biến thể không ai dùng → on-the-fly linh hoạt tuyệt đối nhưng lần request đầu chậm, và là cửa DoS nếu ai đó gọi hàng nghìn kích thước lạ (phải whitelist hoặc ký tham số).
Demo: đo thời gian resize on-the-fly lần đầu và lần sau khi đã cache.

**19. Upload resume được: cần lưu những state gì** 🟡
Naive → gãy: mất mạng ở 90% thì upload lại từ đầu.
Đánh đổi: tự làm chunked + upload session cho bạn toàn quyền nhưng phải tự xử lý hết edge case (chunk trùng, chunk thiếu, session hết hạn, dọn rác) → dùng multipart upload của object storage thì storage lo phần khó, đổi lại phụ thuộc nhà cung cấp và phải hiểu cơ chế abort để không bị tính phí phần dở dang.
Demo: upload file lớn, ngắt mạng giữa đường, thử resume.

**20. Lưu file ở đâu: blob trong DB, filesystem, hay object storage** 🟢
Naive → gãy: lưu vào filesystem của server. Scale lên 2 instance là user upload ở máy A, request rơi vào máy B, ảnh mất.
Đánh đổi: DB blob thì transaction nhất quán và backup cùng dữ liệu, đổi lại DB phình, backup nặng, và tốn kết nối DB để phục vụ byte → filesystem nhanh và đơn giản nhưng không scale ngang và mất khi container restart → object storage giải quyết cả hai nhưng thêm phụ thuộc, thêm latency, và phải quản lý quyền truy cập riêng.
Demo: chạy 2 instance qua load balancer với file lưu local, upload rồi refresh nhiều lần.

**21. Serve file private: proxy qua backend hay signed URL có hạn** 🔴
Naive → gãy: để bucket public rồi dùng URL khó đoán. Không đoán được không có nghĩa là an toàn — URL rò rỉ qua referrer, chat, log là vĩnh viễn.
Đánh đổi: proxy qua BE cho phép check quyền chính xác mỗi lần và revoke tức thì, đổi lại BE tốn băng thông và không dùng được CDN dễ dàng → signed URL rẻ và nhanh nhưng có hiệu lực trong khoảng thời gian đó bất kể quyền thay đổi, và ai có link đều dùng được.
Demo: tạo signed URL, gửi cho người khác, thử truy cập khi chưa hết hạn.

**22. Thanh tiến trình upload thật sự đang đo cái gì** 🟢
Naive → gãy: progress chạy tới 100% rồi treo. User nghĩ app lỗi.
Đánh đổi: progress của XHR chỉ đo byte đã đẩy khỏi client, chưa tính thời gian server xử lý (virus scan, resize, lưu storage). Hiển thị thật thì cần thêm trạng thái xử lý phía server (phức tạp hơn, cần polling hoặc SSE) → hoặc chấp nhận nói dối nhẹ bằng cách dừng ở 90% và đợi.
Demo: upload file kèm xử lý nặng ở server, quan sát khoảng trống sau 100%.

**23. Xóa file: soft delete và vấn đề file mồ côi** 🟡
Naive → gãy: xóa bản ghi DB, quên xóa file. Sáu tháng sau storage đầy file không ai tham chiếu.
Đánh đổi: xóa ngay khi xóa bản ghi thì sạch nhưng không undo được và nếu transaction rollback thì mất file của bản ghi vẫn tồn tại → soft delete + job dọn định kỳ an toàn hơn nhưng cần đối soát hai chiều, và luôn có cửa sổ không nhất quán.
Demo: viết script đếm file trong storage không có bản ghi tương ứng.

**24. Export Excel/CSV vài trăm nghìn dòng mà không sập server** 🟢
Naive → gãy: query hết ra array, build workbook trong memory, trả về. 200 nghìn dòng làm process hết RAM.
Đánh đổi: stream từng chunk giữ memory phẳng nhưng không quay lại sửa được phần đã ghi và khó làm định dạng phức tạp → sinh file nền rồi gửi link thì chịu được mọi kích thước, đổi lại thêm queue, thêm storage, UX là chờ đợi → giới hạn số dòng cho phép export là giải pháp rẻ nhất mà ít ai dám chọn.
Demo: export 10k, 100k, 500k dòng và đo RSS của process.

---

# C. Thiết kế API (12 bài)

**25. REST đúng chuẩn hay endpoint theo hành động** 🟢
Naive → gãy: cố ép mọi thứ vào CRUD. Nghiệp vụ "duyệt đơn kèm gửi thông báo và trừ tồn kho" thành `PATCH /orders/1` với payload khó hiểu.
Đánh đổi: REST thuần nhất quán và dễ đoán nhưng nhiều nghiệp vụ không phải CRUD → endpoint theo hành động (`POST /orders/1/approve`) diễn tả đúng ý định và dễ phân quyền, đổi lại số endpoint tăng và mất tính đồng nhất.
Demo: lấy 5 nghiệp vụ thật trong dự án và thử mô hình cả hai cách.

**26. Phân trang: offset hay cursor** 🟢
Naive → gãy: `LIMIT 20 OFFSET 10000`. DB vẫn phải đi qua 10 nghìn dòng đầu; và nếu có bản ghi mới chèn vào, user thấy trùng hoặc mất item khi sang trang.
Đánh đổi: offset cho phép nhảy tới trang bất kỳ và hiện tổng số trang (UX quen thuộc) nhưng chậm dần và không nhất quán khi dữ liệu thay đổi → cursor nhanh và ổn định nhưng không nhảy trang được, không hiện tổng số dễ dàng, và cần cột sắp xếp ổn định duy nhất.
Demo: seed 1 triệu dòng, đo query time ở offset 0 và offset 500000.

**27. Version API: URL, header, hay không version** 🟡
Naive → gãy: không version, sửa response trực tiếp. App mobile phiên bản cũ trên máy user vỡ ngay.
Đánh đổi: version trong URL rõ ràng và dễ debug nhưng khuyến khích copy toàn bộ code cho v2 → version qua header sạch URL nhưng khó test bằng browser và dễ bị bỏ quên → không version mà chỉ thêm field, không bao giờ xóa, là cách rẻ nhất và bền nhất, đổi lại response phình dần theo năm.
Demo: thêm một field và xóa một field, xem client cũ phản ứng thế nào.

**28. Định dạng lỗi trả về và mã lỗi nội bộ** 🟢
Naive → gãy: trả `500 {"message": "Something went wrong"}`. FE không biết hiển thị gì, không biết có nên retry.
Đánh đổi: mã lỗi chi tiết cho FE xử lý chính xác nhưng thành hợp đồng phải duy trì mãi → message tiếng Việt sẵn từ BE tiện cho FE nhưng chặn đường đa ngôn ngữ → HTTP status đúng nghĩa giúp tầng hạ tầng hiểu (retry, cache) nhưng nhiều lỗi nghiệp vụ không map được vào status nào.
Demo: viết 10 tình huống lỗi thật và thử map sang HTTP status.

**29. PUT hay PATCH, và bài toán phân biệt null với không gửi** 🟢
Naive → gãy: dùng PATCH với body `{name: "A"}`. Muốn xóa giá trị field khác thì gửi `null` — nhưng code không phân biệt được "gửi null để xóa" và "không gửi field này".
Đánh đổi: PUT toàn phần thì rõ ràng không nhập nhằng nhưng client phải gửi đủ và dễ ghi đè mất thay đổi của người khác → PATCH tiết kiệm nhưng cần quy ước rõ về null, và mỗi ngôn ngữ/ORM xử lý khác nhau.
Demo: gửi PATCH với field bằng null và không có field đó, xem code phân biệt được không.

**30. Nested resource: `/users/1/orders` hay `/orders?userId=1`** 🟢
Naive → gãy: nested nhiều tầng `/users/1/orders/2/items/3`. Đường dẫn dài, và ID con vốn đã duy nhất nên tầng cha là dư thừa.
Đánh đổi: nested diễn tả quan hệ rõ và tự nhiên cho việc phân quyền theo cha, đổi lại bùng nổ số route và trùng lặp logic → flat + query param gọn và linh hoạt hơn cho filter phức tạp, nhưng mất ngữ cảnh quyền và dễ quên check "order này có thuộc user này không".
Demo: gọi `/users/1/orders/2` với order thuộc user khác.

**31. Endpoint trả bao nhiêu dữ liệu: over-fetching và under-fetching** 🟡
Naive → gãy: trả về mọi quan hệ cho tiện. Một danh sách 20 đơn hàng kéo theo user, sản phẩm, ảnh — response 2MB cho một màn hình hiển thị 3 field.
Đánh đổi: trả đầy đủ thì FE gọi một lần nhưng nặng và chậm → trả gọn thì FE phải gọi nhiều lần (N+1 ở tầng mạng) → cho client chọn field (`?fields=`) linh hoạt nhưng khó cache và dễ thành GraphQL nửa vời → GraphQL giải quyết đúng vấn đề này nhưng mang theo cả một tầng phức tạp mới.
Demo: đo kích thước response và số request cho một màn hình thật ở cả hai cách.

**32. Bulk operation: 100 item trong một request, lỗi 1 item thì sao** 🟡
Naive → gãy: xử lý tuần tự trong một transaction, lỗi item thứ 50 thì rollback tất cả. User sửa 1 dòng rồi phải gửi lại 100 dòng.
Đánh đổi: all-or-nothing đơn giản và nhất quán nhưng khó chịu với dữ liệu lớn → partial success (trả về kết quả từng item) thân thiện hơn nhưng response phức tạp, FE phải xử lý trạng thái hỗn hợp, và không còn tính nguyên tử → chia nhỏ request về phía client thì đơn giản nhất nhưng tốn round trip.
Demo: gửi bulk 100 item với item thứ 50 sai, xem 99 item còn lại ra sao.

**33. Idempotency key: chống tạo trùng khi client retry** 🔴
Naive → gãy: `POST /orders` bị timeout, client retry. Server đã tạo đơn thành công, chỉ response không về được. Hai đơn.
Đánh đổi: idempotency key giải quyết đúng gốc nhưng phải lưu key + response trong khoảng thời gian, và phải quyết định xử lý thế nào khi request thứ hai đến lúc request đầu chưa xong (khóa? trả 409? chờ?) → dedupe bằng natural key đơn giản hơn nhưng không phải nghiệp vụ nào cũng có khóa tự nhiên.
Demo: gọi cùng một request hai lần với cùng key, và hai lần song song.

**34. Tác vụ chạy lâu: chờ đồng bộ hay trả 202 và cho polling** 🟡
Naive → gãy: giữ request mở 3 phút chờ xử lý xong. Proxy timeout ở 60 giây, client nhận lỗi dù việc vẫn đang chạy.
Đánh đổi: đồng bộ đơn giản nhất, code thẳng, nhưng bị chặn bởi mọi timeout trên đường và giữ connection → 202 + job ID + polling chịu được mọi độ dài nhưng thêm bảng job, thêm state, và FE phức tạp hơn → SSE/WebSocket cho phản hồi tức thì nhưng thêm hạ tầng.
Demo: đặt xử lý mất 90 giây và tìm xem đúng chỗ nào timeout trước.

**35. Filter, sort, search phức tạp trong query string** 🟡
Naive → gãy: tự nghĩ cú pháp `?filter=age>18,name~john`. Ba tháng sau cần OR và ngoặc, cú pháp tự chế không kham nổi.
Đánh đổi: query param đơn giản dễ cache dễ đọc nhưng chỉ diễn tả được AND phẳng → cú pháp filter riêng mạnh hơn nhưng phải viết parser, phải chống injection, và không ai ngoài bạn hiểu → POST kèm body filter thì tự do tuyệt đối nhưng mất cache HTTP và không share được URL.
Demo: viết ra yêu cầu filter phức tạp nhất trong dự án và thử biểu diễn bằng query string.

**36. Rate limit: theo IP, theo user, và chọn thuật toán nào** 🟡
Naive → gãy: giới hạn theo IP. Cả một công ty sau NAT dùng chung IP, một người dùng nhiều làm cả văn phòng bị chặn. Ngược lại kẻ tấn công đổi IP dễ dàng.
Đánh đổi: fixed window đơn giản nhưng cho phép burst gấp đôi ở ranh giới cửa sổ → sliding window chính xác hơn nhưng tốn bộ nhớ lưu timestamp → token bucket cho phép burst có kiểm soát, đúng với thực tế người dùng, nhưng khó giải thích cho user "tại sao tôi bị chặn". Thêm nữa: rate limit ở gateway thì rẻ nhưng không biết ngữ cảnh nghiệp vụ.
Demo: bắn 100 request trong 1 giây ở ranh giới cửa sổ, đếm số request được cho qua.

---

# D. Frontend: dữ liệu & trạng thái (10 bài)

**37. Fetch trong useEffect và bốn thứ bạn quên xử lý** 🟢
Naive → gãy: `useEffect(() => { fetch(url).then(setData) }, [])`. Thiếu cleanup, thiếu xử lý lỗi, thiếu loading, và race condition khi url đổi nhanh — response cũ về sau ghi đè response mới.
Đánh đổi: tự xử lý đủ 4 thứ thì không thêm thư viện nhưng lặp lại ở mọi component và dễ sót → React Query/SWR giải quyết hết cộng cache, đổi lại thêm phụ thuộc và một mô hình tư duy mới phải học.
Demo: gõ nhanh vào search box và log thứ tự response về so với thứ tự request đi.

**38. Server state và client state là hai loại khác nhau** 🟢
Naive → gãy: nhét dữ liệu từ API vào Redux như state thường. Phải tự viết loading, error, invalidate, refetch — tái tạo lại một cache tồi.
Đánh đổi: gộp chung thì một nơi duy nhất chứa mọi thứ, nghe gọn, nhưng phần lớn code là boilerplate quản lý vòng đời dữ liệu server → tách ra thì rõ ràng và ít code hơn nhiều, đổi lại có hai hệ thống state trong app và phải biết cái gì thuộc về đâu.
Demo: đếm số dòng code cho một màn hình danh sách có filter, viết bằng cả hai cách.

**39. Invalidate cache ở FE sau khi mutate** 🟢
Naive → gãy: tạo xong item mới, danh sách vẫn cũ. Hoặc invalidate tất cả cho chắc, app gọi lại 10 query không liên quan.
Đánh đổi: invalidate rộng thì chắc chắn đúng nhưng tốn request và nháy màn hình → invalidate chính xác theo key thì hiệu quả nhưng phải thiết kế key cẩn thận và dễ sót một chỗ → cập nhật cache thủ công (không refetch) nhanh nhất nhưng dữ liệu có thể lệch với server.
Demo: tạo item mới rồi đếm số request phát sinh.

**40. Optimistic update: khi nào đáng làm và rollback thế nào** 🟡
Naive → gãy: cập nhật UI ngay, không xử lý thất bại. Request lỗi nhưng UI vẫn hiện như thành công, user tin là đã lưu.
Đánh đổi: optimistic cho cảm giác tức thì, đúng cho hành động khả năng thành công cao và hậu quả nhỏ (like, toggle) → đổi lại phải lưu snapshot để rollback, phải xử lý nhiều mutation chồng nhau, và với hành động quan trọng (thanh toán) thì cảm giác nhanh giả tạo là nguy hiểm.
Demo: chặn network và thử một optimistic update, xem UI có tự trả về đúng không.

**41. Race condition ở ô tìm kiếm: debounce, throttle, hay abort** 🟢
Naive → gãy: gọi API mỗi lần gõ. 10 request cho một từ khóa, và response cho "ho" về sau response cho "hoa" — kết quả sai hiển thị.
Đánh đổi: debounce giảm request nhưng thêm độ trễ cảm nhận được → abort request cũ giải quyết đúng vấn đề thứ tự nhưng không giảm số request → kết hợp cả hai là đúng nhất, đổi lại code phức tạp hơn. Riêng throttle thường sai lựa chọn cho search.
Demo: log thứ tự request/response khi gõ nhanh, có và không có abort.

**42. Form: controlled, uncontrolled, và validate ở đâu** 🟢
Naive → gãy: controlled với `useState` cho mỗi field. Form 30 field re-render toàn bộ mỗi lần gõ một ký tự.
Đánh đổi: controlled cho kiểm soát tuyệt đối và validate tức thì, đổi lại re-render nhiều → uncontrolled nhanh hơn hẳn nhưng khó làm logic phụ thuộc giữa các field. Về validate: chỉ FE thì UX tốt nhưng vô nghĩa về bảo mật, chỉ BE thì an toàn nhưng user phải chờ, cả hai thì đúng nhưng phải duy trì hai bộ rule (chia sẻ schema là cách thoát).
Demo: form 30 field, đo số lần re-render khi gõ một ký tự.

**43. Global state: Context, Zustand, Redux — chi phí thật của mỗi cái** 🟢
Naive → gãy: nhét mọi thứ vào một Context. Đổi một giá trị làm re-render toàn bộ cây component đang consume.
Đánh đổi: Context có sẵn, không thêm phụ thuộc, nhưng không có cơ chế chọn lọc nên re-render rộng → Zustand nhẹ và có selector, đổi lại thêm thư viện → Redux có devtools và middleware mạnh cho app phức tạp, đổi lại boilerplate và learning curve. Câu hỏi nên hỏi trước: bao nhiêu state trong app thật sự là global?
Demo: đặt một counter vào Context và đếm component re-render.

**44. Phân trang, "tải thêm", hay cuộn vô hạn** 🟢
Naive → gãy: chọn cuộn vô hạn vì trông hiện đại. User không tới được footer, không bookmark được vị trí, và quay lại từ trang chi tiết là mất hết vị trí đã cuộn.
Đánh đổi: phân trang cho phép share URL, bookmark, quay lại đúng chỗ, nhưng cảm giác cũ và tốn click → cuộn vô hạn mượt cho nội dung khám phá nhưng phá điều hướng và tốn bộ nhớ dần → "tải thêm" là dung hòa, giữ được URL nếu làm đúng.
Demo: cuộn 10 trang, vào chi tiết, bấm back, xem có về đúng vị trí không.

**45. Loading state: spinner, skeleton, hay hiện dữ liệu cũ** 🟢
Naive → gãy: mọi thứ là spinner toàn trang. Mỗi lần đổi filter là màn hình trắng, cảm giác chậm hơn thực tế.
Đánh đổi: spinner đơn giản nhưng phá layout và mất ngữ cảnh → skeleton giữ layout, cảm giác nhanh hơn, đổi lại phải làm skeleton cho từng loại nội dung → stale-while-revalidate (hiện dữ liệu cũ, âm thầm cập nhật) cho cảm giác nhanh nhất nhưng user có thể đọc dữ liệu lỗi thời mà không biết.
Demo: throttle mạng về 3G và so sánh cảm nhận ba cách.

**46. Khi API chết, người dùng thấy gì** 🟡
Naive → gãy: không có error boundary. Một component lỗi làm trắng cả app, không log gì.
Đánh đổi: error boundary chặn được crash lan rộng nhưng không bắt lỗi async và event handler → retry tự động cứu được lỗi mạng tạm thời nhưng có thể nhân đôi tải lên server đang sập (cần backoff) → hiện lỗi chi tiết giúp debug nhưng rò rỉ thông tin nội bộ cho người dùng.
Demo: tắt BE giữa lúc dùng app, đi qua mọi màn hình xem cái gì hiện ra.

---

# E. Frontend: render & hiệu năng (10 bài)

**47. CSR, SSR, SSG, ISR: chọn theo tiêu chí nào** 🟡
Naive → gãy: dùng SSR cho tất cả vì "tốt cho SEO". Dashboard sau đăng nhập không cần SEO nhưng phải chịu tải server mỗi request.
Đánh đổi: CSR rẻ nhất về hạ tầng, tương tác tốt, nhưng first load chậm và SEO khó → SSR tốt cho SEO và first paint nhưng mỗi request tốn CPU server và phải xử lý cache cẩn thận → SSG nhanh nhất và rẻ nhất nhưng cần build lại khi nội dung đổi → ISR dung hòa nhưng thêm sự phức tạp về tính tươi của dữ liệu và phụ thuộc nền tảng.
Demo: cùng một trang, dựng cả bốn cách, đo TTFB và LCP.

**48. Server Components: cái gì chạy ở đâu và tại sao dễ nhầm** 🟡
Naive → gãy: dùng `useState` trong Server Component, hoặc gọi trực tiếp DB trong component có `"use client"`. Lỗi khó hiểu vì mô hình tư duy chưa rõ.
Đánh đổi: RSC giảm bundle và cho phép truy cập dữ liệu trực tiếp, đổi lại ranh giới client/server thành thứ phải luôn nghĩ tới, prop truyền qua ranh giới phải serialize được, và thư viện cũ chưa tương thích → giữ client-only thì đơn giản và quen nhưng bundle lớn hơn.
Demo: đặt `console.log` trong cả hai loại component, xem log ra ở đâu.

**49. Hydration mismatch: tại sao xảy ra và cách xử lý đúng** 🟡
Naive → gãy: render `new Date()` hoặc `localStorage` trong component SSR. Server và client render khác nhau, React cảnh báo rồi bỏ luôn phần DOM đó.
Đánh đổi: `suppressHydrationWarning` làm tắt cảnh báo nhưng che vấn đề thật → chuyển sang render sau khi mount thì đúng nhưng gây nháy nội dung và mất lợi ích SSR cho phần đó → đưa dữ liệu đó xuống từ server là đúng nhất nhưng không phải lúc nào cũng làm được (ví dụ timezone của user).
Demo: render thời gian hiện tại trong SSR và đọc cảnh báo trong console.

**50. Bundle size: cắt gì và cắt bằng cách nào** 🟢
Naive → gãy: import cả `lodash` để dùng một hàm `debounce`. Hoặc lazy load mọi thứ, tạo ra hàng chục request nhỏ làm chậm hơn.
Đánh đổi: code splitting theo route là mức hiệu quả nhất với ít rủi ro → splitting quá mịn thì tổng tải nhỏ hơn nhưng nhiều round trip và nháy loading → thay thư viện nặng bằng thư viện nhẹ tiết kiệm thật nhưng mất tính năng và tốn công migrate. Điều hay bị bỏ qua: dữ liệu và ảnh thường nặng hơn JS.
Demo: chạy bundle analyzer, tìm 3 thứ nặng nhất, thử cắt và đo lại.

**51. Ảnh: định dạng, kích thước, lazy load, và LCP** 🟢
Naive → gãy: dùng ảnh gốc 4000px cho khung 300px. Hoặc lazy load cả ảnh hero — ảnh quan trọng nhất tải muộn nhất, LCP tệ đi.
Đánh đổi: WebP/AVIF nhẹ hơn nhiều nhưng cần fallback và tốn CPU encode → responsive srcset đúng đắn nhưng tăng số biến thể phải sinh và quản lý → lazy load tiết kiệm băng thông nhưng phải loại trừ ảnh trong viewport đầu, và cần đặt kích thước trước để không gây CLS.
Demo: đo LCP trước và sau khi bỏ lazy load ở ảnh hero.

**52. Re-render không cần thiết — và React Compiler đổi lời khuyên thế nào** 🟡
Naive → gãy: rải `useMemo`/`useCallback` khắp nơi cho chắc. Bản thân việc memo cũng tốn chi phí, và dependency array sai thì tạo bug khó tìm.
Đánh đổi: memo thủ công có thể cứu component nặng thật nhưng phần lớn trường hợp là tối ưu sớm không đo lường → React Compiler tự lo phần này, làm phần lớn lời khuyên cũ thành lỗi thời, đổi lại bạn mất kiểm soát trực tiếp và cần hiểu khi nào nó không áp dụng được. Nguyên tắc còn nguyên giá trị: đo trước, tối ưu sau.
Demo: dùng React DevTools Profiler tìm component render nhiều nhất, thử memo và đo lại.

**53. Danh sách 10 nghìn dòng: virtualize hay đừng hiển thị hết** 🟢
Naive → gãy: render hết. DOM 10 nghìn node làm trang đứng, scroll giật.
Đánh đổi: virtualize giữ DOM nhỏ và mượt, đổi lại mất Ctrl+F của browser, khó làm chiều cao động, khó accessibility, và phá cả việc in trang → phân trang tránh được toàn bộ vấn đề nhưng đổi UX → hỏi lại nghiệp vụ "user thật sự cần thấy 10 nghìn dòng cùng lúc không" thường là câu trả lời tốt nhất.
Demo: render 10k dòng có và không virtualize, đo FPS khi scroll.

**54. Font: FOIT, FOUT, và CLS** 🟢
Naive → gãy: import font từ Google Fonts bằng `@import` trong CSS. Font tải muộn, chữ nháy đổi kiểu, layout dịch chuyển.
Đánh đổi: `font-display: swap` hiện chữ ngay nhưng nháy khi font thật về → `optional` không nháy nhưng có thể không dùng font của bạn → self-host + preload nhanh nhất nhưng phải tự quản lý file và subset → dùng font hệ thống thì nhanh tuyệt đối, đổi lại mất bản sắc thương hiệu.
Demo: đo CLS với từng giá trị `font-display` trên mạng chậm.

**55. Bạn có thật sự cần Next.js không** 🟡
Naive → gãy: chọn Next.js theo mặc định cho một dashboard nội bộ sau đăng nhập. Không cần SEO, không cần SSR, nhưng phải chịu mô hình build phức tạp và ràng buộc nền tảng.
Đánh đổi: Next.js cho SSR/SSG, routing, image optimization sẵn sàng, cộng đồng lớn — hợp cho site public cần SEO → Vite + router riêng thì đơn giản, build nhanh, deploy đâu cũng được, kiểm soát rõ, đổi lại phải tự lắp nhiều thứ và không có SSR sẵn. Chi phí ẩn của Next: bị dẫn về một nền tảng hosting cụ thể nếu dùng hết tính năng.
Demo: dựng cùng một app nhỏ ở cả hai, so sánh thời gian build và cấu hình deploy.

**56. SEO cho ứng dụng SPA** 🟡
Naive → gãy: tin rằng Google chạy được JS nên không cần làm gì. Google có chạy nhưng chậm và không đảm bảo; các crawler khác (mạng xã hội, công cụ tìm kiếm nhỏ) thì không.
Đánh đổi: SSR giải quyết triệt để nhưng tốn hạ tầng → prerender cho crawler thì rẻ hơn nhưng có nguy cơ bị coi là phục vụ nội dung khác nhau → chỉ làm meta tag động thì đủ cho preview link nhưng không đủ cho index nội dung.
Demo: xem nguồn trang bằng `curl` (không JS) và so với nội dung thật.

---

# F. Database: schema & truy vấn (16 bài)

Nhóm evergreen nhất. Dựng demo dễ, người đọc gặp lại mãi.

**57. Index: khi nào có ích và giá phải trả ở đường ghi** 🟢
Naive → gãy: query chậm thì thêm index. Bảng có 15 index, INSERT chậm gấp ba, và nửa số index không được dùng.
Đánh đổi: mỗi index tăng tốc đọc nhưng làm chậm mọi INSERT/UPDATE/DELETE và tốn dung lượng → index trên cột chọn lọc kém (ví dụ boolean) thường không được dùng → index nhiều cột phục vụ được nhiều query nhưng chỉ khi thứ tự cột đúng.
Demo: seed 1 triệu dòng, đo INSERT với 0, 5, 15 index; và tìm index không dùng bằng `pg_stat_user_indexes`.

**58. Composite index: thứ tự cột quyết định index có được dùng hay không** 🟢
Naive → gãy: có index `(status, created_at)` nhưng query filter theo `created_at` — index không dùng được, tưởng đã tối ưu mà thực ra không.
Đánh đổi: đặt cột chọn lọc cao trước thì tốt cho query lọc theo cột đó, nhưng làm index vô dụng với query bắt đầu từ cột sau → tạo nhiều index cho nhiều thứ tự thì phục vụ được hết nhưng nhân chi phí ghi.
Demo: tạo index `(a,b)`, chạy `EXPLAIN` cho query lọc theo `a`, theo `b`, và theo cả hai.

**59. Đọc EXPLAIN: những dòng thật sự quan trọng** 🟢
Naive → gãy: chạy `EXPLAIN` rồi không biết nhìn gì, chỉ tìm chữ "Seq Scan".
Đánh đổi: `Seq Scan` không phải luôn xấu — với bảng nhỏ nó nhanh hơn index scan. Cái đáng nhìn: rows dự đoán so với rows thật (lệch nhiều nghĩa là statistics cũ), loại join, và chỗ thời gian thật sự đổ vào. `EXPLAIN ANALYZE` cho số thật nhưng thật sự chạy query (nguy hiểm với UPDATE/DELETE).
Demo: chạy `EXPLAIN ANALYZE` trên query chậm nhất bạn có, tìm node tốn thời gian nhất.

**60. N+1 query: tại sao ORM nào cũng gây ra và cách phát hiện sớm** 🟢
Naive → gãy: `orders.forEach(o => o.customer.name)` — 1 query thành 101 query. Local với 10 dòng thì không thấy gì, production 1000 dòng thì sập.
Đánh đổi: eager load hết thì hết N+1 nhưng kéo về dữ liệu không cần và có thể tạo join khổng lồ → lazy load tiết kiệm nhưng dễ sinh N+1 ở chỗ không ngờ → DataLoader/batching giải quyết đẹp nhưng thêm một tầng khái niệm. Cách phòng thật: log số query mỗi request và cảnh báo khi vượt ngưỡng.
Demo: bật query log, gọi một endpoint list, đếm số query thật.

**61. Soft delete: cái giá kéo dài nhiều năm** 🟡
Naive → gãy: thêm `deleted_at` là xong. Rồi phát hiện unique constraint trên email chặn user tạo lại tài khoản đã xóa; mọi query quên `WHERE deleted_at IS NULL` trả về dữ liệu đã xóa; và index không còn hiệu quả.
Đánh đổi: soft delete cho phép hồi phục và giữ toàn vẹn tham chiếu, đổi lại mọi query phức tạp hơn, unique constraint phải thành partial index, và bảng phình mãi → xóa thật thì sạch nhưng mất khả năng khôi phục và có thể vỡ khóa ngoại → chuyển sang bảng archive là dung hòa, đổi lại thêm công đồng bộ.
Demo: tạo user, xóa mềm, thử tạo lại với cùng email.

**62. Khóa chính: auto-increment hay UUID** 🟡
Naive → gãy: chọn UUID v4 cho mọi bảng vì "an toàn hơn, dễ merge". Index phình, insert phân tán khắp B-tree làm chậm dần, và join tốn hơn.
Đánh đổi: auto-increment nhỏ gọn, insert tuần tự thân thiện với index, nhưng để lộ số lượng bản ghi và không tạo được ID ở phía client → UUID v4 an toàn về suy đoán nhưng ngẫu nhiên nên tệ cho index → UUID v7/ULID sắp xếp theo thời gian, dung hòa tốt, nhưng hỗ trợ chưa đồng đều ở mọi ORM.
Demo: insert 500k dòng với BIGINT và UUID v4, so sánh thời gian và kích thước index.

**63. Lưu tiền: tuyệt đối đừng dùng float** 🔴
Naive → gãy: `price FLOAT`. `0.1 + 0.2` không bằng `0.3`, và sau vài nghìn giao dịch số tổng lệch — không ai biết lệch từ đâu.
Đánh đổi: `DECIMAL/NUMERIC` chính xác tuyệt đối nhưng chậm hơn và phải cẩn thận khi ngôn ngữ đọc ra thành float → lưu số nguyên đơn vị nhỏ nhất (đồng, cents) nhanh và an toàn nhưng phải nhớ quy ước ở mọi nơi và khó với đơn vị chia nhỏ (giá trên kg). Với VND thì lưu integer là hợp lý vì không có đơn vị nhỏ hơn đồng.
Demo: cộng `0.1` một nghìn lần bằng float trong ngôn ngữ bạn dùng, in ra kết quả.

**64. Lưu thời gian: timestamptz, UTC, và bài toán múi giờ Việt Nam** 🔴
Naive → gãy: lưu `TIMESTAMP` không timezone, giờ máy server. Deploy lên server UTC là toàn bộ dữ liệu lệch 7 tiếng, và báo cáo "doanh thu hôm nay" sai lệch ở hai đầu ngày.
Đánh đổi: lưu UTC + `timestamptz` là chuẩn, đúng cho mọi phép so sánh, đổi lại phải chuyển đổi ở mọi chỗ hiển thị và query theo "ngày" phải cẩn thận với ranh giới → lưu giờ địa phương thì báo cáo dễ nhưng vỡ khi có nhiều múi giờ hoặc DST. Riêng "ngày sinh" thì không nên là timestamp mà là `DATE`.
Demo: lưu một bản ghi, đổi timezone của session, query lại theo ngày.

**65. Enum: kiểu enum của DB, string, hay bảng lookup** 🟢
Naive → gãy: dùng enum của Postgres. Thêm một giá trị mới cần migration, xóa giá trị thì gần như không thể, và thứ tự thì cố định.
Đánh đổi: DB enum đảm bảo toàn vẹn và tiết kiệm dung lượng nhưng cứng nhắc khi thay đổi → string + check constraint linh hoạt hơn, đổi lại kém an toàn hơn → bảng lookup cho phép thêm giá trị runtime và gắn thêm thuộc tính (nhãn tiếng Việt, thứ tự, màu), đổi lại thêm join ở mọi query.
Demo: thử thêm và xóa một giá trị enum trong Postgres, đọc lỗi.

**66. Cột JSON: khi nào hợp lý và khi nào là nợ kỹ thuật** 🟡
Naive → gãy: nhét mọi field chưa rõ vào cột `metadata JSONB`. Một năm sau không ai biết trong đó có gì, không validate được, và query lọc theo field bên trong thì chậm.
Đánh đổi: JSONB linh hoạt tuyệt đối cho dữ liệu thật sự không có cấu trúc (payload webhook, cấu hình theo tenant, log) → đổi lại mất kiểm tra kiểu, mất khóa ngoại, cần GIN index để query hiệu quả, và không có schema nghĩa là không có tài liệu. Dấu hiệu dùng sai: bạn đang query field trong JSON như thể nó là cột.
Demo: query lọc theo field trong JSONB với và không có GIN index, đo thời gian.

**67. Normalize hay denormalize: đọc nhanh và ghi nhất quán** 🟡
Naive → gãy: denormalize sớm bằng cách copy tên khách hàng vào bảng đơn hàng. Khách đổi tên, 500 đơn cũ vẫn tên cũ — và đôi khi đó lại đúng nghiệp vụ, đôi khi là bug.
Đánh đổi: normalize giữ một nguồn chân lý duy nhất, cập nhật một chỗ, đổi lại nhiều join và query phức tạp hơn → denormalize đọc nhanh và đơn giản nhưng phải đồng bộ ở mọi đường ghi, và luôn có cửa sổ không nhất quán. Câu hỏi quyết định: field này cần giá trị *hiện tại* hay giá trị *tại thời điểm đó*?
Demo: thiết kế bảng order theo cả hai cách, viết query báo cáo và so sánh.

**68. Migration không downtime: thêm cột, xóa cột, đổi tên** 🔴
Naive → gãy: `ALTER TABLE ... ADD COLUMN x NOT NULL` trên bảng 10 triệu dòng. Postgres khóa bảng, mọi request treo, và deploy thành sự cố.
Đánh đổi: thêm cột nullable rồi backfill từng lô rồi mới set NOT NULL — nhiều bước, nhiều lần deploy, đổi lại không downtime → làm một lệnh thì nhanh gọn nhưng khóa bảng. Đổi tên cột thì gần như luôn cần expand-contract (thêm cột mới, ghi cả hai, chuyển đọc, xóa cột cũ) qua nhiều lần release — chậm nhưng an toàn.
Demo: tạo bảng 5 triệu dòng, chạy ALTER với NOT NULL và đo thời gian bảng bị khóa.

**69. Đếm bản ghi trên bảng lớn: COUNT(*) là cái bẫy** 🟢
Naive → gãy: mỗi lần phân trang gọi `SELECT COUNT(*)` để tính tổng số trang. Trên 10 triệu dòng có filter, câu count nặng hơn cả câu lấy dữ liệu.
Đánh đổi: count chính xác thì tổng số trang đúng nhưng chậm và không cache được nếu filter động → dùng số ước lượng từ statistics thì nhanh tức thì nhưng sai số → bỏ tổng số trang, chỉ hiện "có trang sau" (kiểu cursor), là nhanh nhất nhưng đổi UX → cache count theo bộ filter phổ biến là dung hòa.
Demo: đo `COUNT(*)` có filter trên 10 triệu dòng, so với ước lượng từ `EXPLAIN`.

**70. Tìm kiếm: full-text của Postgres hay Elasticsearch** 🟡
Naive → gãy: `LIKE '%keyword%'`. Index không dùng được, quét toàn bảng, và không xếp hạng theo độ liên quan.
Đánh đổi: full-text search của Postgres đủ tốt cho phần lớn ứng dụng, không thêm hạ tầng, nhất quán tức thì với dữ liệu → đổi lại kém về gợi ý, sửa lỗi chính tả, và tìm kiếm phức tạp nhiều tiêu chí → Elasticsearch mạnh hơn hẳn nhưng thêm một hệ thống phải nuôi, phải đồng bộ, và luôn có độ trễ index.
Demo: cùng một tập dữ liệu, so sánh `LIKE`, `tsvector`, và kết quả xếp hạng.

**71. Tìm kiếm tiếng Việt: có dấu, không dấu, và telex** 🟢
Naive → gãy: user gõ "ha noi" không tìm ra "Hà Nội". Hoặc gõ "hà" ra cả kết quả không liên quan.
Đánh đổi: lưu thêm cột không dấu (unaccent) thì đơn giản và nhanh, đổi lại tốn dung lượng và phải đồng bộ khi cập nhật → dùng `unaccent` extension trực tiếp trong query thì không trùng lặp dữ liệu nhưng khó tận dụng index (cần index trên biểu thức) → chuẩn hóa cả telex/VNI thì thân thiện nhất nhưng nhiều luật đặc thù và dễ tạo kết quả rác.
Demo: seed danh sách tỉnh thành, thử tìm bằng cả ba cách nhập.

**72. Connection pool: đặt bao nhiêu và tại sao serverless làm vỡ mọi thứ** 🔴
Naive → gãy: đặt pool 100 connection cho mỗi instance vì "càng nhiều càng tốt". 5 instance là 500 connection, vượt `max_connections` của Postgres, app từ chối kết nối. Hoặc chạy trên serverless: mỗi function instance mở pool riêng, hàng nghìn connection.
Đánh đổi: pool lớn chịu được burst nhưng mỗi connection tốn RAM ở phía DB và quá nhiều connection làm DB *chậm hơn* do tranh chấp → pool nhỏ thì DB khỏe nhưng request phải chờ lấy connection → pgBouncer giải quyết cho serverless nhưng transaction mode phá prepared statement và session state.
Demo: chạy app với pool 5 và pool 100, bắn tải và so sánh p95 latency.

---

# G. Transaction & tính nhất quán (10 bài)

Nhóm 🔴 gần hết. Viết sai ở đây có thể làm ai đó mất dữ liệu hoặc mất tiền.

**73. Ranh giới transaction đặt ở đâu** 🔴
Naive → gãy: mở transaction ở đầu request, đóng ở cuối, gọi API bên ngoài ở giữa. API chậm 3 giây là transaction giữ khóa 3 giây, và nếu API timeout thì DB rollback nhưng bên kia đã nhận.
Đánh đổi: transaction hẹp (chỉ quanh các câu DB) thì giữ khóa ngắn, DB khỏe, đổi lại phải tự lo tính nguyên tử với thao tác bên ngoài → transaction rộng thì code đơn giản, nghĩ ít, nhưng giữ khóa lâu và không bao giờ nên bao lấy I/O bên ngoài.
Demo: mở transaction, gọi một API chậm 5 giây, đo thời gian khóa bằng `pg_locks`.

**74. Isolation level: dirty read, phantom, và mặc định của bạn là gì** 🔴
Naive → gãy: không bao giờ nghĩ tới isolation, cho rằng transaction là đủ. Rồi hai request đồng thời đọc cùng số dư và cùng trừ tiền.
Đánh đổi: Read Committed (mặc định Postgres) rẻ nhất nhưng cho phép cùng một query trong transaction trả kết quả khác nhau → Repeatable Read ổn định hơn nhưng có thể fail với serialization error mà app phải retry → Serializable đúng nhất nhưng nhiều retry và giảm throughput. MySQL và Postgres mặc định khác nhau — đừng giả định.
Demo: mở hai session psql, thực hiện đọc-ghi chồng nhau ở từng isolation level.

**75. Optimistic hay pessimistic locking** 🟡
Naive → gãy: hai người sửa cùng một bản ghi, người lưu sau ghi đè hoàn toàn thay đổi của người trước, không ai biết.
Đánh đổi: pessimistic (`SELECT FOR UPDATE`) đảm bảo tuyệt đối nhưng giữ khóa, giảm đồng thời, và có nguy cơ deadlock → optimistic (cột version) không giữ khóa, throughput cao, đổi lại người dùng có thể bị từ chối sau khi đã điền form và phải xử lý UX cho việc đó. Chọn theo tần suất xung đột thật, không theo cảm giác.
Demo: hai request song song update cùng bản ghi, thử cả hai cách.

**76. Trừ tồn kho khi 100 người mua cùng lúc** 🔴
Naive → gãy: `SELECT quantity` → kiểm tra trong code → `UPDATE quantity - 1`. Giữa đọc và ghi có khoảng trống; bán vượt số lượng có thật.
Đánh đổi: `UPDATE ... SET qty = qty - 1 WHERE qty >= 1` nguyên tử và rẻ nhất, kiểm tra bằng số dòng ảnh hưởng — nhưng khó khi có nghiệp vụ phức tạp hơn → `SELECT FOR UPDATE` linh hoạt hơn nhưng tuần tự hóa tại điểm nóng → giữ tồn kho ở Redis nhanh nhất nhưng phải đối soát với DB và xử lý khi Redis mất dữ liệu.
Demo: bắn 100 request song song mua item có tồn kho 10, đếm số đơn thành công.

**77. Người dùng bấm hai lần: chống trùng ở mấy tầng** 🟡
Naive → gãy: disable nút sau khi bấm. Mạng chậm, user F5 rồi bấm lại, hoặc mở hai tab.
Đánh đổi: chặn ở FE thì UX tốt nhưng không phải bảo vệ thật → unique constraint ở DB là lớp chắc chắn cuối cùng nhưng phải có khóa tự nhiên và phải xử lý lỗi constraint thành thông báo tử tế → idempotency key ở API là giải pháp đúng nhất nhưng phức tạp hơn cả. Thực tế: cần cả ba, mỗi tầng một mục đích.
Demo: mở hai tab, submit cùng lúc, xem có tạo hai bản ghi.

**78. Ghi DB và gửi event: outbox pattern** 🔴
Naive → gãy: `saveOrder()` rồi `publishEvent()`. Nếu publish lỗi thì đơn có mà event không; nếu đảo thứ tự thì event có mà đơn không.
Đánh đổi: outbox (ghi event vào bảng cùng transaction, worker đọc và publish) đảm bảo không mất event, đổi lại thêm bảng, thêm worker, và event là at-least-once nên consumer phải idempotent → publish trực tiếp đơn giản nhưng chấp nhận mất mát → 2PC thì đúng lý thuyết nhưng gần như không ai dùng vì phức tạp và giòn.
Demo: kill process giữa lúc đã commit DB nhưng chưa publish, xem hệ quả.

**79. Giao dịch xuyên nhiều service: saga và bù trừ** 🔴
Naive → gãy: gọi lần lượt 3 service, service thứ 3 lỗi. Hai service đầu đã ghi dữ liệu, không có rollback.
Đánh đổi: saga với hành động bù trừ giải quyết được nhưng mỗi bước cần một hành động nghịch đảo — và nhiều hành động không có nghịch đảo thật (email đã gửi rồi) → orchestration dễ theo dõi nhưng tập trung phụ thuộc → choreography phân tán nhưng khó nhìn thấy toàn cảnh khi debug. Câu hỏi nên hỏi trước: có nhất thiết phải tách service không?
Demo: mô phỏng 3 bước với bước cuối luôn lỗi, viết compensation cho từng bước.

**80. Eventual consistency: người dùng thấy gì trong khoảng thời gian đó** 🟡
Naive → gãy: user tạo bài viết, chuyển sang danh sách, không thấy bài mình vừa tạo (read replica chưa kịp đồng bộ). User tạo lại lần hai.
Đánh đổi: đọc từ replica giảm tải primary nhưng có độ trễ → read-your-own-writes (đọc từ primary cho chính user vừa ghi) giải quyết đúng vấn đề cảm nhận, đổi lại phức tạp trong routing → chỉ dùng primary thì nhất quán nhưng không scale đọc.
Demo: dựng primary + replica với độ trễ nhân tạo, ghi rồi đọc ngay.

**81. Retry an toàn: tại sao retry có thể làm tình hình tệ hơn** 🔴
Naive → gãy: request lỗi thì retry 3 lần ngay lập tức. Server đang quá tải nhận thêm gấp ba tải — retry storm biến sự cố nhỏ thành sập toàn bộ. Và nếu request không idempotent, retry tạo dữ liệu trùng.
Đánh đổi: exponential backoff + jitter tránh dồn cục nhưng làm thời gian phục hồi cảm nhận lâu hơn → circuit breaker bảo vệ hệ thống hạ nguồn nhưng thêm state và phải tune ngưỡng → không retry thì đơn giản nhưng lỗi mạng tạm thời thành lỗi thật với user. Nguyên tắc: chỉ retry cái idempotent, chỉ retry lỗi tạm thời.
Demo: cho một service trả 500, bật retry 3 lần không backoff, đếm request thật tới server.

**82. Deadlock: tại sao xảy ra và cách phòng thực tế** 🟡
Naive → gãy: gặp deadlock thì retry và coi như xong. Không tìm nguyên nhân, deadlock tiếp tục xuất hiện ngẫu nhiên trên production.
Đánh đổi: retry là cần thiết nhưng chỉ là băng cứu thương → thống nhất thứ tự truy cập bản ghi (luôn khóa theo ID tăng dần) là cách phòng gốc, đổi lại phải kỷ luật ở mọi chỗ trong codebase → giảm phạm vi transaction giảm cơ hội deadlock nhưng có thể phá tính nguyên tử mong muốn.
Demo: tạo deadlock có chủ ý bằng hai session khóa hai bản ghi theo thứ tự ngược nhau, đọc log của Postgres.

---

# H. Job nền & hàng đợi (10 bài)

**83. Làm ngay trong request hay đẩy vào queue** 🟢
Naive → gãy: gửi email xác nhận ngay trong request đăng ký. SMTP chậm 5 giây, user chờ 5 giây; SMTP lỗi, đăng ký thất bại dù user đã tạo xong.
Đánh đổi: xử lý đồng bộ đơn giản, dễ debug, phản hồi lỗi ngay cho user — hợp khi kết quả là điều user cần biết → queue cho response nhanh và chịu được lỗi tạm thời, đổi lại thêm hạ tầng, khó debug hơn, và user không biết ngay khi thất bại (phải có cách thông báo sau).
Demo: đo thời gian response endpoint đăng ký có và không có queue.

**84. Cron trong app: chuyện gì xảy ra khi bạn chạy 3 instance** 🟡
Naive → gãy: `@Cron()` trong NestJS gửi báo cáo hàng ngày. Scale lên 3 pod, mỗi ngày gửi 3 email.
Đánh đổi: khóa phân tán (Redis lock) đơn giản và hiệu quả nhưng phải xử lý trường hợp process chết khi đang giữ khóa → tách scheduler ra service riêng chạy 1 replica thì rõ ràng nhưng thành single point of failure → dùng scheduler bên ngoài (K8s CronJob) sạch nhất nhưng job không nằm cùng codebase.
Demo: chạy 3 instance cùng lúc với một cron mỗi phút, đếm số lần thực thi.

**85. Job thất bại: retry, backoff, và dead letter queue** 🟡
Naive → gãy: job lỗi thì mất luôn, không log, không ai biết. Hoặc retry vô hạn, job độc chiếm worker mãi mãi.
Đánh đổi: retry có giới hạn + backoff xử lý được lỗi tạm thời nhưng kéo dài thời gian phát hiện lỗi thật → DLQ giữ lại job chết để xử lý tay, đổi lại cần người thật đi xem DLQ (thường không ai xem) → fail nhanh và báo động ngay thì phát hiện sớm nhưng ồn ào với lỗi tạm thời.
Demo: cho job lỗi luôn, quan sát hành vi retry và xem job dừng ở đâu.

**86. At-least-once, at-most-once, exactly-once** 🔴
Naive → gãy: giả định message được xử lý đúng một lần. Worker xử lý xong nhưng chết trước khi ack — message được giao lại, email gửi hai lần.
Đánh đổi: at-least-once là mặc định thực tế của gần như mọi queue, an toàn về mất mát nhưng buộc consumer phải idempotent → at-most-once không bao giờ trùng nhưng có thể mất → "exactly-once" thường là at-least-once cộng dedupe ở consumer, chứ không phải phép màu của broker.
Demo: kill worker sau khi xử lý xong nhưng trước khi ack, xem message có quay lại.

**87. Thứ tự message: khi nào nó quan trọng và cái giá của việc giữ thứ tự** 🟡
Naive → gãy: hai event "tạo user" và "cập nhật user" xử lý song song, event cập nhật tới trước event tạo. Lỗi khó tái hiện.
Đánh đổi: một partition/một consumer thì giữ được thứ tự nhưng mất khả năng song song → partition theo key (userId) giữ thứ tự trong phạm vi cần thiết và vẫn song song, đổi lại phải chọn key đúng và có thể lệch tải → thiết kế event idempotent và không phụ thuộc thứ tự là bền nhất nhưng khó nhất.
Demo: gửi hai event liên quan liên tiếp với nhiều consumer, quan sát thứ tự xử lý.

**88. Job chạy quá lâu hoặc treo vĩnh viễn** 🟡
Naive → gãy: không có timeout. Một job gọi API bên ngoài không phản hồi, chiếm worker mãi, hàng đợi dồn lại.
Đánh đổi: timeout cứng giải phóng worker nhưng có thể cắt job đang gần xong (và nếu job không idempotent thì retry sau timeout gây trùng) → visibility timeout của queue tự động giao lại nhưng nếu quá ngắn thì job chạy song song hai lần → heartbeat từ worker chính xác nhất nhưng phức tạp.
Demo: tạo job sleep 10 phút, xem hệ thống phản ứng thế nào.

**89. Hàng đợi dồn 100 nghìn job: scale worker hay chấp nhận chậm** 🟡
Naive → gãy: thêm worker cho nhanh. 50 worker cùng đập vào DB làm cạn connection pool, cả hệ thống chậm theo — kể cả request của user thật.
Đánh đổi: nhiều worker xử lý nhanh hơn nhưng chuyển điểm nghẽn sang DB hoặc API bên ngoài → giới hạn concurrency bảo vệ hạ nguồn nhưng backlog lâu hơn → tách queue theo độ ưu tiên để job quan trọng không bị chặn sau job rác, đổi lại thêm phức tạp về vận hành.
Demo: đẩy 10 nghìn job vào queue, tăng worker từ 1 lên 20, đo throughput và latency của DB.

**90. Email/SMS qua bên thứ ba: khi họ chết thì sao** 🟡
Naive → gãy: gọi API gửi email trực tiếp, lỗi thì log rồi bỏ. User không nhận được mã OTP và không ai biết.
Đánh đổi: queue + retry đảm bảo gửi được khi nhà cung cấp hồi phục, đổi lại OTP có thể tới muộn hơn thời gian hiệu lực (retry lâu là vô nghĩa với OTP) → nhiều nhà cung cấp dự phòng thì bền nhưng phải duy trì hai tích hợp và xử lý khác biệt về template → chấp nhận thất bại và cho user bấm gửi lại là giải pháp đơn giản nhất, thường đủ tốt.
Demo: chặn domain của nhà cung cấp bằng hosts file, xem luồng đăng ký ra sao.

**91. Nhận webhook từ bên thứ ba: ba thứ luôn phải làm** 🔴
Naive → gãy: nhận webhook thanh toán, xử lý luôn, trả 200. Không verify chữ ký (ai cũng gọi được endpoint đó để tạo đơn đã thanh toán), không idempotent (họ retry là cộng tiền hai lần), và xử lý nặng làm timeout khiến họ retry thêm.
Đánh đổi: verify chữ ký là bắt buộc, không có đánh đổi → xử lý nặng thì nên nhận, lưu, trả 200 ngay, xử lý sau (an toàn nhưng thêm queue) so với xử lý ngay (đơn giản nhưng rủi ro timeout) → lưu raw payload tốn dung lượng nhưng vô giá khi cần đối soát.
Demo: tự gọi endpoint webhook của mình bằng curl không có chữ ký.

**92. Gửi webhook ra ngoài: khi người nhận chậm hoặc chết** 🟡
Naive → gãy: gọi webhook đồng bộ trong luồng nghiệp vụ. Người nhận treo 30 giây, nghiệp vụ của bạn treo theo.
Đánh đổi: gửi qua queue với timeout ngắn và retry backoff là chuẩn, đổi lại thêm hạ tầng và phải quyết định retry bao lâu thì bỏ → tắt endpoint sau nhiều lần lỗi bảo vệ hệ thống bạn nhưng khách hàng có thể không biết vì sao mất dữ liệu → cho phép họ tự lấy lại lịch sử (endpoint replay) là tính năng đáng có, đổi lại thêm việc.
Demo: trỏ webhook tới một endpoint sleep 60 giây, xem hệ thống bạn bị ảnh hưởng gì.

---

# I. Caching (8 bài)

**93. Cache ở tầng nào: browser, CDN, app, hay DB** 🟡
Naive → gãy: thêm Redis cho mọi thứ vì "cache là nhanh". Nhiều dữ liệu đã được cache sẵn ở tầng khác, và giờ có thêm một nơi có thể lỗi thời.
Đánh đổi: cache càng gần người dùng càng nhanh và rẻ, nhưng càng khó invalidate (bạn không xóa được cache trong browser của người ta) → cache ở app thì kiểm soát hoàn toàn nhưng vẫn tốn round trip mạng → cache trong process nhanh nhất nhưng mỗi instance một bản, không nhất quán.
Demo: đo latency của cùng một dữ liệu ở bốn tầng.

**94. Invalidate cache: TTL hay theo sự kiện** 🟡
Naive → gãy: TTL 1 giờ cho mọi thứ. Dữ liệu quan trọng lỗi thời 1 giờ, dữ liệu ít đổi bị query lại vô ích mỗi giờ.
Đánh đổi: TTL đơn giản, không bao giờ rò rỉ vĩnh viễn, đổi lại luôn có cửa sổ dữ liệu cũ → invalidate theo event thì tươi ngay nhưng phải bắt được mọi đường ghi (sót một chỗ là cache sai mãi mãi) → kết hợp TTL ngắn + event là thực dụng nhất: event lo phần chính, TTL lo phần bạn sót.
Demo: cập nhật dữ liệu qua một đường ghi không có invalidate, xem cache sai bao lâu.

**95. Cache stampede: khi cache hết hạn và 1000 request cùng lao vào DB** 🔴
Naive → gãy: cache key phổ biến hết hạn đúng giờ cao điểm. Nghìn request cùng miss, cùng query DB, DB sập — và sập đúng lúc đông nhất.
Đánh đổi: lock để chỉ một request rebuild (đúng nhưng các request khác phải chờ, và phải xử lý khi kẻ giữ lock chết) → trả dữ liệu cũ trong lúc rebuild nền (UX tốt nhất nhưng phải chấp nhận stale và code phức tạp) → thêm jitter vào TTL để các key không hết hạn cùng lúc (rẻ nhất, hiệu quả bất ngờ).
Demo: bắn 500 request song song vào một key vừa hết hạn, đếm số query tới DB.

**96. Thiết kế cache key và nguy cơ rò rỉ dữ liệu giữa người dùng** 🔴
Naive → gãy: cache theo URL. Endpoint `/api/me` trả dữ liệu khác nhau theo token, nhưng cache key giống nhau — user A thấy dữ liệu của user B.
Đánh đổi: đưa userId/tenantId vào key thì an toàn nhưng hit rate thấp (mỗi user một bản) → không cache dữ liệu cá nhân hóa thì an toàn tuyệt đối nhưng mất lợi ích → cache phần chung riêng, phần riêng riêng, là đúng nhất nhưng phải tách response.
Demo: cache một endpoint có phân quyền theo URL, đăng nhập hai tài khoản và gọi.

**97. Redis là cache hay là nguồn dữ liệu thật** 🔴
Naive → gãy: lưu giỏ hàng chỉ trong Redis. Redis restart hoặc bị evict do hết memory, giỏ hàng của tất cả biến mất.
Đánh đổi: coi Redis là cache thì mất dữ liệu không sao, nhưng không dùng cho state quan trọng → coi Redis là nguồn thật thì phải bật persistence, phải backup, phải hiểu AOF/RDB đánh đổi ra sao, và phải biết `maxmemory-policy` đang evict cái gì → lưu ở DB và cache ở Redis thì an toàn nhưng chậm hơn.
Demo: đặt `maxmemory` nhỏ, đẩy nhiều key, xem key nào bị evict.

**98. HTTP cache header: ETag, Cache-Control, và ai thật sự tuân theo** 🟢
Naive → gãy: không đặt header nào, để mặc định. Browser cache theo phỏng đoán, và sau khi deploy user vẫn thấy JS cũ.
Đánh đổi: `no-store` luôn tươi nhưng mất hết lợi ích → `max-age` dài cho asset có hash trong tên là chuẩn (nhưng HTML phải ngắn) → ETag tiết kiệm băng thông vì trả 304, đổi lại vẫn tốn một round trip và server phải tính ETag. Cạm bẫy: proxy trung gian và CDN có thể bỏ qua hoặc hiểu khác header của bạn.
Demo: deploy phiên bản mới, hard refresh và refresh thường, xem file nào lấy từ cache.

**99. Cache response API ở CDN: khi nào được và khi nào là thảm họa** 🔴
Naive → gãy: bật CDN cache cho toàn bộ `/api/*` để giảm tải. Response có dữ liệu riêng của user bị cache và phục vụ cho người khác.
Đánh đổi: cache API công khai (danh sách sản phẩm, tỷ giá) ở CDN cực hiệu quả → nhưng phải chắc chắn không có gì phụ thuộc header xác thực, hoặc phải khai báo `Vary` đúng (và `Vary: Authorization` thì hit rate về gần 0) → tách hẳn đường dẫn public và private là cách an toàn nhất.
Demo: đặt CDN cache trước một endpoint trả dữ liệu theo token, gọi bằng hai token.

**100. Cache nội dung cá nhân hóa: tách phần chung ra** 🟡
Naive → gãy: trang chủ có tên user ở góc nên không cache được gì cả, dù 95% nội dung giống nhau cho mọi người.
Đánh đổi: cache toàn trang thì nhanh nhất nhưng không cá nhân hóa được → không cache thì linh hoạt nhưng chậm → cache phần chung và chèn phần riêng ở client (hoặc edge) cho cả hai lợi ích, đổi lại kiến trúc phức tạp hơn và có thể nháy nội dung khi phần riêng tải sau.
Demo: đo TTFB của trang cache toàn phần và trang có một phần cá nhân hóa.

---

# J. Realtime (6 bài)

**101. Polling, SSE, hay WebSocket** 🟡
Naive → gãy: chọn WebSocket vì "realtime thì phải WebSocket". Thông báo mỗi 30 giây một lần nhưng phải nuôi connection thường trực, xử lý reconnect, và scale phức tạp.
Đánh đổi: polling đơn giản nhất, hoạt động qua mọi proxy, dễ scale, đổi lại tốn request rỗng và độ trễ bằng chu kỳ → SSE một chiều nhẹ hơn WebSocket nhiều, dùng HTTP thường, đủ cho thông báo và cập nhật trạng thái, nhưng không gửi ngược được và giới hạn số connection trên HTTP/1.1 → WebSocket hai chiều thật sự cần cho chat và collaborative editing, đổi lại toàn bộ độ phức tạp về vận hành.
Demo: dựng cùng một tính năng thông báo bằng cả ba, so sánh số dòng code và tài nguyên.

**102. Xác thực cho WebSocket** 🔴
Naive → gãy: gửi token qua query string khi connect. Token lọt vào log của proxy và log của server.
Đánh đổi: token trong query string dễ làm nhất nhưng rò rỉ qua log → gửi token trong message đầu sau khi connect thì sạch hơn nhưng phải xử lý trạng thái "đã kết nối chưa xác thực" → cookie tự động gửi khi handshake là gọn nhất nhưng vướng CSRF-tương tự và cross-origin. Vấn đề khó hơn: token hết hạn giữa lúc connection đang mở thì làm gì?
Demo: mở WebSocket có token, đọc access log của Nginx.

**103. Scale WebSocket qua nhiều instance** 🟡
Naive → gãy: user A kết nối vào instance 1, user B vào instance 2. A gửi tin, B không nhận được vì instance 1 không biết B ở đâu.
Đánh đổi: Redis pub/sub adapter giải quyết đơn giản và phổ biến, đổi lại mọi message đi qua Redis (điểm nghẽn và điểm lỗi) → sticky session giữ user ở một instance nhưng làm lệch tải và vỡ khi instance restart → dùng dịch vụ realtime bên ngoài thì hết đau đầu nhưng thêm chi phí và phụ thuộc.
Demo: chạy 2 instance sau load balancer, mở hai client, thử gửi tin qua lại.

**104. Reconnect và những message bị mất trong lúc mất kết nối** 🟡
Naive → gãy: reconnect rồi tiếp tục như bình thường. Message trong 5 giây mất mạng biến mất, user không biết mình đã bỏ lỡ gì.
Đánh đổi: gửi lại từ last event ID thì không mất gì nhưng server phải giữ buffer message (tốn bộ nhớ, và bao lâu?) → fetch lại toàn bộ state sau reconnect thì đơn giản và luôn đúng, đổi lại tốn tải và có thể nặng → bỏ qua thì đơn giản nhất, chấp nhận được với dữ liệu chỉ mang tính hiện thời.
Demo: ngắt mạng 10 giây trong lúc có message gửi tới, xem client thấy gì sau khi nối lại.

**105. Thông báo: realtime và lưu trữ là hai việc khác nhau** 🟡
Naive → gãy: chỉ đẩy qua WebSocket. User offline lúc đó là không bao giờ thấy thông báo.
Đánh đổi: lưu DB rồi đẩy realtime là đúng nhưng phải xử lý trạng thái đã đọc ở hai nơi và tránh đếm trùng → chỉ lưu DB rồi để client poll thì đơn giản và không mất, đổi lại độ trễ → thêm push notification cho mobile thì tiếp cận được user đóng app, đổi lại một tích hợp nữa và vấn đề quyền.
Demo: gửi thông báo lúc client offline, mở lại và xem có thấy không.

**106. Trạng thái online: dữ liệu luôn sai một chút** 🟡
Naive → gãy: set online khi connect, offline khi disconnect. Mạng đứt mà không có disconnect event, user "online" mãi mãi.
Đánh đổi: heartbeat + TTL cho trạng thái tự hết hạn (đúng hơn, đổi lại có độ trễ vài chục giây và tốn traffic) → tin vào disconnect event thì rẻ nhưng sai trong trường hợp mất mạng đột ngột → hiển thị "hoạt động 5 phút trước" thay vì đèn xanh/đỏ là cách né vấn đề một cách thông minh.
Demo: rút mạng đột ngột (không đóng tab), xem trạng thái bao lâu mới đúng.

---

# K. Hạ tầng & triển khai (12 bài)

**107. Docker image từ 1.2GB xuống 80MB: cắt ở đâu** 🟢
Naive → gãy: `FROM node:latest`, `COPY . .`, `RUN npm install`. Image 1.2GB, chứa cả devDependencies, source map, và `.git`.
Đánh đổi: multi-stage build cắt được nhiều nhất mà không mất gì → alpine nhỏ hơn nhiều nhưng dùng musl thay glibc, một số native module vỡ và khó debug hơn → distroless nhỏ và an toàn nhất nhưng không có shell để vào xem khi có sự cố.
Demo: build image theo cả ba cách, so sánh size và thử `docker exec` vào từng cái.

**108. Layer cache: tại sao build lại mất 5 phút mỗi lần sửa một dòng** 🟢
Naive → gãy: `COPY . .` trước `npm install`. Sửa một dòng code là invalidate layer, cài lại toàn bộ dependency.
Đánh đổi: copy `package.json` trước rồi install rồi mới copy source — build nhanh hơn hẳn, gần như không có nhược điểm → cache mount của BuildKit nhanh hơn nữa nhưng cần BuildKit và không phải CI nào cũng giữ được cache → `.dockerignore` là thứ rẻ nhất mà nhiều người bỏ qua.
Demo: sửa một dòng code, đo thời gian build trước và sau khi sắp xếp lại Dockerfile.

**109. Docker Compose cho local và cho production: có nên dùng chung** 🟡
Naive → gãy: dùng cùng một `docker-compose.yml`. Local mount source để hot reload, production cũng mount — code trên host thành source of truth, image thành vô nghĩa.
Đánh đổi: file riêng cho từng môi trường thì rõ ràng nhưng dễ lệch nhau → một file với override thì DRY nhưng khó đọc → Compose ở production đơn giản và đủ cho nhiều dự án nhỏ, đổi lại không có rolling update, không tự phục hồi khi node chết.
Demo: chạy production compose và thử deploy phiên bản mới, đo downtime.

**110. Biến môi trường và secret: chỗ nào rò rỉ** 🔴
Naive → gãy: `.env` commit vào git (kể cả đã xóa sau, nó vẫn trong history). Hoặc dùng `ARG` trong Dockerfile cho secret — nó nằm trong image layer, ai pull image cũng đọc được.
Đánh đổi: env var đơn giản, phổ biến, nhưng hiện trong `docker inspect`, trong log crash, và trong danh sách process → file secret mount vào runtime an toàn hơn nhưng thêm bước vận hành → secret manager đúng nhất nhưng thêm phụ thuộc và phải xử lý khi nó không truy cập được. Riêng FE: mọi biến trong bundle đều công khai, không có ngoại lệ.
Demo: build image với `ARG SECRET`, chạy `docker history` và tìm lại giá trị đó.

**111. Health check: liveness và readiness là hai câu hỏi khác nhau** 🟡
Naive → gãy: một endpoint `/health` trả `200 OK` luôn. Container "khỏe" trong khi DB đã mất kết nối; load balancer vẫn gửi traffic vào.
Đánh đổi: health check kiểm tra cả DB thì chính xác nhưng khiến DB chậm làm container bị restart hàng loạt (làm sự cố tệ hơn) → check nông thì ổn định nhưng không phát hiện được lỗi thật → tách liveness (process còn sống không — nên nông) và readiness (có sẵn sàng nhận traffic không — nên sâu) là câu trả lời đúng, đổi lại phải hiểu và cấu hình hai thứ.
Demo: tắt DB, gọi health check, xem orchestrator phản ứng thế nào.

**112. Log: stdout, có cấu trúc, và tại sao đừng ghi vào file** 🟢
Naive → gãy: ghi log vào `/var/log/app.log` trong container. Container restart là mất, và không đọc được từ nhiều instance.
Đánh đổi: log ra stdout để nền tảng thu gom là chuẩn container, đơn giản, đổi lại phụ thuộc hệ thống thu gom bên ngoài → JSON có cấu trúc thì query được nhưng khó đọc bằng mắt khi dev local (giải pháp: pretty ở dev, JSON ở production) → log nhiều thì dễ debug nhưng tốn chi phí lưu trữ thật, và log rác che mất log quan trọng.
Demo: restart container và thử tìm lại log của lần chạy trước.

**113. Reverse proxy: 413, 504, và những giới hạn bạn không biết mình có** 🟢
Naive → gãy: upload file 50MB trả về `413 Request Entity Too Large`. Code app không có lỗi gì — Nginx mặc định `client_max_body_size 1m`.
Đánh đổi: nới giới hạn cho upload lớn thì tiện nhưng mở cửa cho tấn công gửi body khổng lồ → buffer request ở proxy bảo vệ app nhưng tốn disk và thêm độ trễ → stream trực tiếp thì nhanh hơn nhưng app phải chịu client chậm. Các con số phải biết: body size, proxy read timeout, keepalive timeout — và chúng phải khớp với timeout của app.
Demo: dựng Nginx mặc định, upload file 50MB và giữ một request 90 giây, ghi lại lỗi chính xác.

**114. API Gateway: nên có, và cái nó mang theo** 🟡
Naive → gãy: đặt gateway trước mọi thứ vì "kiến trúc chuẩn phải có gateway". Giờ mọi thay đổi route phải qua một nơi, và nó thành điểm lỗi duy nhất.
Đánh đổi: gateway tập trung được auth, rate limit, log, TLS — rất giá trị khi có nhiều service → đổi lại thêm một hop latency, thêm một thứ phải deploy và scale, và cấu hình sai ở gateway làm sập tất cả → không có gateway thì mỗi service tự lo (lặp lại code nhưng độc lập hoàn toàn). Với 1-2 service thì reverse proxy thường là đủ.
Demo: đo latency thêm vào khi có gateway, và thử cấu hình sai một route xem ảnh hưởng tới đâu.

**115. Khi nào Kubernetes là quá mức cần thiết** 🟡
Naive → gãy: dựng K8s cho một app có 200 người dùng. Ba tháng học cluster networking, ingress, PVC — thời gian đó không viết được tính năng nào.
Đánh đổi: K8s cho tự phục hồi, rolling update, scale ngang, hệ sinh thái lớn — đáng khi bạn có nhiều service và có người vận hành → đổi lại độ phức tạp rất lớn, chi phí cao hơn, và khả năng debug đòi hỏi kiến thức chuyên sâu → một VPS với Docker Compose và một script deploy phục vụ tốt hơn nhiều dự án hơn người ta thừa nhận.
Demo: đo thời gian từ zero tới "app chạy được ngoài internet" bằng K8s và bằng một VPS.

**116. Chi phí cloud: hóa đơn bất ngờ đến từ đâu** 🟡
Naive → gãy: deploy lên nền tảng serverless vì có free tier. Traffic tăng, hóa đơn tăng theo cách không đoán được — và phần lớn là egress bandwidth với function invocation, không phải compute.
Đánh đổi: serverless/PaaS rẻ khi nhỏ, không phải quản hạ tầng, scale tự động — đổi lại chi phí phi tuyến và khó dự đoán, cộng vendor lock-in → VPS thì chi phí phẳng và rẻ hơn nhiều ở mức trung bình, đổi lại bạn tự lo backup, bảo mật, uptime, và không tự scale. Ngưỡng chuyển đổi thường thấp hơn người ta nghĩ.
Demo: tính chi phí cho 100 nghìn request/ngày trên cả hai mô hình, gồm cả bandwidth.

**117. Monolith hay microservice: cái giá của việc tách quá sớm** 🟡
Naive → gãy: tách 6 service từ ngày đầu cho "dễ scale sau này". Team 4 người giờ phải quản 6 repo, 6 pipeline, và mọi tính năng cần sửa 3 service cùng lúc.
Đánh đổi: microservice cho phép scale và deploy độc lập, biên giới rõ — đáng khi team lớn và các phần có nhu cầu tài nguyên khác nhau → đổi lại mọi lời gọi hàm thành lời gọi mạng có thể lỗi, transaction thành saga, debug thành distributed tracing → modular monolith cho biên giới rõ ràng trong code mà không có chi phí phân tán, và tách ra sau khi biết chỗ nào thật sự cần.
Demo: đo thời gian từ commit tới production của một tính năng cần sửa 3 service.

**118. Backup: bạn đã bao giờ thử restore chưa** 🔴
Naive → gãy: bật snapshot tự động rồi coi như xong. Đến lúc cần thì phát hiện snapshot chỉ có 3 ngày, hoặc restore mất 6 giờ, hoặc backup thiếu một bảng.
Đánh đổi: backup thường xuyên thì RPO thấp nhưng tốn dung lượng và tải lên DB khi dump → chỉ snapshot thì nhanh nhưng không có point-in-time recovery → PITR cho phục hồi tới từng giây nhưng phức tạp hơn để cài và test. Điều quan trọng nhất: backup chưa từng restore thử không phải là backup.
Demo: restore backup mới nhất vào một môi trường sạch, đo thời gian và đối chiếu dữ liệu.

---

# L. Quan sát & gỡ lỗi (7 bài)

**119. Log cái gì và tuyệt đối không log cái gì** 🔴
Naive → gãy: log toàn bộ request body để dễ debug. Log giờ chứa mật khẩu, số thẻ, CMND — và log được gửi tới dịch vụ bên thứ ba.
Đánh đổi: log đầy đủ giúp debug nhanh nhưng tạo rủi ro tuân thủ và rò rỉ → redact theo danh sách field thì an toàn hơn nhưng luôn sót field mới → allowlist (chỉ log field được phép) an toàn nhất nhưng tốn công duy trì và có thể thiếu thông tin lúc cần.
Demo: gửi request đăng nhập, đọc log, tìm mật khẩu trong đó.

**120. Correlation ID: cách lần theo một request qua nhiều service** 🟡
Naive → gãy: mỗi service log riêng. Có sự cố, không cách nào ghép log của cùng một request lại với nhau.
Đánh đổi: tự truyền một `X-Request-ID` thì đơn giản, hiệu quả ngay, đổi lại phải nhớ truyền ở mọi lời gọi (sót một chỗ là mất dấu) → OpenTelemetry đầy đủ cho cả trace và span, thấy được thời gian ở từng bước, đổi lại setup nặng và overhead thật → async context (AsyncLocalStorage) tự động hóa được nhưng khó debug khi nó không hoạt động.
Demo: gọi qua 3 service, thử ghép log lại với và không có correlation ID.

**121. Metric nào đáng theo dõi: tại sao trung bình luôn nói dối** 🟡
Naive → gãy: theo dõi latency trung bình, thấy 200ms nên yên tâm. Thực tế 5% người dùng chờ 8 giây và họ chính là những người bỏ đi.
Đánh đổi: p50 cho biết trải nghiệm điển hình nhưng che mất phần đuôi → p95/p99 phản ánh trải nghiệm tệ nhất, đúng cái cần theo dõi, đổi lại nhiễu hơn với traffic thấp → theo dõi cả bốn thì đầy đủ nhưng nhiều biểu đồ và tốn chi phí lưu metric. Bộ tối thiểu đáng có: tỷ lệ lỗi, p95 latency, throughput, và độ sâu hàng đợi.
Demo: sinh tải có 5% request chậm, so sánh giá trị trung bình và p95.

**122. Alert: báo khi nào để không ai tắt thông báo** 🟡
Naive → gãy: alert mọi lỗi 500. Ngày 200 thông báo, hai tuần sau cả team mute channel — và sự cố thật đi qua không ai thấy.
Đánh đổi: alert theo triệu chứng người dùng cảm nhận (tỷ lệ lỗi vượt ngưỡng trong khoảng thời gian) thì ít nhiễu và đáng tin, đổi lại phát hiện muộn hơn → alert theo nguyên nhân (CPU cao, disk đầy) sớm hơn nhưng nhiều báo động giả → ngưỡng chặt bắt được nhiều hơn nhưng gây mệt mỏi. Nguyên tắc: mỗi alert phải kèm một hành động cụ thể, nếu không thì nó là dashboard chứ không phải alert.
Demo: đếm số alert trong một tuần và tự đánh giá bao nhiêu cái bạn đã thật sự làm gì.

**123. Lỗi chỉ xảy ra trên production: quy trình lần ra** 🟡
Naive → gãy: không tái hiện được nên bỏ qua, hoặc thêm log rồi deploy chờ lỗi xuất hiện lại — mỗi vòng lặp mất một ngày.
Đánh đổi: log nhiều hơn thì có dữ liệu nhưng chậm và tốn → capture đầy đủ context lúc lỗi (Sentry với breadcrumb, request payload đã redact) rút ngắn nhiều nhưng thêm phụ thuộc và chi phí → feature flag cho phép bật debug cho một user cụ thể, rất mạnh, đổi lại thêm hạ tầng flag. Nguyên nhân phổ biến nhất: khác biệt dữ liệu, khác biệt config, và điều kiện đồng thời — ba thứ local không có.
Demo: lấy một bug production đã fix, viết lại xem đã cần những thông tin gì để tìm ra.

**124. Feature flag: công cụ mạnh và món nợ nó tạo ra** 🟡
Naive → gãy: thêm flag cho mọi tính năng. Một năm sau có 60 flag, không ai biết cái nào còn dùng, và code có 2^60 đường đi trên lý thuyết.
Đánh đổi: flag cho phép deploy tách rời release, rollback tức thì, A/B test — rất giá trị → đổi lại mỗi flag là một nhánh code phải test, và flag không dọn là nợ tích lũy → cần quy tắc rõ: flag tạm thời phải có ngày hết hạn và người chịu trách nhiệm dọn.
Demo: đếm số flag trong dự án và số flag đã bật 100% từ hơn 3 tháng trước.

**125. Error tracking: sampling và tại sao bạn không cần mọi lỗi** 🟢
Naive → gãy: gửi mọi exception lên dịch vụ tracking. Một bug ở vòng lặp tạo 500 nghìn event trong một giờ, hết quota, và những lỗi khác bị chặn.
Đánh đổi: gom nhóm theo fingerprint giữ được thông tin mà không nhân bản, đổi lại nhóm sai thì che mất lỗi khác nhau → sampling giảm chi phí nhưng có thể bỏ sót lỗi hiếm mà quan trọng → rate limit theo loại lỗi bảo vệ quota tốt nhất nhưng cần cấu hình cẩn thận.
Demo: tạo một lỗi trong vòng lặp, xem dịch vụ tracking gom nhóm thế nào.

---

# M. Bảo mật ngoài xác thực (8 bài)

Toàn bộ nhóm này 🔴. Chỉ viết sau khi đã đọc nguồn gốc (OWASP) và tự dựng demo tấn công.

**126. CORS thật sự làm gì — và nó không bảo vệ API của bạn** 🔴
Naive → gãy: hiểu CORS là cơ chế bảo mật cho API. Thực ra nó bảo vệ *người dùng browser*, và `curl` hay Postman không quan tâm CORS chút nào.
Đánh đổi: `Access-Control-Allow-Origin: *` tiện cho API công khai nhưng không dùng được cùng credentials → whitelist origin cụ thể thì đúng nhưng phải quản danh sách → phản chiếu origin của request là lỗi phổ biến và nghiêm trọng (biến whitelist thành cho phép tất cả). Điều cốt lõi: CORS không thay thế cho việc kiểm tra quyền ở server.
Demo: gọi API bị CORS chặn bằng curl, xem nó vẫn trả dữ liệu.

**127. XSS: escape ở đâu và CSP giúp được gì** 🔴
Naive → gãy: sanitize input lúc lưu vào DB. Nhưng cùng một dữ liệu an toàn trong HTML lại nguy hiểm trong attribute, trong URL, trong JS — escape phụ thuộc ngữ cảnh *output*, không phải input.
Đánh đổi: escape lúc output theo ngữ cảnh là đúng đắn nhưng phải làm ở mọi chỗ (framework hiện đại làm sẵn, trừ khi bạn dùng `dangerouslySetInnerHTML`) → sanitize input thì mất dữ liệu gốc và vẫn không đủ → CSP là lớp phòng thủ sâu rất giá trị nhưng khó triển khai với inline script và third-party, và nhiều người đặt `unsafe-inline` làm nó gần như vô nghĩa.
Demo: dựng một form hiển thị lại input, thử payload trong ba ngữ cảnh khác nhau.

**128. SQL injection: ORM có bảo vệ hết không** 🔴
Naive → gãy: dùng ORM nên cho rằng miễn nhiễm. Rồi có một chỗ dùng raw query để tối ưu, hoặc truyền tên cột từ query param vào `ORDER BY` — ORM không tham số hóa được identifier.
Đánh đổi: parameterized query giải quyết giá trị nhưng không giải quyết tên bảng/cột động (phải whitelist) → query builder an toàn hơn raw nhưng vẫn có cửa nếu nối chuỗi → whitelist cho mọi identifier động là đúng nhưng phải kỷ luật. Cạm bẫy khác: `LIKE` với input chứa `%` và `_`.
Demo: tạo endpoint sort theo cột từ query param, thử truyền giá trị lạ.

**129. IDOR: lỗ hổng phổ biến nhất mà ít ai test** 🔴
Naive → gãy: `GET /api/orders/123` chỉ kiểm tra "đã đăng nhập chưa", không kiểm tra "đơn này có phải của bạn không". Đổi ID là xem được đơn của người khác.
Đánh đổi: check ownership ở mỗi endpoint thì đúng nhưng dễ sót một chỗ khi thêm endpoint mới → luôn query kèm điều kiện chủ sở hữu (`WHERE id = ? AND user_id = ?`) là mẫu tốt vì không thể quên → dùng UUID để "khó đoán" không phải là bảo vệ, chỉ là ngụy trang.
Demo: đăng nhập bằng tài khoản A, gọi mọi endpoint với ID của tài khoản B, ghi lại cái nào lọt.

**130. Secret rò rỉ: git history và bundle frontend** 🔴
Naive → gãy: commit API key rồi xóa ở commit sau. Nó vẫn nằm trong history vĩnh viễn, và repo public thì bot quét được trong vài phút.
Đánh đổi: rotate key là việc bắt buộc khi đã lộ (xóa file không đủ) → rewrite history xóa được nhưng phá mọi clone và không đảm bảo với fork → pre-commit hook quét secret là phòng ngừa tốt nhất, đổi lại có báo động giả. Về FE: mọi thứ trong bundle đều công khai, không có cách nào giấu — nếu cần secret thì phải có backend.
Demo: tìm secret trong `git log -p` của dự án, và tìm chuỗi cấu hình trong bundle production.

**131. Dependency: cái bạn không viết vẫn là code của bạn** 🔴
Naive → gãy: `npm install` bất cứ package nào giải quyết vấn đề. Một package nhỏ kéo theo 200 dependency, và một trong số đó bị chiếm quyền.
Đánh đổi: audit và cập nhật thường xuyên giảm rủi ro nhưng tốn thời gian và cập nhật có thể phá vỡ → khóa version (lockfile) đảm bảo tái lập nhưng đóng băng cả lỗ hổng → tự viết thay vì thêm dependency giảm bề mặt tấn công nhưng tốn công và có thể tự tạo bug. Điều đáng làm ngay: bật `npm ci` trong CI thay vì `npm install`.
Demo: chạy `npm ls --all | wc -l` và `npm audit`, xem con số thật của dự án.

**132. Upload file trở thành thực thi mã** 🔴
Naive → gãy: cho upload vào thư mục web root, giữ tên gốc. `shell.php` upload lên rồi truy cập trực tiếp — server thực thi nó.
Đánh đổi: đổi tên file thành ID ngẫu nhiên và bỏ đuôi do người dùng cung cấp là bước rẻ nhất, hiệu quả nhất → lưu ngoài web root hoặc ở object storage riêng domain thì cắt hẳn đường thực thi → serve với `Content-Type` cố định và `Content-Disposition: attachment` chặn thêm việc browser thực thi. Riêng SVG: là XML, chứa được script — cần xử lý riêng.
Demo: upload file `.svg` chứa script và mở nó trực tiếp trên domain của bạn.

**133. Mass assignment: khi user tự cấp quyền admin cho mình** 🔴
Naive → gãy: `User.update(req.body)` cho tiện. User gửi thêm `{"role": "admin"}` trong payload cập nhật profile.
Đánh đổi: whitelist field được phép cập nhật là đúng và bắt buộc, đổi lại phải khai báo và bảo trì ở mọi endpoint → DTO với validation (class-validator trong NestJS) tự động hóa việc này tốt nhưng cần cấu hình `whitelist: true` và `forbidNonWhitelisted` — mặc định không bật → blacklist field nguy hiểm thì luôn sót cái mới.
Demo: gửi thêm field ngoài DTO vào một endpoint update, xem có bị bỏ qua hay được ghi vào DB.

---

# Gợi ý lộ trình 6 tháng

Đừng viết theo thứ tự file này. Trình tự dưới đây tối ưu cho việc **xây uy tín từ vị trí chưa có nhiều kinh nghiệm production**:

**Tháng 1-2 — Toàn 🟢, tập trung nhóm B, F, D.** Upload file, index, N+1, EXPLAIN, phân trang, race condition ở search box. Đây là những bài dựng demo trong một buổi, sai thì hậu quả nhỏ, và người đọc gặp lại mãi. Mục tiêu giai đoạn này là **có số liệu thật của riêng bạn** trong mỗi bài.

**Tháng 3-4 — Thêm 🟡, mở sang nhóm C, E, K.** Thiết kế API, render strategy, Docker. Lúc này bạn đã có thói quen dựng demo trước khi viết, và đã có một tập bài để dẫn chiếu lẫn nhau — điều làm blog trông có chiều sâu.

**Tháng 5-6 — Bắt đầu 🔴 với nhóm A và M.** Token, phân quyền, IDOR, XSS. Để cuối vì hai lý do: bạn cần thời gian đọc OWASP tử tế, và bạn cần đã có uy tín từ các bài trước để cộng đồng góp ý thay vì bác bỏ.

**Nhóm G (transaction) để riêng.** Đây là nhóm khó nhất trong file và cũng ít bài viết tử tế nhất bằng tiếng Việt. Nếu bạn làm được nhóm này cẩn thận, nó là thứ khiến blog của bạn khác biệt hẳn — nhưng cần dựng được demo đồng thời thật (bắn request song song và đo kết quả), nên đừng làm khi chưa quen công cụ.
