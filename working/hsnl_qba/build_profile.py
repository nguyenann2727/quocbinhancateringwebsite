from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "Ho-so-nang-luc-Quoc-Binh-An-ban-nhap-01.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
pdfmetrics.registerFont(TTFont("QBA", FONT))
pdfmetrics.registerFont(TTFont("QBA-Bold", FONT_BOLD))

W, H = A4
M = 16 * mm

INK = HexColor("#173B35")
DARK = HexColor("#102D28")
CREAM = HexColor("#F8F6EF")
MINT = HexColor("#B8E59F")
YELLOW = HexColor("#FFD569")
ORANGE = HexColor("#F0835F")
TEXT = HexColor("#263632")
MUTED = HexColor("#6C7A76")
LINE = HexColor("#D7DDD8")
PALE = HexColor("#EEF2EC")
WHITE = white


def style(size=10, leading=None, color=TEXT, bold=False, align=TA_LEFT):
    return ParagraphStyle(
        name=f"s-{size}-{bold}-{align}",
        fontName="QBA-Bold" if bold else "QBA",
        fontSize=size,
        leading=leading or size * 1.35,
        textColor=color,
        alignment=align,
        spaceAfter=0,
        spaceBefore=0,
    )


def para(c, text, x, top, width, size=10, leading=None, color=TEXT, bold=False, align=TA_LEFT, max_h=300):
    p = Paragraph(text, style(size, leading, color, bold, align))
    _, h = p.wrap(width, max_h)
    p.drawOn(c, x, top - h)
    return top - h


def round_rect(c, x, y, w, h, fill, radius=10, stroke=None, sw=1):
    c.setLineWidth(sw)
    c.setStrokeColor(stroke or fill)
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1 if stroke else 0)


def image_placeholder(c, x, y, w, h, label, note="Ảnh gốc sẽ được thay vào khung này"):
    c.setFillColor(HexColor("#F2F4F0"))
    c.setStrokeColor(HexColor("#9AA9A3"))
    c.setDash(4, 3)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setDash()
    c.setStrokeColor(HexColor("#C4CDC8"))
    c.line(x + 12, y + 12, x + w - 12, y + h - 12)
    c.line(x + 12, y + h - 12, x + w - 12, y + 12)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 8.5)
    c.drawCentredString(x + w / 2, y + h / 2 + 7, "ẢNH CẦN BỔ SUNG")
    para(c, label, x + 18, y + h / 2, w - 36, 10, 13, INK, True, TA_CENTER, h / 2)
    para(c, note, x + 18, y + 28, w - 36, 7.2, 9, MUTED, False, TA_CENTER, 24)


def tag(c, text, x, y, fill=MINT, color=INK, width=None):
    width = width or max(56, pdfmetrics.stringWidth(text, "QBA-Bold", 7.5) + 18)
    round_rect(c, x, y, width, 20, fill, 10)
    c.setFillColor(color)
    c.setFont("QBA-Bold", 7.5)
    c.drawCentredString(x + width / 2, y + 6.5, text.upper())
    return width


def footer(c, page_no, section="HỒ SƠ NĂNG LỰC 2026"):
    c.setStrokeColor(LINE)
    c.line(M, 14 * mm, W - M, 14 * mm)
    c.setFont("QBA", 7.3)
    c.setFillColor(MUTED)
    c.drawString(M, 9.5 * mm, f"QUỐC BÌNH AN CATERING  /  {section}")
    c.drawRightString(W - M, 9.5 * mm, f"{page_no:02d}")


def page_base(c, page_no, kicker, title, intro=None, section=None):
    c.setFillColor(CREAM)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    tag(c, kicker, M, H - 24 * mm, MINT)
    y = para(c, title, M, H - 33 * mm, W - 2 * M, 27, 31, INK, True)
    if intro:
        y = para(c, intro, M, y - 7, W - 2 * M, 10.2, 15, MUTED)
    footer(c, page_no, section or kicker)
    return y - 18


def card(c, x, y, w, h, title, body, fill=WHITE, accent=INK, number=None):
    round_rect(c, x, y, w, h, fill, 10, LINE)
    if number:
        round_rect(c, x + 14, y + h - 36, 24, 24, accent, 12)
        c.setFont("QBA-Bold", 8)
        c.setFillColor(WHITE)
        c.drawCentredString(x + 26, y + h - 28, str(number))
        tx = x + 47
    else:
        c.setFillColor(accent)
        c.circle(x + 20, y + h - 23, 4, fill=1, stroke=0)
        tx = x + 31
    para(c, title, tx, y + h - 14, w - (tx - x) - 14, 10, 13, INK, True, max_h=36)
    para(c, body, x + 14, y + h - 52, w - 28, 8.4, 12.2, TEXT, False, max_h=h - 58)


def stat(c, x, y, w, h, value, label, fill=INK, color=WHITE):
    round_rect(c, x, y, w, h, fill, 12)
    para(c, value, x + 12, y + h - 18, w - 24, 21, 23, color, True, TA_CENTER, 28)
    para(c, label, x + 12, y + h - 50, w - 24, 8.2, 10.5, color, False, TA_CENTER, 34)


def note_band(c, text, y=18 * mm):
    round_rect(c, M, y, W - 2 * M, 24, HexColor("#FFF1E9"), 8)
    para(c, text, M + 12, y + 17, W - 2 * M - 24, 7.3, 9, HexColor("#8A4B36"), False, TA_CENTER, 18)


def cover(c):
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.circle(W - 30 * mm, H - 28 * mm, 58 * mm, fill=1, stroke=0)
    c.setFillColor(ORANGE)
    c.circle(W - 7 * mm, 20 * mm, 34 * mm, fill=1, stroke=0)
    image_placeholder(c, W * 0.52, 88 * mm, W * 0.40, 152 * mm, "Ảnh bìa: đội ngũ hoặc khu bếp đang vận hành")
    image_placeholder(c, M, H - 38 * mm, 46 * mm, 19 * mm, "LOGO QBA", "Ưu tiên PNG nền trong hoặc SVG")
    tag(c, "HỒ SƠ NĂNG LỰC 2026", M, H - 68 * mm, YELLOW, DARK, 112)
    y = para(c, "QUỐC BÌNH AN<br/>CATERING", M, H - 82 * mm, W * 0.45, 31, 34, WHITE, True)
    para(c, "Bữa ăn nóng hổi.<br/>Đúng giờ. Từ cái tâm.", M, y - 15, W * 0.42, 14, 20, MINT, True)
    para(c, "Suất ăn công nghiệp  •  Bếp tại chỗ  •  Bếp trung tâm và vận chuyển", M, 69 * mm, W * 0.42, 9, 13, WHITE)
    c.setStrokeColor(HexColor("#6B8A82"))
    c.line(M, 49 * mm, W * 0.45, 49 * mm)
    para(c, "20 năm kinh nghiệm vận hành và đồng hành cùng doanh nghiệp", M, 42 * mm, W * 0.42, 8.3, 11, HexColor("#D8E7E1"))
    c.showPage()


def build():
    c = canvas.Canvas(str(OUT), pagesize=A4, pageCompression=1)
    c.setTitle("Hồ sơ năng lực Quốc Bình An Catering - Bản nháp 01")
    c.setAuthor("Quốc Bình An Catering")

    cover(c)

    # 02 - Opening story
    y = page_base(c, 2, "CÂU CHUYỆN QBA", "Khởi đầu từ sự thấu hiểu một bữa cơm tử tế", "Quốc Bình An được hình thành từ trải nghiệm rất thật của những người từng đi qua khó khăn và hiểu rằng một bữa cơm nóng, đủ đầy có thể tiếp thêm sức lực lẫn tinh thần cho người lao động.")
    text_w = 96 * mm
    y1 = para(c, "Từ khoảng 600 suất ăn mỗi ngày ở giai đoạn đầu, Quốc Bình An từng bước trưởng thành bằng chính sự gắn bó của khách hàng, khả năng lắng nghe và tinh thần liên tục cải tiến.", M, y, text_w, 10.3, 15, TEXT)
    para(c, "Mỗi dự án là một hành trình riêng. QBA không chỉ cung cấp suất ăn, mà còn cùng doanh nghiệp xây dựng một nhịp phục vụ ổn định, phù hợp khẩu vị và thích nghi với thực tế vận hành của từng nhà máy.", M, y1 - 15, text_w, 10.3, 15, TEXT)
    quote_x = M + 105 * mm
    quote_w = W - M - quote_x
    round_rect(c, quote_x, y - 148, quote_w, 140, INK, 12)
    para(c, "“Chúng tôi nấu bằng sự tươi ngon của nguyên liệu và cái tâm của người làm nghề.”", quote_x + 18, y - 38, quote_w - 36, 12, 18, WHITE, True, TA_CENTER, 104)
    image_placeholder(c, M, 55 * mm, 88 * mm, 92 * mm, "Chân dung ông Nguyễn Quốc Chinh")
    image_placeholder(c, M + 96 * mm, 55 * mm, 88 * mm, 92 * mm, "Chân dung bà Trần Thị Thanh Thuỷ")
    c.showPage()

    # 03 - Company profile
    y = page_base(c, 3, "TỔNG QUAN", "Một nền tảng lâu dài cho dịch vụ suất ăn công nghiệp", "Thông tin doanh nghiệp được trình bày cô đọng để khách hàng, phòng mua hàng và bộ phận hành chính dễ tra cứu.")
    col = (W - 2 * M - 10) / 2
    card(c, M, y - 98, col, 92, "Tên pháp lý", "CÔNG TY TNHH MỘT THÀNH VIÊN QUỐC BÌNH AN<br/><br/><b>Tên giao dịch:</b> Quốc Bình An Catering", WHITE, INK)
    card(c, M + col + 10, y - 98, col, 92, "Đăng ký doanh nghiệp", "<b>Mã số thuế:</b> 3602666032<br/><b>Đăng ký lần đầu:</b> 02/12/2011<br/><b>Thay đổi lần 4:</b> 01/06/2026", WHITE, ORANGE)
    card(c, M, y - 202, col, 94, "Địa chỉ", "Số 35 đường Huỳnh Văn Nghệ, KP Phước Kiểng, phường Nhơn Trạch, tỉnh Đồng Nai.<br/><font color='#8A4B36'>Tên đơn vị hành chính cần đối chiếu giấy đăng ký mới.</font>", WHITE, INK)
    card(c, M + col + 10, y - 202, col, 94, "Liên hệ", "<b>Nguyễn Quốc Chinh - Giám đốc</b><br/>0907 090 572<br/><br/><b>Trần Thị Thanh Thuỷ</b><br/>0909 843 604<br/>quocbinhan975@gmail.com", WHITE, ORANGE)
    image_placeholder(c, M, 54 * mm, W - 2 * M, 72 * mm, "Ảnh trụ sở hoặc toàn cảnh một bếp tiêu biểu")
    c.showPage()

    # 04 - Numbers
    y = page_base(c, 4, "NĂNG LỰC", "Những con số kể câu chuyện vận hành", "Các số liệu dưới đây được tổng hợp từ câu trả lời và cần người có thẩm quyền phê duyệt trước khi phát hành chính thức.")
    gap = 9
    sw = (W - 2 * M - 2 * gap) / 3
    stat(c, M, y - 82, sw, 76, "20 năm", "Kinh nghiệm từ năm 2006", INK)
    stat(c, M + sw + gap, y - 82, sw, 76, "17.000", "Suất/ngày ở mốc cao nhất", ORANGE)
    stat(c, M + 2 * (sw + gap), y - 82, sw, 76, "15.000+", "Năng lực phục vụ/ngày", INK)
    stat(c, M, y - 170, sw, 76, "10 bếp", "Mô hình bếp tại chỗ và trung tâm", HexColor("#2C5A51"))
    stat(c, M + sw + gap, y - 170, sw, 76, "100", "Nhân sự vận hành", HexColor("#2C5A51"))
    stat(c, M + 2 * (sw + gap), y - 170, sw, 76, "3 ca", "Phục vụ liên tục mỗi ngày", HexColor("#2C5A51"))
    image_placeholder(c, M, 54 * mm, W - 2 * M, 70 * mm, "Ảnh quy mô vận hành: dây chuyền chia suất hoặc căng tin đông người")
    note_band(c, "CẦN DUYỆT: công suất thực tế hiện tại, công suất thiết kế, cách tính số bếp và số nhân sự.", 18 * mm)
    c.showPage()

    # 05 - Timeline
    y = page_base(c, 5, "HÀNH TRÌNH", "Từ 600 suất ăn đến năng lực phục vụ quy mô lớn", "Sự phát triển của QBA gắn với những hợp đồng dài hạn, năng lực thích nghi và niềm tin được bồi đắp qua thời gian.")
    items = [
        ("2006", "Khởi đầu", "Khoảng 600 suất/ngày cho khách hàng Royal Hoàng Gia."),
        ("Cuối 2010", "Mở rộng", "Tiếp nhận dự án E-top với khoảng 1.500 suất/ngày."),
        ("Sau 5 năm", "Củng cố", "Nâng quy mô vận hành lên khoảng 3.000 suất/ngày."),
        ("2017", "Tăng trưởng", "Đạt mốc khoảng 10.000 suất/ngày."),
        ("2019", "Mốc cao", "Ghi nhận mức phục vụ khoảng 17.000 suất/ngày."),
        ("Hiện nay", "Thích nghi", "Duy trì uy tín qua biến động và tiếp tục đầu tư thiết bị, quy trình."),
    ]
    line_x = M + 29
    c.setStrokeColor(MINT)
    c.setLineWidth(5)
    c.line(line_x, 66 * mm, line_x, y - 8)
    top = y - 8
    for i, (yr, title, body) in enumerate(items):
        yy = top - i * 78
        c.setFillColor(ORANGE if i in (0, 4) else INK)
        c.circle(line_x, yy - 10, 7, fill=1, stroke=0)
        tag(c, yr, line_x + 19, yy - 20, YELLOW, DARK, 66)
        para(c, title, line_x + 96, yy - 2, 90, 10, 13, INK, True, max_h=20)
        para(c, body, line_x + 190, yy, W - M - line_x - 195, 8.6, 12, TEXT, False, max_h=52)
    note_band(c, "Các mốc thời gian và tên khách hàng cần được duyệt lần cuối trước khi công khai.", 18 * mm)
    c.showPage()

    # 06 - Services
    y = page_base(c, 6, "DỊCH VỤ", "Đáp ứng linh hoạt theo nhịp vận hành của doanh nghiệp", "Từ bữa sáng đến ca đêm, từ bếp tại chỗ đến vận chuyển, QBA tổ chức dịch vụ theo quy mô và đặc thù của từng nhà máy.")
    services = [
        ("Suất ăn trưa công nghiệp", "Thực đơn cân đối, phục vụ đúng khung giờ sản xuất."),
        ("Suất ăn sáng", "Gọn, đủ năng lượng và thuận tiện cho đầu ca."),
        ("Suất ăn ca đêm", "Duy trì chất lượng và độ nóng ở khung giờ đặc thù."),
        ("Thực đơn chay", "Linh hoạt theo nhu cầu văn hóa và chế độ ăn."),
        ("Tiệc và buffet", "Phục vụ hội nghị, sự kiện và chương trình nội bộ."),
        ("Bếp tại chỗ", "Tổ chức nhân sự và vận hành trực tiếp tại nhà máy."),
        ("Bếp trung tâm", "Chế biến tập trung và vận chuyển trong bán kính phù hợp."),
    ]
    cw = (W - 2 * M - 20) / 3
    ch = 82
    for i, (t, b) in enumerate(services[:6]):
        row, col = divmod(i, 3)
        card(c, M + col * (cw + 10), y - (row + 1) * (ch + 10), cw, ch, t, b, WHITE, INK, i + 1)
    card(c, M, 56 * mm, W - 2 * M, 70, services[6][0], services[6][1] + "  Mô hình có thể kết hợp cùng bếp tại chỗ để tăng tính chủ động.", HexColor("#EAF2E7"), ORANGE, 7)
    image_placeholder(c, M, 21 * mm, W - 2 * M, 28 * mm, "Ảnh ghép 3 loại hình dịch vụ tiêu biểu", "Khung ảnh ngang, có thể thay bằng 3 ảnh nhỏ")
    c.showPage()

    # 07 - Models
    y = page_base(c, 7, "MÔ HÌNH PHỤC VỤ", "Hai mô hình - một chuẩn cam kết", "QBA kết hợp bếp tại chỗ và bếp trung tâm để tối ưu độ tươi nóng, thời gian phục vụ và khả năng kiểm soát.")
    half = (W - 2 * M - 12) / 2
    image_placeholder(c, M, y - 150, half, 142, "BẾP TẠI CHỖ: ảnh khu bếp trong nhà máy")
    image_placeholder(c, M + half + 12, y - 150, half, 142, "BẾP TRUNG TÂM: ảnh chế biến và xe giao nhận")
    card(c, M, 63 * mm, half, 112, "Bếp tại chỗ", "• Phù hợp nhà máy có sản lượng ổn định<br/>• Món ăn được chế biến gần thời điểm phục vụ<br/>• Chủ động phối hợp theo ba ca<br/>• Quản lý và nhân sự trực tiếp tại dự án", WHITE, INK)
    card(c, M + half + 12, 63 * mm, half, 112, "Bếp trung tâm và vận chuyển", "• Chế biến tập trung theo kế hoạch<br/>• Kiểm soát thời gian giao nhận<br/>• Sử dụng thiết bị/thùng giữ nhiệt phù hợp<br/>• Phạm vi vận chuyển khai báo: tối đa khoảng 60 km", WHITE, ORANGE)
    note_band(c, "CẦN XÁC NHẬN: số lượng đặt tối thiểu và bán kính 60 km áp dụng cho bếp nào/khu vực nào.", 18 * mm)
    c.showPage()

    # 08 - Strengths
    y = page_base(c, 8, "ĐIỂM MẠNH", "Giữ niềm tin bằng sự lắng nghe và khả năng thích nghi", "QBA xây dựng quan hệ dài hạn bằng một cách rất thực tế: nghe phản hồi, điều chỉnh nhanh và duy trì chất lượng qua từng ca phục vụ.")
    strengths = [
        ("Lắng nghe", "Tiếp nhận ý kiến từ khách hàng và người lao động để điều chỉnh thực đơn, khẩu vị và cách phục vụ."),
        ("Đúng giờ", "Lập kế hoạch theo ca, kiểm soát tiến độ để bữa ăn nóng hổi trước thời điểm phục vụ."),
        ("Quy trình", "Tổ chức một chiều từ lựa chọn nguồn đến lưu mẫu, giảm rủi ro trong vận hành."),
        ("Con người", "Đội ngũ quản lý có kinh nghiệm, nhân viên được huấn luyện và kiểm tra đầu ca."),
        ("Thiết bị", "Liên tục cải tiến bếp, kho lạnh, tủ đông, tủ mát và thiết bị chế biến công nghiệp."),
        ("Phản hồi nhanh", "Đầu mối quản lý tiếp nhận phản ánh và phản hồi ban đầu trong khoảng 15-30 phút."),
    ]
    cw = (W - 2 * M - 12) / 2
    for i, (t, b) in enumerate(strengths):
        row, col = divmod(i, 2)
        card(c, M + col * (cw + 12), y - 88 - row * 98, cw, 86, t, b, WHITE, ORANGE if i in (1, 5) else INK, i + 1)
    round_rect(c, M, 34 * mm, W - 2 * M, 38 * mm, INK, 12)
    para(c, "Phục vụ hơn 15.000 người mỗi ngày là niềm vinh dự - và cũng là trách nhiệm để QBA không ngừng cải tiến.", M + 20, 64 * mm, W - 2 * M - 40, 12, 17, WHITE, True, TA_CENTER, 60)
    c.showPage()

    # 09 - Process map
    y = page_base(c, 9, "QUY TRÌNH MỘT CHIỀU", "Sáu bước kiểm soát từ nguồn đến bàn ăn", "Một quy trình dễ hiểu giúp khách hàng nhìn thấy trách nhiệm, điểm kiểm soát và bằng chứng vận hành ở từng công đoạn.")
    steps = [
        ("01", "Chọn nguồn", "Đánh giá nhà cung cấp và hồ sơ nguồn gốc."),
        ("02", "Kiểm nhận", "Cảm quan, chất lượng và điều kiện giao nhận."),
        ("03", "Sơ chế", "Phân khu sống - chín, dụng cụ và vệ sinh cá nhân."),
        ("04", "Chế biến", "Kiểm soát thời gian, nhiệt độ và định lượng."),
        ("05", "Chia suất", "Đúng cơ cấu món, đúng số lượng, đúng giờ."),
        ("06", "Lưu mẫu", "Lưu mẫu theo quy định và theo dõi sau phục vụ."),
    ]
    sx = M
    sw = (W - 2 * M - 10) / 2
    for i, (n, t, b) in enumerate(steps):
        row, col = divmod(i, 2)
        yy = y - 78 - row * 92
        round_rect(c, sx + col * (sw + 10), yy, sw, 76, WHITE, 10, LINE)
        round_rect(c, sx + col * (sw + 10) + 14, yy + 18, 42, 42, ORANGE if i in (1, 4) else INK, 21)
        para(c, n, sx + col * (sw + 10) + 14, yy + 46, 42, 12, 14, WHITE, True, TA_CENTER, 20)
        para(c, t, sx + col * (sw + 10) + 68, yy + 58, sw - 82, 11, 14, INK, True, max_h=20)
        para(c, b, sx + col * (sw + 10) + 68, yy + 37, sw - 82, 8.2, 11, TEXT, max_h=36)
    image_placeholder(c, M, 34 * mm, W - 2 * M, 51 * mm, "Ảnh tổng quan quy trình: từ nhận nguyên liệu đến chia suất")
    c.showPage()

    # 10 - Sourcing and receiving
    y = page_base(c, 10, "QUY TRÌNH 01-02", "Kiểm soát bắt đầu trước khi nguyên liệu vào bếp", "Nguyên liệu là nền tảng của chất lượng. QBA ưu tiên nguồn cung có hồ sơ rõ ràng và kiểm nhận tại thời điểm giao hàng.")
    image_placeholder(c, M, y - 185, 82 * mm, 178, "Ảnh nhà cung cấp giao hàng / kiểm nhận")
    x = M + 90 * mm
    checks = [
        ("Hồ sơ nguồn gốc", "Theo dõi chứng từ, kiểm dịch và thông tin lô hàng phù hợp."),
        ("Đánh giá cảm quan", "Quan sát màu sắc, trạng thái, độ tươi và dấu hiệu bất thường."),
        ("Mùi và chất lượng thịt", "Kiểm tra đặc điểm cảm quan trước khi tiếp nhận vào khu bếp."),
        ("Ghi nhận", "Lưu thông tin kiểm nhận theo tiêu chí nội bộ của Quốc Bình An."),
    ]
    for i, (t, b) in enumerate(checks):
        card(c, x, y - 74 - i * 78, W - M - x, 66, t, b, WHITE, INK, i + 1)
    image_placeholder(c, M, 37 * mm, W - 2 * M, 56 * mm, "Cận cảnh: tem lô hàng, nhiệt kế, phiếu kiểm nhận và nguyên liệu đạt chuẩn")
    c.showPage()

    # 11 - Storage and prep
    y = page_base(c, 11, "QUY TRÌNH 03", "Bảo quản và sơ chế theo phân khu", "Tổ chức không gian, dụng cụ và luồng di chuyển rõ ràng là điều kiện để hạn chế nhiễm chéo và duy trì vệ sinh.")
    image_placeholder(c, M, y - 158, 61 * mm, 150, "Kho lạnh / tủ đông / tủ mát")
    image_placeholder(c, M + 67 * mm, y - 158, 61 * mm, 150, "Khu sơ chế rau củ")
    image_placeholder(c, M + 134 * mm, y - 158, 61 * mm, 150, "Khu sơ chế thịt cá")
    principles = [
        ("Phân khu", "Khu sống và khu chín được tổ chức tách biệt."),
        ("Dụng cụ", "Dụng cụ sơ chế được quản lý theo mục đích sử dụng."),
        ("Bảo hộ", "Nhân viên mặc đồng phục, mũ trùm, khẩu trang và găng tay."),
        ("Kiểm tra đầu ca", "Giám sát vệ sinh cá nhân và điều kiện khu vực trước khi làm việc."),
    ]
    cw = (W - 2 * M - 12) / 2
    for i, (t, b) in enumerate(principles):
        row, col = divmod(i, 2)
        card(c, M + col * (cw + 12), 55 * mm + (1 - row) * 72, cw, 62, t, b, WHITE, ORANGE if i == 2 else INK)
    c.showPage()

    # 12 - Cooking
    y = page_base(c, 12, "QUY TRÌNH 04", "Chế biến đúng nhịp - giữ trọn độ nóng", "Với QBA, một bữa ăn đúng giờ là bữa ăn còn nóng hổi trước giờ phục vụ. Điều đó đòi hỏi kế hoạch theo ca và phối hợp chặt giữa bếp, chia suất và giao nhận.")
    image_placeholder(c, M, y - 206, 104 * mm, 198, "Ảnh bếp trưởng và dây chuyền chế biến")
    x = M + 112 * mm
    stat(c, x, y - 78, W - M - x, 70, "3 ca/ngày", "Tổ chức phục vụ theo nhịp sản xuất", INK)
    card(c, x, y - 158, W - M - x, 70, "Kế hoạch theo ca", "Chuẩn bị nguyên liệu, nhân sự và thời điểm hoàn thành theo giờ ăn thực tế.", WHITE, INK)
    card(c, x, y - 238, W - M - x, 70, "Kiểm soát nhiệt độ", "Ghi nhận nhiệt độ và điều kiện món ăn tại các điểm cần kiểm soát.", WHITE, ORANGE)
    card(c, x, y - 318, W - M - x, 70, "Định lượng", "Chia đúng cơ cấu suất ăn và tiêu chuẩn đã thống nhất với khách hàng.", WHITE, INK)
    image_placeholder(c, M, 35 * mm, W - 2 * M, 48 * mm, "Cận cảnh: đo nhiệt độ món ăn, ghi biểu mẫu và kiểm tra thành phẩm")
    c.showPage()

    # 13 - Portion and service
    y = page_base(c, 13, "QUY TRÌNH 05", "Từ bếp đến đúng ca phục vụ", "Mỗi suất ăn cần được chia đúng, giữ nhiệt phù hợp và có mặt trước thời điểm người lao động vào ca ăn.")
    image_placeholder(c, M, y - 178, 94 * mm, 170, "Dây chuyền chia suất và kiểm đếm")
    image_placeholder(c, M + 102 * mm, y - 178, W - 2 * M - 102 * mm, 170, "Xe giao nhận / thùng giữ nhiệt / căng tin")
    items = [
        ("Đúng cơ cấu", "Một món chính, món chính phụ, món xào, cơm, canh và tráng miệng."),
        ("Đúng số lượng", "Kiểm đếm theo kế hoạch sản lượng và từng ca."),
        ("Đúng thời điểm", "Phối hợp bếp - vận chuyển - phục vụ để giữ độ nóng."),
        ("Đúng trải nghiệm", "Thu nhận phản hồi về khẩu vị, định lượng và chất lượng phục vụ."),
    ]
    cw = (W - 2 * M - 12) / 2
    for i, (t, b) in enumerate(items):
        row, col = divmod(i, 2)
        card(c, M + col * (cw + 12), 52 * mm + (1 - row) * 72, cw, 62, t, b, WHITE, ORANGE if i == 2 else INK)
    c.showPage()

    # 14 - Sample and hygiene
    y = page_base(c, 14, "QUY TRÌNH 06", "Lưu mẫu, vệ sinh và khép kín hồ sơ", "Công việc chưa kết thúc khi suất ăn đã được phục vụ. QBA duy trì lưu mẫu, vệ sinh cuối ca và ghi nhận để phục vụ truy xuất khi cần.")
    image_placeholder(c, M, y - 170, 62 * mm, 162, "Ảnh lưu mẫu có nhãn và thời gian")
    image_placeholder(c, M + 68 * mm, y - 170, 62 * mm, 162, "Ảnh vệ sinh thiết bị cuối ca")
    image_placeholder(c, M + 136 * mm, y - 170, 59 * mm, 162, "Ảnh hồ sơ/biểu mẫu")
    card(c, M, 63 * mm, 58 * mm, 102, "Lưu mẫu", "Lưu mẫu theo yêu cầu y tế và duy trì mẫu tại nhà ăn sau 24 giờ.", WHITE, INK)
    card(c, M + 64 * mm, 63 * mm, 62 * mm, 102, "Vệ sinh", "Làm sạch khu bếp, dụng cụ và thiết bị theo phân công cuối ca.", WHITE, ORANGE)
    card(c, M + 132 * mm, 63 * mm, 63 * mm, 102, "Chất thải", "Phân tách chất thải và dầu thải; hồ sơ bàn giao cần được bổ sung để công khai.", WHITE, INK)
    note_band(c, "CẦN XÁC NHẬN: khối lượng mẫu, nhiệt độ bảo quản, thời hạn 24 giờ và đơn vị thu gom chất thải/dầu thải.", 18 * mm)
    c.showPage()

    # 15 - Incident response
    y = page_base(c, 15, "PHẢN HỒI KHÁCH HÀNG", "Tiếp nhận nhanh - xử lý có đầu mối", "Sự gắn bó lâu dài bắt đầu từ việc lắng nghe nghiêm túc và phản hồi minh bạch khi có ý kiến hoặc tình huống phát sinh.")
    stat(c, M, y - 92, 62 * mm, 84, "15-30 phút", "Thời gian phản hồi ban đầu khai báo", ORANGE)
    card(c, M + 69 * mm, y - 92, W - 2 * M - 69 * mm, 84, "Đầu mối tiếp nhận", "<b>Bà Trần Thị Thanh Thuỷ</b><br/>Phụ trách quản lý đầu vào và tiếp nhận phản ánh vận hành.", WHITE, INK)
    flow = [
        ("01", "Tiếp nhận", "Ghi nhận nội dung, thời điểm, ca và phạm vi ảnh hưởng."),
        ("02", "Xác minh", "Phối hợp quản lý bếp, hồ sơ lưu mẫu và dữ liệu liên quan."),
        ("03", "Khắc phục", "Thực hiện biện pháp tức thời phù hợp với tình huống."),
        ("04", "Phản hồi", "Thông tin kết quả và thống nhất hành động tiếp theo."),
        ("05", "Phòng ngừa", "Rút kinh nghiệm, điều chỉnh quy trình và đào tạo lại nếu cần."),
    ]
    for i, (n, t, b) in enumerate(flow):
        yy = y - 160 - i * 63
        round_rect(c, M, yy, 34, 34, INK if i != 2 else ORANGE, 17)
        para(c, n, M, yy + 24, 34, 9, 11, WHITE, True, TA_CENTER, 15)
        para(c, t, M + 48, yy + 31, 74, 9.5, 12, INK, True, max_h=20)
        para(c, b, M + 126, yy + 31, W - M - (M + 126), 8.2, 11, TEXT, max_h=30)
    note_band(c, "Quy trình xử lý chính thức, cấp phê duyệt và thời gian đóng sự cố cần được QBA xác nhận.", 18 * mm)
    c.showPage()

    # 16 - Compliance
    y = page_base(c, 16, "AN TOÀN & PHÁP LÝ", "Bằng chứng được chọn lọc và dễ kiểm tra", "Hồ sơ mới chỉ trình bày những chứng nhận còn hiệu lực và được phép công khai; dữ liệu cá nhân nhạy cảm sẽ được che hoặc loại bỏ.")
    image_placeholder(c, M, y - 150, 61 * mm, 142, "Giấy đủ điều kiện ATTP")
    image_placeholder(c, M + 67 * mm, y - 150, 61 * mm, 142, "ISO 22000:2018")
    image_placeholder(c, M + 134 * mm, y - 150, 61 * mm, 142, "Đăng ký doanh nghiệp")
    docs = [
        "Hồ sơ khám sức khỏe nhân viên",
        "Xác nhận tập huấn kiến thức an toàn thực phẩm",
        "Phiếu kiểm nghiệm nước",
        "Hồ sơ kiểm soát côn trùng",
        "Hồ sơ nguồn gốc và kiểm dịch nguyên liệu",
        "Hồ sơ PCCC/bảo hiểm nếu có",
    ]
    cw = (W - 2 * M - 12) / 2
    for i, d in enumerate(docs):
        row, col = divmod(i, 2)
        round_rect(c, M + col * (cw + 12), 52 * mm + (2 - row) * 44, cw, 36, WHITE, 8, LINE)
        c.setFillColor(MINT)
        c.circle(M + col * (cw + 12) + 17, 52 * mm + (2 - row) * 44 + 18, 6, fill=1, stroke=0)
        para(c, d, M + col * (cw + 12) + 30, 52 * mm + (2 - row) * 44 + 25, cw - 42, 8.2, 10.5, TEXT, True, max_h=24)
    note_band(c, "Không sử dụng hình CMND/CCCD trong bản phát hành. Ngày hiệu lực của tất cả chứng nhận phải được kiểm tra.", 18 * mm)
    c.showPage()

    # 17 - Workforce
    y = page_base(c, 17, "NHÂN SỰ", "Một đội ngũ được tổ chức để phục vụ liên tục", "Quy mô nhân sự được bố trí theo quản lý, bếp, sơ chế, chia suất và giao nhận để bảo đảm vận hành ba ca mỗi ngày.")
    image_placeholder(c, M, y - 185, 90 * mm, 177, "Ảnh tập thể nhân sự trong đồng phục QBA")
    x = M + 98 * mm
    stat(c, x, y - 72, W - M - x, 64, "100 nhân sự", "Tổng quy mô khai báo", INK)
    roles = [
        ("5", "Quản lý"),
        ("8", "Bếp trưởng"),
        ("10-12", "Phụ bếp"),
        ("5", "Giao nhận"),
        ("Còn lại", "Sơ chế, chia suất và phục vụ"),
    ]
    for i, (v, lab) in enumerate(roles):
        yy = y - 114 - i * 52
        round_rect(c, x, yy, W - M - x, 42, WHITE, 8, LINE)
        para(c, v, x + 12, yy + 31, 46, 12, 14, ORANGE if i == 4 else INK, True, max_h=20)
        para(c, lab, x + 66, yy + 29, W - M - x - 78, 8.5, 11, TEXT, max_h=24)
    round_rect(c, M, 33 * mm, W - 2 * M, 42 * mm, HexColor("#EAF2E7"), 10)
    para(c, "ĐỒNG PHỤC & BẢO HỘ", M + 16, 66 * mm, 50 * mm, 9, 12, INK, True)
    para(c, "Quần dài, áo đồng phục riêng, mũ trùm tóc, khẩu trang và găng tay; kiểm tra vệ sinh cá nhân trước ca.", M + 66 * mm, 66 * mm, W - 2 * M - 72 * mm, 9, 13, TEXT)
    c.showPage()

    # 18 - Leadership
    y = page_base(c, 18, "ĐỘI NGŨ CHỦ CHỐT", "Kinh nghiệm, trách nhiệm và sự hiện diện tại hiện trường", "Bốn đầu mối quản lý giúp QBA duy trì quyết định nhanh và trách nhiệm rõ trong vận hành ngày - đêm.")
    leaders = [
        ("Nguyễn Quốc Chinh", "Giám đốc", "20 năm kinh nghiệm; phụ trách định hướng, quản lý và cải tiến vận hành."),
        ("Trần Thị Thanh Thuỷ", "Đồng sáng lập - Quản lý đầu vào", "Phụ trách nguyên liệu, phối hợp vận hành và tiếp nhận phản hồi khách hàng."),
        ("Nguyễn Thị Quỳnh", "Quản lý nhà ăn ca ngày", "Tổ chức nhân sự, tiến độ và chất lượng phục vụ ban ngày."),
        ("Nguyễn Thị Hà", "Quản lý nhà ăn ca đêm", "Bảo đảm nhịp vận hành, vệ sinh và phục vụ ở ca đêm."),
    ]
    cw = (W - 2 * M - 12) / 2
    for i, (name, role, bio) in enumerate(leaders):
        row, col = divmod(i, 2)
        x = M + col * (cw + 12)
        yy = y - 184 - row * 202
        image_placeholder(c, x, yy + 78, cw, 104, f"Chân dung {name}", "Ảnh dọc, nền sạch, cùng phong cách")
        round_rect(c, x, yy, cw, 70, WHITE, 8, LINE)
        para(c, name, x + 12, yy + 58, cw - 24, 10.2, 13, INK, True, max_h=18)
        para(c, role, x + 12, yy + 41, cw - 24, 8.2, 10, ORANGE, True, max_h=14)
        para(c, bio, x + 12, yy + 26, cw - 24, 7.4, 9.4, TEXT, max_h=28)
    c.showPage()

    # 19 - Facilities
    y = page_base(c, 19, "CƠ SỞ VẬT CHẤT", "Thiết bị phục vụ cho quy mô và tính ổn định", "QBA khai báo hệ thống 10 bếp, diện tích phổ biến khoảng 400-500 m² và mô hình kết hợp bếp tại chỗ với bếp trung tâm.")
    image_placeholder(c, M, y - 165, 95 * mm, 157, "Toàn cảnh bếp hoặc dây chuyền nấu")
    image_placeholder(c, M + 102 * mm, y - 165, W - 2 * M - 102 * mm, 157, "Kho lạnh / kho khô")
    image_placeholder(c, M, y - 330, 61 * mm, 153, "Thiết bị chế biến")
    image_placeholder(c, M + 67 * mm, y - 330, 61 * mm, 153, "Tủ đông / tủ mát")
    image_placeholder(c, M + 134 * mm, y - 330, 61 * mm, 153, "Xe / thùng giữ nhiệt")
    round_rect(c, M, 24 * mm, W - 2 * M, 28 * mm, INK, 8)
    para(c, "Thiết bị dự kiến giới thiệu: kho lạnh, tủ đông, tủ mát, bếp công nghiệp, tủ hấp, lò nướng, máy trộn, dụng cụ đo nhiệt độ và thiết bị giữ nhiệt.", M + 14, 45 * mm, W - 2 * M - 28, 8.3, 11, WHITE, False, TA_CENTER, 28)
    c.showPage()

    # 20 - Menu
    y = page_base(c, 20, "THỰC ĐƠN", "Đủ vị, linh hoạt và phù hợp người lao động", "Thực đơn do Giám đốc Nguyễn Quốc Chinh và quản lý Trần Thị Thanh Thuỷ duyệt, điều chỉnh theo khẩu vị và phản hồi tại từng dự án.")
    image_placeholder(c, M, y - 160, 61 * mm, 152, "Khay suất ăn thực tế")
    image_placeholder(c, M + 67 * mm, y - 160, 61 * mm, 152, "Món ăn khẩu vị miền Nam")
    image_placeholder(c, M + 134 * mm, y - 160, 61 * mm, 152, "Món Hoa / Đài Loan")
    meal = [
        ("01", "Món chính"),
        ("02", "Món chính phụ"),
        ("03", "Món xào"),
        ("04", "Cơm"),
        ("05", "Canh"),
        ("06", "Tráng miệng theo mùa / sữa chua / sữa đậu nành"),
    ]
    cw = (W - 2 * M - 12) / 2
    for i, (n, lab) in enumerate(meal):
        row, col = divmod(i, 2)
        yy = 51 * mm + (2 - row) * 43
        round_rect(c, M + col * (cw + 12), yy, cw, 35, WHITE, 8, LINE)
        round_rect(c, M + col * (cw + 12) + 9, yy + 7, 22, 22, MINT, 11)
        para(c, n, M + col * (cw + 12) + 9, yy + 23, 22, 7.5, 9, INK, True, TA_CENTER, 10)
        para(c, lab, M + col * (cw + 12) + 39, yy + 25, cw - 49, 8.2, 10.5, TEXT, True, max_h=24)
    note_band(c, "CẦN BỔ SUNG: chu kỳ luân phiên, định lượng/năng lượng mục tiêu, thực đơn dị ứng và mức giá có được công khai hay không.", 18 * mm)
    c.showPage()

    # 21 - Case Etop
    y = page_base(c, 21, "DỰ ÁN TIÊU BIỂU 01", "E-top - niềm tin được duy trì qua nhiều năm", "Một dự án quy mô lớn, vận hành theo mô hình bếp tại chỗ và gắn bó dài hạn cùng Quốc Bình An.")
    image_placeholder(c, M, y - 215, 108 * mm, 207, "Ảnh bếp/căng tin tại dự án E-top")
    x = M + 116 * mm
    image_placeholder(c, x, y - 58, W - M - x, 50, "LOGO E-TOP", "Cần xác nhận quyền sử dụng")
    stat(c, x, y - 132, W - M - x, 64, "5.500", "Suất/ngày khai báo", INK)
    stat(c, x, y - 206, W - M - x, 64, "16 năm", "Thời gian hợp tác khai báo", ORANGE)
    card(c, x, y - 302, W - M - x, 86, "Mô hình", "Bếp tại chỗ, phục vụ suất ăn công nghiệp theo nhiều ca. Địa điểm và số ca cần được xác nhận trước khi phát hành.", WHITE, INK)
    round_rect(c, M, 34 * mm, W - 2 * M, 48 * mm, HexColor("#EAF2E7"), 10)
    para(c, "NỘI DUNG CẦN BỔ SUNG", M + 14, 71 * mm, 54 * mm, 8, 10, ORANGE, True)
    para(c, "Thách thức ban đầu • giải pháp QBA • kết quả đo lường • phản hồi hoặc thư xác nhận từ khách hàng", M + 68 * mm, 71 * mm, W - 2 * M - 82 * mm, 8.5, 12, TEXT)
    c.showPage()

    # 22 - Cases 2 and 3
    y = page_base(c, 22, "DỰ ÁN TIÊU BIỂU 02-03", "Hai mô hình quy mô tại khu công nghiệp", "Các hồ sơ dự án sẽ được hoàn thiện bằng ảnh thực tế, địa điểm chính xác và câu chuyện giải pháp sau khi khách hàng cho phép công khai.")
    half = (W - 2 * M - 12) / 2
    for col, (client, meals, years) in enumerate([
        ("Twin Kie Việt Nam", "1.900 suất/ngày", "12 năm hợp tác"),
        ("Bellinturf Việt Nam", "5.000 suất/ngày", "Thời gian cần xác nhận"),
    ]):
        x = M + col * (half + 12)
        image_placeholder(c, x, y - 56, half, 48, f"LOGO {client}", "Cần xác nhận quyền sử dụng")
        image_placeholder(c, x, y - 202, half, 136, f"Ảnh dự án {client}")
        round_rect(c, x, y - 292, half, 80, WHITE, 10, LINE)
        para(c, client, x + 13, y - 226, half - 26, 11, 14, INK, True, TA_CENTER, 20)
        para(c, meals, x + 13, y - 251, half - 26, 10, 13, ORANGE, True, TA_CENTER, 18)
        para(c, years, x + 13, y - 274, half - 26, 8.2, 11, TEXT, False, TA_CENTER, 18)
        card(c, x, 37 * mm, half, 80, "Cần bổ sung", "Địa điểm chính xác • số ca • thách thức • giải pháp • kết quả • phản hồi khách hàng.", HexColor("#EAF2E7"), INK)
    c.showPage()

    # 23 - Trust and partners
    y = page_base(c, 23, "SỰ TIN CẬY", "Giá trị của một mối quan hệ dài hạn", "QBA trân trọng những khách hàng đã đồng hành qua nhiều chu kỳ phát triển và xem mỗi lần gia hạn là một sự xác nhận cho chất lượng phục vụ.")
    stat(c, M, y - 90, 84 * mm, 82, "20 năm", "Thời gian gắn bó khai báo với Royal Hoàng Gia", INK)
    stat(c, M + 91 * mm, y - 90, W - 2 * M - 91 * mm, 82, "16 năm", "Thời gian gắn bó khai báo với E-top", ORANGE)
    clients = ["Royal Hoàng Gia", "E-top Việt Nam", "Twin Kie Việt Nam", "Bellinturf Việt Nam", "JYS Việt Nam", "Đông Jintian Việt Nam", "Dệt Tah Tong Việt Nam", "Thép Minh Trí"]
    cw = (W - 2 * M - 18) / 4
    for i, client in enumerate(clients):
        row, col = divmod(i, 4)
        image_placeholder(c, M + col * (cw + 6), y - 186 - row * 94, cw, 84, client, "Khung logo")
    round_rect(c, M, 34 * mm, W - 2 * M, 38 * mm, INK, 10)
    para(c, "Mỗi tên và logo khách hàng chỉ được công khai sau khi QBA xác nhận tên pháp lý và quyền sử dụng.", M + 16, 62 * mm, W - 2 * M - 32, 9, 13, WHITE, True, TA_CENTER, 44)
    c.showPage()

    # 24 - CTA
    c.setFillColor(DARK)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(MINT)
    c.circle(W - 12 * mm, H - 20 * mm, 52 * mm, fill=1, stroke=0)
    image_placeholder(c, M, H - 40 * mm, 48 * mm, 20 * mm, "LOGO QBA", "Logo nền trong")
    tag(c, "KẾT NỐI CÙNG QBA", M, H - 70 * mm, YELLOW, DARK, 102)
    y = para(c, "Một bữa ăn tốt<br/>bắt đầu từ một cuộc trao đổi rõ ràng.", M, H - 84 * mm, W - 2 * M, 27, 32, WHITE, True)
    para(c, "Hãy liên hệ để nhận tư vấn mô hình bếp, thực đơn và báo giá phù hợp với quy mô vận hành của doanh nghiệp.", M, y - 16, 104 * mm, 11, 17, HexColor("#DCEAE5"))
    image_placeholder(c, W - M - 70 * mm, 87 * mm, 70 * mm, 104 * mm, "Ảnh kết: đội ngũ QBA / bữa ăn hoàn chỉnh")
    round_rect(c, M, 81 * mm, 96 * mm, 80 * mm, HexColor("#214A42"), 12)
    para(c, "NGUYỄN QUỐC CHINH", M + 16, 147 * mm, 82 * mm, 10, 13, YELLOW, True)
    para(c, "Giám đốc<br/><b>0907 090 572</b>", M + 16, 130 * mm, 82 * mm, 10, 15, WHITE)
    para(c, "TRẦN THỊ THANH THUỶ", M + 16, 111 * mm, 82 * mm, 10, 13, YELLOW, True)
    para(c, "<b>0909 843 604</b>", M + 16, 95 * mm, 82 * mm, 10, 15, WHITE)
    para(c, "quocbinhan975@gmail.com", M, 62 * mm, W - 2 * M, 11, 14, MINT, True)
    para(c, "Số 35 đường Huỳnh Văn Nghệ, KP Phước Kiểng, phường Nhơn Trạch, tỉnh Đồng Nai", M, 48 * mm, W - 2 * M, 8.5, 12, HexColor("#DCEAE5"))
    c.setStrokeColor(HexColor("#41675F"))
    c.line(M, 31 * mm, W - M, 31 * mm)
    para(c, "BẢN NHÁP 01  •  NỘI DUNG VÀ HÌNH ẢNH CHỜ DUYỆT", M, 24 * mm, W - 2 * M, 7.5, 10, HexColor("#9EB7AF"), True, TA_CENTER)
    c.showPage()

    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
