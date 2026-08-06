# Bàn giao — tool dựng video whiteboard animation tiếng Việt

> **Cập nhật 2026-08-04.** File này giữ bối cảnh giai đoạn đầu (theme
> `whiteboard`, phân tích video tham chiếu). Trạng thái hiện tại khác nhiều:
> theme chính giờ là **`bench`**, và công thức mở đầu là **HOOK 5 NHỊP**. Đọc
> [README.md](README.md) và [CONG-THUC.md](CONG-THUC.md) trước, file này sau.
>
> Ba điểm trong file này **đã lỗi thời**:
> - Đường dẫn Python `D:\Downloads\Python311` không còn. Máy hiện tại dùng
>   `py` (Python 3.14) trên PATH; `pillow numpy pyyaml edge-tts imageio-ffmpeg`
>   đã cài. ffmpeg lấy từ `imageio_ffmpeg.get_ffmpeg_exe()`.
> - Vị trí repo giờ là `D:\Project\whiteboard-video`, không phải `E:\`.
> - Remotion đã bỏ, không dùng. Toàn bộ render bằng PIL + numpy, không có Node.
>   Nên phần "giấy phép Remotion" ở mục 5 không còn liên quan.

> File này thay cho việc "chuyển đoạn chat". Lịch sử hội thoại không di chuyển được
> giữa các thư mục dự án, nên toàn bộ **quyết định đã chốt** và **kết quả đã đo được**
> nằm ở đây. Phiên Claude Code mới mở tại `E:\whiteboard-video` đọc file này là đủ
> ngữ cảnh để làm tiếp, không cần hỏi lại.
>
> Ngày bàn giao: 2026-08-02

---

## 1. Mục tiêu

Tool tự dựng video **whiteboard animation** (nét vẽ tay, nền giấy kem lưới chấm)
thuyết minh tiếng Việt, để đăng TikTok/Reels/Shorts.

Dự án này **hoàn toàn độc lập**, không liên quan gì tới `E:\GarageOS`.

---

## 2. Quyết định đã chốt

| Hạng mục | Chốt | Ghi chú |
|---|---|---|
| Phạm vi | **Renderer** — người dùng viết screenplay YAML, tool render ra mp4 | Chưa làm lớp "chủ đề → AI sinh screenplay". Nội dung do người viết quyết, tránh AI viết sai kỹ thuật |
| Giọng đọc | **edge-tts** miễn phí, giọng `vi-VN-HoaiMyNeural` / `vi-VN-NamMinhNeural` | Không cần API key. Nâng cấp ElevenLabs/Azure sau nếu chê chất lượng |
| Tỷ lệ khung | **9:16 dọc, 1080×1920** | Video tham chiếu là 16:9 nên bị co nhỏ khi xem trên TikTok — bản mình làm sẽ ăn full màn |
| Vị trí | `E:\whiteboard-video` | git repo riêng |
| Stack đề xuất | Remotion (React + TypeScript) + rough.js | Xem mục 5 |

---

## 3. Môi trường đã kiểm tra trên máy này

| Thứ | Trạng thái |
|---|---|
| Node | **v20.19.5** ✅ (Remotion cần ≥18) |
| pnpm | **10.34.4** ✅ |
| npm | 10.8.2 |
| Python | **D:\Downloads\Python311\python.exe** — 3.11.9 (KHÔNG có trên PATH, phải gọi full path) |
| `edge_tts` | ✅ đã cài sẵn |
| `cv2`, `imageio_ffmpeg`, `PIL`, `imageio` | ✅ đã cài sẵn |
| ffmpeg | ❌ không có trên PATH. **Dùng bản kèm theo:** `D:\Downloads\Python311\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe` |
| Mạng | npm registry / PyPI / Google Fonts đều 200 ✅ |

---

## 4. Phân tích style từ video tham chiếu

Video gốc: `reference/source-video.mp4` (150s, 1024×576, 30fps — bản snaptik re-encode).
21 khung hình đại diện đã trích ở `reference/keyframes/` — **đây là bảng màu và
bố cục chuẩn để bám theo**, tên file có kèm mốc thời gian.

Cấu trúc: **21 cảnh**, mỗi cảnh vẽ dần rồi xoá sạch trước khi sang cảnh sau
(phát hiện bằng cách đo "lượng mực" — tỉ lệ pixel tối — tụt về 0 giữa các cảnh).

### Thành phần hình ảnh cần dựng lại

| Thành phần | Cách làm |
|---|---|
| Nét vẽ tay xiêu xiêu (khung, mũi tên, vòng khoanh đỏ) | **rough.js** (đúng thư viện Excalidraw dùng) |
| Hiệu ứng "đang được vẽ ra" | `stroke-dasharray` + `stroke-dashoffset` animate trên SVG path |
| Nền giấy kem `#FAFAF5` + lưới chấm mờ, vignette nhẹ ở 4 góc | CSS thuần |
| Sticky note vàng nghiêng, highlight vàng sau chữ | CSS thuần |
| Người que, timeline có mốc, hộp DATABASE/CACHE, badge góc phải | ~8–10 component tái dùng là phủ hết 21 cảnh |
| Phụ đề thuyết minh chân frame (chữ nhỏ, xám) | Sinh từ chính text narration |

### Bảng màu đọc được từ frame

| Vai trò | Màu |
|---|---|
| Nền giấy | `#FAFAF5` |
| Nét chính / chữ đen | `#222222` |
| Đỏ (cái sai, cảnh báo) | `#D32F2F` |
| Xanh lá (đúng, đã xử lý) | `#2E7D32` |
| Xanh dương (nhãn tầng 1) | `#1565C0` |
| Tím (request, luồng phụ) | `#5E35B1` |
| Cam/hổ phách (mốc, nhấn) | `#EF9A00` |
| Hồng (khách hàng, cảm xúc) | `#E91E63` |
| Chữ phụ đề | `#9E9E9E` |

### Mắt xích quan trọng nhất: đồng bộ timing

Sinh TTS **trước**, đọc **duration thật** của từng câu, rồi đặt thời lượng cảnh
bằng đúng độ dài audio. Không canh timing bằng tay. Đây là chỗ tool tự viết
thắng hẳn Canva/CapCut.

---

## 5. Rủi ro đã xác định

### 🔴 Font tiếng Việt — rủi ro số một, CHƯA giải quyết xong

Phần lớn font viết tay rụng dấu ở `ắ ặ ễ ợ ự`. Đã lọc Google Fonts metadata:
**187 font** thuộc nhóm Handwriting/Display **có khai báo subset `vietnamese`**.

Ứng viên sát style video nhất (chưa kiểm tra glyph thật):

- **Playpen Sans** (700) — chữ tiêu đề đậm, sát nhất với headline trong video
- **Shantell Sans** (700) — kiểu bút lông marker, variable weight
- **Patrick Hand** (400) — chữ thân/phụ đề
- **Baloo 2** (800) — tiêu đề tròn đậm
- **Fuzzy Bubbles**, **Mansalva**, **Pangolin**, **Grape Nuts** — dự bị
- **JetBrains Mono** — cho đoạn code (`DEL sanpham:42`, `ttl = ?`)

**Việc còn dở:** `research/fonttest.py` tải TTF qua Google Fonts CSS2 API rồi render
bảng thử toàn bộ dấu để phát hiện ô tofu. **Cách này thất bại** — CSS2 API giờ chỉ
trả `woff2`, mà PIL không đọc được woff2.

**Cách sửa đã biết:** tải TTF trực tiếp từ repo `google/fonts` trên GitHub, ví dụ
`https://raw.githubusercontent.com/google/fonts/main/ofl/patrickhand/PatrickHand-Regular.ttf`.
Dùng `https://api.github.com/repos/google/fonts/contents/ofl/<slug>` để liệt kê file
`.ttf` trong từng thư mục (font variable đặt tên kiểu `PlaypenSans[wght].ttf`).
Đường dẫn có thể ở `ofl/`, `apache/` hoặc `ufl/` tuỳ giấy phép.

**Nguyên tắc:** phải render thử và nhìn bằng mắt trước khi chốt font. Không tin metadata.

### 🟡 Giấy phép Remotion

Miễn phí cho cá nhân và công ty ≤3 người; công ty lớn hơn phải mua license.
Nếu vướng, phương án thay: Playwright chụp frame + ffmpeg ghép (DX tệ hơn nhưng tự do).

---

## 6. Việc tiếp theo, theo thứ tự

1. **Chốt font** — sửa `research/fonttest.py` theo cách ở mục 5, render bảng thử,
   nhìn mắt, chọn 3 font (tiêu đề / thân / mono).
2. `git init` + scaffold Remotion, khổ 1080×1920.
3. Dựng bộ primitive: `Title`, `Box`, `Arrow`, `StickFigure`, `Timeline`,
   `StickyNote`, `CodeSnippet`, `Caption`, `CornerBadge` — dùng rough.js, có
   hiệu ứng vẽ dần.
4. Định nghĩa schema screenplay YAML + loader (nên validate bằng Zod).
5. Pipeline TTS: text → edge-tts → wav + duration → đẩy vào timing cảnh.
6. Render thử: tái dựng 3 cảnh đầu của video tham chiếu để so sánh 1:1 với
   `reference/keyframes/s01…s03`.
7. Đủ giống thì viết screenplay mới hoàn chỉnh.

Ví dụ schema đang hình dung:

```yaml
- scene: timeline
  caption: "Năm mili giây nghe như không có gì."
  marks:
    - { at: 0.3, label: "XOÁ CACHE", color: amber }
    - { at: 0.7, label: "GHI DATABASE", color: blue }
  gap: { from: 0.3, to: 0.7, label: "KHE HỞ", note: "5MS" }
```

---

## 7. Nội dung video tham chiếu (để đối chiếu khi render thử)

Chủ đề: cache invalidation — câu hỏi phỏng vấn *"Cập nhật xong rồi, cache xoá lúc nào?"*

Luận điểm: đáp án "ghi xong thì xoá cache" — 9/10 người trả lời vậy — **đúng nhưng
vẫn trượt**, vì dừng ở đúng chỗ mọi tài liệu cũng dừng. Hai tầng đào sâu:

- **Tầng 1 — thứ tự.** Xoá cache *trước* khi ghi DB tạo khe hở ~5ms; một request chen
  vào đọc DB thấy giá cũ rồi nạp lại chính giá cũ đó vào cache, sau đó không ai xoá
  lần nữa. Khe hở 5ms nhưng cái sai sống suốt TTL 5 phút → **ghi DB trước, xoá cache sau**.
- **Tầng 2 — lệnh xoá thất bại.** `DEL` fail mà không báo lỗi (gọi kiểu bắn-và-quên),
  cache giữ số cũ hàng tuần, khách phát hiện trước bạn → **TTL là lưới cuối**
  (TTL 60s = chấp nhận tối đa 1 phút dữ liệu cũ).

Chốt 4 dòng: (1) ghi DB trước xoá cache sau; (2) xoá trước để lại giá cũ suốt TTL;
(3) lệnh xoá có thể mất nên luôn đặt TTL; (4) TTL 60s = tối đa 1 phút dữ liệu cũ.

Video còn thừa nhận **không có 100%** — hai request đúng thứ tự mà nhịp trùng nhau
thì cache vẫn giữ số cũ. Thông điệp: điểm mười là **nói thẳng chỗ mình chưa chắc**.
