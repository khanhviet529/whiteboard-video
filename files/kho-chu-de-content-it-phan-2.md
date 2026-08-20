# Kho chủ đề content IT — Phần 2 (bài 134-208)

Phần tiếp nối của `kho-chu-de-content-it.md`. Bổ sung 75 đề tài, tổng cộng 208.

## Điểm khác biệt của phần này

Phần 1 dùng một format duy nhất: **naive → gãy → chuỗi đánh đổi → demo**. Format đó hợp với bài toán có nhiều lựa chọn cạnh tranh nhau.

Phần 2 có thêm hai format nữa, vì không phải chủ đề nào cũng là bài toán lựa chọn:

**Format "Tại sao nó ra đời"** (nhóm N) — dùng cho công nghệ nền tảng. Cấu trúc: *bối cảnh trước đó → vấn đề cụ thể → cách nó giải quyết → cái nó KHÔNG giải quyết*. Phần cuối là phần quan trọng nhất và cũng là phần mọi bài "X là gì" đều thiếu.

**Format "Quy trình"** (nhóm O) — dùng cho công việc có nhiều bước. Cấu trúc: *mục tiêu → các bước → chỗ hay sai ở từng bước → mức tối thiểu chấp nhận được*.

Ký hiệu độ khó giữ nguyên: 🟢 dễ dựng demo, rủi ro thấp — 🟡 cần chuẩn bị — 🔴 rủi ro cao nếu viết sai.

---

# G+. Transaction & tiền: mở rộng (15 bài)

Đây là nhóm mình khuyên bạn nhắm tới lâu dài. Toàn bộ 🔴 hoặc 🟡 — nhưng cũng là nhóm trống nhất trong tiếng Việt, và là nhóm mà người đọc có kinh nghiệm sẽ nhớ tên bạn.

Điều kiện tiên quyết trước khi viết nhóm này: bạn phải dựng được **môi trường test đồng thời** — bắn N request song song và đo kết quả. Không có nó thì mọi bài trong nhóm này chỉ là lý thuyết đọc lại.

**134. Lost update: ba cách mất dữ liệu mà transaction không cứu được** 🔴
Naive → gãy: hai người mở form sửa cùng một bản ghi. Cả hai đọc thành công, cả hai ghi thành công, thay đổi của người trước biến mất — không có lỗi nào, không log nào.
Đánh đổi: read-modify-write trong transaction *không* chặn được lost update ở Read Committed (đây là chỗ hầu hết dev hiểu sai) → `SELECT FOR UPDATE` chặn được nhưng tuần tự hóa → cột version chặn được và không giữ khóa nhưng phải xử lý UX khi từ chối → cập nhật nguyên tử (`SET qty = qty - 1`) chặn được nhưng chỉ dùng cho phép toán, không dùng cho form phức tạp.
Demo: hai session psql, cùng đọc `qty`, cùng tính rồi cùng ghi. Chạy ở Read Committed và Repeatable Read, so sánh kết quả.

**135. Write skew: bug mà cả hai transaction đều "đúng" nhưng kết quả sai** 🔴
Naive → gãy: quy tắc "phải luôn có ít nhất 1 bác sĩ trực". Hai bác sĩ cùng xin nghỉ, mỗi transaction đọc thấy còn người kia trực nên cho phép. Kết quả: không ai trực. Không transaction nào ghi vào cùng một dòng, nên locking theo dòng không cứu được.
Đánh đổi: Serializable phát hiện và abort một trong hai (đúng nhất, đổi lại phải retry và giảm throughput) → materializing conflict (tạo một dòng đại diện cho ràng buộc để khóa) thì hoạt động ở isolation thấp hơn nhưng là hack khó hiểu cho người đọc code sau → kiểm tra ở tầng ứng dụng bằng khóa riêng thì tường minh nhưng dễ sót.
Demo: dựng đúng tình huống trên với hai session, chạy ở Repeatable Read và Serializable.

**136. Giữ hàng (reservation) khác với trừ hàng (deduction)** 🔴
Naive → gãy: trừ tồn kho ngay khi user bấm "đặt hàng". User không thanh toán, hàng bị giữ vĩnh viễn — hoặc trừ lúc thanh toán xong thì có thể hết hàng sau khi user đã trả tiền.
Đánh đổi: trừ ngay thì không bao giờ oversell nhưng cần job giải phóng đơn bỏ dở (và job đó chết là hàng bị giam) → trừ lúc thanh toán thì tồn kho luôn phản ánh thật nhưng phải xử lý tình huống hết hàng sau khi đã nhận tiền (hoàn tiền, xin lỗi) → reservation có TTL là mô hình đúng nhất cho thương mại điện tử, đổi lại thêm một trạng thái và một luồng hết hạn phải test.
Demo: đặt hàng rồi bỏ dở, đo bao lâu tồn kho được giải phóng.

**137. Thanh toán qua cổng bên thứ ba: transaction của bạn dừng ở đâu** 🔴
Naive → gãy: mở transaction DB, gọi API cổng thanh toán, commit sau khi có kết quả. API mất 8 giây, transaction giữ khóa 8 giây. Và nếu app crash sau khi cổng đã trừ tiền nhưng trước khi commit — tiền mất, đơn không có.
Đánh đổi: ghi trạng thái `pending` và commit *trước* khi gọi cổng, rồi cập nhật theo webhook — đúng nhất nhưng phải xử lý mọi trạng thái treo và đối soát định kỳ → giữ transaction qua lời gọi ngoài thì code thẳng nhưng sai về bản chất → không bao giờ có cách nào làm hai hệ thống nguyên tử tuyệt đối; chỉ có cách phát hiện và sửa lệch.
Demo: kill process ngay sau khi gọi cổng, xem hệ thống ở trạng thái nào.

**138. Đối soát: chấp nhận rằng hai hệ thống sẽ lệch** 🔴
Naive → gãy: tin rằng webhook luôn tới nên không cần đối soát. Webhook mất 0.1% và không ai phát hiện — cho tới lúc kế toán so sổ cuối tháng.
Đánh đổi: đối soát định kỳ (kéo báo cáo từ cổng, so với DB) là bắt buộc với hệ thống có tiền, đổi lại phải viết và duy trì job đó → tự động sửa lệch thì nhanh nhưng rủi ro sửa sai → chỉ báo động và để người xử lý thì an toàn nhưng cần người thật. Nguyên tắc: mọi hệ thống thanh toán đều lệch, khác nhau là bạn có biết hay không.
Demo: cố tình bỏ một webhook, viết script đối soát tìm ra bản ghi lệch.

**139. Hoàn tiền một phần và bài toán trạng thái đơn hàng** 🔴
Naive → gãy: trạng thái đơn là enum tuyến tính `pending → paid → shipped → done`. Rồi có hoàn một phần, đổi hàng, hủy một item trong đơn nhiều item — enum không diễn tả nổi.
Đánh đổi: state machine tường minh (khai báo transition được phép) thì kiểm soát được và tự tài liệu hóa, đổi lại nặng và phải sửa khi nghiệp vụ đổi → tách trạng thái thanh toán khỏi trạng thái giao hàng (hai trục độc lập) là đúng bản chất hơn nhưng nhiều người thấy phức tạp → lưu event thay vì trạng thái (đơn là tổng của các event) linh hoạt nhất nhưng đảo lộn cách truy vấn.
Demo: viết ra 10 kịch bản đơn hàng thực tế và thử biểu diễn bằng enum tuyến tính.

**140. Ledger: tại sao hệ thống tiền không UPDATE số dư** 🔴
Naive → gãy: `UPDATE accounts SET balance = balance - 100`. Số dư đúng, nhưng không biết vì sao thành số đó, không audit được, và một bug ghi sai là mất vĩnh viễn thông tin để sửa.
Đánh đổi: append-only ledger (chỉ ghi bút toán, số dư là tổng) cho audit trail hoàn hảo và sửa được sai sót bằng bút toán đảo, đổi lại tính số dư tốn kém khi nhiều bản ghi (cần snapshot định kỳ) → lưu balance trực tiếp thì đọc nhanh nhưng mất lịch sử → lưu cả hai (ledger là chân lý, balance là cache có kiểm tra) là mô hình thực tế của hầu hết hệ thống tài chính.
Demo: dựng ledger đơn giản, tính số dư từ 100 nghìn bút toán và đo thời gian.

**141. Double-entry: ràng buộc mà mọi giao dịch tiền phải thỏa** 🟡
Naive → gãy: trừ ví A, cộng ví B, hai câu UPDATE. Nếu một câu lỗi thì tiền bốc hơi hoặc sinh ra từ không khí — và không có cách nào phát hiện tự động.
Đánh đổi: double-entry (mọi giao dịch có tổng bằng 0) cho phép kiểm tra tính đúng đắn bất cứ lúc nào bằng một câu query, đổi lại mô hình dữ liệu phức tạp hơn và cần hiểu khái niệm kế toán → cách đơn giản thì dễ code nhưng không tự kiểm được. Với hệ thống có tiền, khả năng tự kiểm đáng giá hơn sự đơn giản.
Demo: viết query kiểm tra `SUM(amount) = 0` trên toàn bộ ledger, cố tình tạo bút toán lệch.

**142. Idempotency ở tầng nghiệp vụ, không chỉ tầng HTTP** 🔴
Naive → gãy: có idempotency key ở API nên tin là an toàn. Nhưng job trong queue retry cũng gọi cùng logic, và cron chạy hai lần cũng vậy — hai đường đó không đi qua tầng HTTP.
Đánh đổi: đặt kiểm tra idempotent ngay tại hàm nghiệp vụ thì bảo vệ mọi đường vào, đổi lại phải thiết kế khóa idempotent cho từng nghiệp vụ → chỉ ở API thì đơn giản nhưng để hở queue và cron → unique constraint ở DB là lớp cuối không thể vượt qua, nên có bất kể tầng trên đã làm gì.
Demo: gọi cùng một nghiệp vụ qua API, qua queue, và qua cron; xem có tạo trùng.

**143. Audit trail: ghi lại ai làm gì mà không phá hiệu năng** 🟡
Naive → gãy: viết trigger ghi mọi thay đổi vào bảng audit. Bảng audit lớn gấp năm lần bảng chính, và mọi UPDATE chậm đi.
Đánh đổi: trigger ở DB thì không thể bỏ sót nhưng không biết ngữ cảnh ứng dụng (user nào, request nào) và làm chậm đường ghi → ghi ở tầng ứng dụng thì đủ ngữ cảnh nhưng sót khi có ai sửa trực tiếp DB → CDC (đọc WAL) không ảnh hưởng đường ghi nhưng thêm hạ tầng. Câu hỏi phải trả lời trước: audit để tuân thủ, để debug, hay để hiển thị cho user?
Demo: đo thời gian UPDATE với và không có audit trigger trên bảng 1 triệu dòng.

**144. Job chạy lúc nửa đêm và giao dịch bắc qua hai ngày** 🟡
Naive → gãy: job tổng kết doanh thu "hôm qua" chạy lúc 00:05. Giao dịch lúc 23:59:58 commit lúc 00:00:01 — không nằm trong báo cáo nào.
Đánh đổi: lọc theo thời điểm commit thay vì thời điểm bắt đầu thì chính xác hơn nhưng nhiều DB không lưu sẵn → chạy job muộn hơn (01:00) giảm rủi ro nhưng không loại bỏ → đánh dấu bản ghi đã tính vào báo cáo nào là chắc chắn nhất, đổi lại thêm cột và thêm logic. Cộng thêm vấn đề múi giờ: "hôm qua" theo giờ nào?
Demo: tạo giao dịch với thời gian sát ranh giới ngày, chạy job và kiểm tra.

**145. Phân tán ID: tại sao auto-increment không dùng được ở nhiều nơi** 🟡
Naive → gãy: cần tạo ID trước khi ghi DB (để trả về cho client ngay, hoặc để ghi vào nhiều bảng cùng lúc). Auto-increment chỉ có ID sau khi insert.
Đánh đổi: UUID tạo được ở client nhưng tệ cho index → Snowflake/ULID sắp xếp theo thời gian và tạo được ở app, đổi lại phải quản machine ID và phụ thuộc đồng hồ hệ thống (đồng hồ chạy lùi là sinh ID trùng) → sequence riêng trong DB thì an toàn nhưng vẫn cần một round trip.
Demo: tạo 1 triệu ULID trong vòng lặp, kiểm tra tính duy nhất và thứ tự.

**146. Retry với thanh toán: chỗ nguy hiểm nhất của retry** 🔴
Naive → gãy: gọi cổng thanh toán timeout ở giây thứ 30, retry. Nhưng timeout không có nghĩa là thất bại — giao dịch có thể đã thành công. Retry thành trừ tiền hai lần.
Đánh đổi: không retry thì an toàn về trùng nhưng để lại giao dịch trạng thái không xác định → retry với idempotency key của cổng thì an toàn (nếu cổng hỗ trợ, phải đọc docs kỹ) → truy vấn trạng thái trước khi retry là cách đúng phổ quát nhất, đổi lại thêm một lời gọi và cổng có thể chưa cập nhật ngay.
Demo: mô phỏng timeout ở phía client trong khi server vẫn xử lý xong, xem hệ thống kết luận gì.

**147. Số dư âm: chuyện xảy ra khi hai lần trừ chạy song song** 🔴
Naive → gãy: `if (balance >= amount) { deduct() }`. Hai request song song đều thấy đủ, cả hai trừ. Số dư âm.
Đánh đổi: check constraint `balance >= 0` ở DB là lớp cuối không thể vượt (rẻ và tuyệt đối, đổi lại lỗi constraint phải xử lý thành thông báo tử tế) → `UPDATE ... WHERE balance >= amount` nguyên tử và kiểm tra qua số dòng ảnh hưởng → `SELECT FOR UPDATE` linh hoạt cho nghiệp vụ phức tạp nhưng tuần tự hóa điểm nóng. Với tiền, nên có cả hai lớp.
Demo: bắn 50 request rút tiền song song từ ví có số dư đủ cho 10 lần.

**148. Test tính đồng thời: cách dựng môi trường để chứng minh bug tồn tại** 🟡
Naive → gãy: viết unit test tuần tự rồi kết luận code an toàn. Bug đồng thời không bao giờ xuất hiện trong test tuần tự.
Đánh đổi: bắn N request song song bằng `k6`/`autocannon` thì tái hiện được bug thật nhưng không xác định (đôi khi pass đôi khi fail) → điều khiển thứ tự bằng hai kết nối DB thủ công thì xác định và chứng minh được chính xác vấn đề, đổi lại chỉ mô phỏng được tình huống đơn giản → thêm `pg_sleep` vào giữa read và write để mở rộng cửa sổ đua là mẹo rất hiệu quả để bug xuất hiện đều đặn.
Demo: viết một test tái hiện lost update thành công 100% số lần chạy.

---

# N. Tại sao công nghệ này ra đời (15 bài)

Format khác: **bối cảnh trước đó → vấn đề cụ thể → cách nó giải quyết → cái nó KHÔNG giải quyết**.

Phần cuối là phần quyết định giá trị bài viết. Mọi bài "X là gì" trên mạng đều dừng ở phần thứ ba. Người đọc có kinh nghiệm chỉ tin bạn khi bạn nói được cái công nghệ đó *không* làm được.

Lưu ý chung cho cả nhóm: đây là loại content **cạnh tranh cao** vì ai cũng viết. Chỉ viết nếu bạn làm được phần "không giải quyết" và phần bối cảnh lịch sử tử tế. Nếu không thì bỏ qua nhóm này, sang nhóm khác.

**149. Docker ra đời để giải quyết cái gì** 🟢
Bối cảnh: deploy bằng cách cài trực tiếp lên server. Server tồn tại nhiều năm, mỗi lần cài thêm phần mềm là thay đổi trạng thái không ai ghi lại — "snowflake server". Máy dev có Node 14, server có Node 12, thư viện hệ thống khác phiên bản.
Vấn đề: "chạy được trên máy tôi" không chuyển thành "chạy được trên server". Và không ai dựng lại được server giống hệt nếu nó chết.
Giải quyết: đóng gói app cùng toàn bộ dependency và cấu hình hệ thống thành một image bất biến. Dựng lại là chạy lại image, luôn giống nhau.
Cái nó KHÔNG giải quyết: không làm app nhanh hơn, không tự scale, không quản lý nhiều container (đó là việc của orchestrator), không giải quyết state và dữ liệu (volume vẫn là vấn đề riêng), và không phải máy ảo — container dùng chung kernel với host, nên khác biệt kernel vẫn ảnh hưởng.
Demo: chạy cùng một app trên máy có Node phiên bản khác, một lần trực tiếp một lần trong container.

**150. Container khác máy ảo ở đâu, và khi nào VM vẫn đúng** 🟢
Bối cảnh: ảo hóa bằng VM cho phép nhiều hệ điều hành trên một máy vật lý, nhưng mỗi VM mang cả một kernel và OS đầy đủ — nặng hàng GB, khởi động hàng chục giây.
Vấn đề: chạy 50 service nhỏ trên một máy bằng 50 VM là lãng phí khổng lồ.
Giải quyết: container dùng chung kernel host, chỉ cô lập bằng namespace và cgroup. Nhẹ hàng chục MB, khởi động dưới một giây.
Cái nó KHÔNG giải quyết: cô lập yếu hơn VM rõ rệt (chung kernel nghĩa là lỗ hổng kernel ảnh hưởng tất cả), không chạy được OS khác kernel (Windows container không chạy trên Linux host), và với multi-tenant không tin cậy nhau thì VM vẫn là lựa chọn đúng.
Demo: so sánh thời gian khởi động và RAM tiêu thụ của một VM nhỏ và một container.

**151. Kubernetes ra đời để giải quyết cái gì — và cái giá của nó** 🟡
Bối cảnh: đã có container, nhưng chạy 30 container trên 5 máy thì ai quyết định container nào chạy ở đâu? Máy chết thì ai khởi động lại? Deploy phiên bản mới mà không downtime thì làm sao?
Vấn đề: những việc trên làm tay được với 5 container, không làm tay được với 300.
Giải quyết: mô tả trạng thái mong muốn (declarative), K8s liên tục điều chỉnh thực tế về khớp với mong muốn — tự lên lịch, tự khởi động lại, tự rolling update.
Cái nó KHÔNG giải quyết: không làm app của bạn tốt hơn, không giải quyết state (database trong K8s vẫn là chủ đề gây tranh cãi), không giảm chi phí (thường tăng), và mang theo một lượng khái niệm khổng lồ phải học. Với một app và một database, nó gần như luôn là quá mức.
Demo: đếm số khái niệm phải hiểu để deploy một app đơn giản lên K8s so với lên VPS.

**152. Reverse proxy: tại sao không cho app nghe trực tiếp cổng 80** 🟢
Bối cảnh: app Node nghe cổng 3000. Muốn nó phục vụ internet ở cổng 80/443, và muốn nhiều app trên cùng một máy.
Vấn đề: một cổng chỉ một process nghe được; app không nên chạy bằng root để bind cổng thấp; và app không giỏi việc phục vụ file tĩnh, xử lý TLS, hay chịu client chậm.
Giải quyết: proxy nhận mọi request, phân phối theo domain/đường dẫn, xử lý TLS, nén, phục vụ file tĩnh, và cách ly app khỏi client.
Cái nó KHÔNG giải quyết: không phải load balancer đầy đủ (dù nhiều proxy làm được), không giải quyết auth hay rate limit theo nghiệp vụ, và bản thân nó thành điểm lỗi cần cấu hình đúng — sai một giới hạn là app trông như bị lỗi.
Demo: chạy hai app trên một máy sau một Nginx, phân biệt theo domain.

**153. Load balancer: các thuật toán và cái mỗi cái giả định** 🟡
Bối cảnh: một instance không chịu nổi tải, thêm instance thứ hai — nhưng client chỉ biết một địa chỉ.
Vấn đề: phải phân phối request, và phải biết instance nào còn sống.
Giải quyết: round robin đơn giản nhất; least connections tốt hơn khi request có thời lượng khác nhau; IP hash cho sticky session; weighted khi máy không đồng đều.
Cái nó KHÔNG giải quyết: không làm app stateless giúp bạn (session trong memory vẫn vỡ khi request rơi vào instance khác), không phát hiện được instance "sống nhưng sai" nếu health check nông, và round robin giả định mọi request tốn như nhau — giả định thường sai.
Demo: chạy 3 instance với một instance chậm hơn, so sánh round robin và least connections.

**154. CDN: cái nó tăng tốc và cái nó không** 🟢
Bối cảnh: server ở Singapore, user ở Hà Nội. Mỗi request đi 2000km, riêng độ trễ vật lý đã vài chục ms, và mỗi ảnh là một lượt đi về.
Vấn đề: với trang có 50 asset, độ trễ mạng chiếm phần lớn thời gian tải — không phải server chậm.
Giải quyết: đặt bản sao asset ở edge gần user. Request không phải đi tới origin.
Cái nó KHÔNG giải quyết: không tăng tốc nội dung động cá nhân hóa (mỗi user một kết quả thì không cache được), không sửa được API chậm, và mang theo bài toán invalidate — cộng nguy cơ cache sai dữ liệu riêng tư nếu cấu hình sai (xem bài 99).
Demo: đo thời gian tải một ảnh từ origin và từ CDN ở cùng một vị trí.

**155. HTTPS và TLS: chuyện gì xảy ra trong handshake** 🟡
Bối cảnh: HTTP gửi mọi thứ dạng rõ. Ai ở giữa đường (WiFi công cộng, ISP) đọc được và sửa được.
Vấn đề: cần ba thứ cùng lúc — bảo mật nội dung, xác thực đúng server, và phát hiện bị sửa đổi.
Giải quyết: bất đối xứng để trao đổi khóa và xác thực chứng chỉ, rồi chuyển sang đối xứng cho dữ liệu (nhanh hơn nhiều). Chain of trust qua CA.
Cái nó KHÔNG giải quyết: không che được bạn đang truy cập domain nào (SNI, DNS vẫn lộ), không bảo vệ dữ liệu sau khi tới server, không chống XSS hay SQL injection, và chứng chỉ hợp lệ không có nghĩa là site đáng tin — kẻ lừa đảo cũng có HTTPS.
Demo: bắt gói bằng Wireshark, so sánh HTTP và HTTPS, tìm xem còn thấy được gì.

**156. JWT: thiết kế cho vấn đề gì, và bị dùng sai thế nào** 🔴
Bối cảnh: session ID cần server tra cứu mỗi request. Với nhiều service độc lập, mỗi service phải hỏi chung một nơi.
Vấn đề: cần một cách để service tự xác minh danh tính mà không hỏi ai.
Giải quyết: token tự chứa thông tin và chữ ký. Service có public key là verify được, không cần lookup.
Cái nó KHÔNG giải quyết: không revoke được (đây là đặc tính, không phải bug), không bảo mật nội dung (payload chỉ base64, ai cũng đọc được — đừng để dữ liệu riêng trong đó), không giải quyết chỗ lưu ở client, và không phù hợp cho session web thông thường — nơi bạn có một backend và một database, session ID đơn giản hơn và tốt hơn.
Demo: lấy một JWT thật, decode payload bằng base64 mà không cần khóa gì.

**157. Message queue: tại sao không gọi trực tiếp** 🟡
Bối cảnh: service A gọi trực tiếp service B. B chậm thì A chậm theo; B chết thì A lỗi theo; B cần scale thì A phải biết địa chỉ mới.
Vấn đề: hai service dính chặt nhau về thời gian và về tính khả dụng.
Giải quyết: A ghi message rồi đi tiếp; B xử lý khi nào rảnh. B chết thì message chờ, không mất.
Cái nó KHÔNG giải quyết: không làm hệ thống đơn giản hơn (thêm một thành phần phải nuôi), không cho phản hồi ngay cho user, không đảm bảo thứ tự mặc định, và biến bug đồng bộ dễ thấy thành bug bất đồng bộ khó tái hiện. Thêm nữa: queue đầy vẫn là sự cố, chỉ là muộn hơn.
Demo: dựng cùng một luồng gọi trực tiếp và qua queue, tắt service đích ở cả hai.

**158. Redis: tại sao in-memory tạo khác biệt lớn** 🟢
Bối cảnh: mỗi lần cần dữ liệu đều query DB. Query đơn giản nhưng lặp hàng nghìn lần mỗi giây, và DB phải đọc disk, parse SQL, kiểm tra quyền.
Vấn đề: phần lớn dữ liệu đọc nhiều ghi ít, và độ trễ disk lớn hơn RAM hàng nghìn lần.
Giải quyết: lưu trong RAM, cấu trúc dữ liệu đơn giản, single-threaded nên không tốn chi phí đồng bộ. Độ trễ dưới 1ms.
Cái nó KHÔNG giải quyết: RAM đắt và hữu hạn (dataset lớn không nhét hết), không thay thế DB quan hệ (không join, không transaction đầy đủ, không query phức tạp), mất dữ liệu nếu không cấu hình persistence, và single-threaded nghĩa là một lệnh nặng (`KEYS *` trên triệu key) làm đứng toàn bộ.
Demo: chạy `KEYS *` trên 1 triệu key và đo độ trễ của các lệnh khác cùng lúc.

**159. ORM: giải quyết gì và tại sao nhiều người quay lại SQL** 🟡
Bối cảnh: viết SQL thủ công cho mọi truy vấn, tự map kết quả sang object, tự lo escape.
Vấn đề: lặp lại nhiều, dễ sai escape, và refactor schema là sửa hàng trăm chỗ rải rác.
Giải quyết: mô tả schema một lần, ORM sinh query, map object, và cho type safety.
Cái nó KHÔNG giải quyết: không giúp bạn hiểu DB (và che mất N+1, che mất query tệ), không diễn tả tốt query phức tạp (window function, CTE đệ quy — cuối cùng vẫn viết raw), thêm một tầng phải debug, và migration tự sinh thường không an toàn cho production. Xu hướng gần đây nghiêng về query builder — gần SQL hơn, ít trừu tượng hơn.
Demo: viết một báo cáo có group by nhiều tầng bằng ORM và bằng SQL, so sánh.

**160. Microservice: vấn đề thật nó giải quyết là về tổ chức** 🟡
Bối cảnh: monolith với 40 dev. Mỗi lần deploy phải đồng bộ cả team; một bug trong module thanh toán chặn release của module báo cáo.
Vấn đề: không phải kỹ thuật — là con người. Nhiều người sửa cùng một thứ và phải phối hợp.
Giải quyết: chia theo biên giới nghiệp vụ để mỗi team deploy độc lập, chọn công nghệ riêng, scale riêng.
Cái nó KHÔNG giải quyết: không làm code sạch hơn (monolith bừa tách ra thành nhiều service bừa), không tăng hiệu năng (thêm độ trễ mạng), và tạo ra hàng loạt vấn đề mới — distributed transaction, tracing, eventual consistency, quản lý version API nội bộ. Với team dưới 10 người, chi phí gần như luôn lớn hơn lợi ích.
Demo: đếm số bước để thêm một field xuyên 3 service so với trong monolith.

**161. GraphQL: vấn đề nó nhắm tới và cái nó đánh đổi** 🟡
Bối cảnh: REST với nhiều client khác nhau. Mobile cần ít field, web cần nhiều, mỗi màn hình cần một tổ hợp riêng.
Vấn đề: over-fetching (trả quá nhiều) và under-fetching (phải gọi nhiều lần), cộng việc backend phải làm endpoint riêng cho từng nhu cầu.
Giải quyết: client tự khai báo cần gì, một request trả đúng thứ đó.
Cái nó KHÔNG giải quyết: mất HTTP cache dễ dàng (mọi thứ là POST tới một endpoint), N+1 trở thành vấn đề nghiêm trọng cần DataLoader, khó rate limit (một query có thể nặng tùy ý — cần phân tích độ phức tạp), và error handling không dùng được HTTP status. Với một client duy nhất, REST thường đơn giản hơn và đủ.
Demo: viết một query GraphQL lồng sâu và đếm số query DB nó sinh ra.

**162. WebAssembly: chỗ nó thật sự đáng dùng** 🟡
Bối cảnh: JS là ngôn ngữ duy nhất chạy trong browser, và với tính toán nặng thì nó có giới hạn.
Vấn đề: xử lý ảnh/video, mã hóa, giả lập, tính toán khoa học trong browser quá chậm hoặc phải gửi lên server.
Giải quyết: bytecode chạy gần tốc độ native, biên dịch từ C/Rust/Go.
Cái nó KHÔNG giải quyết: không thay thế JS cho UI (truy cập DOM phải qua JS, và chi phí gọi qua ranh giới là thật), không làm app CRUD nhanh hơn (điểm nghẽn ở đó là mạng và DOM), bundle thường lớn hơn, và debug khó hơn nhiều. Nếu app của bạn chậm vì query DB thì WASM không giúp gì.
Demo: so sánh JS và WASM cho một phép tính nặng và cho một tác vụ cập nhật DOM.

**163. Git: mô hình dữ liệu bên dưới và tại sao lệnh git khó nhớ** 🟢
Bối cảnh: quản lý phiên bản tập trung (SVN) — mọi thao tác cần server, branch tốn kém, làm việc offline không được.
Vấn đề: branch đắt nghĩa là người ta không branch, nghĩa là mọi người làm chung một nhánh.
Giải quyết: mỗi commit là snapshot bất biến có hash; branch chỉ là con trỏ tới một commit — nên tạo branch gần như miễn phí. Mọi thứ local, không cần mạng.
Cái nó KHÔNG giải quyết: không quản lý file nhị phân lớn tốt (mỗi phiên bản là một bản đầy đủ — cần LFS), không giải quyết xung đột logic (chỉ xung đột văn bản), và giao diện dòng lệnh nổi tiếng khó vì nó phơi ra mô hình dữ liệu chứ không che đi. Hiểu mô hình (commit, tree, ref) làm mọi lệnh trở nên logic.
Demo: dùng `git cat-file` để đi từ một commit xuống tới nội dung file.

---

# O. Quy trình & vận hành thực tế (13 bài)

Format: **mục tiêu → các bước → chỗ hay sai → mức tối thiểu chấp nhận được**.

Nhóm này ít bài tử tế bằng tiếng Việt vì phần lớn nội dung chỉ dạy từng mảnh rời (cách cài Docker, cách viết Dockerfile) mà không ai nối lại thành một đường đi hoàn chỉnh. Đó chính là cơ hội.

**164. Từ code trên máy tới chạy ngoài internet: toàn bộ đường đi** 🟡
Mục tiêu: người đọc hiểu được *toàn bộ* chuỗi, không phải từng mảnh rời.
Các bước: code → commit → CI chạy test → build image → push registry → deploy lên server → reverse proxy nhận domain → TLS → DNS trỏ về → monitoring xác nhận.
Chỗ hay sai: nhảy thẳng vào Dockerfile mà không hiểu tại sao cần registry; deploy tay rồi không ghi lại được đã deploy commit nào; không có cách rollback; biến môi trường khác nhau giữa các môi trường mà không ai quản lý.
Mức tối thiểu: một lệnh deploy, một cách rollback, và biết được version nào đang chạy.
Demo: dựng toàn bộ chuỗi cho một app hello-world trên VPS 5 đô, ghi lại từng bước và thời gian.

**165. SSH: khóa, agent, config, và những thứ không nên làm** 🟢
Mục tiêu: dùng SSH đúng thay vì copy-paste lệnh.
Các bước: sinh keypair → copy public key lên server → tắt password auth → dùng `~/.ssh/config` để đặt tên ngắn → agent forwarding khi cần (và hiểu rủi ro của nó).
Chỗ hay sai: dùng mật khẩu root; để private key không passphrase trên máy chia sẻ; `chmod 777` thư mục `.ssh` (SSH sẽ từ chối); dùng cùng một key cho mọi server và mọi dịch vụ; agent forwarding tới server không tin cậy (server đó dùng được key của bạn).
Mức tối thiểu: key riêng cho từng mục đích, tắt password auth, và biết `ssh -v` để debug.
Demo: cấu hình một alias trong `~/.ssh/config`, tắt password auth và tự thử đăng nhập lại.

**166. Ba môi trường: local, staging, production — và cách chúng lệch nhau** 🟡
Mục tiêu: hiểu tại sao "chạy ổn ở staging" không đảm bảo gì.
Các bước: đồng nhất phiên bản runtime và DB → dữ liệu staging đủ giống thật về *hình dạng* (không phải kích thước) → cùng cách cấu hình → cùng cách deploy.
Chỗ hay sai: staging có 100 dòng dữ liệu, production có 10 triệu (nên N+1 và missing index không bao giờ lộ ở staging); staging không có TLS nên bug cookie `Secure` chỉ xuất hiện ở production; biến môi trường thiếu ở production và app dùng giá trị mặc định nguy hiểm.
Mức tối thiểu: staging cùng phiên bản runtime và DB, và dữ liệu đủ lớn để query chậm lộ ra.
Demo: seed staging bằng dữ liệu ẩn danh hóa từ production (chú ý: phải ẩn danh hóa thật, đây là rủi ro pháp lý).

**167. CI/CD: cái gì nên chạy ở CI và cái gì đừng** 🟡
Mục tiêu: pipeline nhanh mà vẫn đáng tin.
Các bước: lint + type check (nhanh, chạy trước) → unit test → build → integration test → deploy.
Chỗ hay sai: chạy toàn bộ e2e trên mọi commit làm pipeline 40 phút và cả team ngừng quan tâm; không cache dependency; test phụ thuộc thứ tự nên flaky; secret nằm trong log của CI; deploy tự động lên production mà không có cổng kiểm soát nào.
Mức tối thiểu: pipeline dưới 10 phút, và pipeline đỏ thì không merge được.
Demo: đo thời gian pipeline, tìm bước chậm nhất, thử cache dependency và đo lại.

**168. Domain, DNS, và SSL: chuỗi hay làm người ta mất một buổi chiều** 🟢
Mục tiêu: hiểu đủ để tự xử lý thay vì thử ngẫu nhiên.
Các bước: mua domain → trỏ A/CNAME record về IP → chờ propagate → Let's Encrypt xác thực quyền sở hữu → auto-renew.
Chỗ hay sai: không hiểu TTL nên đổi record rồi sốt ruột; dùng CNAME cho apex domain (không được phép); quên rằng Cloudflare proxy làm chứng chỉ origin thành chuyện khác; cài cert thủ công rồi ba tháng sau hết hạn vào cuối tuần.
Mức tối thiểu: auto-renew hoạt động và có cảnh báo trước khi cert hết hạn.
Demo: trỏ một subdomain, cài cert bằng certbot, rồi chạy `certbot renew --dry-run`.

**169. Deploy không downtime trên một con VPS** 🟡
Mục tiêu: làm được điều người ta tưởng phải có K8s mới làm được.
Các bước: chạy container mới song song → chờ health check pass → proxy chuyển traffic → tắt container cũ (drain connection trước).
Chỗ hay sai: `docker-compose down && up` (có downtime thật); chuyển traffic trước khi app sẵn sàng nhận; không drain nên request đang xử lý bị cắt; migration DB không tương thích ngược nên hai phiên bản chạy cùng lúc thì vỡ.
Mức tối thiểu: migration luôn tương thích ngược, và có health check thật.
Demo: deploy phiên bản mới trong lúc `autocannon` đang bắn tải, đếm số request lỗi.

**170. Rollback: kế hoạch mà ai cũng nói có nhưng ít ai thử** 🔴
Mục tiêu: quay lại được trong 5 phút thay vì debug 2 giờ lúc 2 giờ sáng.
Các bước: giữ image phiên bản trước → một lệnh chuyển về → xác nhận → thông báo.
Chỗ hay sai: rollback code nhưng migration DB đã chạy và không đảo được (đây là lý do migration phải tương thích ngược); dùng tag `latest` nên không biết quay về đâu; rollback rồi phát hiện dữ liệu đã bị phiên bản mới ghi theo format mới.
Mức tối thiểu: mọi migration chỉ thêm, không xóa, không đổi tên — trong cùng một release.
Demo: deploy phiên bản có migration, rollback, xem app cũ còn chạy được không.

**171. Log tập trung khi có nhiều instance** 🟡
Mục tiêu: tìm được log của một request bất kể nó rơi vào máy nào.
Các bước: app ghi JSON ra stdout → agent thu gom → gửi tới nơi lưu trữ có index → query theo correlation ID.
Chỗ hay sai: `docker logs` từng container bằng tay (không scale); không có correlation ID nên không ghép được; log rác chiếm 95% dung lượng làm chi phí tăng và tìm kiếm chậm; giữ log 2 năm mà không ai từng xem quá 7 ngày.
Mức tối thiểu: log có JSON, có request ID, và tìm kiếm được toàn văn.
Demo: dựng một stack log đơn giản, gọi một request qua 2 instance, tìm lại toàn bộ log của nó.

**172. Bảo mật một VPS trong 30 phút đầu** 🔴
Mục tiêu: mức tối thiểu trước khi mở cổng ra internet.
Các bước: tắt password auth và root login → firewall chỉ mở cổng cần → fail2ban → tự động cập nhật bản vá bảo mật → user riêng cho app (không phải root) → không chạy container với `--privileged`.
Chỗ hay sai: để cổng DB (5432, 6379) mở ra internet (Redis không mật khẩu bị chiếm trong vài giờ); chạy app bằng root; cài đủ thứ rồi không bao giờ update; tin rằng "server nhỏ không ai để ý" — bot quét toàn bộ IPv4 liên tục.
Mức tối thiểu: chỉ 22/80/443 mở, key-only SSH, và tự động cập nhật bản vá.
Demo: dựng VPS mới, chạy `ss -tlnp` xem thật sự cái gì đang nghe ra ngoài, và đọc log SSH sau 24 giờ để thấy số lần bị dò.

**173. Backup và khôi phục: quy trình đầy đủ có kiểm chứng** 🔴
Mục tiêu: có thể phục hồi thật, không chỉ có file backup.
Các bước: xác định RPO/RTO cần thiết → dump định kỳ + PITR nếu cần → lưu ở nơi khác máy chủ (và khác nhà cung cấp nếu quan trọng) → mã hóa → **test restore định kỳ** → tài liệu quy trình.
Chỗ hay sai: backup lưu trên cùng máy (máy chết là mất cả hai); backup không mã hóa để ở nơi công khai; chưa từng restore thử; quên backup những thứ không phải DB (file upload, cấu hình, secret).
Mức tối thiểu: một lần restore thử thành công, có ghi lại thời gian mất bao lâu.
Demo: restore backup vào môi trường sạch, so sánh số bản ghi từng bảng với bản gốc.

**174. Xử lý sự cố: 15 phút đầu nên làm gì** 🟡
Mục tiêu: có trình tự thay vì hoảng loạn.
Các bước: xác nhận có sự cố thật (không phải một người) → đánh giá phạm vi → **ưu tiên phục hồi trước tìm nguyên nhân** (rollback nếu vừa deploy) → thông báo → sau khi ổn định mới điều tra → viết lại sự việc.
Chỗ hay sai: debug nguyên nhân trong lúc user đang chịu ảnh hưởng; sửa trực tiếp production không qua git; không ai biết ai đang làm gì nên hai người sửa chồng nhau; không thông báo nên support ngập câu hỏi.
Mức tối thiểu: biết cách rollback, và có một chỗ để thông báo.
Demo: tự gây sự cố ở staging và bấm giờ xem mất bao lâu để phát hiện và phục hồi.

**175. Postmortem: viết để hệ thống tốt lên, không để tìm người sai** 🟡
Mục tiêu: sự cố tương tự không xảy ra lần hai.
Các bước: dòng thời gian sự việc → ảnh hưởng đo được → nguyên nhân (hỏi "tại sao" nhiều lớp) → hành động cụ thể có người phụ trách và deadline.
Chỗ hay sai: kết luận "do dev A bất cẩn" (không sửa được gì — người khác sẽ bất cẩn lần sau); hành động chung chung kiểu "cần cẩn thận hơn"; viết xong rồi không ai thực hiện hành động nào.
Mức tối thiểu: mỗi sự cố sinh ra ít nhất một thay đổi hệ thống ngăn nó lặp lại.
Demo: lấy một bug production đã fix và viết postmortem hồi tố cho nó.

**176. Onboarding: dựng được môi trường dev trong bao lâu** 🟢
Mục tiêu: người mới chạy được app trong một buổi sáng, không phải ba ngày.
Các bước: một lệnh dựng toàn bộ dependency (Docker Compose) → seed dữ liệu mẫu → tài liệu chỉ nói cái không tự động hóa được → có người trực để hỏi.
Chỗ hay sai: README lỗi thời hơn code; "cài Postgres rồi tạo database tên X" bằng tay; secret phải xin từng người; giả định người mới biết mọi quy ước ngầm.
Mức tối thiểu: `docker compose up` là chạy được, có dữ liệu mẫu.
Demo: xóa toàn bộ môi trường local, làm theo đúng README của mình, bấm giờ và ghi lại mọi chỗ vướng.

---

# P. Hash & mã hóa (10 bài)

Đúng yêu cầu của bạn: **giải thích cách hoạt động ở mức đủ hiểu, tập trung vào mỗi loại phù hợp bài toán nào**, không đi vào toán học.

Cả nhóm 🔴 hoặc 🟡. Đây là vùng dễ viết sai mà hậu quả nghiêm trọng — phải đọc nguồn gốc trước khi viết.

**177. Hash và mã hóa là hai thứ khác nhau** 🟡
Cách hoạt động: hash là một chiều (không có hàm ngược), mã hóa là hai chiều (có khóa thì giải được).
Dùng cho bài toán nào: mật khẩu → hash (bạn không cần biết mật khẩu gốc, chỉ cần so sánh); số thẻ, CMND, dữ liệu cần đọc lại → mã hóa; kiểm tra file có bị sửa → hash.
Chỗ hay sai: "mã hóa mật khẩu" (nếu giải được thì DB rò rỉ là mất hết); hash dữ liệu cần đọc lại rồi không lấy được ra; dùng base64 và gọi đó là mã hóa (base64 là encoding, ai cũng giải được).
Demo: hash và mã hóa cùng một chuỗi, thử lấy lại giá trị gốc từ cả hai.

**178. MD5 và SHA-1: tại sao không dùng cho bảo mật nữa** 🟡
Cách hoạt động: hàm hash đa dụng, thiết kế để nhanh — đó chính là vấn đề.
Dùng cho bài toán nào: MD5 vẫn ổn cho checksum phát hiện lỗi truyền file, dedupe file, cache key. Không dùng cho: mật khẩu, chữ ký, bất cứ gì cần chống kẻ tấn công có chủ đích.
Chỗ hay sai: hash mật khẩu bằng MD5 (GPU thử hàng tỷ lần/giây, và rainbow table có sẵn); dùng MD5 để xác minh file tải về không bị *cố ý* thay thế (collision attack đã khả thi từ lâu).
Demo: tra một MD5 của mật khẩu phổ biến trên trang tra cứu hash công khai, thấy nó ra ngay.

**179. SHA-256 nhanh — và tại sao nhanh là nhược điểm với mật khẩu** 🟡
Cách hoạt động: an toàn về collision, nhưng thiết kế để tính nhanh trên mọi phần cứng.
Dùng cho bài toán nào: chữ ký số, checksum, blockchain, HMAC, content addressing (git dùng SHA). Không dùng trực tiếp cho mật khẩu.
Chỗ hay sai: nghĩ "SHA-256 an toàn hơn MD5 nên dùng cho mật khẩu là ổn". An toàn về collision không liên quan tới chống brute force. Với mật khẩu, bạn cần hàm *chậm có chủ đích*.
Demo: đo số lần hash SHA-256 mỗi giây trên máy bạn, so với bcrypt cost 12.

**180. Salt và pepper: giải quyết vấn đề gì khác nhau** 🔴
Cách hoạt động: salt là giá trị ngẫu nhiên riêng cho từng mật khẩu, lưu cùng hash. Pepper là secret chung của hệ thống, lưu ngoài DB.
Dùng cho bài toán nào: salt chặn rainbow table và làm hai người cùng mật khẩu có hash khác nhau — bắt buộc phải có. Pepper thêm một lớp cho trường hợp DB rò rỉ mà secret không rò rỉ.
Chỗ hay sai: dùng cùng một salt cho mọi user (mất tác dụng); salt quá ngắn; nghĩ phải giấu salt (không cần, bcrypt lưu salt ngay trong chuỗi hash); pepper lưu cùng DB (vô nghĩa).
Demo: hash cùng một mật khẩu hai lần bằng bcrypt, so sánh kết quả và tìm salt trong chuỗi output.

**181. bcrypt: cách hoạt động và giới hạn 72 byte** 🔴
Cách hoạt động: hàm chậm có chủ đích, cost factor điều khiển số vòng lặp — cost tăng 1 là chậm gấp đôi. Salt tự sinh và nhúng trong output.
Dùng cho bài toán nào: hash mật khẩu ở phần lớn ứng dụng. Thư viện chín, hỗ trợ rộng, khó dùng sai.
Chỗ hay sai: không biết nó chỉ dùng 72 byte đầu (passphrase dài bị cắt âm thầm); cost quá thấp (dưới 10 hiện nay là yếu); cost quá cao thành cửa DoS ở endpoint login; pre-hash bằng SHA-256 để vượt giới hạn 72 byte mà không cẩn thận về null byte.
Demo: hash hai mật khẩu chỉ khác nhau từ ký tự thứ 73, xem có ra cùng hash.

**182. Argon2: tốn RAM có chủ đích, và ba tham số phải hiểu** 🔴
Cách hoạt động: ngoài thời gian, còn đòi hỏi bộ nhớ — làm việc tấn công bằng GPU/ASIC đắt hơn nhiều (GPU nhiều core nhưng ít RAM mỗi core).
Dùng cho bài toán nào: lựa chọn được khuyến nghị hiện nay cho mật khẩu, đặc biệt khi bạn kiểm soát được cấu hình server. Argon2id là biến thể nên dùng.
Chỗ hay sai: dùng tham số mặc định của thư viện mà không kiểm tra (có thư viện mặc định rất yếu); đặt memory cao rồi server hết RAM khi nhiều người login cùng lúc; chọn Argon2i hay Argon2d mà không hiểu khác biệt.
Demo: đo thời gian và RAM của Argon2id ở ba mức memory khác nhau, tính xem server chịu được bao nhiêu login đồng thời.

**183. Chọn hàm hash mật khẩu: bcrypt, argon2, hay scrypt** 🔴
Cách hoạt động: cả ba đều là "chậm có chủ đích", khác nhau ở loại tài nguyên chúng bắt kẻ tấn công phải trả.
Dùng cho bài toán nào: bcrypt khi ưu tiên độ chín của thư viện và môi trường hạn chế RAM; argon2id khi bạn tune được và muốn chống GPU tốt nhất; scrypt khi đã có sẵn trong hệ sinh thái.
Chỗ hay sai: chuyển thuật toán mà không có kế hoạch migrate (không thể re-hash mật khẩu vì bạn không có bản gốc — phải hash lại lúc user đăng nhập thành công lần tới); tin rằng chọn đúng thuật toán là đủ (mật khẩu yếu vẫn bị đoán bất kể hash gì).
Demo: viết luồng migrate: kiểm tra định dạng hash cũ, verify bằng thuật toán cũ, hash lại bằng thuật toán mới.

**184. HMAC: xác thực chứ không phải bảo mật** 🟡
Cách hoạt động: hash kết hợp với một khóa bí mật. Ai có khóa thì tạo và verify được; không có khóa thì không tạo được HMAC hợp lệ.
Dùng cho bài toán nào: xác minh webhook đến thật từ đối tác; chữ ký cho URL có thời hạn; kiểm tra dữ liệu không bị sửa khi đi qua client (ví dụ token trong cookie).
Chỗ hay sai: tự nối khóa với dữ liệu rồi hash (`sha256(key + data)`) — có lỗ hổng length extension, dùng HMAC chuẩn; so sánh HMAC bằng `==` (rò rỉ qua timing, phải dùng so sánh thời gian hằng); nghĩ HMAC che được nội dung (không, nội dung vẫn rõ).
Demo: verify webhook signature của một dịch vụ thật (Stripe, GitHub), rồi sửa một byte payload và xem verify thất bại.

**185. So sánh chuỗi bí mật: timing attack và cách tránh** 🔴
Cách hoạt động: so sánh `==` thoát ngay khi thấy byte đầu khác nhau. Thời gian phản hồi rò rỉ thông tin về việc bao nhiêu byte đầu đã đúng.
Dùng cho bài toán nào: mọi so sánh liên quan tới token, API key, HMAC, mã OTP.
Chỗ hay sai: cho rằng độ lệch nano giây không khai thác được (đã có nghiên cứu chứng minh khai thác được qua mạng với đủ số lần đo); dùng hàm so sánh thường trong code verify token; so sánh có early return cho độ dài khác nhau.
Demo: đo thời gian so sánh chuỗi khớp 0 byte đầu và khớp 30 byte đầu, chạy hàng triệu lần và vẽ phân bố.

**186. Sinh số ngẫu nhiên: `Math.random()` không dùng cho bảo mật** 🔴
Cách hoạt động: PRNG thường tối ưu cho tốc độ và phân bố, không cho tính không đoán được. CSPRNG lấy entropy từ hệ điều hành.
Dùng cho bài toán nào: token, mã OTP, session ID, salt, reset password → luôn dùng CSPRNG (`crypto.randomBytes`, `crypto.randomUUID`). Chọn màu ngẫu nhiên, xáo trộn danh sách hiển thị → PRNG thường là được.
Chỗ hay sai: `Math.random()` cho mã OTP (đoán được từ vài mẫu); dùng timestamp làm token; `Math.random().toString(36)` cho session ID; OTP 4 số không có rate limit (chỉ 10 nghìn khả năng).
Demo: sinh 1000 giá trị bằng `Math.random()` sau khi biết vài giá trị trước, thử tìm quy luật; so với `crypto.randomBytes`.

---

# Q. Giao diện mượt & hiệu năng cảm nhận (12 bài)

**Đây là nhóm mình đồng ý với bạn là thật sự ít người làm.** Lý do: nó đòi hỏi hiểu cả rendering pipeline của browser lẫn tâm lý cảm nhận của người dùng — hai thứ ít khi nằm cùng một người.

Toàn nhóm 🟢 hoặc 🟡, và demo đều dựng được trong browser với DevTools. Đây là nhóm có tỷ lệ **giá trị trên độ khó** tốt nhất trong cả hai file.

**187. 60fps nghĩa là bạn có 16ms cho mỗi frame** 🟢
Naive → gãy: animation giật mà không biết vì sao, thử ngẫu nhiên vài cách rồi bỏ.
Đánh đổi: hiểu ngân sách 16ms cho một frame là nền tảng — trong đó phải xong cả JS, style, layout, paint, composite. Tối ưu bằng cách bỏ bớt việc trong frame thì hiệu quả thật nhưng cần đo → chuyển việc sang requestIdleCallback hoặc web worker giữ main thread rảnh, đổi lại phức tạp và không phải việc nào cũng chuyển được.
Demo: mở Performance panel, quay lại một animation giật, tìm frame vượt 16ms và xem việc gì chiếm chỗ.

**188. Chỉ animate transform và opacity — và tại sao** 🟢
Naive → gãy: animate `width`, `top`, `margin` cho mượt. Mỗi frame buộc browser tính lại layout cho cả cây, rồi paint lại.
Đánh đổi: `transform` và `opacity` chỉ chạy ở tầng composite, GPU xử lý, không tính lại layout — mượt hơn hẳn. Đổi lại phải nghĩ lại cách viết animation (dùng `translate` thay `top`) và không phải hiệu ứng nào cũng biểu diễn được → animate thuộc tính layout thì tự do hơn nhưng chấp nhận giật ở thiết bị yếu.
Demo: animate `left` và `transform: translateX` cạnh nhau, bật "Paint flashing" và so sánh trên CPU throttle 4x.

**189. Layout thrashing: vòng lặp đọc-ghi làm trang đứng** 🟡
Naive → gãy: vòng lặp qua 100 phần tử, mỗi lần đọc `offsetHeight` rồi set `style.height`. Mỗi lần đọc sau khi ghi buộc browser tính lại layout đồng bộ — 100 lần reflow trong một frame.
Đánh đổi: gom tất cả lần đọc trước, rồi tất cả lần ghi sau (batching) là cách sửa gốc, đổi lại code khó đọc hơn → dùng `ResizeObserver`/`IntersectionObserver` thay vì tự đo thì tránh được hẳn vấn đề, đổi lại phải học API mới → tránh đọc kích thước hoàn toàn (dùng CSS) là tốt nhất khi làm được.
Demo: viết vòng lặp đọc-ghi xen kẽ trên 200 phần tử, xem "Recalculate Style" trong Performance panel, rồi gom lại và đo lại.

**190. Scroll jank: nguyên nhân và cách sửa** 🟢
Naive → gãy: gắn handler vào `scroll` để làm hiệu ứng. Handler chạy hàng chục lần mỗi giây trên main thread, scroll giật.
Đánh đổi: throttle bằng `requestAnimationFrame` giảm số lần chạy nhưng vẫn ở main thread → `IntersectionObserver` cho việc phát hiện phần tử vào viewport thì chạy ngoài main thread, hiệu quả hơn hẳn, nhưng không thay được mọi trường hợp → CSS thuần (`position: sticky`, `scroll-snap`, animation theo scroll của CSS) là nhanh nhất nhưng ít linh hoạt. Thêm: `passive: true` cho touch listener là thay đổi một dòng có tác dụng thật.
Demo: gắn một handler nặng vào scroll, đo FPS, rồi chuyển sang IntersectionObserver.

**191. CLS: layout dịch chuyển và cách chặn từng nguyên nhân** 🟢
Naive → gãy: ảnh không có kích thước, banner quảng cáo chèn vào sau, font đổi — nội dung nhảy khi user đang đọc hoặc đang định bấm.
Đánh đổi: đặt `width`/`height` hoặc `aspect-ratio` cho mọi ảnh là bắt buộc và gần như không có nhược điểm → dành sẵn chỗ cho nội dung tải sau thì hết nhảy nhưng có khoảng trống lúc đầu → chèn nội dung chỉ ở dưới viewport thì không ảnh hưởng CLS nhưng hạn chế thiết kế.
Demo: đo CLS trước và sau khi thêm `aspect-ratio` cho ảnh, trên mạng chậm.

**192. Hiệu năng cảm nhận: nhanh và cảm giác nhanh là hai chỉ số** 🟡
Naive → gãy: tối ưu tổng thời gian tải nhưng user vẫn nói app chậm. Vì họ cảm nhận theo *thời điểm thấy phản hồi đầu tiên*, không theo tổng thời gian.
Đánh đổi: phản hồi ngay lập tức cho hành động (skeleton, optimistic UI, đổi trạng thái nút) làm cảm giác nhanh hơn dù tổng thời gian không đổi — rẻ và hiệu quả → nhưng phản hồi giả tạo mà sau đó thất bại thì phá niềm tin → tối ưu thật thì bền nhưng đắt hơn nhiều. Nguyên tắc: dưới 100ms là cảm giác tức thì, trên 1s cần chỉ báo, trên 10s cần cho user làm việc khác.
Demo: thêm phản hồi tức thì vào một hành động chậm 2 giây, cho vài người thử và hỏi cảm nhận về tốc độ.

**193. Skeleton, spinner, hay không gì cả** 🟢
Naive → gãy: skeleton cho mọi thứ. Với request 200ms, skeleton chỉ nháy một cái — gây cảm giác lộn xộn hơn là không có gì.
Đánh đổi: không hiện gì trong 200ms đầu (delay trước khi hiện loading) là mẹo hiệu quả cho request nhanh → skeleton giữ layout và đáng cho nội dung có hình dạng đoán được, đổi lại phải làm và bảo trì → spinner nhanh làm nhưng mất ngữ cảnh và không giảm được cảm giác chờ.
Demo: cùng một request 150ms, so sánh có skeleton, có delay 200ms rồi mới hiện, và không có gì.

**194. Danh sách dài nhưng vẫn mượt: ngoài virtualize còn gì** 🟡
Naive → gãy: chỉ nghĩ tới virtualize. Nhưng nhiều trường hợp vấn đề không phải số phần tử mà là mỗi phần tử quá nặng.
Đánh đổi: virtualize giảm số node nhưng mất Ctrl+F và khó với chiều cao động (xem bài 53) → `content-visibility: auto` là một dòng CSS cho browser tự bỏ qua phần ngoài viewport, hiệu quả bất ngờ, đổi lại hỗ trợ không đồng đều và ảnh hưởng scrollbar → làm nhẹ từng item (bỏ shadow phức tạp, bỏ ảnh không cần) thường cho kết quả tốt hơn cả virtualize.
Demo: render 2000 item, thử virtualize và thử `content-visibility: auto`, so sánh FPS và thời gian render đầu.

**195. Transition và micro-interaction: khi nào thêm giá trị, khi nào gây chậm** 🟢
Naive → gãy: thêm transition 500ms cho mọi thứ vì "trông mượt". Mọi tương tác giờ mất nửa giây, app cảm giác chậm hơn dù không chậm hơn.
Đánh đổi: transition ngắn (100-200ms) cho phản hồi tức thì thì tăng cảm giác chất lượng → transition dài phù hợp cho chuyển cảnh lớn (mở modal) nhưng cản trở tương tác nhanh lặp lại → không transition thì nhanh nhất nhưng thay đổi đột ngột khó theo dõi bằng mắt. Bắt buộc phải có: tôn trọng `prefers-reduced-motion`.
Demo: đặt transition 500ms lên một nút bấm nhiều lần, cảm nhận sự cản trở; giảm về 120ms và so sánh.

**196. Font: subset, preload, và fallback đo được** 🟡
Naive → gãy: tải font đầy đủ với mọi ký tự Unicode. Font Latin + Việt + Cyrillic + Greek nặng gấp ba lần cần thiết.
Đánh đổi: subset chỉ ký tự cần dùng (tiếng Việt cần dải riêng — nhiều font không có sẵn) giảm dung lượng nhiều nhất, đổi lại phải tự xử lý và cẩn thận với nội dung do user nhập → `size-adjust` và `ascent-override` cho fallback khớp kích thước font thật, gần như xóa được CLS do font, đổi lại phải đo và tune thủ công.
Demo: subset một font cho tiếng Việt, so sánh dung lượng và kiểm tra ký tự có dấu không bị thiếu.

**197. Web Vitals: đo ở lab và đo ở người dùng thật** 🟡
Naive → gãy: Lighthouse điểm 98 nên kết luận app nhanh. Người dùng thật trên điện thoại tầm trung với 4G thấy khác hoàn toàn.
Đánh đổi: lab test (Lighthouse) tái lập được và dùng trong CI để chống hồi quy, đổi lại không phản ánh thực tế đa dạng → RUM (đo từ người dùng thật) cho sự thật nhưng cần hạ tầng thu thập và chỉ biết sau khi đã phát hành → throttle CPU 4x và mạng chậm trong lúc dev là cách rẻ nhất để tiếp cận thực tế.
Demo: chạy Lighthouse, rồi chạy lại với CPU throttle 4x và Slow 4G, so sánh điểm.

**198. Accessibility và hiệu năng cảm nhận đi cùng nhau** 🟡
Naive → gãy: coi accessibility là việc riêng làm sau. Nhưng focus management kém, thiếu trạng thái loading cho screen reader, và animation không tắt được là những thứ làm app *cảm giác* hỏng với mọi người, không chỉ người khuyết tật.
Đánh đổi: làm đúng từ đầu (semantic HTML, focus trap trong modal, `aria-live` cho thông báo) gần như miễn phí → thêm vào sau thì đắt và thường làm nửa vời → `prefers-reduced-motion` là một media query nhưng là khác biệt lớn với người bị say chuyển động.
Demo: dùng app của bạn chỉ bằng bàn phím, và một lần với screen reader bật.

---

# R. SEO kỹ thuật (10 bài)

Về nhận định "ít người làm": SEO nói chung thì rất nhiều bài, nhưng gần hết là **SEO nội dung** (từ khóa, backlink) do người làm marketing viết. **SEO kỹ thuật cho dev** — render, crawl budget, structured data, i18n — thì đúng là thiếu người viết, vì nó đòi hỏi hiểu cả frontend lẫn cách crawler hoạt động.

Cảnh báo: SEO là vùng thuật toán thay đổi liên tục và nhiều thông tin trên mạng đã lỗi thời. Chỉ dẫn nguồn từ tài liệu chính thức của Google Search Central, và ghi rõ thời điểm bạn kiểm tra.

**199. Crawler thấy gì: render và index là hai bước riêng** 🟡
Naive → gãy: tin rằng Google chạy JS nên SPA không cần làm gì. Google có hai đợt — crawl HTML trước, render JS sau (có thể muộn nhiều ngày), và render có thể bị bỏ nếu tốn tài nguyên.
Đánh đổi: SSR đưa nội dung vào HTML đầu tiên nên chắc chắn được thấy, đổi lại hạ tầng → prerender cho crawler thì rẻ hơn nhưng phải cẩn thận không phục vụ nội dung khác người dùng → chỉ CSR thì có thể index được nhưng chậm và không đảm bảo, và các crawler khác (mạng xã hội, AI, công cụ nhỏ) thường không chạy JS.
Demo: `curl` trang của bạn và tìm nội dung chính trong HTML thô.

**200. Crawl budget: tại sao Google không index hết site của bạn** 🟡
Naive → gãy: site 500 nghìn trang, chỉ 30 nghìn được index, không hiểu vì sao. Phần lớn crawl budget bị đốt vào trang lọc trùng lặp (`?color=red&size=m` sinh ra vô số URL cùng nội dung).
Đánh đổi: `robots.txt` chặn crawl thì tiết kiệm budget nhưng trang bị chặn không truyền được tín hiệu link → `noindex` cho phép crawl mà không index (tốn budget nhưng đúng hơn cho trang cần đi qua) → canonical gom trùng lặp nhưng chỉ là gợi ý, Google có thể bỏ qua. Phân biệt ba cái này là nội dung cốt lõi của bài.
Demo: xem báo cáo Crawl Stats và Pages trong Search Console, tìm loại URL đốt nhiều crawl nhất.

**201. Canonical: gợi ý chứ không phải lệnh** 🟡
Naive → gãy: đặt canonical rồi tin là xong. Nhưng nếu canonical trỏ tới trang có nội dung khác, hoặc chuỗi canonical vòng, hoặc canonical trỏ tới trang `noindex` — Google bỏ qua và tự chọn.
Đánh đổi: canonical tự trỏ về chính nó trên mọi trang là mặc định an toàn → canonical xuyên domain hợp nhất được nội dung syndicate nhưng mất kiểm soát → 301 redirect là tín hiệu mạnh hơn canonical nhiều, dùng khi thật sự muốn hợp nhất.
Demo: kiểm tra "Google-selected canonical" trong URL Inspection cho vài trang, so với canonical bạn khai.

**202. Structured data: cái gì thật sự sinh rich result** 🟢
Naive → gãy: thêm mọi loại schema có thể vì "càng nhiều càng tốt". Phần lớn không sinh ra hiển thị đặc biệt nào, và schema sai gây lỗi trong Search Console.
Đánh đổi: JSON-LD được khuyến nghị và dễ quản lý nhất → microdata nằm trong HTML nên khó lệch với nội dung hiển thị, đổi lại rối markup → chỉ làm loại schema có rich result thật (Product, FAQ, Article, Breadcrumb, LocalBusiness) thì hiệu quả rõ, đổi lại phải theo dõi vì Google thay đổi loại nào được hỗ trợ. Quy tắc cứng: structured data phải khớp nội dung người dùng thấy.
Demo: chạy Rich Results Test trên một trang sản phẩm, sửa lỗi, và xem lại sau khi Google crawl lại.

**203. Sitemap và robots.txt: vai trò thật của mỗi cái** 🟢
Naive → gãy: liệt kê mọi URL vào sitemap và tin rằng Google sẽ index hết. Sitemap là gợi ý phát hiện URL, không phải cam kết index.
Đánh đổi: sitemap đầy đủ giúp phát hiện trang mới nhanh, đặc biệt với site lớn hoặc ít link nội bộ → sitemap chứa URL `noindex` hoặc lỗi 404 làm giảm độ tin cậy của cả sitemap → chia nhiều sitemap theo loại nội dung giúp chẩn đoán tốt hơn trong Search Console, đổi lại thêm việc.
Demo: so sánh số URL trong sitemap với số URL được index trong Search Console, tìm nguyên nhân chênh lệch.

**204. Core Web Vitals ảnh hưởng xếp hạng tới đâu** 🟡
Naive → gãy: dồn toàn lực tối ưu điểm Lighthouse và mong xếp hạng nhảy vọt. Web Vitals là tín hiệu xếp hạng nhưng yếu hơn nhiều so với mức độ khớp nội dung.
Đánh đổi: tối ưu Web Vitals có giá trị thật cho tỷ lệ chuyển đổi và người dùng — đó mới là lý do chính đáng → nhưng đầu tư nó thay cho nội dung tốt là sai thứ tự ưu tiên. Google dùng dữ liệu từ người dùng thật (CrUX), không dùng điểm Lighthouse của bạn — nên tối ưu cho lab test có thể không đổi gì.
Demo: so sánh điểm Lighthouse với dữ liệu CrUX thật của site trong Search Console.

**205. URL, redirect, và di chuyển site không mất thứ hạng** 🔴
Naive → gãy: đổi cấu trúc URL cho đẹp hơn, không redirect. Toàn bộ thứ hạng và backlink của URL cũ mất, traffic tụt và mất nhiều tháng để hồi phục.
Đánh đổi: 301 truyền phần lớn tín hiệu và là lựa chọn đúng cho di chuyển vĩnh viễn → 302 giữ URL cũ trong index, dùng cho tạm thời → chuỗi redirect nhiều bước làm mất tín hiệu và tốn crawl budget, phải map trực tiếp. Với site lớn, di chuyển theo lô để phát hiện vấn đề sớm.
Demo: dựng một map redirect cho 20 URL, kiểm tra không có chuỗi nào dài hơn 1 bước bằng `curl -IL`.

**206. Trang phân trang, lọc, và nội dung trùng lặp** 🟡
Naive → gãy: mỗi tổ hợp filter là một URL index được. Site 1000 sản phẩm sinh ra 200 nghìn URL nội dung gần giống nhau.
Đánh đổi: `noindex` trang lọc thì gọn index nhưng mất cơ hội xếp hạng cho từ khóa dài (một số trang lọc có nhu cầu tìm kiếm thật) → chọn lọc: index một số tổ hợp giá trị, chặn phần còn lại — đúng nhất nhưng cần phân tích từ khóa → dùng fragment hoặc POST cho filter thì crawler không thấy, đổi lại mất khả năng share URL.
Demo: đếm số URL duy nhất mà crawler có thể tới được từ trang danh mục của bạn.

**207. Đa ngôn ngữ: hreflang và những lỗi phổ biến** 🟡
Naive → gãy: có bản tiếng Việt và tiếng Anh nhưng không khai hreflang. Google coi hai trang là trùng lặp và chọn một, hoặc hiển thị sai ngôn ngữ cho người dùng.
Đánh đổi: hreflang phải khai *hai chiều* (trang A trỏ B thì B phải trỏ A) — sót một chiều là bị bỏ qua → tự động chuyển ngôn ngữ theo IP thì tiện cho user nhưng chặn crawler thấy các bản khác → subdomain, subdirectory, hay ccTLD: subdirectory dễ nhất và tập trung được uy tín domain, ccTLD tín hiệu địa phương mạnh nhất nhưng như dựng site mới từ đầu.
Demo: kiểm tra hreflang hai chiều trên site đa ngôn ngữ, tìm trang thiếu chiều ngược.

**208. SEO cho thị trường Việt Nam: khác biệt cần biết** 🟡
Naive → gãy: áp dụng nguyên lời khuyên SEO tiếng Anh. Nhưng người Việt tìm kiếm không dấu rất nhiều, hành vi tìm trên Facebook và TikTok đáng kể, và tỷ lệ dùng điện thoại rất cao.
Đánh đổi: tối ưu cho cả từ khóa có dấu và không dấu (nội dung có dấu, nhưng URL và alt nên không dấu) → mobile-first là bắt buộc chứ không phải tùy chọn → nội dung tiếng Việt chất lượng còn ít trong nhiều lĩnh vực kỹ thuật, nên cơ hội xếp hạng cao hơn thị trường tiếng Anh nhiều. Đây chính là lợi thế của việc bạn viết tiếng Việt.
Demo: tra vài từ khóa kỹ thuật bằng tiếng Việt, xem chất lượng top 10 — thường là chỗ bạn thấy cơ hội rõ nhất.

---

# Tổng kết hai file: 208 đề tài

| Nhóm | Bài | Đặc điểm |
|---|---|---|
| A. Xác thực & phiên | 1-14 | Hút người đọc nhất, rủi ro cao nhất |
| B. Upload & media | 15-24 | Dễ demo, nên bắt đầu ở đây |
| C. Thiết kế API | 25-36 | Nhiều lựa chọn, ít bài phân tích tử tế |
| D. FE dữ liệu & state | 37-46 | Rất nhiều người gặp |
| E. FE render & hiệu năng | 47-56 | Cạnh tranh trung bình |
| F. Database | 57-72 | Evergreen nhất, demo dễ |
| G. Transaction | 73-82 | Khó nhất, trống nhất |
| G+. Transaction & tiền | 134-148 | Sâu hơn nữa, cần môi trường test đồng thời |
| H. Job & queue | 83-92 | Ít bài tiếng Việt |
| I. Caching | 93-100 | Nhiều bẫy bảo mật ít ai nói |
| J. Realtime | 101-106 | Người ta hay chọn sai công cụ |
| K. Hạ tầng & deploy | 107-118 | Nhu cầu cao |
| L. Quan sát & debug | 119-125 | Ít ai viết, giá trị cao cho dev đi làm |
| M. Bảo mật | 126-133 | Rủi ro cao, phải đọc OWASP |
| N. Tại sao ra đời | 149-163 | Cạnh tranh cao — chỉ viết nếu làm được phần "không giải quyết" |
| O. Quy trình & vận hành | 164-176 | Ít bài nối được toàn chuỗi |
| P. Hash & mã hóa | 177-186 | Rủi ro cao, nhu cầu cao |
| Q. Giao diện mượt | 187-198 | **Tỷ lệ giá trị/độ khó tốt nhất** |
| R. SEO kỹ thuật | 199-208 | Trống với đối tượng dev |

## Nếu chỉ chọn ba nhóm để bắt đầu

**Nhóm Q (giao diện mượt)** — demo hoàn toàn trong browser với DevTools, không cần server, không cần dữ liệu lớn. Rủi ro viết sai gần như không. Và gần như không có ai viết nhóm này bằng tiếng Việt cho dev.

**Nhóm F (database)** — dựng được bằng Docker và một script seed. Evergreen tuyệt đối, người đọc gặp lại suốt sự nghiệp.

**Nhóm B (upload)** — bạn đã tự nghĩ ra chủ đề này, nghĩa là bạn có cảm nhận đúng về nó. Demo chỉ cần Nginx và vài file lớn.

Ba nhóm này cho bạn khoảng 40 bài — đủ 8-10 tháng nếu đăng mỗi tuần một bài. Đến lúc hết, bạn đã có kinh nghiệm thật để viết nhóm G và M.
