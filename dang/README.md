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
2. Thêm **hai** product (**Add products**):
   - **Login Kit** — bắt buộc để có luồng OAuth `/v2/auth/authorize/`. Không có
     nó thì không đăng nhập được, dù các product khác đã bật. Cấp
     `user.info.basic`.
   - **Content Posting API** — cấp `video.upload`. Bật thêm công tắc
     **Direct Post** trong panel của nó để có `video.publish`.

   Ba product còn lại trong danh sách (**Share Kit**, **Webhooks**, **Data
   Portability API**) đều không dùng: Share Kit mở app TikTok để *người dùng tự*
   đăng — ngược mục đích tự động hoá; Webhooks cần một URL công khai để TikTok
   gọi vào, mà tool chạy trên máy bạn (và tool đã tự poll `status/fetch/`); Data
   Portability API là để xuất dữ liệu theo yêu cầu GDPR/DSA.

   Khai product không dùng **không vô hại**: TikTok ghi rõ mọi product và scope
   đã khai đều phải được demo trong video review, thiếu là hoãn duyệt.

3. Scope đến **từ product**, đừng bấm **Add scopes** khai tay — khai một scope
   không có product đỡ là cách chắc chắn nhận `scope not authorized` khi chạy.
   Panel Scopes phải có đúng ba dòng:

   | Scope | Đến từ | Để làm gì |
   |---|---|---|
   | `user.info.basic` | Login Kit | `open_id` + tên hiển thị, để biết đang đăng vào tài khoản nào |
   | `video.upload` | Content Posting API | đẩy vào inbox — dùng trước khi audit |
   | `video.publish` | Content Posting API + Direct Post | đăng trực tiếp — dùng sau khi audit |

   **`video.list` không có ở đây, và đó là chuyện bình thường.** Nó thuộc
   **Display API** — một product riêng mà TikTok **không phát cho mọi app**; nhiều
   app không thấy nó trong danh sách **Add products** chút nào. Hệ quả: `so-lieu`
   và bảng view / bình luận trong UI không chạy được. Luồng đăng video không ảnh
   hưởng gì; xem số liệu trong app TikTok hoặc TikTok Studio.

   Đây cũng là lý do `auth` mặc định chỉ xin **ba** scope: TikTok từ chối **cả**
   request uỷ quyền nếu trong `scope` có một scope chưa được cấp — không phải cấp
   phần còn lại rồi bỏ qua. Nếu app của bạn *có* Display API thì thêm tay:

   ```powershell
   py dang\dang.py auth --scope "user.info.basic,video.upload,video.publish,video.list"
   ```

4. Trong **Platforms**, tick **Desktop**. Rồi khai **Redirect URI** ở tab
   **Desktop** của Login Kit, đúng bằng chuỗi trong `.env`:

   ```
   http://127.0.0.1:8723/callback/
   ```

   **Phải là tab Desktop, không phải Web.** Hai tab có luật khác nhau:

   | | Web | Desktop |
   |---|---|---|
   | Scheme | chỉ `https` | `http` **và** `https` |
   | Host | domain công khai | chỉ `localhost` hoặc `127.0.0.1` |
   | PKCE | không | **bắt buộc** |

   Tài liệu Desktop ghi: *"Only `localhost` or loopback IP `127.0.0.1` are allowed
   host names in URI"*, ví dụ chính thức là `http://127.0.0.1:*/callback/`. Còn tab
   Web thì từ chối cả `http` lẫn IP — kể cả `https://127.0.0.1` cũng bị từ chối.

   Vì sao chọn Desktop: `code` đi từ browser sang tool **qua localhost**, không
   bao giờ ra internet. Phương án còn lại là dùng một domain công khai làm redirect,
   lúc đó URL kèm `code` đi qua server của domain đó.

   Cái giá phải trả là **PKCE** — tool tự lo, nhưng có một chi tiết đáng ghi: TikTok
   đòi `code_challenge` là **SHA256 dạng hex**, không phải base64url như hầu hết
   provider khác. Dùng base64url thì bị từ chối với lỗi mơ hồ.

   Dấu `/` cuối là cố ý — giữ đúng định dạng trong ví dụ của TikTok.

   Ba ô còn lại (**Web/Desktop URL**, **Terms of Service URL**, **Privacy Policy
   URL**) vẫn cần URL https công khai thật — form không nhận `127.0.0.1` ở đó. Repo
   này có sẵn ba trang trong `docs/` để bật GitHub Pages:

   ```
   https://<user>.github.io/whiteboard-video/
   https://<user>.github.io/whiteboard-video/terms.html
   https://<user>.github.io/whiteboard-video/privacy.html
   ```

5. Copy `Client key` và `Client secret` → `dang/.env` theo `dang/.env.example`.

### Đăng nhập một lần

```powershell
py dang\dang.py auth
```

Trang đăng nhập TikTok mở ra, bạn đăng nhập và đồng ý — xong. Tool dựng một
HTTP server tạm trên `127.0.0.1:8723`, bắt `code` từ callback, đổi lấy token, rồi
in ra scope **thật** nhận được. Thiếu scope nào nó cảnh báo ngay.

Không phải copy dán gì. `code_verifier` của PKCE chỉ sống trong tiến trình đó,
không ghi ra đĩa — nó chỉ cần tồn tại từ lúc mở browser đến lúc đổi token.

Nếu cổng 8723 đang bị tiến trình khác giữ, tool báo rõ và chỉ cách đổi cổng (phải
đổi **cả hai** chỗ: `.env` và Redirect URI trong app TikTok).

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

# 1b. view / like / bình luận (cần scope video.list -> cần product Display
#     API, thứ TikTok không phát cho mọi app; thiếu thì lệnh này báo rõ)
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

## Vòng lặp chết khi đăng ký app, và đường ra

Production **không Save được** cho đến khi mục App review có demo video
(`Please upload at least one video`). Mà demo video thì TikTok bắt phải quay bằng
**sandbox**. Nên đừng bắt đầu từ production.

Sandbox là môi trường thử, **không qua duyệt** — nó không đòi demo video, không
đòi ToS/Privacy URL. Thứ tự đúng:

1. Tạo sandbox, khai tay Login Kit + Content Posting API (**không clone** từ
   production — production chưa save thì không có gì để clone)
2. Lấy key của sandbox → `dang/.env` → `auth` → quay demo
3. **Rồi** mới về production: tải video lên, Save, Submit

Trước khi khai vào portal, in ra đúng chuỗi phải dán — chạy được cả khi chưa có
key:

```powershell
py dang\dang.py cau-hinh
```

Redirect URI phải trùng **y nguyên** giữa `.env` và ô trong Login Kit. Lệch một
ký tự — thiếu dấu `/` cuối, hay `http` vs `https` — thì TikTok từ chối với lỗi
không nói được nguyên nhân. Chép từ output của lệnh đó thì không thể gõ sai.

## Quay demo video cho app review

TikTok bắt app **chưa được duyệt** phải quay demo bằng **sandbox**, và demo phải
cho thấy **mọi** product/scope đã khai — thiếu một cái là hoãn duyệt. `quay.py`
tự lo phần máy móc:

```powershell
# diễn tập trước: không gọi mạng, không cần key. Kiểm khung hình và nhịp.
py dang\quay.py --thu

# quay thật
py dang\quay.py out\<video>.mp4
```

Nó bật `ffmpeg` (gdigrab) quay cả màn hình, chạy đúng thứ tự reviewer cần thấy,
rồi **cắt thành 5 file — một file một scope**. TikTok cho tải 5 file, mỗi file
≤50MB; một file cho một scope thì reviewer đối chiếu được ngay thay vì tua tìm
trong video hai phút.

Việc của người quay còn đúng ba chỗ: đăng nhập TikTok khi browser mở, và mở
tiktok.com cho thấy bản nháp / video đã lên. Script nhắc từng chỗ.

Ba chi tiết đáng biết:

- **Chữ trên màn hình là tiếng Anh, có ý.** Reviewer đọc tiếng Anh; terminal in
  tiếng Việt thì coi như không có bằng chứng.
- **Sandbox có cặp key riêng.** Đổi key trong `.env` rồi `auth` lại — token lưu
  theo từng `client_key` (`token-<vân tay>.json`) nên hai môi trường không lấn
  nhau, đổi qua đổi lại không phải `auth` lại.
- **Quay cả màn hình**, kể cả thông báo bật lên. Đóng hết thứ không liên quan
  trước khi bắt đầu; script nhắc điều này ở màn chuẩn bị.

File thô ghi ra `.mkv` chứ không `.mp4`: mp4 ghi `moov` atom ở **cuối** file, nên
bị kill giữa đường là mất trắng; mkv thì vẫn xem được.

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
