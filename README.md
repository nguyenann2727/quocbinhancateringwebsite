# Website Quốc Bình An — bản draft

Website giới thiệu dịch vụ suất ăn công nghiệp dạng one-page, thiết kế theo phong cách chuyên nghiệp, hiện đại và gần gũi. Trang không có mục Blog hoặc Tuyển dụng.

## Xem website

Mở trực tiếp file `index.html` bằng trình duyệt. Khi đưa lên hosting, tải toàn bộ thư mục này lên cùng một vị trí để giữ nguyên liên kết hình ảnh, giao diện và hiệu ứng.

## Thông tin cần thay trước khi xuất bản

Các nội dung còn cần chủ doanh nghiệp xác nhận trước khi xuất bản chính thức:

1. Địa chỉ pháp lý và địa chỉ chính xác của từng bếp nếu cần công khai hoặc thay các vị trí đại diện trên bản đồ.
2. Quyền sử dụng công khai logo của các doanh nghiệp trong mục **Khách hàng**.
3. Các ảnh thực đơn còn trống ở nhóm 40K.
4. Hiệu lực và phạm vi công khai của các chứng nhận đang hiển thị.
5. File Hồ sơ năng lực PDF chính thức để mở nút tải.

## Cấu trúc

- `index.html`: toàn bộ nội dung website.
- `styles.css`: màu sắc, bố cục, hiệu ứng và giao diện điện thoại.
- `script.js`: menu mobile, hiệu ứng khi cuộn, bộ đếm, thực đơn tương tác, hotline, gửi biểu mẫu và trình quản lý ảnh.
- `assets/`: hình ảnh hero, thực đơn, đối tác, chứng nhận và thiết bị đang dùng cho website.
- `image-config.json`: cấu hình ảnh xuất bản; tệp mặc định rỗng và được cập nhật bằng công cụ quản lý ảnh.
- `robots.txt`: cho phép công cụ tìm kiếm lập chỉ mục website.

## Logo Quốc Bình An

Website đang dùng logo chính thức từ ảnh người dùng cung cấp ngày 07/07/2026. Bản đầy đủ có dòng **“Tận tâm trong từng bữa ăn”** nằm tại `assets/qba-logo-full.jpg` và đang xuất hiện ở hero, footer và khung Hồ sơ doanh nghiệp; bản biểu tượng dùng cho header/footer và icon trình duyệt nằm tại `assets/qba-logo-mark.png` và `assets/favicon.png`. Hero hiện đặt trực tiếp ảnh bếp/chế biến thực phẩm `assets/hero-kitchen-cooking-bright-7476.jpg` trong HTML để luôn hiện trước, có khói nhẹ rồi lật sang ảnh xe QBA tại công ty `assets/hero-qba-truck-bellinturf-20260708.jpg`; người dùng bật giảm chuyển động sẽ thấy ảnh bếp/chế biến thực phẩm tĩnh.

## Biểu mẫu liên hệ

Biểu mẫu đã kết nối FormSubmit để chuyển yêu cầu đến `quocbinhan975@gmail.com` khi website chạy trên hosting bằng HTTP/HTTPS.

Biểu mẫu thu thập các dữ liệu cần thiết cho tư vấn B2B: người liên hệ, tên doanh nghiệp, điện thoại, email, sản lượng dự kiến, dịch vụ, khu vực và nhu cầu cụ thể.

1. Sau khi đưa website lên hosting, gửi thử biểu mẫu một lần.
2. Mở hộp thư `quocbinhan975@gmail.com` và bấm liên kết kích hoạt do FormSubmit gửi đến. Kiểm tra cả thư Spam.
3. Từ lần tiếp theo, trình duyệt sẽ gửi trực tiếp biểu mẫu đến FormSubmit bằng `action` và `method` của form; FormSubmit sẽ hiển thị trang phản hồi sau khi xử lý.

Mẫu gửi thử nên dùng:

- Họ và tên: `Khách test website`
- Tên doanh nghiệp: `Công ty kiểm tra form`
- Số điện thoại: `0907090572`
- Email nhận phản hồi: email đang dùng để kiểm tra
- Số suất / ngày: `500`
- Dịch vụ quan tâm: `Suất ăn trưa`
- Khu vực cần phục vụ: `TP. Đồng Nai`
- Nhu cầu: `Đây là mẫu kiểm tra e-form từ website Quốc Bình An.`

Nếu muốn đổi email nhận mẫu, sửa cả `action` và `data-recipient-email` trong thẻ `<form id="contact-form">` ở `index.html`.

Khi mở trực tiếp bằng `file://`, biểu mẫu chuyển sang phương án dự phòng là mở ứng dụng email với nội dung đã điền sẵn. Khi chạy bằng HTTP/HTTPS, JavaScript không chặn submit và không gửi AJAX cho biểu mẫu này.

## Hotline

Bấm vào số điện thoại hoặc nút điện thoại nổi để mở bảng hotline. Hai nút **Gọi ngay** sử dụng liên kết `tel:` và sẽ mở màn hình gọi trên thiết bị hỗ trợ.

## Ngôn ngữ

Thanh đầu trang hỗ trợ năm ngôn ngữ: Tiếng Việt, English, 한국어, 日本語 và 中文. Lựa chọn được lưu trên trình duyệt và áp dụng cho cả nội dung tĩnh lẫn các thành phần được tạo bằng JavaScript như lịch tuần và thư viện thực đơn.

- `i18n.js`: từ điển, bộ máy dịch nội dung và lưu lựa chọn ngôn ngữ.
- `script.js`: dữ liệu nghiệp vụ và các tương tác; nội dung mới bằng tiếng Việt sẽ được bộ máy dịch xử lý khi có bản dịch tương ứng.

## Hồ sơ năng lực

Phần Giới thiệu có khung **Hồ sơ năng lực Quốc Bình An**. Website đang dùng ảnh dự án làm bìa xem trước; ảnh này vẫn có thể được thay bằng vị trí `Ảnh bìa Hồ sơ năng lực` trong trình quản lý ảnh. Bìa, logo và nút PDF mở hồ sơ chính thức tại `output/pdf/HSNL-Quoc-Binh-An-Catering-WEBSITE.pdf`.

Riêng bản **HSNL PDF draft** có editor trực tiếp. Mở `Mo-HSNL-Editor.command` để tự khởi động bản chỉnh sửa và PDF hoàn chỉnh trên máy. Công cụ này chạy nền, tự tìm cổng còn hoạt động và hạn chế lỗi `ERR_CONNECTION_REFUSED` khi mở lại sau một thời gian. Khi bấm **Dựng lại PDF**, bản `FINAL` và bản nhẹ cho web cũng được cập nhật cùng lúc.

Để dựng bộ static asset dùng cho production, chạy `python3 scripts/build_site_dist.py`. Thư mục `dist/` chỉ chứa các file runtime đang được website tham chiếu và bản PDF public nói trên.

## Chứng nhận, quy trình và năng lực

Khung **An toàn từ nguồn** đang dùng ảnh ISO 22000:2018 tại `assets/hsnl/chung-nhan/iso-22000-qba-2023-2026.jpg`. Hai khung chứng nhận kế bên đang phục hồi đúng về chứng nhận đào tạo ISO 22000:2018 của **Trần Thị Thanh Thuỷ** và **Nguyễn Quốc Chinh** tại `assets/hsnl/chung-nhan/iso-dao-tao-tran-thi-thanh-thuy.png` và `assets/hsnl/chung-nhan/iso-dao-tao-nguyen-quoc-chinh.png`. Hiệu lực/phạm vi công khai của các chứng nhận vẫn cần chủ doanh nghiệp xác nhận trước khi xuất bản chính thức.

Mục **04 / Quy trình** có sáu ảnh mặc định trong `assets/process/` cho các bước chọn nguồn, kiểm nhận, sơ chế, chế biến, chia suất và lưu mẫu. Các ảnh này vẫn là slot chỉnh được bằng trình quản lý ảnh.

Ảnh năng lực cuối trang đang là cụm năm ảnh trong `assets/capacity/`: đội ngũ áo xanh họp, máy móc thiết bị bếp, máy cắt thịt, thao tác chia suất và ảnh nhà ăn đông công nhân. Ảnh nhà ăn mới được tối ưu tại `assets/capacity/capacity-dining-hall-4k.jpg`.

Mục **02 / Dịch vụ** hiện có ảnh mặc định cho cả năm mô hình phục vụ. Riêng **Suất ăn trưa**, **Tiệc sự kiện**, **Thực đơn chay** và **Suất ăn sáng** đang dùng ảnh ưu tiên mới trong `assets/services/`: `service-lunch-tray-v4.jpg`, `service-event-banquet-v3.png`, `service-vegan-tray-v3.jpg` và `service-breakfast-prep-v3.png`. Ảnh nền Suất ăn trưa bản V4 đặt khay rõ hơn và chừa vùng nền dịu cho chữ; khung ảnh Thực đơn chay được tăng chiều cao để khay nhìn rõ hơn. Bộ ảnh vẫn có thể thay trực tiếp bằng trình quản lý ảnh.

Ngày 20/07/2026 bổ sung khối **Thực đơn mẫu QBA** trong mục Dịch vụ. Nội dung được gõ lại và trình bày thành các bảng tương tác từ ảnh thực đơn đang nấu do người dùng cung cấp, gồm mẫu Thực đơn Việt Nam, Bellinturf chay, ETOP Bếp 1 và ba mẫu nhiều ca A/B/C. Mẫu chay hiển thị đủ Thứ 2 đến Chủ nhật; mẫu ETOP Bếp 1 giữ đúng phạm vi Thứ 2 đến Thứ 7 và đánh dấu ô tăng ca không có món bằng gạch ngang; các mẫu nhiều ca hiển thị đủ Thứ 2 đến Chủ nhật khi ảnh nguồn có Chủ nhật. Website không nhúng nguyên ảnh bảng tính thô; chỉ dùng nội dung món đã biên tập để khách hàng xem nhanh trên desktop và điện thoại.

Ngày 23/07/2026 thêm file `open-qba-site.command` để mở bản xem cục bộ ổn định tại `http://127.0.0.1:8787/index.html#services`. File này tự kiểm tra máy chủ cục bộ, tự bật lại nếu đang tắt và dùng `nohup` để hạn chế lỗi reload bị `ERR_CONNECTION_REFUSED` khi xem website trong trình duyệt.

Ngày 23/07/2026 cập nhật minh họa bản đồ Việt Nam trong mục **Vùng phục vụ**: giữ các điểm vùng phục vụ hiện tại và bổ sung hai cụm chấm đảo không ghi nhãn tên để thể hiện phần biển đảo, đồng thời ghi chú rõ đây là minh họa không thể hiện ranh giới hành chính chi tiết.

## Thực đơn tuần

Mục 3 gồm năm mức giá **23K**, **24K**, **25K**, **40K** và **45–50K chuyên gia**. Giao diện hiện tách thành hai phần: bảng thực đơn tuần tinh gọn theo Thứ 2–Thứ 7 ở phía trên và khu hình ảnh suất ăn ở phía dưới. Bảng tuần hiển thị nhóm món ngắn gọn theo ngày, không hiển thị calories.

Ngày 23/07/2026, phần lịch món theo ngân sách được chỉnh chỉ hiển thị các món của **ca trưa** để khớp với ảnh một khay suất ăn trưa. Các dòng món và nhãn nhóm món trong lịch Thứ 2 đến Thứ 7 đã mở quyền **Chỉnh nội dung** trực tiếp; nội dung sửa được lưu theo từng đơn giá, từng ngày và từng dòng món.

Mỗi mức giá vẫn có sáu vị trí ảnh mẫu, tổng cộng 30 khung ảnh độc lập; có thể chuyển mẫu bằng nút mũi tên hoặc vuốt trên điện thoại. Khu ảnh được tách riêng khỏi bảng món để dễ xem ảnh thực tế và thay ảnh bằng trình quản lý ảnh.

Nút **Nhận báo giá thực đơn này** tự điền mức giá đang xem vào biểu mẫu liên hệ. Nút **Xem toàn bộ hình ảnh** mở thư viện ảnh theo đơn giá; ảnh trong thư viện dùng chung với khung trình chiếu nên chỉ cần thay một lần.

Theo yêu cầu ngày 23/07/2026, nhóm **23K** vẫn giữ bộ món 23K cũ từ Thứ 2 đến Thứ 7, nhưng phần ảnh đại diện/lưới ảnh tuần của bảng thực đơn chỉ dùng các ảnh V3 mới đã xác nhận để tránh lẫn ảnh sai. Mẫu 01/06 dùng ảnh khay gà luộc lá chanh được phục hồi từ ảnh chụp màn hình tại `assets/menu/qba-23k-mon-ga-luoc-la-chanh-restored.jpg`, Thứ 3 dùng ảnh cá ba sa, Thứ 5 dùng ảnh khay có sữa/chuối cho món gà kho sả, Thứ 6 dùng ảnh ba rọi chiên mè tại `assets/menu/qba-23k-fri-ba-roi-chien-me-restored.jpg`; các ngày chưa có ảnh V3 riêng sẽ hiện ô “Chờ ảnh V3” thay vì tự lấy lại ảnh 22K cũ.

Ảnh trong lưới **Ảnh suất ăn theo tuần** có slot chỉnh sửa riêng dạng `menu-week-{đơn giá}-{thứ}` cho từng ngày Thứ 2–Thứ 7. Khi bật chế độ **Hình ảnh**, có thể bấm hoặc thả ảnh trực tiếp vào từng ô lịch tuần; ảnh này tách riêng khỏi sáu khung **Hình ảnh suất ăn** bên dưới để không làm lẫn ảnh đại diện lịch món với ảnh thực tế tự ghép.

Ngày 23/07/2026, chế độ **Hình ảnh** của khu **Hình ảnh suất ăn** được chỉnh để hiện thành lưới 6 khung của đúng đơn giá đang chọn. Bản public vẫn chỉ hiển thị một ảnh active tinh gọn như cũ, nhưng trong chế độ chỉnh sửa có thể bấm/thả ảnh cho đủ Thứ 2–Thứ 7 mà không phải chuyển từng ngày.

Khu **Hình ảnh suất ăn** tách riêng của nhóm 23K hiện có ảnh mặc định cho mẫu 01/06 là khay gà luộc lá chanh, còn các vị trí mẫu 02–06 để trống để người dùng tự ghép ảnh khay mẫu 23K khác vào bằng trình quản lý ảnh. Khi mở bằng `?edit=1`, khung trống active vẫn hiển thị để dễ bấm/thả ảnh; bản public không bị ép hiện ảnh 23K cũ ở các mẫu chưa xác nhận. Mốc làm mới `qba-menu-price-remap-revision` xoá các ảnh lưu cục bộ cũ của 23K/25K khi mở bằng chế độ chỉnh sửa, tránh reload xong quay lại ảnh sai.

Nhóm **25K** đang được để trống theo yêu cầu ngày 18/07/2026 vì bộ 23K cũ là suất ăn rẻ hơn và không còn dùng làm nội dung tạm cho 25K. Tab 25K vẫn được giữ trong hệ thực đơn để sau này bổ sung thực đơn và ảnh chính thức, nhưng hiện không có món, không có ảnh đại diện theo tuần và không có ảnh mặc định `menu-energy-*`.

Nhóm 24K hiện đã có đủ 6 ảnh khay thực tế theo tuần tại `assets/menu-24k-real-pro-01.jpg` đến `assets/menu-24k-real-pro-06.jpg`. Các ảnh được xử lý đồng bộ theo phong cách nền xám sạch, giữ nguyên khay/món/vị trí thực tế; riêng mẫu 01/06 được xoay ngang theo yêu cầu để đồng bộ với các ảnh còn lại. Nội dung món trong bảng tuần 24K được cập nhật theo thực đơn ETOP Bếp 2 ngày 6/7–11/7; ảnh bảng gốc được lưu tham chiếu tại `assets/menu/menu-weekly-24k-etop-20260706-11.jpg`.

Nhóm 40K hiện có một ảnh không kèm canh đã được làm sạch, căn thẳng và giữ nguyên định lượng tại `assets/menu-40k-pro-01.jpg`. Các mẫu 02–06 vẫn để trống chờ bổ sung.

Nhóm 45–50K chuyên gia hiện có đủ 6 ảnh bàn ăn chuyên gia theo tuần tại `assets/menu/qba-expert-mon-table-7580.jpg` đến `assets/menu/qba-expert-sat-table-7586.jpg`. Các ảnh này đi theo cặp ngày với nhóm 25K: 25K là khay cơm người lao động, 45–50K là bàn ăn chuyên gia.

Ảnh bảng thực đơn 23K người dùng gửi ngày 07/07/2026 được tối ưu và lưu tham chiếu tại `assets/menu/menu-weekly-23k-table.jpg`. Bảng thực đơn 24K ETOP Bếp 2 gửi ngày 14/07/2026 được lưu tại `assets/menu/menu-weekly-24k-etop-20260706-11.jpg`. Bảng thực đơn 25K ETOP Bếp 2 gửi ngày 08/07/2026 được lưu tại `assets/menu/menu-weekly-25k-etop-20260622-27.jpg`.

Mục đối tác hiện có đủ 9 ảnh nhận diện mặc định cho E-top, Twinkle, Hoàng Gia, JYS, Bellinturf, Jintian, Lewo/Leow Foods, Tah Tong và Minh Trị. Ảnh tùy chỉnh luôn được ưu tiên và có thể kéo/chỉnh trực tiếp bằng trình quản lý ảnh.

## Chỉnh sửa draft trực tiếp

Ở góc trái phía dưới có nút **Chỉnh sửa draft**. Khi bấm vào, website mở bảng nhỏ để chọn **Chỉnh hình ảnh** hoặc **Chỉnh nội dung**. Công cụ này chỉ hiện khi mở trực tiếp trên máy hoặc khi thêm `?edit=1` vào cuối địa chỉ website.

Ví dụ khi xem bản online hoặc preview cục bộ: `https://tenmien.vn/?edit=1`.

## Chỉnh sửa hình ảnh trực tiếp

1. Bấm **Chỉnh sửa draft** rồi chọn **Chỉnh hình ảnh**, hoặc bấm nhanh nút **Hình ảnh** ở góc trái phía dưới.
2. Khi website đã đưa lên hosting, công cụ chỉnh ảnh được ẩn với khách truy cập. Thêm `?edit=1` vào cuối địa chỉ website để bật chế độ chỉnh ảnh, ví dụ `https://tenmien.vn/?edit=1`.
3. Bấm trực tiếp vào từng khung trên trang để thay ảnh từ file máy, hoặc kéo-thả ảnh JPG, PNG, WebP vào đúng vị trí mong muốn.
4. Ảnh được thu nhỏ tối đa còn 1.600px, tối ưu dung lượng và lưu tự động trong IndexedDB của trình duyệt, không gửi ra ngoài.
5. Trong bảng quản lý, có thể thay ảnh, khôi phục, chỉnh tâm ngang, tâm dọc, độ phóng, góc xoay và kích thước khung. Với ảnh nền, có thêm lớp phủ để chữ dễ đọc.
6. Sau khi chọn ảnh, có thể bấm giữ và kéo ngay trong khung để căn nhanh phần đẹp nhất của ảnh.
7. Khi bật chế độ chỉnh ảnh, kéo các nút tròn ở cạnh hoặc góc khung để nới rộng, thu hẹp ngang dọc; bấm **Khôi phục khung** nếu muốn trả riêng khung đó về mặc định.
8. Logo khách hàng được thay bằng cách bấm trực tiếp vào vòng tròn số 01–09.
9. Dùng **Xuất dữ liệu ảnh** để tải file `image-config.json`. Đặt file này cùng cấp với `index.html` khi đưa website lên hosting; bản online sẽ tự nạp toàn bộ ảnh và kích thước khung đã chỉnh.
10. Dùng **Nhập dữ liệu ảnh** để tiếp tục chỉnh sửa bộ ảnh trên trình duyệt hoặc máy tính khác.

Ảnh tối đa 10MB. Khi tắt chế độ chỉnh sửa, toàn bộ nút quản trị sẽ được ẩn khỏi giao diện khách hàng.

Lưu ý: `?edit=1` là chế độ chỉnh sửa cục bộ, không phải hệ thống đăng nhập quản trị. Các thay đổi mới chỉ tồn tại trong trình duyệt cho đến khi xuất và đưa file `image-config.json` lên hosting.

## Chỉnh sửa chữ và số trực tiếp

1. Bấm **Chỉnh sửa draft** rồi chọn **Chỉnh nội dung**, hoặc bấm nhanh nút **Nội dung** ở góc trái phía dưới.
2. Bấm trực tiếp vào vùng chữ hoặc số có viền nhẹ để sửa; nội dung tự lưu sau khi dừng nhập.
3. Nhấn `Ctrl/Command + Enter` để lưu nhanh và thoát khỏi ô đang sửa, hoặc bấm **Xong** để đóng chế độ chỉnh nội dung.
4. **Khôi phục mục** chỉ hoàn tác vùng đang chọn; **Khôi phục tất cả** đưa toàn bộ chữ và số về nội dung ban đầu.
5. Khi sửa số điện thoại hoặc email trong khu vực liên hệ, đường dẫn gọi điện/gửi email tương ứng cũng được cập nhật tự động.

Nội dung chỉnh sửa được lưu trong `localStorage` của trình duyệt và công cụ chỉ xuất hiện khi mở file trực tiếp hoặc dùng `?edit=1`. Chế độ này tự chuyển về tiếng Việt để tránh sửa nhầm bản dịch và không can thiệp vào biểu mẫu liên hệ hay menu điều hướng.
