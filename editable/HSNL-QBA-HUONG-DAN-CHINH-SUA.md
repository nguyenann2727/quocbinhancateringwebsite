# Hướng dẫn chỉnh sửa HSNL Quốc Bình An

## 0. Chỉnh trực tiếp trên bản PDF draft

Cách đúng để chỉnh trực tiếp HSNL PDF là chạy editor cục bộ:

```bash
/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/serve_hsnl_pdf_editor.py
```

Sau đó mở:

```text
http://127.0.0.1:8791/
```

Trong editor:

- **Sửa chữ & ảnh**: hiện cùng lúc toàn bộ khung ảnh và khung chữ để chỉnh nhanh trên bản PDF draft.
- **Tự lưu trực tiếp**: khi gõ chữ, thay ảnh, kéo ảnh hoặc đổi cỡ chữ, editor tự ghi vào `editable/hsnl-pdf-editor-state.json` sau một nhịp ngắn.
- **Chỉnh ảnh**: bấm khung ảnh trên trang PDF, kéo khung để đổi vị trí, kéo cạnh/góc để phóng to thu nhỏ khung.
- **Kéo khung**: di chuyển cả khung chứa ảnh sang trái/phải/lên/xuống.
- **Kéo ảnh bên trong**: giữ nguyên khung, chỉ căn lại phần ảnh bên trong khung.
- **Chọn ảnh từ Downloads**: bấm khung ảnh, chọn **Chọn ảnh từ Downloads**, sau đó bấm ảnh muốn thay trong danh sách hiện ra.
- **Thay ảnh từ máy**: vẫn có thể chọn file ảnh JPG/PNG/WebP từ máy; ảnh được lưu vào `editable/hsnl-pdf-editor-state.json`.
- **HEIC trong Downloads**: ảnh HEIC sẽ được tự chuyển sang JPG khi bấm chọn trong bảng Downloads.
- **Zoom ảnh trong khung**: dùng **Zoom -**, **Zoom +**, **Zoom 100%** hoặc thanh **Phóng ảnh** để phóng ảnh tới 600% và căn rõ chi tiết cần thấy.
- **Chỉnh chữ**: bấm vùng chữ trên trang PDF, sửa nội dung trong panel hoặc trực tiếp trong khung chữ.
- **Cỡ chữ**: dùng nút **A-**, **A+**, thanh kéo hoặc ô nhập số để chỉnh chữ to/nhỏ ngay trên trang.
- **Lưu vào dự án**: ghi chỉnh sửa vào `editable/hsnl-pdf-editor-state.json`.
- **Dựng lại PDF**: xuất lại `output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01.pdf` và bản web.
- **Xoá nút tạm**: tắt nút chỉnh sửa đang nằm trên trang bìa PDF và dựng lại bản PDF sạch.

Nút tạm trên trang bìa PDF được điều khiển bằng `editable/hsnl-pdf-edit-button.json`. Khi cần xoá khỏi bản chính thức, đặt `"enabled": false` hoặc bấm **Xoá nút tạm** trong editor rồi dựng lại PDF.

Các file editor chính:

- `editable/hsnl-pdf-editor.html`
- `editable/hsnl-pdf-editor.js`
- `editable/hsnl-pdf-editor.css`
- `editable/hsnl-pdf-editor-state.json`
- `editable/hsnl-pdf-editor-manifest.json`
- `editable/hsnl-pdf-edit-button.json`
- `editable/hsnl-pdf-pages/`

## 1. Thay ảnh

- Mở `editable/hsnl-image-overrides.json`.
- Tìm dòng ảnh muốn thay.
- Điền đường dẫn ảnh mới vào phần value.
- Nếu để trống, PDF sẽ dùng ảnh hiện tại.

Ví dụ:

```json
"references/hsnl-goc/khau-phan-bo-sung-20260707/original/suat-an-canh-rong-bien-trai-cay-sua.jpg": "references/hsnl-goc/khau-phan-bo-sung-20260707/original/anh-moi.jpg"
```

## 2. Sửa chữ

- Mở `editable/hsnl-text-overrides.json`.
- Điền nội dung mới vào đúng câu muốn sửa.
- Có thể thêm câu mới theo mẫu `"chữ hiện tại": "chữ mới"`.
- Nội dung có thẻ `<br/>` là xuống dòng, giữ lại nếu muốn bố cục không bị vỡ.

Ví dụ:

```json
"Suất ăn chủ lực": "Giải pháp suất ăn chủ lực"
```

## 3. Xuất lại PDF

Sau khi thay ảnh hoặc sửa chữ, chạy lại:

```bash
/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_hsnl_qba_full.py
/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/build_hsnl_web_pdf.py
```

## 4. Vị trí ảnh chính theo trang

| Trang | Mục | Ảnh đang dùng |
|---:|---|---|
| 1, 28 | Nền hero | `assets/qba-hero-natural-v2.jpg` |
| 1, 2, 28 | Logo tròn QBA | `references/hsnl-goc/nhan-dien-bo-sung-20260707/qba-logo-full.jpg` |
| 2 | Họp/điều phối đội ngũ | `references/hsnl-goc/nhan-dien-bo-sung-20260707/hop-doi-ngu-quan-ly.png` |
| 8 | Giải pháp chủ lực | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/suat-an-canh-rong-bien-trai-cay-sua.jpg` |
| 9 | Nhà ăn đông ca | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/nha-an-dong-cong-nhan.jpg` |
| 9 | Thực đơn theo ca | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/khay-canh-rau-ca-muc.jpg` |
| 9 | Suất chuyên gia | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/suat-an-trai-cay-sua-canh-do.jpg` |
| 11 | Chia suất/rau xanh | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/03-chia-suat-va-rau-xanh.png` |
| 11 | Sơ chế rau xanh | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/04-so-che-rau-xanh.png` |
| 11 | Khu đồ sống/rau | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/05-phan-khu-song-rau.png` |
| 13 | Xe/nguyên liệu vào bếp | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/11-xe-nguyen-lieu.jpg` |
| 13 | Ký nhận giao nhận | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/09-ky-nhan-giao-nhan.png` |
| 13 | Kệ rau củ | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/08-ke-nguyen-lieu-rau-cu.png` |
| 13 | Kiểm tra cảm quan | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/07-so-che-thit-va-kiem-soat-nguyen-lieu.png` |
| 14 | Giấy ATTP | `assets/hsnl/chung-nhan/chung-nhan-attp-2024.jpg` |
| 15 | Tập huấn ATTP public | `assets/hsnl/chung-nhan/tap-huan-attp-01-public.jpg` |
| 15 | Thẻ ATLĐ public | `assets/hsnl/chung-nhan/the-an-toan-lao-dong-public.jpg` |
| 18 | Lưu mẫu | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/10-luu-mau.png` |
| 19 | Thiết bị thái/sơ chế | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/02-may-thai-so-che.png` |
| 19 | Bếp nóng | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/01-che-bien-bep-nong.png` |
| 19 | Thiết bị/tủ nấu | `references/hsnl-goc/anh-bo-sung-20260707/quy-trinh/06-thiet-bi-va-bep.png` |
| 20 | Cơ cấu suất ăn | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/suat-an-trai-cay-sua-canh-do.jpg` |
| 21 | Suất tiêu chuẩn | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/suat-an-canh-thuong.jpg` |
| 21 | Suất tăng năng lượng | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/khay-tom-thit-nhieu-suat.jpg` |
| 21 | Suất chuyên gia/sự kiện | `references/hsnl-goc/khau-phan-bo-sung-20260707/original/khay-canh-bi-tom-thit.jpg` |

## 5. Lưu ý

- Không sửa trực tiếp file PDF nếu muốn giữ chất lượng. Hãy sửa file trong `editable/` rồi xuất lại.
- Ảnh mới nên là JPG/PNG, ngang hoặc vuông, rõ nét. Nếu ảnh nằm trong Downloads, editor có thể chọn trực tiếp và tự xử lý HEIC.
- File PDF vẫn là bản xuất cuối; quyền sửa nằm ở các file nguồn trong dự án.
