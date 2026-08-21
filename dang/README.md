# Đăng video lên TikTok

Tool đăng `out/*.mp4` lên TikTok qua **Content Posting API** chính thức. Chỉ dùng
stdlib Python, không thêm phụ thuộc.

Hợp đồng API kiểm ngày **2026-08-20** tại
[developers.tiktok.com](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post).

---

## Ba giới hạn phải biết trước khi lên kế hoạch

**1. App chưa qua audit → mọi bài bị khoá riêng tư.** Tài liệu ghi thẳng:
*"All content posted by unaudited clients will be restricted to private viewing
mode."* Đặt `privacy_level: PUBLIC_TO_EVERYONE` lúc đó **không** làm bài public —
chỉ làm mình tưởng đã public. Muốn đăng công khai thật thì phải gửi app cho TikTok
audit. Vì vậy mặc định của tool là `SELF_ONLY`.

**2. `access_token` sống 24 giờ**, `refresh_token` 365 ngày. Tool tự refresh khi
còn dưới 5 phút, và lưu vào `dang/token.json`. Hệ quả cho bước deploy: **server
phải có ổ đĩa ghi được bền** — free tier kiểu ephemeral filesystem sẽ mất token
sau mỗi lần restart, và hôm sau cron chạy là chết.

**3. Giọng đọc là AI sinh** → tool bật `is_aigc: true` mặc định. Đây là trường
riêng của TikTok cho nội dung AI. Tắt bằng `--khong-aigc`, nhưng đừng tắt.

---

## Chuẩn bị key

1. Vào <https://developers.tiktok.com/apps>, tạo app.
2. Bật product **Content Posting API**, chọn scope:
   - `video.publish` — đăng trực tiếp lên trang (tool này dùng cái này)
   - `video.upload` — chỉ đẩy vào inbox, người dùng tự bấm đăng trong app
3. Khai **Redirect URI** đúng bằng chuỗi bạn sẽ đặt trong `.env`. Lệch một ký tự
   là TikTok từ chối. Mặc định của tool: `http://127.0.0.1:8723/callback`
4. Copy `Client key` và `Client secret`.
5. Tạo `dang/.env` theo `dang/.env.example`.

`dang/.env` và `dang/token.json` đều bị `.gitignore` — repo này public, đừng bao
giờ commit chúng. Tool không in giá trị token ra log.

---

## Dùng — bấm trong UI (cách chính)

```powershell
py dang\web.py        # -> http://127.0.0.1:8724
```

Một bảng liệt kê mọi `out/*.mp4`: tên, dung lượng, độ dài, **fps**, đã đăng chưa.
Mỗi dòng có ô tiêu đề, chọn quyền xem, cờ `is_aigc`, và nút **Đăng**. Bấm xong log
chạy ngay dưới dòng đó — chunk nào đang đẩy, trạng thái TikTok trả về.

Ba thứ UI tự lo:

- **Cảnh báo bản nháp** — video render `--fps 20` bị gắn cờ *"bản nháp, TikTok có
  thể từ chối"*. Cũng cảnh báo nếu khung không phải 1080×1920.
- **Nút bị vô hiệu** với video đã đăng, đọc từ `da-dang.json`.
- **Trạng thái token** ở đầu trang: đã đăng nhập chưa, access_token còn bao phút.
  Không in giá trị token.

Chỉ bind `127.0.0.1`, không có xác thực. **Đừng mở ra ngoài** — ai vào được trang
này là đăng được video lên tài khoản của bạn.

## Dùng — dòng lệnh (để script hoá về sau)

```powershell
# 1. đăng nhập một lần — mở browser, tool bắt `code` qua HTTP server tạm
py dang\dang.py auth

# 2. xem giới hạn THẬT của tài khoản (privacy nào được phép, độ dài tối đa...)
py dang\dang.py creator

# 3. xem chính xác sẽ gửi gì, không gọi mạng
py dang\dang.py dang out\cache-stale.mp4 --dry-run

# 4. đăng thật, chờ TikTok xử lý xong
py dang\dang.py dang out\cache-stale.mp4 --tieu-de "Cache hết hạn sai lúc" --cho

# 5. hỏi lại trạng thái bất kỳ lúc nào
py dang\dang.py trang-thai <publish_id>
```

### Chống đăng trùng

`dang/da-dang.json` ghi sổ theo **sha1 của nội dung file**, không theo tên. Đổi tên
file không qua được — và đó là cố ý: lịch chạy tự động không được đăng trùng. Muốn
đăng lại thật thì thêm `--lai`.

---

## Luồng API thực tế

```
POST /v2/oauth/token/                      code -> access_token + refresh_token
POST /v2/post/publish/creator_info/query/  BẮT BUỘC gọi trước khi đăng
POST /v2/post/publish/video/init/          -> publish_id + upload_url (sống 1 giờ)
PUT  {upload_url}                          từng chunk, Content-Range tuyệt đối
POST /v2/post/publish/status/fetch/        publish_id -> status + fail_reason
```

Trạng thái: `PROCESSING_UPLOAD` → `PUBLISH_COMPLETE`, hoặc `FAILED` kèm
`fail_reason`. Các mã hay gặp: `duration_check_failed`, `picture_size_check_failed`,
`frame_rate_check_failed`, `spam_risk_too_many_posts`.

### Chunk

| | |
|---|---|
Tối thiểu | 5 MB/chunk |
Tối đa | 64 MB/chunk (chunk **cuối** được vượt, tới 128 MB) |
Số chunk | tối đa 1000 |
File | tối đa 4 GB |
File < 5 MB | phải đẩy nguyên một lần |

Tool đẩy **một chunk** cho mọi file ≤ 64 MB. Video của repo này ~17 MB nên luôn
một chunk. Trên 64 MB mới chia, phần dư dồn vào chunk cuối.

---

## Video của repo này có hợp không

| Yêu cầu | Repo xuất ra |
|---|---|
Định dạng | `video/mp4` ✅ |
Khung | 1080×1920 (9:16 dọc) ✅ |
FPS | 30 ✅ |
Audio | AAC 48 kHz stereo ✅ |
Dung lượng | ~17 MB ✅ |

Nếu render bằng `--fps 20` (bản nháp) thì **đừng đăng** — TikTok có
`frame_rate_check_failed`, và bản nháp cũng lệch sync nhẹ. Đăng bản cuối
(`medium`/30fps).

---

## Bước sau: chạy theo giờ

Chưa làm, và **đừng làm trước khi app qua audit** — đăng tự động ra bài riêng tư
thì vô nghĩa.

Khi làm, ba thứ quyết định chọn server:

1. **Ổ đĩa bền** cho `token.json`. Ephemeral filesystem là loại trừ.
2. **Băng thông ra** đủ cho ~17 MB/video.
3. **`spam_risk_too_many_posts`** — TikTok chặn đăng quá nhiều trong 24 giờ. Rải
   thưa, đừng đẩy cả loạt 90 video một hôm.

Cách rẻ nhất là giữ tool ở máy này với Task Scheduler: token nằm trên đĩa thật,
không phải trả tiền server, và video đã có sẵn ở `out/`.
