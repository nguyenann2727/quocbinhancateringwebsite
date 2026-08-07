# Checkpoint dự án HSNL Quốc Bình An

## Trạng thái hiện tại - 07/07/2026

- Đã hoàn thành storyboard gốc 26 trang tại `HSNL-QBA-STORYBOARD-26-TRANG.md`.
- Đã mở rộng bản nháp HSNL lên 28 trang, khổ A4, giọng văn B2B và đồng bộ nhận diện website.
- Bản chất lượng cao: `output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01.pdf`.
- Bản nhẹ cho điện thoại/flipbook: `output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01-web.pdf`.
- Ảnh bìa dùng cho website: `output/pdf/HSNL-Quoc-Binh-An-Catering-cover.jpg`.
- Script dựng bản đầy đủ: `scripts/build_hsnl_qba_full.py`.
- Script tạo bản nhẹ: `scripts/build_hsnl_web_pdf.py`.
- Bộ file chỉnh sửa nhanh: `editable/hsnl-image-overrides.json`, `editable/hsnl-text-overrides.json` và `editable/HSNL-QBA-HUONG-DAN-CHINH-SUA.md`.
- Đã tích hợp nhóm giấy tờ ATTP, tập huấn, thẻ an toàn lao động, ISO, chứng từ nhà cung cấp và phiếu kiểm nghiệm nước.
- Đã tích hợp bộ ảnh thực tế mới tại `references/hsnl-goc/anh-bo-sung-20260707/`.
- Đã tích hợp bộ chứng nhận bổ sung tại `references/hsnl-goc/chung-nhan-iso-va-ncc/original/`.
- Đã tích hợp logo QBA và ảnh họp đội ngũ bổ sung tại `references/hsnl-goc/nhan-dien-bo-sung-20260707/`.
- Đã tích hợp bộ ảnh khẩu phần/nhà ăn bổ sung tại `references/hsnl-goc/khau-phan-bo-sung-20260707/original/` và bản xử lý đưa vào PDF tại `assets/hsnl/khau-phan-20260707/`.
- Trang 1, 2 và 28 đã dùng logo tròn QBA mới; trang 2 đã thay ảnh chân dung placeholder bằng ảnh họp/điều phối đội ngũ.
- Trang 8, 9, 20 và 21 đã thay/chuẩn hóa ảnh khẩu phần theo khung lớn, giữ trọn khay ăn, canh, trái cây và sữa; ảnh được xử lý nền mờ, tăng nét và cân sáng trước khi đưa vào PDF.
- Các trang 11, 12, 13, 16, 17, 18 và 19 đã được làm lại/bổ sung bằng ảnh thật, sơ đồ quy trình mới và khung nội dung riêng.
- Trang 11: nhấn mạnh đồng phục, tách khu đồ sống/rau xanh và nhịp phối hợp theo công đoạn; đã căn lại ảnh để thấy rõ nguyên liệu, đồng phục và không gian bếp.
- Trang 12: dựng sơ đồ tổ chức vận hành bếp ăn theo phong cách khối vàng tương tự mẫu người dùng cung cấp; đã tăng cỡ chữ để đọc rõ hơn.
- Trang 13: dựng sơ đồ đầu vào - kiểm nhận - chế biến - lưu mẫu và gắn ảnh giao nhận, kiểm tra cảm quan, kệ nguyên liệu; đã tăng cỡ sơ đồ và tối ưu khung ảnh.
- Trang 15: ảnh danh sách tập huấn và thẻ an toàn lao động public đã che rộng hơn để không công bố STT, họ tên, chữ ký và thông tin định danh cá nhân.
- Trang 16: thêm chứng nhận ISO 22000:2018 và 4 chứng nhận đào tạo nhận thức; ghi rõ ISO hệ thống cần bản gia hạn vì giấy thể hiện hết hiệu lực 10/01/2026.
- Trang 17: thêm chứng từ nhà cung cấp Sao Biển và Nguyễn Thị Thuý Dương; ghi rõ trạng thái hiệu lực theo ngày trên từng giấy.
- Trang 18: đã thay placeholder bằng ảnh lưu mẫu thực tế.
- Trang 19: đã thay ảnh nhà cung cấp bằng ảnh thiết bị thực tế tại bếp QBA; khung thiết bị - sơ chế được phóng lớn để thấy áo chữ Quốc Bình An, máy cắt và nguyên liệu.
- Đã QA trực quan lại các trang 11-19 sau khi thay nội dung; hai tệp PDF đều xuất thành công và đủ 28 trang.
- Đã QA trực quan lại các trang 8, 9, 11, 12, 13, 15, 20 và 21 sau khi thay ảnh/chỉnh khung; hai tệp PDF đều xuất thành công và đủ 28 trang.
- Script dựng PDF đã hỗ trợ thay ảnh/sửa chữ bằng file trong thư mục `editable/`; nếu file override để trống thì PDF giữ nguyên nội dung hiện tại.

## Nội dung cần bổ sung trước bản chính thức

1. Nếu có, bổ sung thêm logo QBA bản gốc dạng SVG/AI/EPS hoặc PNG nền trong suốt để in ấn sắc nét hơn; hiện bản JPG logo đã được tích hợp vào PDF.
2. Ảnh nhà sáng lập: 01 ảnh ngang chung hoặc 02 ảnh chân dung đồng bộ.
3. Nếu muốn làm dày hơn phần quy trình, bổ sung thêm ảnh đo nhiệt độ, vệ sinh cuối ca và ảnh lưu mẫu ở góc rộng hơn.
4. Xác nhận tên/model một số thiết bị chính nếu muốn ghi chi tiết hơn trong HSNL.
5. Mỗi dự án Royal, E-top, Twin Kie và Bellinturf cần 2-4 ảnh ngang, số ca và thời gian hợp tác chính xác.
6. Bản scan giấy đăng ký thay đổi lần 4 để chốt địa chỉ và ngày đăng ký thay đổi.
7. Công suất hiện tại, sản lượng bình quân, số lượng đặt tối thiểu và ngân hàng món cần xác nhận.
8. Quy định lưu mẫu nội bộ: định lượng, thời gian và nhiệt độ bảo quản.
9. Chứng nhận ISO 22000/HACCP còn hiệu lực nếu đã gia hạn.
10. Bản chứng nhận nhà cung cấp Sao Biển còn hiệu lực nếu vẫn muốn công bố như nhà cung cấp đang được duyệt.
11. Hai ảnh HEIC `IMG_7548.HEIC` và `IMG_7549.HEIC` đã lưu trong thư mục tư liệu, nhưng chưa dùng trong PDF vì bản chuyển đổi hiện không trả kích thước đọc được bằng bộ xử lý ảnh.

## Nguyên tắc triển khai website

- Chưa liên kết bản nháp vào website vì còn ô ảnh chờ và dữ liệu cần xác nhận.
- Sau khi duyệt nội dung, đổi tên bản chính thức, bỏ nhãn “BẢN NHÁP”, gắn PDF nhẹ vào flipbook và dùng ảnh bìa đã xuất.
- Khi cần thay ảnh hoặc sửa chữ, ưu tiên chỉnh trong `editable/` rồi xuất lại PDF, không sửa trực tiếp file PDF cuối.
