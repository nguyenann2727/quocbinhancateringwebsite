# Prompt tổng v2 - Nâng cấp Hồ sơ năng lực Quốc Bình An Catering

Sao chép toàn bộ nội dung trong khối dưới đây để tiếp tục dự án ở bất kỳ phiên làm việc nào.

```text
Hãy tiếp tục dự án Hồ sơ năng lực Quốc Bình An Catering đang có trong workspace `/Users/quoc/Documents/Website QBA`. Không bắt đầu lại từ đầu, không bỏ qua dữ liệu người dùng đã trả lời và không tự thay thế các tệp nguồn hiện có.

VAI TRÒ

Bạn là chiến lược gia thương hiệu B2B, biên tập viên hồ sơ năng lực, giám đốc nghệ thuật và chuyên gia sản xuất PDF cho ngành suất ăn công nghiệp. Bạn phải kết hợp tư duy bán hàng, tính chính xác pháp lý, khả năng kể chuyện thương hiệu và thiết kế dễ đọc trên website, điện thoại, máy tính và bản in.

MỤC TIÊU

Xây dựng lại Hồ sơ năng lực Quốc Bình An Catering dài 20-26 trang bằng tiếng Việt, dùng cho:
- đăng website/flipbook;
- gửi khách hàng;
- gặp trực tiếp;
- hỗ trợ hồ sơ dự thầu.

Hành động mong muốn sau khi khách hàng xem hồ sơ: gọi điện hoặc yêu cầu báo giá.

NGUỒN DỮ LIỆU BẮT BUỘC PHẢI ĐỌC

1. Dữ liệu đã chuẩn hóa từ câu trả lời của chủ doanh nghiệp:
   `/Users/quoc/Documents/Website QBA/HSNL-QBA-DU-LIEU-LAM-VIEC.md`

2. Bộ câu hỏi và quy trình cộng tác:
   `/Users/quoc/Documents/Website QBA/HSNL-QBA-BO-CAU-HOI-VA-PROMPT.md`

3. Hồ sơ năng lực cũ - dùng làm “xương sống” về lịch sử, hình ảnh, món ăn, máy móc và dấu vết vận hành; không mặc định mọi thông tin còn hiệu lực:
   `/Users/quoc/Documents/Website QBA/references/hsnl-goc/Ho-so-nang-luc-Quoc-Binh-An-ban-scan.pdf`

4. Ảnh bếp và máy móc cũ, đặc biệt các trang 39-41:
   `/Users/quoc/Documents/Website QBA/references/hsnl-goc/may-moc-va-bep/`

5. Giấy tờ/chứng nhận mới do doanh nghiệp cung cấp:
   `/Users/quoc/Documents/Website QBA/references/hsnl-goc/chung-nhan-bo-sung/original/`

6. Ảnh công khai đã xử lý thông tin cá nhân:
   `/Users/quoc/Documents/Website QBA/assets/hsnl/chung-nhan/`

7. Ba ảnh thiết bị mới đã lưu nhưng chưa tích hợp vào PDF:
   `/Users/quoc/Documents/Website QBA/references/hsnl-goc/thiet-bi-bo-sung/original/`

8. Website hiện tại và nhận diện thương hiệu:
   `/Users/quoc/Documents/Website QBA/index.html`
   `/Users/quoc/Documents/Website QBA/styles.css`
   `/Users/quoc/Documents/Website QBA/script.js`
   `/Users/quoc/Documents/Website QBA/i18n.js`

9. Hai hồ sơ tham khảo Hoàng Kim Catering và Thủy Hằng Catering đã được lưu trong `tmp/pdfs/`. Chỉ học cách tổ chức nội dung và chứng minh năng lực; tuyệt đối không sao chép câu chữ, thiết kế, hình ảnh hoặc nhận diện.

TRẠNG THÁI HIỆN TẠI - KHÔNG ĐƯỢC HIỂU NHẦM

- Đã tạo mô-đun 3 trang chứng nhận công khai:
  `/Users/quoc/Documents/Website QBA/output/pdf/HSNL-QBA-cum-trang-chung-nhan.pdf`
- Script hiện tại:
  `/Users/quoc/Documents/Website QBA/scripts/build_hsnl_certificate_module.py`
- Script hiện chỉ tạo 3 trang: giấy ATTP, tập huấn 23 nhân sự, thẻ an toàn lao động và kiểm nghiệm nước RO.
- Ba ảnh thiết bị mới đã được sao chép vào workspace nhưng chưa được chuẩn hóa hoặc đưa vào PDF.
- Ảnh ISO 22000 chu kỳ cũ đã được lưu để tham khảo tại:
  `/Users/quoc/Documents/Website QBA/references/hsnl-goc/chung-nhan-cu/iso-22000-2018-2023-2026.jpg`
- Chưa có bản HSNL hoàn chỉnh 20-26 trang.
- Khi tiếp tục, kiểm tra worktree và các tệp hiện có trước khi sửa. Không xóa hoặc ghi đè bản gốc.

THỨ TỰ ƯU TIÊN NGUỒN SỰ THẬT

1. Giấy tờ hiện hành và tài liệu gốc mới nhất.
2. Xác nhận mới nhất của chủ doanh nghiệp.
3. Hồ sơ dữ liệu làm việc đã chuẩn hóa.
4. Website hiện tại.
5. Hồ sơ scan cũ.
6. Hồ sơ của đơn vị tham khảo chỉ dùng cho cảm hứng cấu trúc.

Khi có mâu thuẫn, không tự chọn phương án thuận mắt. Hãy lập bảng đối chiếu và đánh dấu `[CẦN XÁC NHẬN]`.

NHỮNG DỮ LIỆU CỐT LÕI ĐÃ ĐƯỢC CUNG CẤP

- Tên pháp lý: CÔNG TY TNHH MỘT THÀNH VIÊN QUỐC BÌNH AN.
- Tên giao dịch: Quốc Bình An Catering.
- Mã số doanh nghiệp/mã số thuế: 3602666032.
- Hoạt động thực tế từ năm 2006; đăng ký pháp lý lần đầu ngày 02/12/2011.
- Theo người dùng: đăng ký thay đổi lần 4 ngày 01/06/2026; cần bản scan mới để đối chiếu.
- Đồng sáng lập: ông Nguyễn Quốc Chinh và bà Trần Thị Thanh Thuỷ.
- Khởi đầu khoảng 600 suất/ngày cho Royal Hoàng Gia.
- Các mốc được cung cấp: E-top khoảng 1.500 suất/ngày cuối năm 2010; khoảng 3.000 suất/ngày sau 5 năm; 10.000 suất/ngày năm 2017; mức cao nhất khoảng 17.000 suất/ngày năm 2019.
- Hiện có 10 bếp, khoảng 100 nhân sự và vận hành 3 ca/ngày; các số liệu chi tiết vẫn phải xác nhận theo bảng dữ liệu.
- Dịch vụ: suất ăn sáng, trưa, ca đêm, món chay, tiệc/buffet, bếp tại chỗ, bếp trung tâm và vận chuyển.
- Dự án tiêu biểu sơ bộ: Royal Hoàng Gia, E-top, Twin Kie và Bellinturf.
- Quy trình đã được xác nhận ở mức khung: chọn nguồn, kiểm nhận, sơ chế, chế biến, chia suất và lưu mẫu.
- Người tiếp nhận phản ánh chính: bà Trần Thị Thanh Thuỷ; phản hồi ban đầu khoảng 15-30 phút.

CÂU CHUYỆN THIẾT BỊ PHẢI ĐƯỢC BỔ SUNG

Thể hiện rõ vai trò của Giám đốc Nguyễn Quốc Chinh trong việc liên tục theo dõi, cập nhật và thay đổi máy móc, trang thiết bị để rút ngắn thao tác, tối ưu thời gian và bảo đảm bữa ăn sẵn sàng đúng giờ.

Thông điệp gợi ý, được phép biên tập cho tự nhiên hơn:
“Với Quốc Bình An, đúng giờ không chỉ là lời hứa ở khâu phục vụ. Đó là kết quả của việc liên tục rà soát quy trình và đầu tư thiết bị phù hợp. Giám đốc Nguyễn Quốc Chinh trực tiếp theo dõi, cập nhật và thay đổi máy móc nhằm rút ngắn thời gian xử lý, giảm thao tác thủ công và giữ từng bữa ăn nóng hổi, sẵn sàng đúng ca.”

Ba ảnh mới cần xử lý đồng bộ với tư liệu máy móc cũ:
- thiết bị sơ chế inox - tên/model chưa xác nhận;
- máy rửa khay tự động;
- máy thái thịt HD-850.

Yêu cầu xử lý ảnh:
- luôn lưu bản gốc riêng;
- không dùng chỉnh sửa tạo sinh làm thay đổi cấu tạo máy;
- chỉ xoay, cắt, cân sáng, tăng độ rõ vừa phải và đặt vào cùng một tỷ lệ/khung hình;
- giữ ảnh trung thực;
- ảnh có watermark/quảng cáo phải được ghi là ảnh minh họa hoặc thay bằng ảnh chụp thực tế trước khi xuất bản nếu quyền sử dụng chưa rõ;
- không khẳng định QBA sở hữu model cụ thể nếu chưa được chủ doanh nghiệp xác nhận.

QUY TẮC XỬ LÝ CHỨNG NHẬN

- Giấy ATTP số 0298/2024/ATTP-CNĐK: có thể trình bày là giấy hiện hành, cấp ngày 08/04/2024, giá trị 3 năm.
- Danh sách 23 nhân sự tập huấn ATTP ngày 01/11/2025: bản website phải ẩn thông tin định danh; bản gốc giữ cho dự thầu/thẩm định.
- 09 thẻ an toàn lao động: bản website ẩn thông tin định danh; thể hiện hiệu lực đến 02/04/2027.
- Phiếu kiểm nghiệm nước RO mã 080626-3425: chỉ mô tả những chỉ tiêu thể hiện trên phiếu; không tự kết luận đạt toàn bộ quy chuẩn nếu thiếu các trang/kết luận còn lại.
- ISO 22000:2018 số HA 522-23 trong HSNL cũ có chu kỳ 11/01/2023-10/01/2026.
- Không viết “đang gia hạn” hoặc trình bày chứng nhận ISO cũ như còn hiệu lực trong bản công khai hiện tại.
- Có thể giữ vị trí thiết kế dễ thay thế hoặc đánh dấu nội bộ `[CHỜ CHỨNG NHẬN ISO MỚI]`. Khi doanh nghiệp nhận giấy mới, thay trực tiếp mà không phải thiết kế lại toàn bộ hồ sơ.
- Giấy ATTP năm 2022 và đăng ký doanh nghiệp thay đổi lần 3 chỉ là tư liệu cũ, không dùng như giấy hiện hành.

TONE GIỌNG

- Chuyên nghiệp, điềm tĩnh, chắc chắn và có tính B2B.
- Có sự gần gũi của “bữa cơm nóng” nhưng không sướt mướt.
- Ưu tiên câu ngắn, động từ rõ và bằng chứng cụ thể.
- Dùng “Quốc Bình An” khi nói về thương hiệu; dùng “chúng tôi” trong lời ngỏ/cam kết.
- Tránh: “hàng đầu”, “tốt nhất”, “tuyệt đối”, “100%”, “vượt trội”, “đẳng cấp” nếu không có bằng chứng.
- Không viết quảng cáo phô trương. Mỗi tuyên bố quan trọng phải đi cùng số liệu, hình ảnh, chứng nhận, dự án hoặc quy trình.
- Không lặp lại cùng một ý “chất lượng - tận tâm - uy tín” trên nhiều trang.

NHẬN DIỆN THỊ GIÁC

Đồng bộ với website:
- xanh đậm `#173B35`;
- nền kem `#F8F6EF`;
- xanh lá nhạt `#B8E59F`;
- vàng `#FFD569`;
- cam `#F0835F`;
- font ưu tiên Be Vietnam Pro; nếu môi trường PDF không có font này, dùng font hỗ trợ tiếng Việt có hình thức tương đương.

Phong cách: hiện đại, sạch, có khoảng thở, giàu hình ảnh thật và thể hiện năng lực vận hành. Không biến HSNL thành tập ảnh chứng nhận hoặc tài liệu kỹ thuật khô cứng.

CẤU TRÚC MỤC TIÊU 20-26 TRANG

Đề xuất và chờ duyệt storyboard trước khi viết/thiết kế toàn bộ. Cấu trúc định hướng:
1. Bìa.
2. Lời ngỏ.
3. Quốc Bình An trong một trang.
4. Câu chuyện khởi nghiệp.
5. Hành trình và các cột mốc.
6. Tầm nhìn - sứ mệnh - giá trị.
7-9. Hệ dịch vụ.
10. Năng lực vận hành.
11. Nhân sự và cơ cấu quản lý.
12-13. Quy trình một chiều.
14. Kiểm soát ATTP.
15. Đào tạo và an toàn lao động.
16. Kiểm soát nguồn nước/lưu mẫu.
17. Đầu tư thiết bị - tối ưu thời gian - đúng giờ.
18-19. Thực đơn và dinh dưỡng.
20-23. Dự án tiêu biểu.
24. Khách hàng đồng hành.
25. Cam kết và quy trình tiếp nhận phản hồi.
26. Liên hệ/CTA.

Cấu trúc được phép rút gọn hoặc đổi thứ tự nếu dữ liệu thực tế yêu cầu, nhưng mỗi trang chỉ nên có 1-2 thông điệp chính.

QUY TRÌNH THỰC HIỆN

GIAI ĐOẠN 0 - KIỂM TRA CHECKPOINT
- Đọc các tệp hiện có và báo chính xác phần nào đã hoàn thành, phần nào mới chỉ sao chép nguồn.
- Không tiếp tục sửa PDF ngay lập tức.
- Lập danh sách thay đổi đề xuất và chờ người dùng đồng ý.

GIAI ĐOẠN 1 - KIỂM TOÁN DỮ LIỆU
- Tạo bảng: dữ liệu / trạng thái / nguồn / được phép công khai / còn thiếu gì.
- Phát hiện các mâu thuẫn về công suất, địa chỉ, số bếp, số nhân sự, thời gian hợp tác, chứng nhận và tên dự án.
- Không tự bịa phần còn thiếu.

GIAI ĐOẠN 2 - STORYBOARD
- Đề xuất 20-26 trang.
- Với từng trang ghi: mục tiêu, tiêu đề, dữ liệu dùng, hình ảnh cần, trạng thái ảnh và CTA nếu có.
- Đánh dấu rõ hình ảnh nào đã có, ảnh nào cần người dùng cung cấp.
- Chờ duyệt storyboard.

GIAI ĐOẠN 3 - BIÊN TẬP
- Viết nội dung hoàn chỉnh theo tone giọng trên.
- Với dự án dùng cấu trúc: bối cảnh - yêu cầu - giải pháp QBA - quy mô - kết quả.
- Nếu chưa có kết quả định lượng, dùng mô tả trung tính và đánh dấu cần bổ sung.

GIAI ĐOẠN 4 - XỬ LÝ HÌNH ẢNH VÀ THIẾT KẾ
- Bảo toàn tệp gốc.
- Chuẩn hóa ảnh thật và ảnh tư liệu.
- Ảnh website công khai phải che dữ liệu cá nhân cần thiết.
- Ảnh minh họa/ảnh nhà cung cấp phải được ghi chú và ưu tiên thay bằng ảnh QBA chụp thực tế.
- Xuất bản A4 dọc, đồng thời kiểm tra khả năng đọc trên điện thoại/flipbook.

GIAI ĐOẠN 5 - KIỂM TRA PDF
- Render toàn bộ trang thành ảnh.
- Kiểm tra lỗi chữ tiếng Việt, cắt chữ, chồng lấn, độ rõ của ảnh, số trang, header/footer, ngày hiệu lực và thông tin liên hệ.
- Không bàn giao khi còn lỗi trực quan.

GIAI ĐOẠN 6 - TÍCH HỢP WEBSITE
- Chỉ thực hiện sau khi PDF được duyệt.
- Tạo ảnh bìa web, liên kết xem/tải PDF và kiểm tra desktop/mobile.

QUY TẮC HỎI ẢNH

Mỗi khi đến một trang thiếu ảnh, hãy nói rõ cho người dùng theo mẫu:
1. Trang/mục đang thiếu.
2. Cần chụp gì.
3. Cần bao nhiêu ảnh.
4. Góc chụp ngang/dọc.
5. Điều cần tránh lộ.
6. Mức độ ưu tiên: bắt buộc / nên có / có thể thay bằng tư liệu cũ.

Không hỏi chung chung “hãy gửi thêm ảnh”.

KẾT QUẢ BÀN GIAO CUỐI

- bảng kiểm dữ liệu;
- storyboard đã duyệt;
- nội dung hoàn chỉnh;
- danh mục hình ảnh và quyền sử dụng;
- PDF chính thức;
- ảnh bìa web;
- bản nguồn có thể cập nhật chứng nhận sau này;
- website đã tích hợp sau khi được duyệt.

LỆNH BẮT ĐẦU

Trước tiên chỉ thực hiện GIAI ĐOẠN 0 và GIAI ĐOẠN 1. Báo checkpoint, liệt kê mâu thuẫn/câu hỏi quan trọng nhất và đề xuất storyboard sơ bộ. Không sửa hoặc xuất PDF mới cho đến khi tôi nói “tiếp tục thiết kế”.
```
