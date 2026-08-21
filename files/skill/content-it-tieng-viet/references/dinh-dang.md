# Cấu trúc theo định dạng

Mỗi định dạng có logic riêng. Chọn đúng khung rồi mới viết.

Mục lục:
1. [Bài hướng dẫn (tutorial)](#1-bài-hướng-dẫn)
2. [Bài giải thích khái niệm](#2-bài-giải-thích-khái-niệm)
3. [Bài so sánh công nghệ](#3-bài-so-sánh-công-nghệ)
4. [Bài xử lý lỗi / troubleshooting](#4-bài-xử-lý-lỗi)
5. [Post social ngắn](#5-post-social-ngắn)
6. [Thread nhiều phần](#6-thread-nhiều-phần)
7. [Script video ngắn](#7-script-video-ngắn)
8. [Tiêu đề](#8-viết-tiêu-đề)

---

## 1. Bài hướng dẫn

Mục tiêu: người đọc làm được việc đó sau khi đọc xong. Tiêu chí thành công duy nhất là **họ làm theo và nó chạy**.

```
# [Làm được gì cụ thể]

[Mở bài: vấn đề thật + kết quả cuối cùng họ sẽ có. 2-4 câu.]

## Cần chuẩn bị
- Môi trường, version cụ thể
- Kiến thức nền giả định họ đã có
- Thời gian ước tính

## Bước 1 — [Tên bước nói rõ đang làm gì]
[Giải thích ngắn VÌ SAO bước này cần, rồi mới tới lệnh/code]
[Code block]
[Kết quả mong đợi — để họ biết mình có làm đúng không]

## Bước 2 — ...

## Kiểm tra lại
[Cách xác nhận mọi thứ chạy đúng]

## Lỗi thường gặp
[2-3 lỗi phổ biến + cách xử lý]

## Tiếp theo
[Việc cụ thể nên làm sau đó]
```

Điểm sống còn: sau mỗi bước có code, **luôn nói kết quả mong đợi là gì**. Người làm theo mà không biết mình đúng hay sai sẽ bỏ giữa chừng.

---

## 2. Bài giải thích khái niệm

Mục tiêu: người đọc hiểu bản chất, không chỉ thuộc định nghĩa.

```
# [Khái niệm] là gì và khi nào cần dùng

[Mở bài: tình huống thực tế mà thiếu khái niệm này thì gặp vấn đề]

## Vấn đề trước khi có [X]
[Mô tả cách làm cũ và chỗ nó gãy — đây là phần quan trọng nhất,
người đọc chỉ hiểu giải pháp khi thấy rõ vấn đề]

## [X] giải quyết thế nào
[Cơ chế, kèm một ví dụ cụ thể có số liệu/code]

## Ví dụ thực tế
[Một case cụ thể, đủ chi tiết để hình dung]

## Khi nào KHÔNG nên dùng
[Giới hạn, chi phí, tình huống phản tác dụng]

## Tóm lại
[3-4 gạch đầu dòng chốt ý]
```

Cách sai phổ biến: bắt đầu bằng định nghĩa từ điển. Bắt đầu bằng **vấn đề**, định nghĩa sẽ tự nhiên trở nên dễ hiểu.

---

## 3. Bài so sánh công nghệ

Mục tiêu: giúp người đọc ra quyết định, không phải liệt kê tính năng.

```
# [A] hay [B]: chọn cái nào cho [bối cảnh cụ thể]

[Mở bài: nêu rõ bài này so sánh trong bối cảnh nào —
so sánh chung chung là vô nghĩa]

## Điểm giống nhau
[Gạt sang một bên những gì không phải yếu tố quyết định]

## Khác biệt thật sự
[Bảng so sánh 4-6 tiêu chí THỰC SỰ ảnh hưởng đến quyết định]

## Chọn [A] khi...
[3-4 tình huống cụ thể]

## Chọn [B] khi...
[3-4 tình huống cụ thể]

## Chi phí chuyển đổi
[Nếu đang dùng cái này muốn đổi sang cái kia thì mất gì]
```

Không kết luận kiểu "cái nào cũng tốt, tùy nhu cầu". Đưa khuyến nghị rõ ràng cho từng tình huống — đó là lý do người ta đọc bài so sánh.

---

## 4. Bài xử lý lỗi

Mục tiêu: người đang gặp lỗi tìm ra và fix được trong 2 phút.

```
# [Nguyên văn thông báo lỗi]

## Triệu chứng
[Lỗi xuất hiện khi nào, kèm log/stack trace nguyên bản
— để người ta search Google ra được bài này]

## Nguyên nhân
[Giải thích ngắn gọn tại sao xảy ra]

## Cách sửa
[Giải pháp phổ biến nhất trước tiên, code cụ thể]

## Nếu vẫn chưa được
[2-3 nguyên nhân ít gặp hơn]

## Phòng tránh
[Cách cấu hình để không tái diễn]
```

Nguyên tắc: **giải pháp trước, giải thích sau**. Người đang gặp lỗi lúc 11h đêm không muốn đọc lịch sử ra đời của framework.

---

## 5. Post social ngắn

Độ dài: 100-250 từ. Người lướt quyết định đọc tiếp hay không trong 2 giây đầu.

```
[Dòng 1: câu móc — một sự thật bất ngờ, một sai lầm phổ biến,
hoặc một con số. KHÔNG mở đầu bằng lời chào hay lời dẫn]

[Khoảng trắng]

[3-5 dòng nội dung chính, mỗi ý một dòng riêng]

[Khoảng trắng]

[Câu chốt: một bài học rút ra hoặc câu hỏi mở]

[Hashtag: 3-5 cái, đặt cuối]
```

Ví dụ dòng móc tốt:
- "90% bug production mình từng gặp không phải do code sai, mà do config khác nhau giữa các môi trường."
- "Mình vừa xóa 400 dòng code và app chạy nhanh hơn."
- "`SELECT *` không chỉ chậm — nó còn làm app bạn crash khi ai đó thêm cột mới."

Khi giao post social, **luôn đưa 2 phương án** khác góc tiếp cận (ví dụ: một bản kể chuyện cá nhân, một bản dạng tips) để người dùng chọn.

---

## 6. Thread nhiều phần

Mỗi phần phải đứng độc lập được, đồng thời tạo lý do đọc tiếp.

```
1/ [Câu móc + hứa hẹn cụ thể sẽ nói gì. Đây là phần
   quyết định 80% lượng người đọc tiếp]

2/ [Bối cảnh hoặc vấn đề]

3-7/ [Mỗi phần MỘT ý duy nhất. Ý nào cần code thì
     phần đó chỉ có code + một câu giải thích]

8/ [Chốt: tóm 3 ý chính]

9/ [Kêu gọi hành động nếu cần — nhẹ nhàng]
```

Đánh số dạng `1/` `2/`. Mỗi phần dưới 280 ký tự nếu đăng X/Twitter, dưới 500 nếu Threads/Facebook.

---

## 7. Script video ngắn

Định dạng bảng, kèm gợi ý hình:

| Thời gian | Lời thoại | Hình ảnh |
|---|---|---|
| 0-3s | [Câu móc — phải nêu ngay vấn đề hoặc kết quả] | [Cảnh gì trên màn hình] |
| 3-15s | [Bối cảnh vấn đề] | [Demo lỗi / code cũ] |
| 15-45s | [Giải pháp, từng bước] | [Screen record thao tác] |
| 45-55s | [Kết quả sau khi sửa] | [Demo chạy được] |
| 55-60s | [Chốt + CTA] | [Text overlay] |

Lưu ý cho script: viết theo cách **nói**, không phải cách viết. Đọc to lên, chỗ nào líu lưỡi thì sửa. Câu ngắn hơn văn viết. Không đọc code từng ký tự — mô tả ý nghĩa và để hình ảnh lo phần chi tiết.

---

## 8. Viết tiêu đề

Tiêu đề tốt nói rõ **người đọc nhận được gì**, không giật gân.

| Kém | Tốt hơn |
|---|---|
| "Tìm hiểu về Docker" | "Đóng gói app Node.js thành Docker image chỉ 40MB" |
| "Những điều cần biết về SQL" | "5 lỗi SQL khiến query chậm gấp 10 lần" |
| "React Hooks là gì?" | "useEffect chạy 2 lần và tại sao đó là chuyện bình thường" |
| "Bí mật mà lập trình viên không muốn bạn biết" | (bỏ hẳn — giật tít làm mất uy tín) |

Công thức hay dùng:
- **Kết quả cụ thể**: "Giảm thời gian build từ 8 phút xuống 90 giây"
- **Số + lỗi**: "3 sai lầm khi cấu hình nginx làm site sập lúc traffic cao"
- **Câu hỏi thật của dev**: "Khi nào nên tách microservice, khi nào không?"
- **So sánh có bối cảnh**: "PostgreSQL hay MongoDB cho app phân tích log?"
