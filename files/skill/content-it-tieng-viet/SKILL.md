---
name: content-it-tieng-viet
description: Viết content kiến thức công nghệ thông tin bằng tiếng Việt — bài blog hướng dẫn, giải thích khái niệm, so sánh công nghệ, post social, thread, script video ngắn. Dùng skill này bất cứ khi nào người dùng yêu cầu viết bài, viết content, viết post, viết thread, viết script hay soạn tài liệu về chủ đề IT (lập trình, DevOps, cloud, AI, bảo mật, database, network, tool dev...) bằng tiếng Việt — kể cả khi họ chỉ nói ngắn gọn như "viết bài về Docker", "làm post giải thích API", "content về AI cho page mình", hoặc đưa một chủ đề kỹ thuật kèm yêu cầu đăng ở đâu đó. Cũng dùng khi người dùng nhờ biên tập, rút gọn, hoặc Việt hóa một bài kỹ thuật có sẵn.
---

# Content kiến thức IT tiếng Việt

Skill này giúp viết content công nghệ tiếng Việt vừa chính xác về kỹ thuật, vừa đọc được — thay vì loại bài dịch máy đầy sáo ngữ hoặc bài dài mà không dạy được gì.

Ba thứ quyết định chất lượng, theo đúng thứ tự ưu tiên:

1. **Đúng** — sai kỹ thuật thì hay cỡ nào cũng vứt đi
2. **Người đọc hiểu được** — đúng độ sâu với đúng đối tượng
3. **Đọc trôi** — giọng văn tự nhiên, không sáo rỗng

## Quy trình

### Bước 1 — Chốt 3 biến số trước khi viết

Đừng viết ngay. Ba thứ này quyết định toàn bộ bài, và người dùng thường không nói rõ:

| Biến số | Cần biết gì |
|---|---|
| **Người đọc** | Người mới / sinh viên IT? Dev đã đi làm 1-3 năm? Senior, tech lead? Người không chuyên (sếp, sales, khách hàng)? |
| **Định dạng & nơi đăng** | Blog dài, post Facebook, thread, script video, tài liệu nội bộ? Mỗi nơi một cấu trúc khác hẳn. |
| **Mục tiêu bài** | Dạy làm được một việc? Giải thích để hiểu bản chất? Thuyết phục chọn công nghệ? Bắt trend để hút tương tác? |

Nếu người dùng đã nói rõ cả ba, viết luôn. Nếu thiếu, chỉ hỏi những gì thật sự thiếu — thường một câu hỏi gộp là đủ. Nếu người dùng có vẻ muốn thấy kết quả ngay, chọn giả định hợp lý nhất (mặc định: dev đi làm 1-3 năm, blog, mục tiêu dạy làm được việc), viết bản nháp, rồi nói rõ mình đã giả định gì để họ chỉnh.

**Về độ sâu kỹ thuật** — đây là chỗ hay hỏng nhất. Viết cho người mới mà dùng thuật ngữ chưa giải thích thì họ bỏ giữa chừng; viết cho senior mà giải thích lại "biến là gì" thì họ thấy bị coi thường. Khi đã chốt đối tượng, giữ nguyên độ sâu đó xuyên suốt bài.

### Bước 2 — Kiểm tra tính chính xác trước khi viết

Content IT sai kỹ thuật thì phản tác dụng, và người đọc IT phát hiện rất nhanh. Trước khi viết:

- **Version và cú pháp thay đổi theo thời gian.** Nếu bài liên quan đến API, CLI flag, cú pháp framework, giá dịch vụ cloud, hay tính năng mới — kiến thức có thể đã cũ. Nêu rõ version đang nói tới, và nói thẳng với người dùng nếu cần họ kiểm tra lại docs chính thức.
- **Không bịa số liệu.** Benchmark, thị phần, "nhanh hơn 40%" — chỉ đưa khi có nguồn thật. Nếu muốn nhấn mạnh hiệu năng mà không có số, mô tả định tính ("giảm đáng kể thời gian cold start") thay vì bịa con số cho oai.
- **Code phải chạy được.** Không viết code minh họa kiểu giả tưởng. Nếu là pseudo-code thì ghi rõ. Nếu đoạn code cần cài đặt gì trước, nói ra.
- **Đánh dấu chỗ chưa chắc.** Thà ghi "cách này áp dụng từ v14 trở đi, bản cũ hơn cần kiểm tra lại" còn hơn khẳng định chắc nịch rồi sai.

### Bước 3 — Chọn cấu trúc theo định dạng

Đọc `references/dinh-dang.md` để lấy khung cho đúng định dạng. File đó có template chi tiết cho: bài hướng dẫn (tutorial), bài giải thích khái niệm, bài so sánh công nghệ, bài giải quyết lỗi, post social ngắn, thread, và script video.

Đừng dùng một cấu trúc chung cho mọi định dạng — bài hướng dẫn và bài so sánh công nghệ có logic hoàn toàn khác nhau.

### Bước 4 — Viết theo giọng văn chuẩn

Đọc `references/giong-van-va-thuat-ngu.md` trước khi viết bản đầu tiên. File đó xử lý hai vấn đề đặc thù của content IT tiếng Việt:

- **Thuật ngữ**: khi nào giữ tiếng Anh, khi nào dịch, khi nào dịch kèm chú thích
- **Sáo ngữ cần tránh**: danh sách cụ thể kèm ví dụ sửa lại

### Bước 5 — Rà lại trước khi giao

Tự kiểm bản nháp theo checklist này, sửa những gì chưa đạt rồi mới đưa:

- [ ] Câu mở đầu có nêu một vấn đề thật người đọc gặp không, hay chỉ là lời dẫn chung chung?
- [ ] Có thuật ngữ nào xuất hiện lần đầu mà chưa giải thích, trong khi đối tượng là người mới?
- [ ] Mọi đoạn code có chạy được không? Có ghi rõ version/môi trường không?
- [ ] Có số liệu nào mình không chắc nguồn không?
- [ ] Đọc to lên có thấy chỗ nào sáo rỗng, thừa chữ không?
- [ ] Người đọc gấp mà chỉ lướt tiêu đề + đoạn đầu mỗi phần thì có nắm được ý chính không?
- [ ] Kết bài có cho họ việc cụ thể để làm tiếp không, hay chỉ chúc chung chung?

## Định dạng đầu ra

**Bài dài (blog, hướng dẫn, tài liệu):** tạo file `.md` trong `/mnt/user-data/outputs/` rồi dùng `present_files` để giao. Bài dài đọc trong chat rất khó theo dõi, và người dùng thường cần copy đi đăng.

**Bài ngắn (post social, thread, caption):** trả thẳng trong chat, trừ khi người dùng xin file. Với post social, viết luôn 2 phương án khác góc tiếp cận để họ chọn — chi phí thấp mà hữu ích hơn hẳn một bản duy nhất.

**Script video:** trình bày dạng bảng hoặc chia block theo thời gian, kèm gợi ý hình ảnh cho mỗi đoạn.

## Nguyên tắc xuyên suốt

**Người đọc content IT không đọc để giải trí, họ đọc để giải quyết vấn đề.** Mỗi đoạn phải đưa họ tiến gần hơn tới việc làm được điều gì đó. Đoạn nào cắt đi mà bài không yếu hơn thì cắt.

**Ví dụ cụ thể thắng giải thích trừu tượng.** "Rate limiting" giải thích ba đoạn không bằng một ví dụ: API cho phép 100 request/phút, request thứ 101 nhận 429, client phải retry sau. Với khái niệm khó, dùng một phép so sánh đời thường rồi lập tức quay lại thuật ngữ chính xác — đừng dừng ở phép so sánh, vì so sánh nào cũng có chỗ sai.

**Nói cả mặt trái.** Bài chỉ khen một công nghệ đọc như quảng cáo. Nêu giới hạn, chi phí, khi nào không nên dùng — đó là thứ khiến dev có kinh nghiệm tin bài viết.

**Viết cho người bận.** Tiêu đề phụ phải nói rõ nội dung bên dưới ("Cấu hình health check" chứ không phải "Bước 3"). Đoạn văn 3-5 dòng. Ý nào liệt kê được thì gạch đầu dòng.
