# Giọng văn và thuật ngữ

Hai vấn đề khiến content IT tiếng Việt dở nhất: dịch thuật ngữ sai cách, và viết đầy sáo ngữ. File này xử lý cả hai.

## Phần 1 — Xử lý thuật ngữ tiếng Anh

Tiếng Việt chưa có từ tương đương cho phần lớn thuật ngữ IT, và cộng đồng dev Việt đã quen dùng nguyên bản tiếng Anh. Dịch cưỡng ép làm bài khó đọc hơn chứ không dễ hơn.

### Ba nhóm thuật ngữ

**Nhóm 1 — Giữ nguyên tiếng Anh, không dịch**

Thuật ngữ mà dev Việt luôn nói bằng tiếng Anh trong đời thực. Dịch ra sẽ gây khó hiểu ngược:

deploy, commit, merge, pull request, build, debug, refactor, cache, container, endpoint, framework, library, repository, backend, frontend, database, query, index, token, session, request, response, thread, callback, middleware, migration, rollback, staging, production, log, monitoring, pipeline, dependency...

> ✗ "Hãy triển khai ứng dụng lên môi trường sản xuất và kiểm tra nhật ký hệ thống"
> ✓ "Deploy ứng dụng lên production rồi kiểm tra log"

**Nhóm 2 — Dùng tiếng Việt, đã phổ biến và tự nhiên**

Một số khái niệm đã có từ tiếng Việt được dùng rộng rãi. Dùng tiếng Việt ở đây tự nhiên hơn:

máy chủ (server), mạng, bộ nhớ, ổ cứng, phần mềm, phần cứng, mã nguồn, lỗ hổng bảo mật, mã hóa, xác thực, phân quyền, sao lưu, đồng bộ, tệp tin/file, thư mục, biến, hàm, vòng lặp, điều kiện, kiểu dữ liệu, mảng, chuỗi.

Lưu ý: một số từ dùng được cả hai, chọn theo đối tượng. Viết cho người mới thì "hàm", viết cho dev thì "function" đều ổn — miễn là nhất quán trong cùng một bài.

**Nhóm 3 — Giữ tiếng Anh nhưng giải thích lần đầu**

Thuật ngữ chuyên sâu mà đối tượng có thể chưa biết. Công thức: **thuật ngữ tiếng Anh + giải thích ngắn ngay sau đó**, rồi từ đó về sau dùng thuật ngữ trần.

> ✓ "Idempotency — tính chất mà gọi API cùng một request nhiều lần vẫn cho ra kết quả như gọi một lần — là thứ bắt buộc phải có ở tầng thanh toán."

Đừng đặt phần giải thích vào ngoặc dài dòng cuối câu; người đọc đã quên mất đang nói về gì.

### Quy tắc chung

- **Nhất quán trong một bài.** Đã chọn "API endpoint" thì đừng đoạn sau đổi thành "điểm cuối API".
- **Không viết tắt mà chưa mở ngoặc lần đầu.** "CI/CD (Continuous Integration / Continuous Deployment)" ở lần xuất hiện đầu tiên, sau đó viết tắt thoải mái.
- **Đừng chèn tiếng Anh vào chỗ tiếng Việt có sẵn từ tốt.** "Mình sẽ share một số tips để improve performance" — đây là thói quen nói chuyện, không phải văn viết. Viết: "Mình chia sẻ vài cách cải thiện hiệu năng."
- **Danh từ riêng giữ nguyên chính tả gốc.** PostgreSQL, Kubernetes, Node.js, GitHub — viết đúng hoa thường như nhà phát triển đặt.

## Phần 2 — Sáo ngữ cần tránh

Đây là những cụm làm bài viết mất uy tín ngay từ dòng đầu. Danh sách kèm cách sửa.

### Mở bài sáo rỗng

| Tránh | Vì sao | Thay bằng |
|---|---|---|
| "Trong thời đại công nghệ 4.0 hiện nay..." | Không nói gì cả, người đọc lướt qua ngay | Vào thẳng vấn đề cụ thể |
| "Không thể phủ nhận rằng X đang ngày càng phổ biến" | Câu đệm rỗng | Nêu con số thật hoặc bỏ hẳn |
| "Chắc hẳn các bạn đã từng nghe đến..." | Giả định thay cho nội dung | "Nếu bạn từng gặp lỗi X thì..." |
| "Hãy cùng mình tìm hiểu nhé!" | Câu dẫn thừa | Bỏ, chuyển thẳng sang nội dung |
| "Bài viết này sẽ giúp bạn hiểu rõ về..." | Nói về bài thay vì viết bài | Bắt đầu bằng chính nội dung đó |

**Ví dụ sửa mở bài:**

> ✗ "Trong thời đại công nghệ 4.0, Docker đang ngày càng trở nên phổ biến. Không thể phủ nhận rằng container hóa đã thay đổi cách chúng ta phát triển phần mềm. Hãy cùng mình tìm hiểu về Docker nhé!"

> ✓ "Code chạy ngon trên máy bạn nhưng lên server thì lỗi tùm lum — vấn đề kinh điển này là lý do Docker ra đời. Bài này đi qua cách đóng gói một app Node.js thành container chạy được ở mọi nơi."

### Kết bài sáo rỗng

| Tránh | Thay bằng |
|---|---|
| "Hy vọng bài viết hữu ích với các bạn" | Việc cụ thể tiếp theo họ nên làm |
| "Cảm ơn các bạn đã theo dõi!" | Bỏ, hoặc một câu hỏi mở thật sự |
| "Đừng quên like và share nhé" | Chỉ giữ nếu là post social và viết tự nhiên hơn |
| "Chúc các bạn thành công!" | Bỏ |

> ✓ Kết bài tốt: "Cấu hình trên đủ cho môi trường dev. Trước khi lên production, còn ba thứ cần xử lý: giới hạn tài nguyên cho container, health check, và chuyển secret ra khỏi file compose. Mình sẽ viết riêng về phần này."

### Từ đệm thừa trong thân bài

Cắt hết những từ này khi chúng không thêm nghĩa: "thực sự", "vô cùng", "cực kỳ", "đáng kể", "một cách", "có thể nói rằng", "như chúng ta đã biết", "điều đáng nói ở đây là", "chính vì vậy mà".

> ✗ "Việc sử dụng index một cách hợp lý thực sự có thể giúp cải thiện đáng kể hiệu năng truy vấn một cách rõ rệt."
> ✓ "Index đúng chỗ có thể giảm thời gian truy vấn từ vài giây xuống vài mili giây."

Câu thứ hai ngắn hơn và **nói được nhiều hơn** — vì thay từ nhấn mạnh rỗng bằng thông tin thật.

### Emoji và định dạng

- Blog kỹ thuật: không emoji, hoặc tối đa ở tiêu đề nếu phong cách trẻ trung.
- Post social: 2-4 emoji, đặt ở đầu dòng để phân tách ý, không rải giữa câu.
- Không in đậm cả câu dài. In đậm 2-5 từ để mắt bắt được ý chính khi lướt.
- Không viết HOA cả cụm để nhấn mạnh.

## Phần 3 — Giọng mặc định

Khi người dùng chưa nêu yêu cầu riêng, dùng giọng này:

**Xưng hô:** "mình" — "bạn". Tự nhiên với cộng đồng dev Việt, không quá suồng sã cũng không xa cách. Nếu là tài liệu nội bộ công ty hoặc bài cho khách hàng doanh nghiệp, chuyển sang giọng trung tính, không xưng hô cá nhân.

**Thái độ:** Như một đồng nghiệp có kinh nghiệm ngồi giải thích cho bạn, không phải giảng viên đọc giáo trình. Thẳng thắn về cái gì khó, cái gì dở, cái gì mình chưa chắc.

**Độ dài câu:** Chủ yếu câu ngắn và vừa. Câu dài chỉ dùng khi cần diễn tả quan hệ nhân quả phức tạp — và không quá một câu dài liên tiếp.

**Ví dụ giọng chuẩn:**

> "Nhìn qua thì Redis và Memcached khá giống nhau: đều là in-memory store, đều nhanh, đều dùng để cache. Khác biệt thật sự nằm ở chỗ Redis có cấu trúc dữ liệu (list, set, sorted set) và có thể ghi xuống đĩa. Nếu bạn chỉ cần cache key-value đơn giản và muốn tiết kiệm RAM, Memcached vẫn là lựa chọn tốt — nó nhẹ hơn thật. Còn nếu có lúc nào đó bạn nghĩ 'giá mà cache này xếp hạng được' thì chọn Redis từ đầu cho đỡ phải chuyển sau."
