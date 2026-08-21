# Đăng video lên TikTok

Tool đăng `out/*.mp4` lên TikTok qua **Content Posting API** chính thức. Chỉ dùng
stdlib Python, không thêm phụ thuộc.

Hợp đồng API kiểm ngày **2026-08-20** tại
[developers.tiktok.com](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post).

---

## Hai đường đăng — chọn đúng, không thì làm lại từ đầu

Trang product của TikTok có **hai** sản phẩm khác nhau. Tool hỗ trợ cả hai.

| | Upload API | Direct Post |
|---|---|---|
Scope | `video.upload` | `video.publish` |
Endpoint | `/v2/post/publish/inbox/video/init/` | `/v2/post/publish/video/init/` |
Video đi đâu | **inbox** TikTok dạng nháp | đăng thẳng lên trang |
Ai bấm đăng cuối | **bạn**, trong app TikTok | tool, tự động |
Tiêu đề / quyền xem | đặt trong app | đặt trong request |
Bị hạn chế chưa-audit | **không** | **có** |

**Điểm quyết định:** tài liệu ghi *"All content posted by unaudited clients will be
restricted to private viewing mode"* — nhưng câu đó nằm ở trang **Direct Post**, và
tài liệu endpoint inbox không có hạn chế đó. Lý do hợp lý: bài cuối do *người* bấm
đăng qua luồng tạo bình thường của TikTok, không phải do API đăng.

Nên:

- **Bây giờ, chưa audit** → dùng **inbox** (mặc định của tool). Đây là đường duy
  nhất ra video **public thật**. Đổi lại: mỗi video bạn phải mở app bấm một lần —
  mà đó đúng là quy trình "chủ động click đăng" bạn muốn.
- **Sau khi audit** → chuyển sang **direct post** để tự động hoá hoàn toàn.

Bật **cả hai scope** trong app TikTok ngay từ đầu thì sau này không phải khai lại.

## Hai giới hạn còn lại

**1. `access_token` sống 24 giờ**, `refresh_token` 365 ngày. Tool tự refresh khi
còn dưới 5 phút, và lưu vào `dang/token.json`. Hệ quả cho bước deploy: **server
phải có ổ đĩa ghi được bền** — free tier kiểu ephemeral filesystem sẽ mất token
sau mỗi lần restart, và hôm sau cron chạy là chết.

**2. Giọng đọc là AI sinh** → tool bật `is_aigc: true` mặc định. Đây là trường
riêng của TikTok cho nội dung AI. Tắt bằng `--khong-aigc`, nhưng đừng tắt.

---

## Chuẩn bị key

Bạn **không** lấy access token / refresh token bằng tay. Bạn chỉ cần **Client key**
và **Client secret**; `py dang/dang.py auth` tự làm phần OAuth và tự lưu cả hai
token vào `dang/token.json`, rồi tự refresh sau đó.

1. Vào <https://developers.tiktok.com/apps>, tạo app.
2. Thêm **ba** product:
   - **Login Kit** — bắt buộc để có luồng OAuth `/v2/auth/authorize/`. Không có
     nó thì không đăng nhập được, dù các product khác đã bật.
   - **Content Posting API** — cấp `video.upload` và `video.publish`.
   - **Display API** — cấp `video.list` và `user.info.basic`. Thiếu nó thì mục
     "Đã đăng" trong UI không lấy được view / like / bình luận.
3. Bật **cả bốn** scope (xin hết một lần để sau không phải `auth` lại):

   | Scope | Để làm gì |
   |---|---|
   | `video.upload` | đẩy vào inbox — dùng trước khi audit |
   | `video.publish` | đăng trực tiếp — dùng sau khi audit |
   | `video.list` | đọc view / like / bình luận |
   | `user.info.basic` | điều kiện kèm của Display API |

4. Khai **Redirect URI** trong Login Kit, đúng bằng chuỗi trong `.env`:

   ```
   https://127.0.0.1:8723/callback
   ```

   **TikTok chỉ nhận `https`** — tài liệu Login Kit ghi *"must be absolute and
   begin with https"*. Không nhận `http`, kể cả localhost. Lệch một ký tự là bị
   từ chối.

   Vì sao chọn `https://127.0.0.1`: browser sẽ **không kết nối được** (không có
   server HTTPS ở đó), dừng lại ở trang lỗi — nhưng `code` vẫn nằm trong thanh địa
   chỉ. Nghĩa là mã uỷ quyền **không đi ra khỏi máy bạn**. Nếu khai domain của
   người khác thì `code` được gửi thẳng tới server họ.

5. Copy `Client key` và `Client secret` → `dang/.env` theo `dang/.env.example`.

### Đăng nhập một lần

```powershell
py dang\dang.py auth
```

Ba bước, tool in ra sẵn:

1. Trang đăng nhập TikTok mở ra
2. Đăng nhập và đồng ý → browser báo **không kết nối được
   `https://127.0.0.1:8723/callback`**. Đúng là như vậy, không phải lỗi.
3. Copy **toàn bộ URL** trên thanh địa chỉ, dán vào terminal

Tool tự tách `code`, giải url-encode (`code` của TikTok có ký tự `*` bị mã hoá
thành `%2A` — không giải thì đổi token thất bại với lỗi mơ hồ), đổi lấy token, và
in ra scope thật nhận được. Thiếu scope nào nó cảnh báo ngay.

Từ đó trở đi không phải làm gì nữa trong 365 ngày.

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
# 1. xem giới hạn THẬT của tài khoản (privacy nào được phép, độ dài tối đa...)
py dang\dang.py creator

# 1b. view / like / bình luận của video đã đăng (cần scope video.list)
py dang\dang.py so-lieu

# 3. xem chính xác sẽ gửi gì, không gọi mạng
py dang\dang.py dang out\cache-stale.mp4 --dry-run

# 4a. đẩy vào inbox (khuyên dùng khi chưa audit) — rồi mở app TikTok bấm đăng
py dang\dang.py dang out\cache-stale.mp4 --inbox --cho

# 4b. đăng trực tiếp (chỉ có nghĩa sau khi app qua audit)
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

Trạng thái: `PROCESSING_UPLOAD` → `PUBLISH_COMPLETE` (direct post) hoặc
→ `SEND_TO_USER_INBOX` (inbox — **kết ở đây**, không bao giờ lên
`PUBLISH_COMPLETE`, vì bước đăng cuối do người làm trong app). Hoặc `FAILED` kèm
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
