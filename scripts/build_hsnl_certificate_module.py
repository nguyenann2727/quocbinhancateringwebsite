from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
from reportlab.lib.colors import Color, HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "references/hsnl-goc/chung-nhan-bo-sung/original"
LEGACY = ROOT / "references/hsnl-goc/may-moc-va-bep"
ASSETS = ROOT / "assets/hsnl/chung-nhan"
OUTPUT = ROOT / "output/pdf/HSNL-QBA-cum-trang-chung-nhan.pdf"

INK = HexColor("#173B35")
INK_2 = HexColor("#214B42")
PAPER = HexColor("#F8F6EF")
WHITE = HexColor("#FFFEFB")
MUTED = HexColor("#68736C")
LINE = HexColor("#D7DDD7")
LIME = HexColor("#B8E59F")
YELLOW = HexColor("#FFD569")
ORANGE = HexColor("#F0835F")

FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("QBA", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("QBA-Bold", FONT_BOLD))


def save_jpeg(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, quality=94, subsampling=0, optimize=True)


def clean_photo(
    path: Path,
    crop: tuple[int, int, int, int] | None = None,
    rotate_cw: bool = False,
    rotate_ccw: bool = False,
) -> Image.Image:
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    if rotate_cw:
        image = image.rotate(-90, expand=True, resample=Image.Resampling.BICUBIC)
    if rotate_ccw:
        image = image.rotate(90, expand=True, resample=Image.Resampling.BICUBIC)
    if crop:
        image = image.crop(crop)
    image = ImageEnhance.Contrast(image).enhance(1.025)
    image = image.filter(ImageFilter.UnsharpMask(radius=0.8, percent=85, threshold=3))
    return image


def redact(image: Image.Image, boxes: list[tuple[int, int, int, int]]) -> Image.Image:
    public = image.copy()
    draw = ImageDraw.Draw(public)
    for box in boxes:
        draw.rounded_rectangle(box, radius=7, fill=(232, 235, 231), outline=(215, 221, 215), width=2)
    return public


def prepare_assets() -> dict[str, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    training_1 = clean_photo(ORIGINAL / "01-tap-huan-attp-danh-sach-01.jpg", (25, 40, 880, 1120))
    training_2 = clean_photo(ORIGINAL / "02-tap-huan-attp-danh-sach-02.jpg", (25, 70, 890, 970))
    cards = clean_photo(ORIGINAL / "03-the-an-toan-lao-dong.jpg", rotate_cw=True)
    attp = clean_photo(ORIGINAL / "04-chung-nhan-attp-2024.jpg", (0, 0, 900, 1245))
    water = clean_photo(ORIGINAL / "05-kiem-nghiem-nuoc-ro-2026.jpg")

    paths["training_1"] = ASSETS / "tap-huan-attp-01-public.jpg"
    paths["training_2"] = ASSETS / "tap-huan-attp-02-public.jpg"
    paths["cards"] = ASSETS / "the-an-toan-lao-dong-public.jpg"
    paths["attp"] = ASSETS / "chung-nhan-attp-2024.jpg"
    paths["water"] = ASSETS / "kiem-nghiem-nuoc-ro-2026.jpg"

    # Danh sách 23 nhân sự tập huấn ATTP dùng bản gốc theo yêu cầu.
    cards_public = redact(cards, [(8, 112, 867, 402), (8, 528, 867, 820), (8, 950, 867, 1240)])

    save_jpeg(training_1, paths["training_1"])
    save_jpeg(training_2, paths["training_2"])
    save_jpeg(cards_public, paths["cards"])
    save_jpeg(attp, paths["attp"])
    save_jpeg(water, paths["water"])

    for key, filename in {
        "legacy_kitchen": "trang-39-khu-bep-tu-quay-thit.jpg",
        "legacy_equipment_1": "trang-40-thiet-bi-phuc-vu-va-bep.jpg",
        "legacy_equipment_2": "trang-41-thiet-bi-che-bien-bao-quan.jpg",
    }.items():
        image = clean_photo(LEGACY / filename, rotate_ccw=True)
        path = ASSETS / f"{key}.jpg"
        save_jpeg(image, path)
        paths[key] = path

    return paths


def paragraph(c: canvas.Canvas, text: str, x: float, y_top: float, width: float, style: ParagraphStyle) -> float:
    item = Paragraph(text, style)
    _, height = item.wrap(width, 1000)
    item.drawOn(c, x, y_top - height)
    return height


def draw_contain(c: canvas.Canvas, path: Path, x: float, y: float, width: float, height: float, pad: float = 0) -> None:
    with Image.open(path) as image:
        iw, ih = image.size
    scale = min((width - pad * 2) / iw, (height - pad * 2) / ih)
    dw, dh = iw * scale, ih * scale
    c.drawImage(ImageReader(str(path)), x + (width - dw) / 2, y + (height - dh) / 2, dw, dh, preserveAspectRatio=True, mask="auto")


def draw_cover(c: canvas.Canvas, path: Path, x: float, y: float, width: float, height: float) -> None:
    with Image.open(path) as image:
        iw, ih = image.size
        scale = max(width / iw, height / ih)
        crop_w, crop_h = width / scale, height / scale
        left = (iw - crop_w) / 2
        top = (ih - crop_h) / 2
        cropped = image.crop((int(left), int(top), int(left + crop_w), int(top + crop_h))).resize(
            (max(1, int(width * 2)), max(1, int(height * 2))), Image.Resampling.LANCZOS
        )
    c.drawImage(ImageReader(cropped), x, y, width, height, mask="auto")


def rounded_frame(c: canvas.Canvas, x: float, y: float, width: float, height: float, fill=WHITE, stroke=LINE, radius: float = 14) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(0.8)
    c.roundRect(x, y, width, height, radius, stroke=1, fill=1)


def page_chrome(c: canvas.Canvas, page_no: int, section: str) -> None:
    width, height = A4
    c.setFillColor(INK)
    c.roundRect(34, height - 62, 34, 34, 10, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 8.5)
    c.drawCentredString(51, height - 49, "QBA")
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 9)
    c.drawString(78, height - 42, "QUỐC BÌNH AN CATERING")
    c.setFillColor(MUTED)
    c.setFont("QBA", 7.8)
    c.drawString(78, height - 55, section.upper())
    c.setStrokeColor(LINE)
    c.line(34, 44, width - 34, 44)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7.5)
    c.drawString(34, 28, "HỒ SƠ NĂNG LỰC 2026 • BẢN TỐI ƯU CHO WEBSITE")
    c.drawRightString(width - 34, 28, f"{page_no:02d}")


def page_base(c: canvas.Canvas, page_no: int, section: str) -> None:
    width, height = A4
    c.setFillColor(PAPER)
    c.rect(0, 0, width, height, stroke=0, fill=1)
    page_chrome(c, page_no, section)


def fact_card(c: canvas.Canvas, x: float, y: float, width: float, label: str, value: str, accent) -> None:
    rounded_frame(c, x, y, width, 74, fill=WHITE)
    c.setFillColor(accent)
    c.roundRect(x + 12, y + 45, 30, 16, 8, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 17)
    c.drawString(x + 12, y + 20, value)
    c.setFillColor(MUTED)
    c.setFont("QBA-Bold", 6.8)
    c.drawString(x + 49, y + 50, label.upper())


def build_pdf(paths: dict[str, Path]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    width, height = A4

    title_style = ParagraphStyle(
        "title", fontName="QBA-Bold", fontSize=27, leading=30, textColor=INK, alignment=TA_LEFT, spaceAfter=0
    )
    body_style = ParagraphStyle(
        "body", fontName="QBA", fontSize=9, leading=13, textColor=MUTED, alignment=TA_LEFT
    )
    small_style = ParagraphStyle(
        "small", fontName="QBA", fontSize=7.4, leading=10, textColor=MUTED, alignment=TA_LEFT
    )

    # Trang 1 - Giấy chứng nhận ATTP và kết nối với tư liệu thiết bị cũ.
    page_base(c, 1, "Năng lực tuân thủ")
    paragraph(c, "An toàn thực phẩm.<br/><font color='#F0835F'>Hồ sơ còn hiệu lực.</font>", 34, 735, 350, title_style)
    paragraph(c, "Giấy chứng nhận cho bếp ăn tập thể tại KCN Mỹ Xuân B1 - Tiến Hùng, cấp ngày 08/04/2024 và có giá trị 03 năm kể từ ngày ký.", 382, 724, 175, body_style)

    rounded_frame(c, 34, 86, 330, 554, fill=WHITE)
    draw_contain(c, paths["attp"], 43, 95, 312, 536, pad=2)

    fact_card(c, 382, 564, 175, "Số chứng nhận", "0298/2024", LIME)
    fact_card(c, 382, 476, 175, "Hiệu lực", "Đến 04/2027", YELLOW)
    fact_card(c, 382, 388, 175, "Loại hình", "Bếp ăn tập thể", ORANGE)

    c.setFillColor(INK)
    c.setFont("QBA-Bold", 10)
    c.drawString(382, 357, "TƯ LIỆU VẬN HÀNH")
    paragraph(c, "Ảnh bếp và thiết bị từ hồ sơ gốc được giữ lại như lớp bằng chứng lịch sử; các ảnh mới sẽ thay thế khi có bộ chụp hiện trường chất lượng cao.", 382, 343, 175, small_style)
    for idx, key in enumerate(["legacy_kitchen", "legacy_equipment_1", "legacy_equipment_2"]):
        y = 263 - idx * 62
        rounded_frame(c, 382, y, 175, 52, fill=WHITE, radius=9)
        draw_cover(c, paths[key], 387, y + 5, 165, 42)
    page_chrome(c, 1, "Năng lực tuân thủ")
    c.showPage()

    # Trang 2 - Đào tạo ATTP.
    page_base(c, 2, "Đào tạo an toàn thực phẩm")
    paragraph(c, "Đào tạo định kỳ.<br/><font color='#317A58'>Kỷ luật từ con người.</font>", 34, 735, 360, title_style)
    paragraph(c, "23 nhân sự được tập huấn kiến thức an toàn vệ sinh thực phẩm ngày 01/11/2025.", 382, 724, 175, body_style)
    fact_card(c, 382, 621, 82, "Nhân sự", "23", LIME)
    fact_card(c, 475, 621, 82, "Ngày tập huấn", "11/2025", YELLOW)

    rounded_frame(c, 34, 88, 253, 565, fill=WHITE)
    rounded_frame(c, 308, 88, 249, 510, fill=WHITE)
    draw_contain(c, paths["training_1"], 41, 96, 239, 549, pad=2)
    draw_contain(c, paths["training_2"], 315, 96, 235, 494, pad=2)
    c.setFillColor(INK_2)
    c.setFont("QBA-Bold", 8)
    c.drawString(308, 608, "HỒ SƠ TẬP HUẤN • TRANG 2/2")
    paragraph(c, "Danh sách 23 nhân sự tập huấn ATTP đang dùng ảnh gốc không che mờ; thẻ an toàn lao động vẫn được xử lý riêng để minh họa hồ sơ.", 308, 82, 249, small_style)
    page_chrome(c, 2, "Đào tạo an toàn thực phẩm")
    c.showPage()

    # Trang 3 - An toàn lao động và kiểm nghiệm nước.
    page_base(c, 3, "Kiểm soát điều kiện vận hành")
    paragraph(c, "An toàn lao động.<br/><font color='#F0835F'>Kiểm soát nguồn nước.</font>", 34, 735, 350, title_style)
    paragraph(c, "Huấn luyện an toàn nghề nghiệp và kiểm nghiệm nước RO trung tâm.", 382, 724, 175, body_style)

    fact_card(c, 34, 575, 150, "Thẻ an toàn lao động", "09 thẻ", LIME)
    fact_card(c, 194, 575, 170, "Hiệu lực thẻ", "Đến 02/04/2027", YELLOW)
    fact_card(c, 382, 575, 175, "Chỉ tiêu trên phiếu", "18 chỉ tiêu", ORANGE)

    rounded_frame(c, 34, 120, 265, 430, fill=WHITE)
    rounded_frame(c, 317, 120, 240, 430, fill=WHITE)
    draw_contain(c, paths["cards"], 42, 128, 249, 414, pad=2)
    draw_contain(c, paths["water"], 325, 128, 224, 414, pad=2)

    c.setFillColor(INK)
    c.setFont("QBA-Bold", 8)
    c.drawString(34, 105, "THẺ AN TOÀN LAO ĐỘNG")
    c.drawString(317, 105, "KIỂM NGHIỆM NƯỚC RO • MÃ 080626-3425")
    paragraph(c, "Bản công khai đã ẩn thông tin định danh cá nhân.", 34, 93, 265, small_style)
    paragraph(c, "Các kết quả trên trang phiếu được đối chiếu với giới hạn tối đa cho phép; không diễn giải thay cho kết luận tổng thể của đơn vị kiểm nghiệm.", 317, 93, 240, small_style)
    page_chrome(c, 3, "Kiểm soát điều kiện vận hành")
    c.showPage()

    c.save()


def main() -> None:
    register_fonts()
    paths = prepare_assets()
    build_pdf(paths)
    print(OUTPUT)


if __name__ == "__main__":
    main()
