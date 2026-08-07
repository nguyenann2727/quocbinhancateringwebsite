from __future__ import annotations

import base64
import re
from collections import defaultdict
from io import BytesIO
import json
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps, ImageStat
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
CERT = ASSETS / "hsnl/chung-nhan"
CERT_EXTRA = ROOT / "references/hsnl-goc/chung-nhan-iso-va-ncc/original"
EQUIP_ORIGINAL = ROOT / "references/hsnl-goc/thiet-bi-bo-sung/original"
EQUIP_OUT = ASSETS / "hsnl/thiet-bi"
BANQUET = ROOT / "references/hsnl-goc/ban-tiec-va-mon-an"
PROCESS_PHOTOS = ROOT / "references/hsnl-goc/anh-bo-sung-20260707/quy-trinh"
BRAND = ROOT / "references/hsnl-goc/nhan-dien-bo-sung-20260707"
MEAL_ORIGINAL = ROOT / "references/hsnl-goc/khau-phan-bo-sung-20260707/original"
MEAL_OUT = ASSETS / "hsnl/khau-phan-20260707"
HERO_BG_OUT = ASSETS / "hsnl/hero-bg"
QUALITY_OUT = ASSETS / "hsnl/quality"
LEGAL_OUT = ASSETS / "hsnl/legal"
HERO_LOGO = ASSETS / "qba-hero-frame-signature-20260729.jpg"
EDITABLE = ROOT / "editable"
IMAGE_OVERRIDES_FILE = EDITABLE / "hsnl-image-overrides.json"
TEXT_OVERRIDES_FILE = EDITABLE / "hsnl-text-overrides.json"
PDF_EDITOR_STATE_FILE = EDITABLE / "hsnl-pdf-editor-state.json"
PDF_EDITOR_MANIFEST_FILE = EDITABLE / "hsnl-pdf-editor-manifest.json"
PDF_EDITOR_UPLOADS = EDITABLE / "hsnl-pdf-editor-uploads"
PDF_EDIT_BUTTON_FILE = EDITABLE / "hsnl-pdf-edit-button.json"
OUTPUT = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01.pdf"
LEGAL_SOURCE_PAGE_1 = Path("/Users/quoc/Downloads/IMG_8627.PNG")
LEGAL_SOURCE_PAGE_2 = Path("/Users/quoc/Downloads/IMG_8628.PNG")
LEGAL_STRENGTH_SOURCE = Path("/Users/quoc/Desktop/Screenshot 2026-07-24 at 1.39.47\u202fam.png")

INK = HexColor("#173B35")
INK_2 = HexColor("#214B42")
INK_3 = HexColor("#2C5A4E")
PAPER = HexColor("#F8F6EF")
WHITE = HexColor("#FFFEFB")
MUTED = HexColor("#4D5F56")
LINE = HexColor("#D6DDD7")
LIME = HexColor("#B8E59F")
GREEN = HexColor("#317A58")
YELLOW = HexColor("#FFD569")
ORANGE = HexColor("#F0835F")
RED = HexColor("#B84B38")
FLOW_AMBER = HexColor("#BC7B28")
FLOW_GOLD = HexColor("#F1C83F")
FLOW_LINE = HexColor("#94601D")
LOGO_ICON_CROP = (390, 40, 890, 540)

FONT_REGULAR = "/System/Library/Fonts/Supplemental/Arial.ttf"
FONT_BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
INTER_REGULAR_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Inter.ttf",
    "/Library/Fonts/Inter.ttf",
    "/Library/Fonts/Inter-Regular.ttf",
    str(Path.home() / "Library/Fonts/Inter.ttf"),
    str(Path.home() / "Library/Fonts/Inter-Regular.ttf"),
]
INTER_BOLD_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Inter Bold.ttf",
    "/Library/Fonts/Inter-Bold.ttf",
    "/Library/Fonts/Inter Bold.ttf",
    str(Path.home() / "Library/Fonts/Inter-Bold.ttf"),
    str(Path.home() / "Library/Fonts/Inter Bold.ttf"),
]
W, H = A4


def load_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"File chỉnh sửa không đúng JSON: {path}") from exc


def load_editable_overrides(path: Path, key: str) -> dict[str, str]:
    data = load_json_file(path)
    values = data.get(key, data)
    return {str(k): str(v) for k, v in values.items() if str(v).strip()}


def normalize_editor_text(value: str) -> str:
    value = str(value).strip()
    value = re.sub(r"&(?:nbsp|#160|#xA0);", " ", value, flags=re.IGNORECASE)
    value = value.replace("\u00a0", " ")
    # contenteditable can emit a closing BR tag; normalize it before ReportLab parses the text.
    value = re.sub(r"</br\s*>", "<br/>", value, flags=re.IGNORECASE)
    value = re.sub(r"<div>\s*<br\s*/?>\s*</div>", "<br/>", value, flags=re.IGNORECASE)
    value = re.sub(r"</div>\s*<div>", "<br/>", value, flags=re.IGNORECASE)
    value = re.sub(r"^\s*<div>", "", value, flags=re.IGNORECASE)
    value = re.sub(r"</div>\s*$", "", value, flags=re.IGNORECASE)
    value = re.sub(r"<br\s*/?>", "<br/>", value, flags=re.IGNORECASE)
    return value


IMAGE_OVERRIDES = load_editable_overrides(IMAGE_OVERRIDES_FILE, "images")
TEXT_OVERRIDES = load_editable_overrides(TEXT_OVERRIDES_FILE, "texts")
PDF_EDIT_BUTTON_CONFIG = {
    "enabled": True,
    "url": f"http://127.0.0.1:{os.environ.get('HSNL_EDITOR_PORT', '8791')}/editable/hsnl-pdf-editor.html?mode=all",
    **load_json_file(PDF_EDIT_BUTTON_FILE),
}
PDF_EDITOR_STATE = load_json_file(PDF_EDITOR_STATE_FILE)
PDF_EDITOR_IMAGES = PDF_EDITOR_STATE.get("images", {}) if isinstance(PDF_EDITOR_STATE.get("images", {}), dict) else {}
PDF_EDITOR_TEXTS = PDF_EDITOR_STATE.get("texts", {}) if isinstance(PDF_EDITOR_STATE.get("texts", {}), dict) else {}
for _text_record in PDF_EDITOR_TEXTS.values():
    if not isinstance(_text_record, dict):
        continue
    original = str(_text_record.get("original", "")).strip()
    value = normalize_editor_text(str(_text_record.get("value", "")).strip())
    if original and value:
        TEXT_OVERRIDES[original] = value

IMAGE_SLOT_COUNTER: defaultdict[tuple[int, str, str], int] = defaultdict(int)
TEXT_SLOT_COUNTER: defaultdict[int, int] = defaultdict(int)
PDF_EDITOR_MANIFEST: dict = {
    "version": 1,
    "page": {"width": W, "height": H},
    "images": [],
    "texts": [],
}
DATA_URL_IMAGE_CACHE: dict[str, Path] = {}


def project_key(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return value[:54] or "slot"


def as_project_path(value: str | Path) -> Path:
    path = Path(str(value))
    if not path.is_absolute():
        path = ROOT / path
    return path


def data_url_to_path(slot_id: str, data_url: str) -> Path:
    if slot_id in DATA_URL_IMAGE_CACHE:
        return DATA_URL_IMAGE_CACHE[slot_id]
    if "," not in data_url:
        raise RuntimeError(f"Ảnh base64 không hợp lệ cho khung: {slot_id}")
    header, payload = data_url.split(",", 1)
    ext = "png"
    if "jpeg" in header or "jpg" in header:
        ext = "jpg"
    elif "webp" in header:
        ext = "webp"
    PDF_EDITOR_UPLOADS.mkdir(parents=True, exist_ok=True)
    out_path = PDF_EDITOR_UPLOADS / f"{slot_id}.{ext}"
    out_path.write_bytes(base64.b64decode(payload))
    DATA_URL_IMAGE_CACHE[slot_id] = out_path
    return out_path


def set_slot_page_alias(c: canvas.Canvas, page: int) -> None:
    c._qba_slot_page_alias = int(page)


def slot_page_number(c: canvas.Canvas) -> int:
    try:
        return int(getattr(c, "_qba_slot_page_alias"))
    except (TypeError, ValueError, AttributeError):
        return int(c.getPageNumber())


def image_slot_id(c: canvas.Canvas, path: Path, mode: str) -> str:
    page = slot_page_number(c)
    key = project_key(path)
    counter_key = (page, key, mode)
    IMAGE_SLOT_COUNTER[counter_key] += 1
    return f"p{page:02d}-{slugify(Path(key).stem)}-{IMAGE_SLOT_COUNTER[counter_key]:02d}"


def image_editor_record(slot_id: str) -> dict:
    record = PDF_EDITOR_IMAGES.get(slot_id, {})
    return record if isinstance(record, dict) else {}


def resolve_image_for_slot(path: Path, slot_id: str) -> Path:
    record = image_editor_record(slot_id)
    if str(record.get("dataUrl", "")).startswith("data:image/"):
        return data_url_to_path(slot_id, str(record["dataUrl"]))
    replacement = str(record.get("replacement") or record.get("path") or "").strip()
    if replacement:
        replacement_path = as_project_path(replacement)
        if not replacement_path.exists():
            raise FileNotFoundError(f"Ảnh thay thế không tồn tại: {replacement_path}")
        return replacement_path
    return resolve_image(path)


def image_layout_for_slot(
    c: canvas.Canvas,
    path: Path,
    mode: str,
    x: float,
    y: float,
    w: float,
    h: float,
    align=(0.5, 0.5),
    *,
    fit: str = "cover",
) -> tuple[str, Path, float, float, float, float, tuple[float, float], float, float]:
    slot_id = image_slot_id(c, path, mode)
    record = image_editor_record(slot_id)
    x = float(record.get("x", x))
    y = float(record.get("y", y))
    w = max(8.0, float(record.get("w", w)))
    h = max(8.0, float(record.get("h", h)))
    align = (
        max(0.0, min(1.0, float(record.get("alignX", align[0])))),
        max(0.0, min(1.0, float(record.get("alignY", align[1])))),
    )
    zoom = max(20.0, min(600.0, float(record.get("zoom", 100))))
    rotate = max(-45.0, min(45.0, float(record.get("rotate", 0))))
    resolved = resolve_image_for_slot(path, slot_id)
    PDF_EDITOR_MANIFEST["images"].append(
        {
            "id": slot_id,
            "page": c.getPageNumber(),
            "source": project_key(path),
            "effectiveSource": project_key(resolved),
            "mode": mode,
            "fit": fit,
            "x": x,
            "y": y,
            "w": w,
            "h": h,
            "alignX": align[0],
            "alignY": align[1],
            "zoom": zoom,
            "rotate": rotate,
            "label": Path(project_key(path)).stem.replace("-", " ").replace("_", " "),
        }
    )
    return slot_id, resolved, x, y, w, h, align, zoom, rotate


def center_crop(im: Image.Image, width: int, height: int) -> Image.Image:
    if im.width < width or im.height < height:
        canvas_im = Image.new(im.mode, (max(width, im.width), max(height, im.height)), im.getpixel((im.width // 2, im.height // 2)))
        canvas_im.paste(im, ((canvas_im.width - im.width) // 2, (canvas_im.height - im.height) // 2))
        im = canvas_im
    left = max(0, (im.width - width) // 2)
    top = max(0, (im.height - height) // 2)
    return im.crop((left, top, left + width, top + height))


def rotate_keep_frame(im: Image.Image, angle: float) -> Image.Image:
    if abs(angle) < 0.01:
        return im
    fill = im.getpixel((im.width // 2, im.height // 2))
    rotated = im.rotate(-angle, resample=Image.Resampling.BICUBIC, expand=True, fillcolor=fill)
    return center_crop(rotated, im.width, im.height)


def next_text_slot_id(c: canvas.Canvas) -> tuple[int, str]:
    page = slot_page_number(c)
    TEXT_SLOT_COUNTER[page] += 1
    return page, f"p{page:02d}-text-{TEXT_SLOT_COUNTER[page]:03d}"


def text_editor_record(slot_id: str, original: str | None = None) -> dict:
    record = PDF_EDITOR_TEXTS.get(slot_id, {})
    if not isinstance(record, dict):
        return {}
    if original is not None:
        saved_original = normalize_editor_text(str(record.get("original", "")).strip())
        current_original = normalize_editor_text(str(original).strip())
        if saved_original and saved_original != current_original:
            return {}
    return record


def resolve_text_for_slot(slot_id: str, text: str) -> str:
    record = text_editor_record(slot_id, text)
    value = normalize_editor_text(str(record.get("value", "")).strip())
    if value:
        return value
    return resolve_text(text)


def text_font_size_for_slot(slot_id: str, base_size: float, original: str | None = None) -> float:
    record = text_editor_record(slot_id, original)
    raw_size = record.get("fontSize")
    try:
        if raw_size not in {None, ""}:
            return max(4.0, min(86.0, float(raw_size)))
    except (TypeError, ValueError):
        pass
    try:
        scale = float(record.get("fontScale", 100))
    except (TypeError, ValueError):
        scale = 100
    return max(4.0, min(86.0, base_size * scale / 100))


def paragraph_style_for_slot(style: ParagraphStyle, slot_id: str, original: str | None = None) -> ParagraphStyle:
    base_size = float(getattr(style, "fontSize", 9))
    font_size = text_font_size_for_slot(slot_id, base_size, original)
    ratio = font_size / base_size if base_size else 1
    base_leading = float(getattr(style, "leading", base_size * 1.25))
    return ParagraphStyle(
        f"{getattr(style, 'name', 'text')}-{slot_id}",
        parent=style,
        fontSize=font_size,
        leading=base_leading * ratio,
    )


def record_text_slot(
    c: canvas.Canvas,
    slot_id: str,
    text: str,
    value: str,
    x: float,
    y: float,
    w: float,
    h: float,
    align: str = "left",
    *,
    font_name: str = "QBA",
    base_font_size: float = 9.0,
    font_size: float | None = None,
) -> None:
    plain = str(text).strip()
    if not plain or plain in {"•"}:
        return
    if getattr(c, "_qba_suppress_text_recording", False):
        return
    page = c.getPageNumber()
    effective_size = float(font_size if font_size is not None else base_font_size)
    PDF_EDITOR_MANIFEST["texts"].append(
        {
            "id": slot_id,
            "page": page,
            "original": plain,
            "value": value,
            "x": float(x),
            "y": float(y),
            "w": max(8.0, float(w)),
            "h": max(7.0, float(h)),
            "align": align,
            "fontName": font_name,
            "baseFontSize": float(base_font_size),
            "fontSize": effective_size,
            "fontScale": round((effective_size / float(base_font_size)) * 100, 2) if base_font_size else 100,
        }
    )


def resolve_image(path: Path) -> Path:
    path = Path(path)
    override = IMAGE_OVERRIDES.get(project_key(path)) or IMAGE_OVERRIDES.get(path.name)
    if not override:
        return path
    replacement = Path(override)
    if not replacement.is_absolute():
        replacement = ROOT / replacement
    if not replacement.exists():
        raise FileNotFoundError(f"Ảnh thay thế không tồn tại: {replacement}")
    return replacement


def editable_asset_alias(path: Path, file_name: str) -> Path:
    QUALITY_OUT.mkdir(parents=True, exist_ok=True)
    out_path = QUALITY_OUT / file_name
    source = resolve_image(path)
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im)
        if out_path.suffix.lower() in {".jpg", ".jpeg"}:
            im.convert("RGB").save(out_path, quality=95, subsampling=0, optimize=True)
        else:
            im.convert("RGBA").save(out_path, optimize=True)
    return out_path


def save_cropped_asset(source: Path, out_path: Path, crop_ratio: tuple[float, float, float, float], *, rotate: int = 0) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not source.exists():
        return out_path
    with Image.open(source) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        if rotate:
            im = im.rotate(rotate, expand=True, fillcolor=(255, 255, 255))
        left, top, right, bottom = crop_ratio
        box = (
            int(im.width * left),
            int(im.height * top),
            int(im.width * right),
            int(im.height * bottom),
        )
        im = im.crop(box)
        im = ImageEnhance.Contrast(im).enhance(1.08)
        im = ImageEnhance.Sharpness(im).enhance(1.05)
        im.save(out_path, quality=95, subsampling=0, optimize=True)
    return out_path


def normalize_legal_documents() -> dict[str, Path]:
    docs = {
        "registration_page_1": save_cropped_asset(
            LEGAL_SOURCE_PAGE_1,
            LEGAL_OUT / "dang-ky-doanh-nghiep-page-1.jpg",
            (0.02, 0.23, 0.995, 0.585),
        ),
        "registration_page_2": save_cropped_asset(
            LEGAL_SOURCE_PAGE_2,
            LEGAL_OUT / "dang-ky-doanh-nghiep-page-2.jpg",
            (0.02, 0.26, 0.995, 0.91),
        ),
        "strength_scan": save_cropped_asset(
            LEGAL_STRENGTH_SOURCE,
            LEGAL_OUT / "the-manh-doanh-nghiep-scan.jpg",
            (0.08, 0.18, 0.94, 0.90),
            rotate=-90,
        ),
    }
    return docs


def resolve_text(text: str) -> str:
    return normalize_editor_text(TEXT_OVERRIDES.get(text, text))


def normalize_inline_editor_text(value: str) -> str:
    """Prevent contenteditable markup from appearing literally in single-line canvas text."""
    value = normalize_editor_text(value)
    value = re.sub(r"<br\s*/?>", " ", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def enable_editable_text(c: canvas.Canvas) -> None:
    original_draw_string = c.drawString
    original_draw_centred = c.drawCentredString
    original_draw_right = c.drawRightString

    def draw_with_font(draw_fn, x, y, value, font_name, base_size, font_size, *args, **kwargs):
        old_font_name = getattr(c, "_fontname", font_name)
        old_font_size = float(getattr(c, "_fontsize", base_size))
        if abs(font_size - old_font_size) > 0.01 or font_name != old_font_name:
            c.setFont(font_name, font_size)
        try:
            return draw_fn(x, y, value, *args, **kwargs)
        finally:
            if abs(font_size - old_font_size) > 0.01 or font_name != old_font_name:
                c.setFont(old_font_name, old_font_size)

    def draw_string(x, y, text, *args, **kwargs):
        original = str(text)
        if getattr(c, "_qba_suppress_text_recording", False):
            return original_draw_string(x, y, resolve_text(original), *args, **kwargs)
        page, slot_id = next_text_slot_id(c)
        base_font_size = float(getattr(c, "_fontsize", 9))
        font_name = getattr(c, "_fontname", "QBA")
        font_size = text_font_size_for_slot(slot_id, base_font_size, original)
        value = normalize_inline_editor_text(resolve_text_for_slot(slot_id, original))
        width = max(8.0, pdfmetrics.stringWidth(value, font_name, font_size))
        record_text_slot(
            c,
            slot_id,
            original,
            value,
            x,
            y - font_size * 0.25,
            width,
            font_size * 1.25,
            "left",
            font_name=font_name,
            base_font_size=base_font_size,
            font_size=font_size,
        )
        return draw_with_font(original_draw_string, x, y, value, font_name, base_font_size, font_size, *args, **kwargs)

    def draw_centred(x, y, text, *args, **kwargs):
        original = str(text)
        if getattr(c, "_qba_suppress_text_recording", False):
            return original_draw_centred(x, y, resolve_text(original), *args, **kwargs)
        page, slot_id = next_text_slot_id(c)
        base_font_size = float(getattr(c, "_fontsize", 9))
        font_name = getattr(c, "_fontname", "QBA")
        font_size = text_font_size_for_slot(slot_id, base_font_size, original)
        value = normalize_inline_editor_text(resolve_text_for_slot(slot_id, original))
        width = max(8.0, pdfmetrics.stringWidth(value, font_name, font_size))
        record_text_slot(
            c,
            slot_id,
            original,
            value,
            x - width / 2,
            y - font_size * 0.25,
            width,
            font_size * 1.25,
            "center",
            font_name=font_name,
            base_font_size=base_font_size,
            font_size=font_size,
        )
        return draw_with_font(original_draw_centred, x, y, value, font_name, base_font_size, font_size, *args, **kwargs)

    def draw_right(x, y, text, *args, **kwargs):
        original = str(text)
        if getattr(c, "_qba_suppress_text_recording", False):
            return original_draw_right(x, y, resolve_text(original), *args, **kwargs)
        page, slot_id = next_text_slot_id(c)
        base_font_size = float(getattr(c, "_fontsize", 9))
        font_name = getattr(c, "_fontname", "QBA")
        font_size = text_font_size_for_slot(slot_id, base_font_size, original)
        value = normalize_inline_editor_text(resolve_text_for_slot(slot_id, original))
        width = max(8.0, pdfmetrics.stringWidth(value, font_name, font_size))
        record_text_slot(
            c,
            slot_id,
            original,
            value,
            x - width,
            y - font_size * 0.25,
            width,
            font_size * 1.25,
            "right",
            font_name=font_name,
            base_font_size=base_font_size,
            font_size=font_size,
        )
        return draw_with_font(original_draw_right, x, y, value, font_name, base_font_size, font_size, *args, **kwargs)

    c.drawString = draw_string
    c.drawCentredString = draw_centred
    c.drawRightString = draw_right


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("QBA", FONT_REGULAR))
    pdfmetrics.registerFont(TTFont("QBA-Bold", FONT_BOLD))
    inter_regular = next((path for path in INTER_REGULAR_CANDIDATES if Path(path).exists()), FONT_REGULAR)
    inter_bold = next((path for path in INTER_BOLD_CANDIDATES if Path(path).exists()), FONT_BOLD)
    pdfmetrics.registerFont(TTFont("QBA-Inter", inter_regular))
    pdfmetrics.registerFont(TTFont("QBA-Inter-Bold", inter_bold))


def rgb(color) -> tuple[int, int, int]:
    return tuple(int(v * 255) for v in color.rgb())


def rounded(c: canvas.Canvas, x: float, y: float, w: float, h: float, fill=WHITE, stroke=LINE, radius=16, sw=0.8) -> None:
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.setLineWidth(sw)
    c.roundRect(x, y, w, h, radius, stroke=1, fill=1)


def soft_shadow(c: canvas.Canvas, x: float, y: float, w: float, h: float, radius=22, alpha=0.08) -> None:
    c.saveState()
    c.setFillColor(HexColor("#0A2A23"))
    c.setFillAlpha(alpha)
    c.roundRect(x + 2.5, y - 3, w, h, radius, stroke=0, fill=1)
    c.restoreState()


def premium_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, *, radius=22, fill=WHITE, stroke=HexColor("#E1EAE4")) -> None:
    soft_shadow(c, x, y, w, h, radius=radius, alpha=0.075)
    rounded(c, x, y, w, h, fill=fill, stroke=stroke, radius=radius, sw=0.65)


def draw_check_icon(c: canvas.Canvas, cx: float, cy: float, size=13, *, fill=GREEN) -> None:
    c.setFillColor(fill)
    c.circle(cx, cy, size / 2, stroke=0, fill=1)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1.4)
    c.line(cx - size * 0.20, cy - size * 0.02, cx - size * 0.04, cy - size * 0.18)
    c.line(cx - size * 0.04, cy - size * 0.18, cx + size * 0.25, cy + size * 0.18)


def quality_kpi_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, desc: str) -> None:
    premium_card(c, x, y, w, h, radius=20)
    c.setFillColor(HexColor("#E8F6ED"))
    c.circle(x + 20, y + h - 20, 8, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.circle(x + 20, y + h - 20, 5, stroke=0, fill=1)
    c.setFillColor(INK)
    title_size = min(10.4, max(7.2, (w - 44) / max(1, pdfmetrics.stringWidth(title, "QBA-Inter-Bold", 1))))
    c.setFont("QBA-Inter-Bold", title_size)
    c.drawString(x + 36, y + h - 24, title)
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter", 7.7)
    c.drawString(x + 14, y + 16, desc)


def commitment_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, text: str) -> None:
    premium_card(c, x, y, w, h, radius=16, fill=HexColor("#FFFFFF"), stroke=HexColor("#E4EEE8"))
    draw_check_icon(c, x + 17, y + h / 2, size=12, fill=GREEN)
    c.setFillColor(INK_2)
    text_size = min(7.4, max(5.8, (w - 40) / max(1, pdfmetrics.stringWidth(text, "QBA-Inter-Bold", 1))))
    c.setFont("QBA-Inter-Bold", text_size)
    c.drawString(x + 31, y + h / 2 - text_size * 0.32, text)


def training_certificate_card(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float, name: str) -> None:
    premium_card(c, x, y, w, h, radius=16)
    rounded(c, x + 8, y + 7, 48, h - 14, fill=HexColor("#F6FAF7"), stroke=HexColor("#E1EAE4"), radius=10, sw=0.45)
    image_contain_trim(c, path, x + 12, y + 10, 40, h - 20, pad=1)
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 7.0)
    c.drawString(x + 63, y + h - 23, name)
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 5.8)
    c.drawString(x + 63, y + h - 37, "ISO 22000:2018")
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter", 5.6)
    c.drawString(x + 63, y + 12, "Đào tạo nhận thức")


def hero_corner_logo(c: canvas.Canvas, *, dark=True) -> None:
    fill = HexColor("#FFFFFF") if dark else WHITE
    stroke = HexColor("#DDEAE2") if not dark else HexColor("#EAF4EC")
    # Extend beyond the decorative outline so the complete QBA signature fills the hero frame cleanly.
    premium_card(c, 339, 634, 228, 152, radius=32, fill=fill, stroke=stroke)
    # Use a dedicated asset name so this editable hero frame never collides with the header logo slot.
    c.saveState()
    logo_clip = c.beginPath()
    logo_clip.roundRect(341, 636, 224, 148, 30)
    c.clipPath(logo_clip, stroke=0, fill=0)
    image_contain_trim(c, HERO_LOGO, 341, 636, 224, 148, pad=0)
    c.restoreState()


def para(c: canvas.Canvas, text: str, x: float, y_top: float, w: float, style: ParagraphStyle) -> float:
    original = str(text)
    page, slot_id = next_text_slot_id(c)
    text = resolve_text_for_slot(slot_id, original)
    applied_style = paragraph_style_for_slot(style, slot_id, original)
    p = Paragraph(text, applied_style)
    _, height = p.wrap(w, H)
    record_text_slot(
        c,
        slot_id,
        original,
        text,
        x,
        y_top - height,
        w,
        height,
        "left",
        font_name=applied_style.fontName,
        base_font_size=float(getattr(style, "fontSize", applied_style.fontSize)),
        font_size=float(applied_style.fontSize),
    )
    c._qba_suppress_text_recording = True
    p.drawOn(c, x, y_top - height)
    c._qba_suppress_text_recording = False
    return height


def legal_kpi_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, label: str, value: str, note: str | None = None) -> None:
    premium_card(c, x, y, w, h, radius=20)
    c.setFillColor(HexColor("#E8F6ED"))
    c.roundRect(x + 14, y + h - 28, 30, 16, 8, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.roundRect(x + 18, y + h - 24, 22, 8, 4, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter-Bold", 6.9)
    c.drawString(x + 52, y + h - 22, label.upper())
    c.setFillColor(INK)
    value_size = min(17.6, max(9.2, (w - 28) / max(1, pdfmetrics.stringWidth(value, "QBA-Inter-Bold", 1))))
    c.setFont("QBA-Inter-Bold", value_size)
    c.drawString(x + 14, y + 28, value)
    if note:
        c.setFillColor(MUTED)
        c.setFont("QBA-Inter", 6.7)
        c.drawString(x + 14, y + 14, note)


def legal_detail_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, body_text: str) -> None:
    premium_card(c, x, y, w, h, radius=18, fill=HexColor("#FFFFFF"), stroke=HexColor("#E4EEE8"))
    draw_check_icon(c, x + 18, y + h - 21, size=12, fill=GREEN)
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 8.4)
    c.drawString(x + 34, y + h - 24, title)
    legal_small = ParagraphStyle("legal-detail-small", fontName="QBA-Inter", fontSize=6.9, leading=9.4, textColor=MUTED)
    para(c, body_text, x + 14, y + h - 40, w - 28, legal_small)


def strength_card(c: canvas.Canvas, x: float, y: float, w: float, h: float, number: str, title: str, desc: str) -> None:
    premium_card(c, x, y, w, h, radius=20)
    c.setFillColor(HexColor("#E8F6ED"))
    c.circle(x + 24, y + h - 28, 13, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 7.4)
    c.drawCentredString(x + 24, y + h - 31, number)
    c.setFillColor(INK)
    title_size = min(9.2, max(7.2, (w - 58) / max(1, pdfmetrics.stringWidth(title, "QBA-Inter-Bold", 1))))
    c.setFont("QBA-Inter-Bold", title_size)
    c.drawString(x + 46, y + h - 32, title)
    strength_small = ParagraphStyle("strength-small", fontName="QBA-Inter", fontSize=6.7, leading=8.6, textColor=MUTED)
    para(c, desc, x + 46, y + h - 43, w - 62, strength_small)


def image_cover(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float, align=(0.5, 0.5)) -> None:
    _, path, x, y, w, h, align, zoom, rotate = image_layout_for_slot(c, path, "image", x, y, w, h, align, fit="cover")
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        iw, ih = im.size
        scale = max(w / iw, h / ih) * (zoom / 100) * (1 + abs(rotate) / 90)
        crop_w, crop_h = w / scale, h / scale
        left = max(0, min(iw - crop_w, (iw - crop_w) * align[0]))
        top = max(0, min(ih - crop_h, (ih - crop_h) * align[1]))
        crop = im.crop((int(left), int(top), int(left + crop_w), int(top + crop_h)))
        crop = crop.resize((max(1, int(w * 2.2)), max(1, int(h * 2.2))), Image.Resampling.LANCZOS)
        crop = rotate_keep_frame(crop, rotate)
    c.drawImage(ImageReader(crop), x, y, w, h, mask="auto")


def alpha_composite_clipped(frame: Image.Image, image: Image.Image, x: int, y: int) -> None:
    src_left = max(0, -x)
    src_top = max(0, -y)
    src_right = min(image.width, frame.width - x)
    src_bottom = min(image.height, frame.height - y)
    if src_right <= src_left or src_bottom <= src_top:
        return
    frame.alpha_composite(image.crop((src_left, src_top, src_right, src_bottom)), (max(0, x), max(0, y)))


def image_circle_crop(c: canvas.Canvas, path: Path, x: float, y: float, size: float, crop_box=None) -> None:
    _, path, x, y, w, h, align, zoom, rotate = image_layout_for_slot(c, path, "logo", x, y, size, size, (0.5, 0.5), fit="cover")
    size = min(w, h)
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGBA")
        if crop_box:
            im = im.crop(crop_box)
        else:
            side = min(im.size)
            left = int(max(0, min(im.width - side, (im.width - side) * align[0])))
            top = int(max(0, min(im.height - side, (im.height - side) * align[1])))
            im = im.crop((left, top, left + side, top + side))
        if zoom != 100:
            side = min(im.size)
            crop_side = max(1, int(side / (zoom / 100)))
            left = int(max(0, min(im.width - crop_side, (im.width - crop_side) * align[0])))
            top = int(max(0, min(im.height - crop_side, (im.height - crop_side) * align[1])))
            im = im.crop((left, top, left + crop_side, top + crop_side))
        im = im.resize((572, 572), Image.Resampling.LANCZOS)
        im = rotate_keep_frame(im, rotate)
        canvas_im = Image.new("RGBA", (640, 640), (255, 255, 255, 0))
        canvas_im.alpha_composite(im, (34, 34))
        mask = Image.new("L", (640, 640), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 639, 639), fill=255)
        canvas_im.putalpha(mask)
    c.setFillColor(WHITE)
    c.circle(x + size / 2, y + size / 2, size / 2, stroke=0, fill=1)
    c.drawImage(ImageReader(canvas_im), x, y, size, size, mask="auto")


def image_contain(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float, pad=0) -> None:
    _, path, x, y, w, h, align, zoom, rotate = image_layout_for_slot(c, path, "image", x, y, w, h, align=(0.5, 0.5), fit="contain")
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGBA")
        iw, ih = im.size
        scale = min((w - 2 * pad) / iw, (h - 2 * pad) / ih) * (zoom / 100)
        dw, dh = max(1, int(iw * scale * 2.2)), max(1, int(ih * scale * 2.2))
        resized = im.resize((dw, dh), Image.Resampling.LANCZOS)
        frame = Image.new("RGBA", (max(1, int(w * 2.2)), max(1, int(h * 2.2))), (255, 255, 255, 0))
        px = int((frame.width - resized.width) * align[0])
        py = int((frame.height - resized.height) * align[1])
        alpha_composite_clipped(frame, resized, px, py)
        frame = rotate_keep_frame(frame, rotate)
    c.drawImage(ImageReader(frame), x, y, w, h, mask="auto")


def image_contain_trim(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float, pad=0, threshold=246) -> None:
    _, path, x, y, w, h, align, zoom, rotate = image_layout_for_slot(c, path, "image", x, y, w, h, align=(0.5, 0.5), fit="contain")
    with Image.open(path) as im:
        im = ImageOps.exif_transpose(im).convert("RGB")
        mask = im.point(lambda p: 255 if p < threshold else 0).convert("L")
        bbox = mask.getbbox()
        if bbox:
            left, top, right, bottom = bbox
            inset = 8
            im = im.crop((max(0, left - inset), max(0, top - inset), min(im.width, right + inset), min(im.height, bottom + inset)))
        iw, ih = im.size
        scale = min((w - 2 * pad) / iw, (h - 2 * pad) / ih) * (zoom / 100)
        dw, dh = max(1, int(iw * scale * 2.2)), max(1, int(ih * scale * 2.2))
        resized = im.convert("RGBA").resize((dw, dh), Image.Resampling.LANCZOS)
        frame = Image.new("RGBA", (max(1, int(w * 2.2)), max(1, int(h * 2.2))), (255, 255, 255, 0))
        px = int((frame.width - resized.width) * align[0])
        py = int((frame.height - resized.height) * align[1])
        alpha_composite_clipped(frame, resized, px, py)
        frame = rotate_keep_frame(frame, rotate)
    c.drawImage(ImageReader(frame), x, y, w, h, mask="auto")


def overlay(c: canvas.Canvas, color, alpha: float, x=0, y=0, w=W, h=H) -> None:
    c.saveState()
    c.setFillColor(color)
    c.setFillAlpha(alpha)
    c.rect(x, y, w, h, stroke=0, fill=1)
    c.restoreState()


def page_bg(c: canvas.Canvas, color=PAPER) -> None:
    c.setFillColor(color)
    c.rect(0, 0, W, H, stroke=0, fill=1)


def cover_crop_for_background(im: Image.Image, width: int, height: int, align=(0.5, 0.5)) -> Image.Image:
    iw, ih = im.size
    scale = max(width / iw, height / ih)
    resized = im.resize((max(1, int(iw * scale)), max(1, int(ih * scale))), Image.Resampling.LANCZOS)
    left = int(max(0, min(resized.width - width, (resized.width - width) * align[0])))
    top = int(max(0, min(resized.height - height, (resized.height - height) * align[1])))
    return resized.crop((left, top, left + width, top + height))


def horizontal_alpha(width: int, height: int, start: int, end: int) -> Image.Image:
    row = Image.new("L", (width, 1))
    row.putdata([int(start + (end - start) * (x / max(1, width - 1))) for x in range(width)])
    return row.resize((width, height))


def vertical_alpha(width: int, height: int, start: int, end: int) -> Image.Image:
    col = Image.new("L", (1, height))
    col.putdata([int(start + (end - start) * (y / max(1, height - 1))) for y in range(height)])
    return col.resize((width, height))


def normalize_hero_backgrounds() -> dict[str, Path]:
    HERO_BG_OUT.mkdir(parents=True, exist_ok=True)
    specs = {
        "cover": (ASSETS / "hero-kitchen-cooking-bright-7476.jpg", (0.48, 0.54), rgb(ORANGE), "kitchen"),
        "overview": (ASSETS / "services/service-lunch-tray-v4.jpg", (0.50, 0.50), rgb(YELLOW), "meal"),
        "services": (ASSETS / "services/service-lunch-dining-hall.jpg", (0.54, 0.56), rgb(LIME), "dining"),
        "capacity": (ASSETS / "capacity/capacity-dining-hall-4k.jpg", (0.50, 0.52), rgb(YELLOW), "capacity"),
        "equipment": (ASSETS / "capacity/capacity-equipment.jpg", (0.48, 0.50), rgb(ORANGE), "equipment"),
        "response": (ASSETS / "process/process-receive-handover.jpg", (0.54, 0.50), rgb(LIME), "process"),
        "contact": (ASSETS / "hero-qba-truck-bellinturf-20260708.jpg", (0.57, 0.50), rgb(YELLOW), "delivery"),
    }
    out: dict[str, Path] = {}
    target_w, target_h = 1600, 2263
    for key, (path, align, accent, suffix) in specs.items():
        source = resolve_image(path)
        with Image.open(source) as im:
            base = cover_crop_for_background(ImageOps.exif_transpose(im).convert("RGB"), target_w, target_h, align=align)
        base = ImageEnhance.Color(base).enhance(1.08)
        base = ImageEnhance.Contrast(base).enhance(1.08)
        base = ImageEnhance.Sharpness(base).enhance(1.04)
        canvas_im = base.convert("RGBA")

        dark = rgb(INK)
        left_wash = Image.new("RGBA", canvas_im.size, (*dark, 0))
        left_wash.putalpha(horizontal_alpha(target_w, target_h, 224, 116))
        canvas_im.alpha_composite(left_wash)
        bottom_wash = Image.new("RGBA", canvas_im.size, (7, 26, 22, 0))
        bottom_wash.putalpha(vertical_alpha(target_w, target_h, 16, 178))
        canvas_im.alpha_composite(bottom_wash)

        draw = ImageDraw.Draw(canvas_im, "RGBA")
        accent_soft = (*accent, 78)
        accent_line = (*accent, 96)
        draw.polygon(
            [
                (int(target_w * 0.62), 0),
                (target_w, 0),
                (target_w, int(target_h * 0.30)),
                (int(target_w * 0.77), int(target_h * 0.22)),
            ],
            fill=accent_soft,
        )
        draw.polygon(
            [
                (0, int(target_h * 0.76)),
                (int(target_w * 0.30), target_h),
                (0, target_h),
            ],
            fill=(*accent, 46),
        )
        for i in range(8):
            y = int(target_h * 0.13 + i * 34)
            draw.line((int(target_w * 0.70), y, target_w - 90, y + 72), fill=accent_line, width=3)
        for i in range(6):
            x = int(target_w * 0.78 + i * 58)
            draw.ellipse((x, int(target_h * 0.72), x + 190, int(target_h * 0.72) + 190), outline=(255, 254, 251, 34), width=3)
        draw.rounded_rectangle(
            (int(target_w * 0.58), int(target_h * 0.075), target_w - 92, int(target_h * 0.24)),
            radius=38,
            outline=(255, 254, 251, 58),
            width=4,
        )
        draw.rounded_rectangle(
            (70, target_h - 430, int(target_w * 0.52), target_h - 94),
            radius=38,
            outline=(*accent, 72),
            width=4,
        )
        out_path = HERO_BG_OUT / f"{key}-{suffix}.jpg"
        canvas_im.convert("RGB").save(out_path, quality=94, subsampling=0, optimize=True)
        out[key] = out_path
    return out


def hero_page_bg(c: canvas.Canvas, hero_bgs: dict[str, Path], key: str, *, overlay_alpha: float = 0.18) -> None:
    image_cover(c, hero_bgs[key], 0, 0, W, H, align=(0.5, 0.5))
    overlay(c, INK, overlay_alpha)


def reset_pdf_editor_manifest() -> None:
    IMAGE_SLOT_COUNTER.clear()
    TEXT_SLOT_COUNTER.clear()
    PDF_EDITOR_MANIFEST["images"] = []
    PDF_EDITOR_MANIFEST["texts"] = []
    PDF_EDITOR_MANIFEST["page"] = {"width": W, "height": H}
    PDF_EDITOR_MANIFEST["version"] = 1


def write_pdf_editor_manifest(page_count: int) -> None:
    PDF_EDITOR_MANIFEST["pageCount"] = page_count
    PDF_EDITOR_MANIFEST_FILE.write_text(
        json.dumps(PDF_EDITOR_MANIFEST, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def chrome(c: canvas.Canvas, page: int, section: str, dark=False) -> None:
    set_slot_page_alias(c, page)
    current_page = c.getPageNumber()
    if getattr(c, "_qba_chrome_page", None) == current_page:
        return
    c._qba_chrome_page = current_page
    fg = WHITE if dark else INK
    muted = LIME if dark else MUTED
    line = HexColor("#54736B") if dark else LINE
    header_logo_size = 40
    image_circle_crop(c, BRAND / "qba-logo-full.jpg", 33.5, H - 56, header_logo_size, LOGO_ICON_CROP)
    c.setFillColor(fg)
    c.setFont("QBA-Bold", 9.0)
    c.drawString(33.5 + header_logo_size + 24, H - 38, "QUỐC BÌNH AN CATERING")
    c.setFillColor(muted)
    c.setFont("QBA", 7.6)
    c.drawString(33.5 + header_logo_size + 24, H - 50, section.upper())
    c.setStrokeColor(line)
    c.line(34, 42, W - 34, 42)
    c.setFillColor(muted)
    c.setFont("QBA", 7.4)
    c.drawString(34, 26, "HỒ SƠ NĂNG LỰC • 07/2026")
    c.drawRightString(W - 34, 26, f"{c.getPageNumber():02d}")


def section_title(c: canvas.Canvas, kicker: str, title: str, subtitle: str | None = None, dark=False, y=720, width=420) -> None:
    fg = WHITE if dark else INK
    accent = YELLOW if dark else ORANGE
    c.setFillColor(accent)
    c.setFont("QBA-Bold", 8.2)
    c.drawString(34, y + 30, kicker.upper())
    style = ParagraphStyle("section-title", fontName="QBA-Bold", fontSize=28, leading=32, textColor=fg)
    used = para(c, title, 34, y + 15, width, style)
    if subtitle:
        sub = ParagraphStyle("section-sub", fontName="QBA", fontSize=10.2, leading=14.2, textColor=LIME if dark else MUTED)
        para(c, subtitle, 34, y - used - 2, 450, sub)


def stat(c: canvas.Canvas, x: float, y: float, w: float, value: str, label: str, accent=LIME, dark=False) -> None:
    fill = INK_2 if dark else WHITE
    stroke = HexColor("#49675F") if dark else LINE
    rounded(c, x, y, w, 82, fill=fill, stroke=stroke, radius=14)
    c.setFillColor(accent)
    c.roundRect(x + 13, y + 53, 28, 14, 7, stroke=0, fill=1)
    c.setFillColor(WHITE if dark else INK)
    value_font = min(19, max(12, (w - 24) / max(1, pdfmetrics.stringWidth(value, "QBA-Bold", 1))))
    c.setFont("QBA-Bold", value_font)
    c.drawString(x + 13, y + 22, value)
    c.setFillColor(LIME if dark else MUTED)
    label_text = label.upper()
    label_font = min(6.6, max(5.2, (w - 58) / max(1, pdfmetrics.stringWidth(label_text, "QBA-Bold", 1))))
    c.setFont("QBA-Bold", label_font)
    c.drawString(x + 48, y + 56, label_text)


def pill(c: canvas.Canvas, text: str, x: float, y: float, fill=LIME, fg=INK, width=None) -> float:
    if width is None:
        width = pdfmetrics.stringWidth(text, "QBA-Bold", 7) + 22
    c.setFillColor(fill)
    c.roundRect(x, y, width, 20, 10, stroke=0, fill=1)
    c.setFillColor(fg)
    c.setFont("QBA-Bold", 7)
    c.drawCentredString(x + width / 2, y + 7, text.upper())
    return width


def temporary_pdf_edit_button(c: canvas.Canvas) -> None:
    if not PDF_EDIT_BUTTON_CONFIG.get("enabled", True):
        return
    url = str(PDF_EDIT_BUTTON_CONFIG.get("url") or "").strip()
    if not url:
        return
    x, y, w, h = W - 236, H - 94, 198, 46
    c.saveState()
    c.setFillColor(YELLOW)
    c.setStrokeColor(WHITE)
    c.setLineWidth(1.1)
    c.roundRect(x, y, w, h, 16, stroke=1, fill=1)
    c._qba_suppress_text_recording = True
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 8.1)
    c.drawCentredString(x + w / 2, y + 27, "CHỈNH SỬA PDF")
    c.setFont("QBA", 7.2)
    c.drawCentredString(x + w / 2, y + 14, "Nội dung & hình ảnh - nút tạm")
    c._qba_suppress_text_recording = False
    c.linkURL(url, (x, y, x + w, y + h), relative=0, thickness=0)
    c.restoreState()


def placeholder(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, note: str) -> None:
    rounded(c, x, y, w, h, fill=HexColor("#EEF1EC"), stroke=HexColor("#B9C5BC"), radius=16)
    c.setStrokeColor(HexColor("#B9C5BC"))
    c.setDash(5, 4)
    c.roundRect(x + 7, y + 7, w - 14, h - 14, 12, stroke=1, fill=0)
    c.setDash()
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 10)
    c.drawCentredString(x + w / 2, y + h / 2 + 8, title)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7.2)
    c.drawCentredString(x + w / 2, y + h / 2 - 8, note)


def centered_box_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    font_name: str = "QBA-Bold",
    font_size: float = 9.5,
    leading: float | None = None,
    color=WHITE,
) -> None:
    original = str(text)
    page, slot_id = next_text_slot_id(c)
    text = resolve_text_for_slot(slot_id, original)
    style = ParagraphStyle(
        "box-center",
        fontName=font_name,
        fontSize=text_font_size_for_slot(slot_id, font_size, original),
        leading=(leading or (font_size + 2)) * (text_font_size_for_slot(slot_id, font_size, original) / font_size if font_size else 1),
        alignment=TA_CENTER,
        textColor=color,
    )
    p = Paragraph(text, style)
    _, text_h = p.wrap(w - 14, h - 10)
    record_text_slot(
        c,
        slot_id,
        original,
        text,
        x + 7,
        y + (h - text_h) / 2 + 1,
        w - 14,
        text_h,
        "center",
        font_name=font_name,
        base_font_size=font_size,
        font_size=float(style.fontSize),
    )
    c._qba_suppress_text_recording = True
    p.drawOn(c, x + 7, y + (h - text_h) / 2 + 1)
    c._qba_suppress_text_recording = False


def flow_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    fill=FLOW_AMBER,
    stroke=FLOW_AMBER,
    text_color=WHITE,
    font_size: float = 9.4,
    radius: float = 12,
) -> None:
    rounded(c, x, y, w, h, fill=fill, stroke=stroke, radius=radius, sw=1.2)
    centered_box_text(c, text, x, y, w, h, color=text_color, font_size=font_size)


def flow_box_outline(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    stroke=FLOW_LINE,
    text_color=INK,
    font_size: float = 9.6,
    radius: float = 12,
) -> None:
    rounded(c, x, y, w, h, fill=WHITE, stroke=stroke, radius=radius, sw=1.6)
    centered_box_text(c, text, x, y, w, h, color=text_color, font_size=font_size)


def arrow_down(c: canvas.Canvas, x: float, y_top: float, y_bottom: float, color=FLOW_LINE) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    c.line(x, y_top, x, y_bottom)
    path = c.beginPath()
    path.moveTo(x, y_bottom)
    path.lineTo(x - 4, y_bottom + 6)
    path.lineTo(x + 4, y_bottom + 6)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.restoreState()


def arrow_right(c: canvas.Canvas, x_left: float, x_right: float, y: float, color=FLOW_LINE) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    c.line(x_left, y, x_right, y)
    path = c.beginPath()
    path.moveTo(x_right, y)
    path.lineTo(x_right - 6, y + 4)
    path.lineTo(x_right - 6, y - 4)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.restoreState()


def arrow_left(c: canvas.Canvas, x_left: float, x_right: float, y: float, color=FLOW_LINE) -> None:
    c.saveState()
    c.setStrokeColor(color)
    c.setFillColor(color)
    c.setLineWidth(1.2)
    c.line(x_right, y, x_left, y)
    path = c.beginPath()
    path.moveTo(x_left, y)
    path.lineTo(x_left + 6, y + 4)
    path.lineTo(x_left + 6, y - 4)
    path.close()
    c.drawPath(path, stroke=0, fill=1)
    c.restoreState()


def photo_tile(
    c: canvas.Canvas,
    path: Path,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    note: str = "",
    *,
    align=(0.5, 0.5),
    dark: bool = False,
    title_size: float = 9.5,
    note_size: float = 7.0,
    note_top: float = 17,
) -> None:
    fill = INK_2 if dark else WHITE
    stroke = HexColor("#49675F") if dark else LINE
    title_color = WHITE if dark else INK
    note_style = ParagraphStyle(
        "photo-note-dark" if dark else "photo-note",
        fontName="QBA",
        fontSize=note_size,
        leading=note_size + 2,
        textColor=HexColor("#EEF7F0") if dark else MUTED,
    )
    rounded(c, x, y, w, h, fill=fill, stroke=stroke, radius=16)
    image_h = h - (68 if note else 44)
    image_cover(c, path, x + 8, y + h - image_h - 8, w - 16, image_h, align=align)
    c.setFillColor(title_color)
    c.setFont("QBA-Bold", title_size)
    c.drawString(x + 12, y + 26, title)
    if note:
        para(c, note, x + 12, y + note_top, w - 24, note_style)


def menu_table_label(c: canvas.Canvas, text: str, x: float, y: float, *, accent=GREEN) -> None:
    c.setFillColor(accent)
    c.roundRect(x, y - 10, 126, 20, 10, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 7.0)
    c.drawCentredString(x + 63, y - 3, text.upper())


def menu_week_table(
    c: canvas.Canvas,
    x: float,
    y_top: float,
    w: float,
    days: list[str],
    rows: list[tuple[str, list[str], float]],
    *,
    accent=GREEN,
    label_width: float = 70,
    font_size: float = 6.4,
) -> float:
    """Draw a compact, editable weekly menu table without source-sheet branding."""
    header_h = 21
    column_w = (w - label_width) / len(days)
    cell_style = ParagraphStyle(
        "menu-week-cell",
        fontName="QBA",
        fontSize=font_size,
        leading=font_size + 1.45,
        textColor=INK,
        alignment=TA_CENTER,
    )
    y = y_top - header_h
    c.setFillColor(INK_2)
    c.rect(x, y, w, header_h, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 6.6)
    c.drawCentredString(x + label_width / 2, y + 7, "NHÓM MÓN")
    for index, day in enumerate(days):
        cx = x + label_width + index * column_w
        c.drawCentredString(cx + column_w / 2, y + 7, day.upper())
    c.setStrokeColor(HexColor("#CBD8D0"))
    c.setLineWidth(0.45)
    c.rect(x, y, w, header_h, stroke=1, fill=0)
    for index in range(len(days)):
        line_x = x + label_width + index * column_w
        c.line(line_x, y, line_x, y + header_h)

    for row_index, (label, values, row_h) in enumerate(rows):
        row_y = y - row_h
        label_fill = HexColor("#E8F3EA") if row_index % 2 == 0 else HexColor("#F2F6F3")
        c.setFillColor(label_fill)
        c.rect(x, row_y, label_width, row_h, stroke=0, fill=1)
        c.setFillColor(INK_2)
        c.setFont("QBA-Bold", 6.25)
        c.drawCentredString(x + label_width / 2, row_y + row_h / 2 - 2.1, label.upper())
        c.setStrokeColor(HexColor("#CBD8D0"))
        c.rect(x, row_y, w, row_h, stroke=1, fill=0)
        c.line(x + label_width, row_y, x + label_width, row_y + row_h)
        for index in range(len(days)):
            cx = x + label_width + index * column_w
            c.setFillColor(WHITE)
            c.rect(cx, row_y, column_w, row_h, stroke=0, fill=1)
            c.setStrokeColor(HexColor("#CBD8D0"))
            c.rect(cx, row_y, column_w, row_h, stroke=1, fill=0)
            value = values[index] if index < len(values) else ""
            if value:
                para(c, value, cx + 3.5, row_y + row_h - 4.5, column_w - 7, cell_style)
        y = row_y
    return y


def normalize_equipment() -> dict[str, Path]:
    EQUIP_OUT.mkdir(parents=True, exist_ok=True)
    specs = {
        "prep": (EQUIP_ORIGINAL / "01-thiet-bi-so-che-can-xac-nhan.jpeg", None),
        "washer": (EQUIP_ORIGINAL / "02-may-rua-khay-tu-dong.jpg", None),
        "slicer": (EQUIP_ORIGINAL / "03-may-thai-thit-hd-850.png", (0, 0, 900, 744)),
    }
    out: dict[str, Path] = {}
    for key, (path, crop) in specs.items():
        im = ImageOps.exif_transpose(Image.open(resolve_image(path))).convert("RGB")
        if crop:
            im = im.crop(crop)
        im = ImageEnhance.Contrast(im).enhance(1.025)
        im = im.filter(ImageFilter.UnsharpMask(radius=0.8, percent=80, threshold=3))
        canvas_im = Image.new("RGB", (1600, 1000), rgb(PAPER))
        shadow = Image.new("RGBA", canvas_im.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rounded_rectangle((78, 70, 1538, 940), radius=34, fill=(23, 59, 53, 36))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        canvas_im.paste(shadow, (0, 0), shadow)
        card = Image.new("RGB", (1420, 840), rgb(WHITE))
        max_w, max_h = 1340, 760
        scale = min(max_w / im.width, max_h / im.height)
        nw, nh = int(im.width * scale), int(im.height * scale)
        resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        card.paste(resized, ((card.width - nw) // 2, (card.height - nh) // 2))
        canvas_im.paste(card, (90, 70))
        draw = ImageDraw.Draw(canvas_im)
        draw.rounded_rectangle((90, 70, 1510, 910), radius=28, outline=rgb(LINE), width=4)
        out_path = EQUIP_OUT / f"{key}-normalized.jpg"
        canvas_im.save(out_path, quality=94, subsampling=0, optimize=True)
        out[key] = out_path
    return out


def normalize_logos() -> dict[str, Path]:
    logo_out = ASSETS / "hsnl/logos"
    logo_out.mkdir(parents=True, exist_ok=True)
    source = {
        "royal": ASSETS / "partner-hoang-gia.png",
        "etop": ASSETS / "partner-e-top.webp",
        "twin": ASSETS / "partner-twinkle.webp",
        "bellinturf": ASSETS / "partner-bellinturf.jpeg",
        "jys": ASSETS / "partner-jys.jpeg",
        "jintian": ASSETS / "partner-jintian.png",
        "leow": ASSETS / "partner-leow-foods.jpg",
        "tahtong": ASSETS / "partner-tah-tong.webp",
        "minhtri": ASSETS / "partner-minh-tri.webp",
        "kinhthien": ASSETS / "partner-kinh-thien-viet-nam-yongxing.png",
        "vinhhung": ASSETS / "partner-vinh-hung-kinte.jpg",
        "kangna": ASSETS / "partner-kang-na-viet-nam.webp",
    }
    out = {}
    for key, path in source.items():
        im = ImageOps.exif_transpose(Image.open(resolve_image(path))).convert("RGBA")
        if key == "kangna":
            im = crop_studio_subject(im.convert("RGB")).convert("RGBA")
        bg = Image.new("RGBA", (1000, 600), (255, 254, 251, 255))
        scale = min(820 / im.width, 420 / im.height)
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.Resampling.LANCZOS)
        bg.alpha_composite(im, ((1000 - im.width) // 2, (600 - im.height) // 2))
        out_path = logo_out / f"{key}.png"
        bg.convert("RGB").save(out_path, quality=95)
        out[key] = out_path
    return out


def crop_studio_subject(im: Image.Image, threshold: int = 14, pad_ratio: float = 0.055) -> Image.Image:
    corner = max(24, min(im.width, im.height) // 18)
    patches = [
        im.crop((0, 0, corner, corner)),
        im.crop((im.width - corner, 0, im.width, corner)),
        im.crop((0, im.height - corner, corner, im.height)),
        im.crop((im.width - corner, im.height - corner, im.width, im.height)),
    ]
    means = [ImageStat.Stat(patch).mean for patch in patches]
    bg = tuple(sum(mean[index] for mean in means) / len(means) for index in range(3))
    mask = Image.new("L", im.size, 0)
    mask_pixels = mask.load()
    pixels = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b = pixels[x, y]
            if max(abs(r - bg[0]), abs(g - bg[1]), abs(b - bg[2])) > threshold:
                mask_pixels[x, y] = 255
    bbox = mask.getbbox()
    if not bbox:
        return im
    left, top, right, bottom = bbox
    pad = int(max(right - left, bottom - top) * pad_ratio)
    left = max(0, left - pad)
    top = max(0, top - pad)
    right = min(im.width, right + pad)
    bottom = min(im.height, bottom + pad)
    if right - left < im.width * 0.18 or bottom - top < im.height * 0.18:
        return im
    return im.crop((left, top, right, bottom))


def normalize_meal_photos() -> dict[str, Path]:
    MEAL_OUT.mkdir(parents=True, exist_ok=True)
    specs = {
        "featured": ("suat-an-khay-co-bat-canh-20260720.png", (1600, 2000), 0.9, 0, True),
        "structure": ("suat-an-cau-chuyen-khay-day-du-20260710.png", (1600, 2000), 0.84, 0, True),
        "standard": ("suat-tieu-chuan-phuong-an-1-20260714.png", (1600, 2000), 0.86, 0, True),
        "energy": ("suat-tang-nang-luong-phuong-an-2-20260714.png", (1600, 2000), 0.86, 0, True),
        "expert": ("suat-chuyen-gia-khay-day-du-20260709.png", (1600, 2000), 0.84, 90, True),
        "vegetarian": ("khay-chay-day-du-20260714.png", (1600, 2000), 0.86, 0, True),
        "fish_menu": ("nhieu-khay-thuc-don-theo-ca-20260720.png", (1600, 2000), 0.98, 0, True),
        "dining_hall": ("nha-an-dong-cong-nhan.jpg", (1800, 1500), 0.92, 0, False),
    }
    out: dict[str, Path] = {}
    for key, (filename, size, fit, rotate, studio) in specs.items():
        source = ImageOps.exif_transpose(Image.open(resolve_image(MEAL_ORIGINAL / filename))).convert("RGB")
        if rotate:
            source = source.rotate(-rotate, expand=True)
        source = ImageEnhance.Color(source).enhance(1.08)
        source = ImageEnhance.Contrast(source).enhance(1.07)
        source = ImageEnhance.Sharpness(source).enhance(1.14)
        if studio:
            source = crop_studio_subject(source)
        target_w, target_h = size

        if studio:
            bg = Image.new("RGB", (target_w, target_h), (226, 226, 224))
        else:
            bg = source.copy()
            scale = max(target_w / bg.width, target_h / bg.height)
            bg = bg.resize((max(1, int(bg.width * scale)), max(1, int(bg.height * scale))), Image.Resampling.LANCZOS)
            left = max(0, (bg.width - target_w) // 2)
            top = max(0, (bg.height - target_h) // 2)
            bg = bg.crop((left, top, left + target_w, top + target_h))
            bg = bg.filter(ImageFilter.GaussianBlur(radius=22))
            bg = ImageEnhance.Brightness(bg).enhance(0.94)
            bg = ImageEnhance.Contrast(bg).enhance(0.94)

        max_w = int(target_w * fit)
        max_h = int(target_h * fit)
        scale = min(max_w / source.width, max_h / source.height)
        fg = source.resize((max(1, int(source.width * scale)), max(1, int(source.height * scale))), Image.Resampling.LANCZOS)

        shadow = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        fx = (target_w - fg.width) // 2
        fy = (target_h - fg.height) // 2
        shadow_draw.rounded_rectangle((fx + 16, fy + 18, fx + fg.width + 16, fy + fg.height + 18), radius=28, fill=(12, 32, 28, 36))
        shadow = shadow.filter(ImageFilter.GaussianBlur(22))
        canvas_im = bg.convert("RGBA")
        canvas_im.alpha_composite(shadow)
        canvas_im.paste(fg, (fx, fy))

        if not studio:
            draw = ImageDraw.Draw(canvas_im)
            draw.rounded_rectangle((fx, fy, fx + fg.width - 1, fy + fg.height - 1), radius=20, outline=(255, 254, 251, 170), width=5)
        out_path = MEAL_OUT / f"{key}.jpg"
        canvas_im.convert("RGB").save(out_path, quality=95, subsampling=0, optimize=True)
        out[key] = out_path
    return out


def build() -> None:
    reset_pdf_editor_manifest()
    register_fonts()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    equip = normalize_equipment()
    logos = normalize_logos()
    meals = normalize_meal_photos()
    hero_bgs = normalize_hero_backgrounds()
    legal_docs = normalize_legal_documents()
    process_photos = {
        "hot_kitchen": PROCESS_PHOTOS / "01-che-bien-bep-nong.png",
        "slicer_prep": PROCESS_PHOTOS / "02-may-thai-so-che.png",
        "lineup_service": PROCESS_PHOTOS / "03-chia-suat-va-rau-xanh.png",
        "greens_prep": PROCESS_PHOTOS / "04-so-che-rau-xanh.png",
        "raw_green_zone": PROCESS_PHOTOS / "05-phan-khu-song-rau.png",
        "equipment_room": PROCESS_PHOTOS / "06-thiet-bi-va-bep.png",
        "raw_meat_check": PROCESS_PHOTOS / "07-so-che-thit-va-kiem-soat-nguyen-lieu.png",
        "veg_storage": PROCESS_PHOTOS / "08-ke-nguyen-lieu-rau-cu.png",
        "receipt_signoff": PROCESS_PHOTOS / "09-ky-nhan-giao-nhan.png",
        "retained_samples": PROCESS_PHOTOS / "10-luu-mau.png",
        "food_prep_process": ASSETS / "hsnl/process/12-so-che-che-bien-thuc-pham-20260731.png",
        "meal_portioning_process": ASSETS / "hsnl/process/13-chia-suat-giao-ca-20260731.png",
        "retained_samples_process": ASSETS / "hsnl/process/14-luu-mau-sau-phuc-vu-20260731.png",
        "delivery_truck": PROCESS_PHOTOS / "11-xe-nguyen-lieu.jpg",
        "tray_washer": EQUIP_OUT / "may-rua-khay-chuyen-dung-chuyen-ca.jpg",
    }
    project_photos = {
        "royal": ROOT / "assets/hsnl/projects/royal-group-tray-portioning-20260729.png",
        "etop": ROOT / "assets/hsnl/projects/etop-vietnam-dining-hall-20260729.png",
        "bellinturf": ROOT / "assets/hsnl/projects/bellinturf-qba-truck-20260707.png",
    }
    extra_certs = {
        "iso_qba": CERT_EXTRA / "iso-22000-qba-2023-2026.png",
        "iso_chinh": CERT_EXTRA / "iso-dao-tao-nguyen-quoc-chinh.png",
        "iso_thuy": CERT_EXTRA / "iso-dao-tao-tran-thi-thanh-thuy.png",
        "iso_quynh": CERT_EXTRA / "iso-dao-tao-nguyen-thi-quynh.png",
        "iso_ha": CERT_EXTRA / "iso-dao-tao-nguyen-thi-ha.png",
        "supplier_sao_bien": CERT_EXTRA / "ncc-attp-sao-bien-2017-2020.png",
        "supplier_thuy_duong": CERT_EXTRA / "ncc-attp-thuy-duong-2025-2028.png",
        "supplier_beef_quarantine": CERT_EXTRA / "ncc-kiem-dich-thit-bo-dong-thap-2026.jpg",
    }
    quality_certs = {
        "iso_qba": editable_asset_alias(extra_certs["iso_qba"], "quality-system-iso-22000-qba.png"),
        "iso_chinh": editable_asset_alias(extra_certs["iso_chinh"], "quality-training-nguyen-quoc-chinh.png"),
        "iso_thuy": editable_asset_alias(extra_certs["iso_thuy"], "quality-training-tran-thi-thanh-thuy.png"),
        "iso_quynh": editable_asset_alias(extra_certs["iso_quynh"], "quality-training-nguyen-thi-quynh.png"),
        "iso_ha": editable_asset_alias(extra_certs["iso_ha"], "quality-training-nguyen-thi-ha.png"),
    }
    c = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
    enable_editable_text(c)
    c.setTitle("Hồ sơ năng lực Quốc Bình An Catering")
    c.setAuthor("Quốc Bình An Catering")

    body = ParagraphStyle("body", fontName="QBA", fontSize=10.2, leading=14.6, textColor=MUTED)
    body_dark = ParagraphStyle("body-dark", fontName="QBA", fontSize=10.2, leading=14.6, textColor=HexColor("#F0F7F1"))
    small = ParagraphStyle("small", fontName="QBA", fontSize=8.2, leading=11.4, textColor=MUTED)
    small_dark = ParagraphStyle("small-dark", fontName="QBA", fontSize=8.2, leading=11.4, textColor=HexColor("#E6F1E9"))
    milestone_note_dark = ParagraphStyle("milestone-note-dark", fontName="QBA", fontSize=7.0, leading=9.6, textColor=HexColor("#E6F1E9"))
    meal_desc = ParagraphStyle("meal-desc", fontName="QBA-Bold", fontSize=9.8, leading=13.0, textColor=HexColor("#1F443C"))
    h2 = ParagraphStyle("h2", fontName="QBA-Bold", fontSize=18, leading=21, textColor=INK)
    h2_dark = ParagraphStyle("h2-dark", fontName="QBA-Bold", fontSize=18, leading=21, textColor=WHITE)
    quote = ParagraphStyle("quote", fontName="QBA-Bold", fontSize=14, leading=19, textColor=INK)
    quote_dark = ParagraphStyle("quote-dark", fontName="QBA-Bold", fontSize=14, leading=19, textColor=WHITE)
    project_note = ParagraphStyle("project-note", fontName="QBA", fontSize=9.3, leading=12.8, textColor=MUTED)

    # 01 - Cover
    set_slot_page_alias(c, 1)
    hero_page_bg(c, hero_bgs, "cover", overlay_alpha=0.26)
    image_circle_crop(c, BRAND / "qba-logo-full.jpg", 38, H - 91, 58, LOGO_ICON_CROP)
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 11)
    c.drawString(108, H - 57, "QUỐC BÌNH AN")
    c.setFillColor(LIME)
    c.setFont("QBA", 8)
    c.drawString(108, H - 73, "INDUSTRIAL CATERING")
    temporary_pdf_edit_button(c)
    hero_corner_logo(c)
    pill(c, "Hồ sơ năng lực 2026", 38, 654, fill=YELLOW)
    cover_title = ParagraphStyle("cover", fontName="QBA-Bold", fontSize=38, leading=43, textColor=WHITE)
    para(c, "Bữa ăn an tâm.<br/><font color='#B8E59F'>Năng lượng bền bỉ.</font>", 38, 620, 500, cover_title)
    para(c, "Thiết kế và vận hành suất ăn công nghiệp theo nhu cầu thực tế - ngon miệng, đúng giờ và được kiểm soát từ đầu vào đến từng khay ăn.", 40, 476, 390, body_dark)
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 9)
    c.drawString(40, 108, "SUẤT ĂN CÔNG NGHIỆP • BẾP TẠI CHỖ • CATERING")
    c.setFillColor(LIME)
    c.setFont("QBA", 8)
    c.drawString(40, 88, "CÔNG TY TNHH MỘT THÀNH VIÊN QUỐC BÌNH AN")
    c.showPage()

    # 02 - Letter
    page_bg(c)
    chrome(c, 2, "Lời ngỏ")
    c.setFillColor(INK)
    c.rect(0, 0, 238, H, stroke=0, fill=1)
    image_circle_crop(c, BRAND / "qba-logo-full.jpg", 34, 646, 70, LOGO_ICON_CROP)
    para(c, "Một bữa ăn<br/>đúng giờ bắt đầu<br/>từ trách nhiệm.", 34, 610, 178, quote_dark)
    para(c, "“Chúng tôi hiểu giá trị của một bữa cơm nóng, no bụng và hợp khẩu vị đối với người lao động sau mỗi giờ làm việc.”", 34, 474, 172, body_dark)
    c.setFillColor(ORANGE)
    c.setFont("QBA-Bold", 8)
    c.drawString(276, 754, "LỜI NGỎ")
    letter_title = ParagraphStyle(
        "letter-title",
        fontName="QBA-Bold",
        fontSize=22,
        leading=25,
        textColor=INK,
    )
    para(c, "Kính gửi Quý Khách hàng<br/>và Đối tác,", 276, 730, 280, letter_title)
    para(c, "Quốc Bình An bắt đầu hành trình từ những khó khăn rất thật của người lao động và người làm nghề. Từ khoảng 600 suất ăn đầu tiên, chúng tôi chọn cách phát triển bằng sự lắng nghe: lắng nghe khẩu vị, nhịp sản xuất, yêu cầu an toàn và cả những phản hồi nhỏ nhất trong từng ca ăn.", 276, 610, 280, body)
    para(c, "Qua mỗi dự án, hệ thống bếp, thiết bị và cách tổ chức công việc tiếp tục được điều chỉnh. Mục tiêu không thay đổi: mang đến những bữa cơm chất lượng, nóng hổi và sẵn sàng đúng giờ.", 276, 500, 280, body)
    para(c, "Quốc Bình An trân trọng cơ hội được đồng hành và chăm lo bữa ăn hằng ngày cho đội ngũ của Quý doanh nghiệp.", 276, 410, 280, body)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 10)
    c.drawString(276, 330, "NGUYỄN QUỐC CHINH")
    c.setFillColor(MUTED)
    c.setFont("QBA", 8)
    c.drawString(276, 314, "Đồng sáng lập - Giám đốc")
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 10)
    c.drawString(420, 330, "TRẦN THỊ THANH THUỶ")
    c.setFillColor(MUTED)
    c.setFont("QBA", 8)
    c.drawString(420, 314, "Đồng sáng lập - Quản lý đầu vào")
    rounded(c, 276, 82, 280, 196, fill=WHITE)
    image_cover(c, BRAND / "hop-doi-ngu-quan-ly.png", 286, 126, 260, 142, align=(0.5, 0.66))
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 9.5)
    c.drawString(292, 105, "Điều phối đội ngũ quản lý")
    c.setFillColor(MUTED)
    c.setFont("QBA", 7.2)
    c.drawString(292, 94, "Họp ca, rà soát chứng từ và thống nhất nhịp vận hành trước phục vụ.")
    chrome(c, 2, "Lời ngỏ")
    c.showPage()

    # 03 - Legal foundation
    page_bg(c, HexColor("#F7FAF8"))
    chrome(c, 30, "Nền tảng pháp lý")
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 8.2)
    c.drawString(34, 735, "00 / NỀN TẢNG PHÁP LÝ")
    premium_card(c, 34, 86, 218, 582, radius=24)
    c.setFillColor(HexColor("#E8F6ED"))
    c.roundRect(58, 614, 116, 22, 11, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 7.2)
    c.drawCentredString(116, 622, "GIẤY ĐĂNG KÝ DN")
    rounded(c, 48, 282, 190, 300, fill=HexColor("#FBFDFB"), stroke=HexColor("#E5EEE8"), radius=20, sw=0.5)
    image_contain(c, legal_docs["registration_page_1"], 55, 294, 176, 276, pad=1)

    legal_title = ParagraphStyle("legal-title", fontName="QBA-Inter-Bold", fontSize=23.5, leading=27, textColor=INK)
    para(c, "Hồ sơ pháp lý<br/>doanh nghiệp", 274, 704, 270, legal_title)
    legal_subtitle = ParagraphStyle("legal-subtitle", fontName="QBA-Inter", fontSize=9.0, leading=12.8, textColor=MUTED)
    para(c, "Quốc Bình An được đăng ký hoạt động dưới loại hình công ty trách nhiệm hữu hạn một thành viên, có hồ sơ pháp lý cập nhật và nền tảng vốn điều lệ rõ ràng để triển khai dịch vụ suất ăn công nghiệp dài hạn.", 274, 638, 278, legal_subtitle)

    legal_kpis = [
        ("Mã số doanh nghiệp", "3602666032", "Đồng thời là mã số thuế"),
        ("Đăng ký lần đầu", "02/12/2011", "Hồ sơ pháp lý gốc"),
        ("Thay đổi lần 4", "01/06/2026", "Cập nhật gần nhất"),
        ("Vốn điều lệ", "15 tỷ đồng", "15.000.000.000 VND"),
    ]
    for i, (label, value, note) in enumerate(legal_kpis):
        x = 274 + (i % 2) * 144
        y = 500 - (i // 2) * 88
        legal_kpi_card(c, x, y, 132, 74, label, value, note)

    legal_detail_card(
        c,
        274,
        284,
        278,
        76,
        "Tên pháp lý",
        "CÔNG TY TNHH MỘT THÀNH VIÊN QUỐC BÌNH AN",
    )
    legal_detail_card(
        c,
        274,
        192,
        278,
        76,
        "Trụ sở chính",
        "Số 35 Đường Huỳnh Văn Nghệ, KP Phước Kiểng, Phường Nhơn Trạch, Thành phố Đồng Nai, Việt Nam.",
    )
    legal_detail_card(
        c,
        274,
        100,
        278,
        76,
        "Đại diện pháp luật",
        "Ông Nguyễn Quốc Chinh - Giám đốc, chịu trách nhiệm điều hành và phê duyệt định hướng vận hành dịch vụ.",
    )
    chrome(c, 30, "Nền tảng pháp lý")
    c.showPage()

    # 04 - Enterprise strengths
    page_bg(c, HexColor("#F7FAF8"))
    chrome(c, 31, "Thế mạnh doanh nghiệp")
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 8.2)
    c.drawString(34, 735, "00 / THẾ MẠNH DOANH NGHIỆP")
    strength_title = ParagraphStyle("strength-title", fontName="QBA-Inter-Bold", fontSize=24.5, leading=28, textColor=INK)
    para(c, "Nền tảng vững.<br/>Vận hành đáng tin cậy.", 34, 704, 500, strength_title)
    para(c, "Từ vốn điều lệ, hồ sơ pháp lý đến kinh nghiệm tổ chức bếp ăn, Quốc Bình An xây dựng năng lực phục vụ bằng sự ổn định, kiểm soát và khả năng đồng hành lâu dài với nhà máy.", 34, 632, 500, legal_subtitle)

    premium_card(c, 34, 390, 238, 172, radius=24)
    c.setFillColor(HexColor("#E8F6ED"))
    c.roundRect(58, 520, 88, 22, 11, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 7.2)
    c.drawCentredString(102, 528, "VỐN ĐIỀU LỆ")
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 38)
    c.drawString(58, 468, "15")
    c.setFont("QBA-Inter-Bold", 15)
    c.drawString(126, 486, "tỷ đồng")
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter", 7.8)
    c.drawString(58, 438, "Nền tảng tài chính để đầu tư thiết bị, nhân sự")
    c.drawString(58, 424, "và kiểm soát chất lượng theo hợp đồng dài hạn.")

    premium_card(c, 34, 180, 238, 184, radius=22)
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 10.4)
    c.drawString(58, 326, "Năng lực cốt lõi")
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter", 6.9)
    c.drawString(58, 310, "Biên tập từ tài liệu thế mạnh doanh nghiệp.")
    core_items = [
        ("01", "Chất lượng sản phẩm", "Tươi ngon, sạch, đủ dinh dưỡng và đổi mới thực đơn."),
        ("02", "Tận tâm dịch vụ", "Phục vụ nhanh, chủ động lắng nghe và xử lý phản hồi."),
        ("03", "An toàn vệ sinh", "Kiểm soát rủi ro trong tiếp nhận, chế biến và phục vụ."),
    ]
    for i, (num, title, desc) in enumerate(core_items):
        row_y = 280 - i * 42
        c.setFillColor(HexColor("#E8F6ED"))
        c.circle(66, row_y + 12, 11, stroke=0, fill=1)
        c.setFillColor(GREEN)
        c.setFont("QBA-Inter-Bold", 6.5)
        c.drawCentredString(66, row_y + 9, num)
        c.setFillColor(INK)
        c.setFont("QBA-Inter-Bold", 7.8)
        c.drawString(84, row_y + 16, title)
        c.setFillColor(MUTED)
        c.setFont("QBA-Inter", 6.4)
        c.drawString(84, row_y + 4, desc)

    strength_items = [
        ("01", "Pháp lý cập nhật", "Đăng ký thay đổi lần 4 ngày 01/06/2026, thông tin doanh nghiệp rõ ràng để ký kết hợp đồng."),
        ("02", "Chất lượng suất ăn", "Kiểm soát dinh dưỡng, khẩu phần và khẩu vị để món ăn phù hợp người lao động."),
        ("03", "An toàn thực phẩm", "Áp dụng kiểm thực, lưu mẫu, vệ sinh khu bếp và truy xuất khi cần."),
        ("04", "Phản hồi nhanh", "Đầu mối quản lý trực tiếp, tiếp nhận phản ánh và điều chỉnh theo ca phục vụ."),
        ("05", "Nguồn lực vận hành", "Tổ chức nhân sự, thiết bị và quy trình để duy trì bếp tại chỗ hoặc phục vụ theo ca."),
        ("06", "Đồng hành dài hạn", "Ưu tiên sự ổn định, đúng giờ và cải tiến thực đơn theo nhu cầu từng nhà máy."),
    ]
    for i, (num, title, desc) in enumerate(strength_items):
        x = 300
        y = 552 - i * 74
        strength_card(c, x, y, 252, 66, num, title, desc)
    chrome(c, 31, "Thế mạnh doanh nghiệp")
    c.showPage()

    # 03 - Snapshot
    hero_page_bg(c, hero_bgs, "overview", overlay_alpha=0.24)
    chrome(c, 3, "Quốc Bình An trong một trang", dark=True)
    section_title(c, "01 / Tổng quan", "20 năm vun bồi<br/><font color='#B8E59F'>một bữa cơm tử tế.</font>", "Hoạt động thực tế từ năm 2006; đăng ký pháp lý từ năm 2011.", dark=True, y=720)
    hero_corner_logo(c)
    stats = [("2006", "BẮT ĐẦU HÀNH TRÌNH"), ("10", "BẾP ĐANG VẬN HÀNH"), ("03", "CA PHỤC VỤ MỖI NGÀY"), ("~100", "NHÂN SỰ")]
    for i, (v, l) in enumerate(stats):
        stat(c, 34 + (i % 2) * 266, 475 - (i // 2) * 104, 248, v, l, [YELLOW, LIME, ORANGE, YELLOW][i], dark=True)
    para(c, "Quốc Bình An cung cấp suất ăn công nghiệp, vận hành bếp tại chỗ và tổ chức nấu tại bếp trung tâm - vận chuyển theo yêu cầu. Mỗi mô hình được điều chỉnh theo sản lượng, số ca, khẩu vị và điều kiện mặt bằng thực tế.", 34, 300, 520, body_dark)
    c.setFillColor(LIME)
    c.setFont("QBA-Bold", 9)
    c.drawString(34, 175, "DẤU MỐC CAO NHẤT ĐƯỢC DOANH NGHIỆP GHI NHẬN")
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 32)
    c.drawString(34, 128, "17.000")
    c.setFont("QBA", 11)
    c.drawString(170, 138, "suất ăn/ngày • năm 2019")
    para(c, "Sau biến động dịch bệnh và Covid, Quốc Bình An vẫn duy trì 15.000+ suất/ngày tính tới 2026.", 170, 118, 128, milestone_note_dark)
    chrome(c, 3, "Quốc Bình An trong một trang", dark=True)
    c.showPage()

    # 04 - Origin story
    page_bg(c)
    chrome(c, 4, "Câu chuyện khởi nghiệp")
    section_title(c, "02 / Câu chuyện", "Từ những khó khăn,<br/><font color='#F0835F'>hiểu giá trị bữa cơm nóng.</font>", y=720)
    rounded(c, 30, 76, 296, 504, fill=WHITE)
    image_contain(c, meals["structure"], 42, 88, 272, 480, pad=2)
    para(c, "Xuất thân từ những khó khăn, ông Nguyễn Quốc Chinh hiểu rằng một bữa cơm nóng và no bụng không chỉ tiếp sức cho người lao động. Đó còn là khoảng nghỉ cần thiết để họ trở lại ca làm việc với năng lượng tốt hơn.", 334, 548, 222, body)
    para(c, "Cùng bà Trần Thị Thanh Thuỷ phụ trách đầu vào nguyên liệu, ông bắt đầu Quốc Bình An với tinh thần của người làm nghề: chọn thực phẩm tươi, nấu hợp khẩu vị và lắng nghe khách hàng để thay đổi mỗi ngày.", 334, 430, 222, body)
    para(c, "Từ khoảng 600 suất ăn/ngày cho Royal Hoàng Gia, mỗi hợp đồng tiếp theo trở thành một hành trình cải tiến riêng - từ cách quản lý, thiết bị đến nhịp phối hợp với nhà máy.", 334, 305, 222, body)
    pill(c, "600 suất ăn/ngày khi khởi đầu", 334, 195, fill=YELLOW, width=190)
    rounded(c, 334, 96, 222, 76, fill=HexColor("#EEF1EC"), stroke=LINE, radius=14)
    image_contain(c, BRAND / "qba-logo-history-card.jpg", 350, 124, 190, 34, pad=0)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 7.4)
    c.drawString(350, 112, "TƯ LIỆU THƯƠNG HIỆU 2006-2010")
    c.setFillColor(MUTED)
    c.setFont("QBA", 6.4)
    c.drawString(350, 103, "Quốc Bình An - tận tâm trong từng bữa ăn")
    chrome(c, 4, "Câu chuyện khởi nghiệp")
    c.showPage()

    # 05 - Timeline
    page_bg(c)
    chrome(c, 5, "Hành trình phát triển")
    section_title(c, "03 / Dấu mốc", "Lớn lên cùng<br/><font color='#F0835F'>niềm tin khách hàng.</font>", "Các mốc dưới đây do doanh nghiệp cung cấp và sẽ được đối chiếu trước bản chính thức.", y=720)
    milestones = [
        ("2006", "600 suất/ngày", "Bắt đầu cùng Royal Hoàng Gia"),
        ("2010", "3.000+ suất/ngày", "Tiếp nhận dự án E-top"),
        ("2017", "10.000+ suất/ngày", "Đạt dấu mốc vận hành mới"),
        ("2019", "17.000 suất/ngày", "Mức cao nhất được ghi nhận"),
        ("2026", "10 bếp • 3 ca", "Dù biến động khó khăn, đặc biệt thời kỳ Covid-19, QBA vẫn duy trì 15.000+ suất/ngày đến 2026 hiện nay."),
    ]
    c.setStrokeColor(LINE)
    c.setLineWidth(3)
    c.line(94, 134, 94, 590)
    for i, (year, value, text) in enumerate(milestones):
        y = 570 - i * 82
        c.setFillColor([ORANGE, YELLOW, LIME, ORANGE, YELLOW, GREEN][i])
        c.circle(94, y, 10, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 14)
        c.drawString(126, y + 11, year)
        c.setFont("QBA-Bold", 10)
        c.drawString(214, y + 11, value)
        c.setFillColor(MUTED)
        c.setFont("QBA", 8.5)
        c.drawString(126, y - 8, text)
    chrome(c, 5, "Hành trình phát triển")
    c.showPage()

    # 06 - Vision mission values
    page_bg(c)
    chrome(c, 6, "Tầm nhìn - Sứ mệnh - Giá trị")
    section_title(c, "04 / Định hướng", "Chất lượng bắt đầu<br/><font color='#F0835F'>từ cách chúng tôi hành động.</font>", y=720)
    cards = [
        ("TẦM NHÌN", "Phát triển hệ thống suất ăn công nghiệp linh hoạt, thích nghi với nhịp sản xuất và nhu cầu ngày càng cao của doanh nghiệp.", LIME),
        ("SỨ MỆNH", "Mang đến những bữa cơm chất lượng, nóng hổi và được nấu bằng trách nhiệm của người làm nghề.", YELLOW),
        ("GIÁ TRỊ", "Lắng nghe • Trách nhiệm • Thích nghi • Đúng giờ", ORANGE),
    ]
    for i, (label, text, color) in enumerate(cards):
        y = 466 - i * 148
        rounded(c, 34, y, 522, 124, fill=WHITE)
        c.setFillColor(color)
        c.roundRect(52, y + 78, 84, 22, 11, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 8)
        c.drawCentredString(94, y + 86, label)
        para(c, text, 158, y + 94, 370, quote if i < 2 else h2)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 76, "Nội dung định hướng đang ở bản dự thảo và cần Ban Giám đốc duyệt trước khi phát hành.")
    chrome(c, 6, "Tầm nhìn - Sứ mệnh - Giá trị")
    c.showPage()

    # 07 - Services
    hero_page_bg(c, hero_bgs, "services", overlay_alpha=0.25)
    chrome(c, 7, "Hệ giải pháp", dark=True)
    section_title(c, "05 / Dịch vụ", "Một hệ giải pháp.<br/><font color='#FFD569'>Nhiều nhịp phục vụ.</font>", dark=True, y=720)
    hero_corner_logo(c)
    services = ["Suất ăn trưa", "Suất ăn sáng", "Suất ăn ca đêm", "Thực đơn chay", "Tiệc & buffet", "Bếp tại chỗ", "Bếp trung tâm & vận chuyển"]
    for i, s in enumerate(services):
        col, row = i % 2, i // 2
        x, y = 34 + col * 266, 532 - row * 104
        rounded(c, x, y, 248, 82, fill=INK_2, stroke=HexColor("#49675F"), radius=14)
        c.setFillColor([LIME, YELLOW, ORANGE][i % 3])
        c.setFont("QBA-Bold", 18)
        c.drawString(x + 14, y + 41, f"{i + 1:02d}")
        c.setFillColor(WHITE)
        c.setFont("QBA-Bold", 11)
        c.drawString(x + 58, y + 45, s)
        c.setFillColor(HexColor("#C8D8CD"))
        c.setFont("QBA", 7.5)
        c.drawString(x + 58, y + 26, "Linh hoạt theo sản lượng và điều kiện thực tế")
    chrome(c, 7, "Hệ giải pháp", dark=True)
    c.showPage()

    # 08 - Industrial meals
    page_bg(c)
    chrome(c, 8, "Suất ăn công nghiệp")
    section_title(c, "06 / Giải pháp chủ lực", "Đúng khẩu phần.<br/><font color='#F0835F'>Đúng ca. Đúng thời điểm.</font>", y=720)
    rounded(c, 34, 190, 344, 450, fill=WHITE)
    image_cover(c, meals["featured"], 44, 200, 324, 430, align=(0.5, 0.5))
    para(c, "Quốc Bình An tổ chức bữa ăn theo số lượng, số ca và đặc thù công việc. Thực đơn được duyệt bởi Giám đốc Nguyễn Quốc Chinh và bà Trần Thị Thanh Thuỷ, đồng thời điều chỉnh theo phản hồi thực tế tại nhà ăn.", 398, 612, 158, body)
    bullets = ["Món chính, món phụ, rau, canh, cơm và tráng miệng", "Khẩu vị miền Nam, món Trung Hoa và Đài Loan", "Bếp tại chỗ hoặc nấu tập trung - vận chuyển", "Phục vụ 3 ca mỗi ngày"]
    for i, text in enumerate(bullets):
        y = 438 - i * 64
        c.setFillColor([LIME, YELLOW, ORANGE, LIME][i])
        c.circle(409, y + 6, 7, stroke=0, fill=1)
        para(c, text, 426, y + 18, 126, small)
    pill(c, "Suất ăn chủ lực", 398, 160, fill=YELLOW, width=132)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 86, "Ảnh khẩu phần được căn chỉnh để thấy rõ món chính, rau và bát canh trong khay.")
    chrome(c, 8, "Suất ăn công nghiệp")
    c.showPage()

    # 09 - Flexible services
    page_bg(c)
    chrome(c, 9, "Dịch vụ linh hoạt")
    section_title(c, "07 / Dịch vụ bổ sung", "Từ ca đêm<br/><font color='#F0835F'>đến những dịp đặc biệt.</font>", y=720)
    service_cards = [
        (meals["dining_hall"], "Nhà ăn đông ca", "Phục vụ số lượng lớn theo nhịp sản xuất thực tế"),
        (meals["fish_menu"], "Thực đơn theo ca", "Canh, rau và món mặn được đổi theo thực tế"),
    ]
    for i, (path, title, desc) in enumerate(service_cards):
        x = 34 + i * 272
        rounded(c, x, 330, 250, 300, fill=WHITE)
        if i == 0:
            image_cover(c, path, x + 10, 430, 230, 188, align=(0.5, 0.5))
        else:
            image_contain(c, path, x + 10, 430, 230, 188, pad=2)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 13.5)
        c.drawString(x + 16, 405, title)
        desc_h = para(c, desc, x + 16, 378, 218, meal_desc)
        c.setFillColor([ORANGE, LIME][i])
        c.rect(x + 16, max(338, 378 - desc_h - 12), 52, 5, stroke=0, fill=1)
    rounded(c, 34, 126, 522, 182, fill=WHITE)
    image_contain(c, meals["expert"], 46, 140, 312, 154, pad=2)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 14)
    c.drawString(382, 274, "Suất chuyên gia")
    para(c, "Linh hoạt về món, định lượng và cách trình bày; khay ảnh được xoay ngang để nhìn rõ đầy đủ khẩu phần.", 382, 248, 150, meal_desc)
    c.setFillColor(YELLOW)
    c.rect(382, 158, 52, 5, stroke=0, fill=1)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 90, "Ảnh minh họa được căn chỉnh để thấy rõ bối cảnh phục vụ và cơ cấu khẩu phần.")
    chrome(c, 9, "Dịch vụ linh hoạt")
    c.showPage()

    # 10 - Capacity
    hero_page_bg(c, hero_bgs, "capacity", overlay_alpha=0.28)
    chrome(c, 10, "Năng lực vận hành", dark=True)
    section_title(c, "08 / Năng lực", "Sẵn sàng cho<br/><font color='#B8E59F'>mỗi nhịp sản xuất.</font>", dark=True, y=720)
    hero_corner_logo(c)
    cap = [("10", "BẾP"), ("03", "CA/NGÀY"), ("~100", "NHÂN SỰ"), ("60 km", "BÁN KÍNH VẬN CHUYỂN")]
    for i, (v, l) in enumerate(cap):
        stat(c, 34 + (i % 2) * 266, 484 - (i // 2) * 104, 248, v, l, [LIME, YELLOW, ORANGE, LIME][i], dark=True)
    rounded(c, 34, 145, 522, 188, fill=INK_2, stroke=HexColor("#49675F"), radius=18)
    c.setFillColor(YELLOW)
    c.setFont("QBA-Bold", 30)
    c.drawString(55, 260, "17.000")
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 12)
    c.drawString(190, 270, "suất ăn/ngày")
    c.setFillColor(LIME)
    c.setFont("QBA", 8)
    c.drawString(190, 252, "Dấu mốc cao nhất được ghi nhận năm 2019")
    para(c, "Số liệu trên do doanh nghiệp cung cấp. Bản chính thức cần đối chiếu công suất hiện tại, công suất thiết kế và sản lượng bình quân.", 55, 225, 470, small_dark)
    capacity_notes = ["Đối chiếu công suất hiện tại", "Theo dõi sản lượng từng ca", "Điều chỉnh đội hình phục vụ"]
    for i, text in enumerate(capacity_notes):
        x = 55 + i * 158
        rounded(c, x, 158, 142, 40, fill=HexColor("#274C44"), stroke=HexColor("#49675F"), radius=10)
        para(c, text, x + 10, 188, 122, small_dark)
    chrome(c, 10, "Năng lực vận hành", dark=True)
    c.showPage()

    # 11 - People
    page_bg(c)
    chrome(c, 11, "Con người vận hành")
    section_title(c, "09 / Đội ngũ", "Kinh nghiệm được tổ chức<br/><font color='#F0835F'>thành trách nhiệm rõ ràng.</font>", y=720)
    photo_tile(
        c,
        process_photos["lineup_service"],
        34,
        280,
        326,
        358,
        "Phối hợp theo công đoạn",
        "Tổ nấu, sơ chế và chia suất vận hành đồng bộ trong cùng một nhịp ca.",
        align=(0.52, 0.55),
        title_size=10.8,
        note_size=7.6,
    )
    photo_tile(
        c,
        process_photos["greens_prep"],
        374,
        456,
        192,
        182,
        "Rau xanh tách khu",
        "Sơ chế, lựa rửa và hoàn thiện tại khu riêng.",
        align=(0.48, 0.56),
        title_size=10.0,
        note_size=7.2,
    )
    photo_tile(
        c,
        process_photos["raw_green_zone"],
        374,
        268,
        192,
        176,
        "Thực phẩm sống tách biệt",
        "Khu đồ sống và rau xanh bố trí riêng.",
        align=(0.46, 0.68),
        title_size=9.5,
        note_size=6.9,
    )
    rounded(c, 34, 96, 522, 158, fill=WHITE)
    para(
        c,
        "Đội ngũ vận hành tuân thủ đồng phục đầy đủ gồm áo, tạp dề, mũ trùm tóc, khẩu trang và bao tay trong suốt ca làm việc. Việc phân tách khu chế biến thực phẩm sống, rau xanh và bếp nóng giúp nhà ăn duy trì tính một chiều, kiểm soát tốt VSATTP và giữ nhịp ra món ổn định.",
        52,
        228,
        488,
        body,
    )
    highlights = [
        ("Đồng phục đầy đủ", "Mũ trùm, khẩu trang, tạp dề và bao tay là yêu cầu bắt buộc."),
        ("Phân khu rõ ràng", "Khu đồ sống, khu rau xanh và khu bếp nóng được tổ chức tách tuyến."),
        ("Sẵn sàng theo ca", "Nhịp phối hợp giữa sơ chế, nấu và chia suất bám sát giờ phục vụ."),
    ]
    for i, (title, note) in enumerate(highlights):
        x = 52 + i * 162
        rounded(c, x, 104, 146, 70, fill=HexColor("#EEF1EC"), stroke=LINE, radius=12)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 8.5)
        c.drawString(x + 10, 154, title)
        para(c, note, x + 10, 141, 126, small)
    chrome(c, 11, "Con người vận hành")
    c.showPage()

    # 12 - Process 1
    page_bg(c)
    chrome(c, 12, "Quy trình tổ chức nhà ăn")
    section_title(c, "10 / Quy trình", "Tổ chức vận hành<br/><font color='#F0835F'>bếp ăn một chiều.</font>", y=720)
    flow_box(c, 206, 632, 180, 40, "Ban giám đốc", fill=FLOW_AMBER, font_size=13.3)
    flow_box(c, 206, 574, 180, 40, "Phòng sản xuất", fill=FLOW_GOLD, text_color=INK, font_size=12.7)
    arrow_down(c, 296, 632, 614)
    flow_box(c, 34, 506, 150, 40, "Phòng thu mua", fill=FLOW_AMBER, font_size=11.3)
    flow_box(c, 203, 506, 154, 40, "Quản lý cơ sở", fill=FLOW_GOLD, text_color=INK, font_size=11.9)
    flow_box(c, 376, 506, 150, 40, "Kho công ty", fill=FLOW_AMBER, font_size=11.3)
    c.setStrokeColor(FLOW_LINE)
    c.setLineWidth(1.2)
    c.line(296, 574, 296, 554)
    c.line(109, 554, 451, 554)
    arrow_down(c, 109, 554, 546)
    arrow_down(c, 280, 554, 546)
    arrow_down(c, 451, 554, 546)
    flow_box(c, 216, 452, 160, 36, "Bếp trưởng", fill=FLOW_GOLD, text_color=INK, font_size=12.3)
    arrow_down(c, 280, 506, 488)
    flow_box(c, 34, 384, 152, 44, "Bếp chính<br/>Quản lý C1", fill=FLOW_AMBER, font_size=11.2)
    flow_box(c, 203, 384, 152, 44, "Bếp chính<br/>Quản lý C2", fill=FLOW_AMBER, font_size=11.2)
    flow_box(c, 372, 384, 152, 44, "Bếp chính<br/>Quản lý C3", fill=FLOW_AMBER, font_size=11.2)
    arrow_down(c, 296, 452, 428)
    col_w = 118
    col_x = [34, 168, 302, 438]
    groups = [
        ("Tổ thức ăn chính", ["Nhận hàng<br/>thực phẩm", "Rửa & sơ chế", "Chế biến"]),
        ("Tổ rau xanh", ["Nhận hàng<br/>rau củ", "Rửa, lựa<br/>rau xanh", "Hoàn thiện<br/>món phụ"]),
        ("Tổ cơm & chia suất", ["Nhận số lượng<br/>gạo", "Nấu cơm", "Kiểm tra &<br/>ra khay"]),
        ("Tổ vệ sinh", ["Vệ sinh<br/>trong bếp", "Khử khuẩn<br/>dụng cụ", "Hoàn tất<br/>cuối ca"]),
    ]
    c.line(110, 384, 110, 348)
    c.line(279, 384, 279, 360)
    c.line(448, 384, 448, 348)
    c.line(229, 360, 329, 360)
    arrow_down(c, 110, 348, 346)
    arrow_down(c, 229, 360, 346)
    arrow_down(c, 361, 360, 346)
    arrow_down(c, 448, 348, 346)
    for i, (title, steps) in enumerate(groups):
        x = col_x[i]
        flow_box(c, x, 308, col_w, 38, title, fill=FLOW_GOLD, text_color=INK, font_size=9.5)
        for j, step in enumerate(steps):
            y = 252 - j * 54
            flow_box(c, x, y, col_w, 42, step, fill=FLOW_AMBER, font_size=9.5)
            if j == 0:
                arrow_down(c, x + col_w / 2, 308, 294)
            else:
                arrow_down(c, x + col_w / 2, y + 54, y + 42)
        arrow_down(c, x + col_w / 2, 144, 122)
    flow_box(
        c,
        34,
        78,
        522,
        44,
        "PHỤC VỤ KHÁCH HÀNG ĐÚNG GIỜ, ĐÚNG ĐỊNH LƯỢNG VÀ ĐẢM BẢO VSATTP",
        fill=FLOW_GOLD,
        text_color=INK,
        font_size=11.5,
        radius=14,
    )
    chrome(c, 12, "Quy trình tổ chức nhà ăn")
    c.showPage()

    # 13 - Process 2
    page_bg(c)
    chrome(c, 13, "Quy trình kiểm nhận và chế biến")
    section_title(c, "10 / Quy trình", "Chuỗi kiểm soát đầu vào<br/><font color='#F0835F'>đến lưu mẫu sau phục vụ.</font>", y=720)
    flow_box_outline(c, 100, 606, 156, 40, "Ban giám đốc", font_size=12.1)
    flow_box_outline(c, 100, 552, 156, 40, "Phòng sản xuất", font_size=11.6)
    flow_box_outline(c, 100, 498, 156, 40, "Thực đơn", font_size=11.6)
    flow_box_outline(c, 82, 440, 192, 42, "Kế hoạch đặt hàng", font_size=11.6)
    arrow_down(c, 178, 606, 592)
    arrow_down(c, 178, 552, 538)
    arrow_down(c, 178, 498, 482)
    supplier_specs = [(34, "Nhà cung cấp 1"), (127, "Nhà cung cấp 2"), (220, "Nhà cung cấp 3")]
    for x, label in supplier_specs:
        flow_box_outline(c, x, 350, 86, 40, label, font_size=9.1)
    c.setStrokeColor(FLOW_LINE)
    c.setLineWidth(1.1)
    c.line(178, 440, 178, 406)
    c.line(77, 406, 263, 406)
    arrow_down(c, 77, 406, 390)
    arrow_down(c, 170, 406, 390)
    arrow_down(c, 263, 406, 390)
    flow_box_outline(c, 84, 290, 188, 40, "Kiểm tra cảm quan<br/>và ký nhận giao nhận", font_size=10.6)
    c.line(170, 350, 170, 330)
    flow_box_outline(c, 34, 230, 120, 40, "Nhập kho<br/>sản xuất", font_size=9.8)
    flow_box_outline(c, 198, 230, 122, 40, "Trả NCC nếu<br/>không đạt", font_size=9.5)
    arrow_left(c, 154, 178, 250)
    arrow_right(c, 178, 198, 250)
    flow_box_outline(c, 78, 166, 202, 40, "Sơ chế, chế biến thực phẩm", font_size=10.8)
    arrow_down(c, 178, 290, 206)
    flow_box_outline(c, 78, 108, 202, 36, "Chia suất - giao ca", font_size=10.8)
    arrow_down(c, 178, 166, 144)
    flow_box_outline(c, 78, 56, 202, 34, "Lưu mẫu - vệ sinh - phục vụ", font_size=10.2)
    arrow_down(c, 178, 108, 90)
    # Restore the original receiving and vegetable-storage evidence before the preparation stage.
    rounded(c, 326, 526, 230, 112, fill=WHITE, stroke=LINE, radius=16)
    image_cover(c, process_photos["receipt_signoff"], 334, 574, 101, 56, align=(0.52, 0.72))
    image_cover(c, process_photos["veg_storage"], 446, 574, 102, 56, align=(0.50, 0.46))
    compact_caption = ParagraphStyle("process-compact-caption", fontName="QBA-Bold", fontSize=5.7, leading=6.8, textColor=INK, alignment=TA_CENTER)
    para(c, "Ký nhận giao nhận", 334, 571, 101, compact_caption)
    para(c, "Kệ nguyên liệu rau củ", 446, 571, 102, compact_caption)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 8.0)
    c.drawString(338, 551, "Kiểm tra giao nhận & kiểm soát rau củ")
    compact_note = ParagraphStyle("process-compact-note", fontName="QBA", fontSize=6.1, leading=7.6, textColor=MUTED)
    para(c, "Kiểm tra cảm quan, ký nhận và bảo quản nguyên liệu trước khi sơ chế.", 338, 539, 206, compact_note)
    photo_tile(
        c,
        process_photos["food_prep_process"],
        326,
        372,
        230,
        144,
        "Sơ chế, chế biến thực phẩm",
        "Phân khu thực phẩm sống, rau xanh và bếp nóng theo quy trình một chiều.",
        align=(0.52, 0.40),
        title_size=9.2,
        note_size=6.2,
        note_top=21,
    )
    photo_tile(
        c,
        process_photos["meal_portioning_process"],
        326,
        220,
        230,
        144,
        "Chia suất - giao ca",
        "Chia theo định lượng, bảo đảm đúng số lượng và giờ phục vụ mỗi ca.",
        align=(0.5, 0.67),
        title_size=9.2,
        note_size=6.2,
        note_top=21,
    )
    photo_tile(
        c,
        process_photos["retained_samples_process"],
        326,
        92,
        230,
        112,
        "Lưu mẫu sau phục vụ",
        "Niêm phong, ghi nhận và bảo quản mẫu theo quy định ATVSTP.",
        align=(0.5, 0.54),
        title_size=9.2,
        note_size=6.2,
        note_top=21,
    )
    chrome(c, 13, "Quy trình kiểm nhận và chế biến")
    c.showPage()

    # 14 - ATTP
    page_bg(c)
    chrome(c, 14, "Chứng nhận an toàn thực phẩm")
    section_title(c, "11 / Tuân thủ", "An toàn thực phẩm.<br/><font color='#F0835F'>Hồ sơ còn hiệu lực.</font>", y=720)
    rounded(c, 34, 90, 332, 554, fill=WHITE)
    image_contain(c, CERT / "chung-nhan-attp-2024.jpg", 44, 100, 312, 534, pad=2)
    stat(c, 388, 532, 168, "0298/2024", "SỐ CHỨNG NHẬN", LIME)
    stat(c, 388, 428, 168, "04/2027", "GIÁ TRỊ ĐẾN", YELLOW)
    stat(c, 388, 324, 168, "Bếp tập thể", "LOẠI HÌNH", ORANGE)
    para(c, "Cấp cho địa điểm kinh doanh số 02 tại KCN Mỹ Xuân B1 - Tiến Hùng. Bản chính thức sẽ giữ nguyên hình ảnh giấy chứng nhận và thông tin trên văn bản.", 388, 286, 168, small)
    chrome(c, 14, "Chứng nhận an toàn thực phẩm")
    c.showPage()

    # 15 - Training and safety
    page_bg(c)
    chrome(c, 15, "Đào tạo và an toàn lao động")
    section_title(c, "12 / Con người", "Đào tạo định kỳ.<br/><font color='#317A58'>Kỷ luật từ ca làm việc.</font>", y=720)
    stat(c, 34, 566, 160, "23", "NHÂN SỰ TẬP HUẤN ATTP", LIME)
    stat(c, 208, 566, 160, "01/11/2025", "NGÀY TẬP HUẤN", YELLOW)
    stat(c, 382, 566, 174, "09 thẻ", "AN TOÀN LAO ĐỘNG", ORANGE)
    rounded(c, 34, 102, 254, 438, fill=WHITE)
    image_contain(c, CERT / "tap-huan-attp-01-public.jpg", 42, 110, 238, 422, pad=2)
    rounded(c, 306, 102, 250, 438, fill=WHITE)
    image_contain(c, CERT / "tap-huan-attp-02-public.jpg", 314, 110, 234, 422, pad=2)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 82, "Danh sách 23 nhân sự tập huấn ATTP hiển thị ảnh gốc đầy đủ; thẻ an toàn lao động lưu riêng trong hồ sơ chứng từ.")
    chrome(c, 15, "Đào tạo và an toàn lao động")
    c.showPage()

    # 16 - Quality commitment
    page_bg(c, HexColor("#F7FAF8"))
    chrome(c, 16, "Cam kết chất lượng")
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 8.2)
    c.drawString(34, 735, "13 / CAM KẾT CHẤT LƯỢNG")
    premium_card(c, 34, 86, 218, 582, radius=24)
    c.setFillColor(HexColor("#E8F6ED"))
    c.roundRect(58, 614, 94, 22, 11, stroke=0, fill=1)
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 7.2)
    c.drawCentredString(105, 622, "ISO 22000:2018")
    rounded(c, 48, 248, 190, 342, fill=HexColor("#FBFDFB"), stroke=HexColor("#E5EEE8"), radius=20, sw=0.5)
    image_contain_trim(c, quality_certs["iso_qba"], 55, 260, 176, 318, pad=1)
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 8.0)
    c.drawCentredString(143, 208, "Giấy chứng nhận ISO 22000:2018")
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter", 6.6)
    c.drawCentredString(143, 195, "Hệ thống quản lý an toàn thực phẩm")

    header_style = ParagraphStyle("quality-header", fontName="QBA-Inter-Bold", fontSize=23.5, leading=27, textColor=INK)
    para(c, "Hệ thống quản lý<br/>chất lượng", 274, 704, 270, header_style)
    subtitle_style = ParagraphStyle("quality-subtitle", fontName="QBA-Inter", fontSize=9.0, leading=12.8, textColor=MUTED)
    para(c, "Quốc Bình An vận hành theo hệ thống quản lý an toàn thực phẩm ISO 22000:2018 nhằm đảm bảo chất lượng đồng nhất trong toàn bộ quy trình từ nguyên liệu đến suất ăn phục vụ khách hàng.", 274, 638, 278, subtitle_style)

    kpi_cards = [
        ("ISO 22000:2018", "Được chứng nhận"),
        ("Kiểm thực 3 bước", "Thực hiện mỗi ngày"),
        ("Lưu mẫu thực phẩm", "Theo quy định ATVSTP"),
        ("Kiểm soát chất lượng", "Xuyên suốt quy trình"),
    ]
    for i, (title, desc) in enumerate(kpi_cards):
        x = 274 + (i % 2) * 144
        y = 510 - (i // 2) * 84
        quality_kpi_card(c, x, y, 132, 70, title, desc)

    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 10.6)
    c.drawString(274, 392, "Cam kết vận hành")
    commitment_items = [
        "Nguyên liệu có nguồn gốc rõ ràng",
        "Quy trình chế biến khép kín",
        "Đội ngũ được đào tạo định kỳ",
        "Vệ sinh theo tiêu chuẩn ISO",
        "Giao suất ăn đúng thời gian",
        "Truy xuất nguồn gốc khi cần",
    ]
    for i, text in enumerate(commitment_items):
        x = 274 + (i % 2) * 144
        y = 346 - (i // 2) * 42
        commitment_card(c, x, y, 132, 30, text)

    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 11.0)
    c.drawString(274, 214, "Đào tạo & Năng lực nhân sự")
    c.setFillColor(MUTED)
    c.setFont("QBA-Inter", 7.0)
    c.drawString(274, 199, "Chứng chỉ nhận thức ISO của đội ngũ quản lý, lưu cùng hồ sơ năng lực.")
    iso_people = [
        (quality_certs["iso_chinh"], "Nguyễn Quốc Chinh"),
        (quality_certs["iso_thuy"], "Trần Thị Thanh Thuỷ"),
        (quality_certs["iso_quynh"], "Nguyễn Thị Quỳnh"),
        (quality_certs["iso_ha"], "Nguyễn Thị Hà"),
    ]
    for i, (path, name) in enumerate(iso_people):
        x = 274 + (i % 2) * 144
        y = 122 - (i // 2) * 64
        training_certificate_card(c, path, x, y, 132, 54, name)
    chrome(c, 16, "Cam kết chất lượng")
    c.showPage()

    # 17 - Supplier certificates
    page_bg(c)
    chrome(c, 17, "Hồ sơ nhà cung cấp")
    section_title(c, "14 / Nhà cung cấp", "Chứng từ đầu vào<br/><font color='#F0835F'>được lưu cùng hồ sơ.</font>", "Tài liệu nhà cung cấp được trình bày như bằng chứng truy xuất; trạng thái hiệu lực cần đối chiếu theo ngày trên từng giấy.", y=720)
    supplier_cards = [
        (
            extra_certs["supplier_sao_bien"],
            "Sao Biển",
            "Suất ăn chế biến sẵn",
            "Giấy thể hiện hiệu lực đến 13/04/2020 - dùng như tài liệu lưu trữ, cần bản mới nếu tiếp tục công bố.",
            ORANGE,
        ),
        (
            extra_certs["supplier_thuy_duong"],
            "Nguyễn Thị Thuý Dương",
            "Sơ chế, kinh doanh rau củ",
            "Giấy thể hiện hiệu lực đến 12/06/2028 - phù hợp để lưu cùng hồ sơ kiểm soát đầu vào.",
            LIME,
        ),
        (
            extra_certs["supplier_beef_quarantine"],
            "Kiểm dịch Đồng Tháp",
            "Thịt bò - chứng từ vận chuyển",
            "Giấy kiểm dịch sản phẩm động vật, thể hiện hạn đến 17/06/2026 - lưu cùng hồ sơ đầu vào.",
            YELLOW,
        ),
    ]
    for i, (path, title, scope, note, accent) in enumerate(supplier_cards):
        x = 34 + i * 178
        rounded(c, x, 104, 166, 516, fill=WHITE)
        image_contain_trim(c, path, x + 10, 294, 146, 306, pad=2)
        c.setFillColor(accent)
        c.roundRect(x + 14, 252, 66, 18, 9, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 7)
        c.drawCentredString(x + 47, 259, "NHÀ CUNG CẤP")
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 8.6)
        c.drawString(x + 14, 226, title)
        c.setFillColor(MUTED)
        c.setFont("QBA-Bold", 6.8)
        c.drawString(x + 14, 210, scope)
        para(c, note, x + 14, 190, 138, small)
    chrome(c, 17, "Hồ sơ nhà cung cấp")
    c.showPage()

    # 18 - Water and retention
    page_bg(c)
    chrome(c, 18, "Kiểm soát nguồn nước và lưu mẫu")
    section_title(c, "15 / Kiểm soát", "Nguồn nước được kiểm tra.<br/><font color='#F0835F'>Mẫu ăn được lưu lại.</font>", y=720)
    rounded(c, 34, 108, 278, 526, fill=WHITE)
    image_contain(c, CERT / "kiem-nghiem-nuoc-ro-2026.jpg", 44, 118, 258, 506, pad=2)
    stat(c, 334, 524, 222, "18 chỉ tiêu", "THỂ HIỆN TRÊN PHIẾU", ORANGE)
    para(c, "Phiếu kiểm nghiệm nước RO mã 080626-3425 do Viện Pasteur TP.HCM thực hiện. Các kết quả trên trang được đối chiếu với giới hạn tối đa thể hiện trên phiếu và là căn cứ cho kiểm soát nước sử dụng trong bếp.", 334, 486, 222, body)
    photo_tile(
        c,
        process_photos["retained_samples"],
        334,
        306,
        222,
        202,
        "Lưu mẫu sau phục vụ",
        "Mẫu được lưu theo từng bữa ăn, dán nhãn nhận diện để phục vụ truy xuất khi cần.",
        align=(0.5, 0.5),
        title_size=10,
        note_size=6.8,
    )
    rounded(c, 334, 108, 222, 182, fill=WHITE)
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 10.5)
    c.drawString(352, 262, "ĐIỂM KIỂM SOÁT KHI LƯU MẪU")
    checkpoints = [
        "Lưu riêng từng bữa: sáng, trưa, tối.",
        "Ghi rõ ngày, tháng và ca phục vụ trên nhãn.",
        "Bảo quản tách biệt để sẵn sàng truy xuất khi cần.",
    ]
    for i, text in enumerate(checkpoints):
        y = 226 - i * 42
        rounded(c, 350, y, 188, 30, fill=HexColor("#EEF1EC"), stroke=LINE, radius=10)
        c.setFillColor(INK)
        c.setFont("QBA", 7.5)
        c.drawString(360, y + 11, text)
    chrome(c, 18, "Kiểm soát nguồn nước và lưu mẫu")
    c.showPage()

    # Community contribution recognition - placed between retained-sample control and equipment investment.
    page_bg(c, HexColor("#F7FAF8"))
    chrome(c, 43, "Đồng hành cùng cộng đồng")
    section_title(
        c,
        "16 / Cộng đồng",
        "Nấu bằng cái tâm.<br/><font color='#F0835F'>Lan tỏa giá trị sẻ chia.</font>",
        "Phục vụ vì cộng đồng là cách Quốc Bình An chia sẻ nguồn lực thiết thực qua từng bữa ăn tử tế.",
        y=720,
    )

    premium_card(c, 34, 210, 320, 392, radius=24)
    rounded(c, 48, 350, 292, 228, fill=HexColor("#FBFDFB"), stroke=HexColor("#E5EEE8"), radius=18, sw=0.5)
    image_contain(c, ASSETS / "hsnl/cong-dong/bang-khen-cong-dong-2026.png", 50, 352, 288, 224, pad=0)
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 10.5)
    c.drawString(54, 326, "Giấy khen vì cộng đồng")
    community_note = ParagraphStyle("community-note", fontName="QBA-Inter", fontSize=7.5, leading=10.2, textColor=MUTED)
    para(
        c,
        "Ghi nhận đóng góp của Công ty TNHH MTV Quốc Bình An cho bếp ăn từ thiện Bệnh viện Tâm thần Tiền Giang năm 2025.",
        54,
        308,
        276,
        community_note,
    )

    premium_card(c, 376, 412, 180, 190, radius=20, fill=INK, stroke=HexColor("#49675F"))
    c.setFillColor(YELLOW)
    c.roundRect(394, 562, 88, 18, 9, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 6.7)
    c.drawCentredString(438, 568, "CHIA SẺ LỢI ÍCH")
    c.setFillColor(WHITE)
    c.setFont("QBA-Inter-Bold", 13.2)
    c.drawString(394, 528, "Cùng nhau")
    c.drawString(394, 510, "làm điều tốt.")
    community_dark = ParagraphStyle("community-dark", fontName="QBA-Inter", fontSize=7.6, leading=10.5, textColor=HexColor("#E6F1E9"))
    para(
        c,
        "Đồng hành cùng bếp ăn từ thiện, QBA góp phần mang đến sự chăm lo thiết thực cho người bệnh và cộng đồng.",
        394,
        478,
        142,
        community_dark,
    )

    premium_card(c, 376, 210, 180, 180, radius=20)
    c.setFillColor(GREEN)
    c.roundRect(394, 350, 96, 18, 9, stroke=0, fill=1)
    c.setFillColor(WHITE)
    c.setFont("QBA-Inter-Bold", 6.7)
    c.drawCentredString(442, 356, "PHỤC VỤ CỘNG ĐỒNG")
    c.setFillColor(INK)
    c.setFont("QBA-Inter-Bold", 13.0)
    c.drawString(394, 314, "Tử tế từ")
    c.drawString(394, 296, "những điều gần gũi.")
    para(
        c,
        "Mỗi phần ăn được chuẩn bị với sự trân trọng, trách nhiệm và mong muốn lan tỏa giá trị bền vững.",
        394,
        264,
        142,
        small,
    )

    rounded(c, 34, 76, 522, 108, fill=HexColor("#E8F3EA"), stroke=HexColor("#D3E5D8"), radius=20, sw=0.7)
    c.setFillColor(GREEN)
    c.setFont("QBA-Inter-Bold", 8.0)
    c.drawString(56, 153, "GIÁ TRỊ CỐT LÕI")
    community_quote = ParagraphStyle("community-quote", fontName="QBA-Inter-Bold", fontSize=16.2, leading=20, textColor=INK)
    para(c, "“Nấu bằng cái tâm” vẫn luôn là giá trị cốt lõi của Quốc Bình An.", 56, 134, 456, community_quote)
    chrome(c, 43, "Đồng hành cùng cộng đồng")
    c.showPage()

    # 19 - Equipment
    hero_page_bg(c, hero_bgs, "equipment", overlay_alpha=0.30)
    chrome(c, 19, "Đầu tư thiết bị", dark=True)
    section_title(c, "16 / Cải tiến", "Thiết bị tốt hơn.<br/><font color='#FFD569'>Bữa ăn đúng giờ hơn.</font>", dark=True, y=720)
    hero_corner_logo(c)
    para(c, "Giám đốc Nguyễn Quốc Chinh trực tiếp theo dõi, cập nhật và thay đổi máy móc nhằm rút ngắn thời gian xử lý, giảm thao tác thủ công và giữ bữa ăn sẵn sàng đúng ca.", 34, 625, 520, body_dark)
    photo_tile(
        c,
        process_photos["slicer_prep"],
        34,
        194,
        250,
        392,
        "Thiết bị thái - sơ chế",
        "Khung lớn giữ rõ người vận hành, áo Quốc Bình An và khu vực máy cắt.",
        align=(0.5, 0.5),
        dark=True,
        title_size=10.6,
        note_size=7.0,
    )
    photo_tile(
        c,
        process_photos["hot_kitchen"],
        306,
        386,
        250,
        200,
        "Bếp nóng công suất lớn",
        "Dàn bếp và chảo inox đồng bộ, phù hợp sản lượng lớn.",
        align=(0.50, 0.62),
        dark=True,
        title_size=9.8,
        note_size=6.6,
    )
    photo_tile(
        c,
        process_photos["tray_washer"],
        306,
        194,
        250,
        180,
        "Máy rửa khay chuyên dụng",
        "Rút ngắn thời gian chuẩn bị cho chuyển ca, tăng tốc thu hồi và vệ sinh khay.",
        align=(0.55, 0.54),
        dark=True,
        title_size=9.2,
        note_size=6.2,
    )
    rounded(c, 34, 84, 522, 82, fill=INK_2, stroke=HexColor("#49675F"), radius=14)
    commitments = [
        "Rút ngắn thời gian sơ chế và hoàn thiện món ăn.",
        "Giảm thao tác thủ công, giữ nhịp ra món ổn định.",
        "Tăng khả năng vệ sinh, bảo quản và tổ chức bếp một chiều.",
    ]
    for i, text in enumerate(commitments):
        x = 52 + i * 166
        rounded(c, x, 102, 148, 44, fill=HexColor("#274C44"), stroke=HexColor("#49675F"), radius=10)
        para(c, text, x + 10, 133, 128, small_dark)
    chrome(c, 19, "Đầu tư thiết bị", dark=True)
    c.showPage()

    # 20 - Meal structure
    page_bg(c)
    chrome(c, 20, "Cơ cấu suất ăn")
    section_title(c, "17 / Thực đơn", "Một khay ăn.<br/><font color='#F0835F'>Đủ thành phần cần thiết.</font>", y=720)
    rounded(c, 30, 216, 332, 424, fill=WHITE)
    image_contain(c, meals["structure"], 42, 228, 308, 400, pad=2)
    components = [
        ("01", "Món mặn sốt"),
        ("02", "Đậu hũ thịt bằm"),
        ("03", "Rau cải xanh"),
        ("04", "Cơm trắng"),
        ("05", "Canh bí xanh"),
    ]
    for i, (num, name) in enumerate(components):
        x = 380
        y = 552 - i * 66
        c.setFillColor([LIME, YELLOW, ORANGE][i % 3])
        c.circle(x + 20, y + 20, 22, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 9.4)
        c.drawCentredString(x + 20, y + 16, num)
        c.setFont("QBA-Bold", 12.2)
        c.drawString(x + 54, y + 16, name)
    para(c, "Cơ cấu món có thể điều chỉnh theo ngân sách, tính chất công việc và khẩu vị từng nhà máy. Mỗi khay giữ nguyên nguyên tắc: đủ năng lượng, dễ ăn, sạch và nóng.", 372, 210, 184, meal_desc)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 90, "Hình ảnh khẩu phần minh họa; giá bán và định lượng chi tiết sẽ được xác nhận trước phát hành.")
    chrome(c, 20, "Cơ cấu suất ăn")
    c.showPage()

    # 21 - Vegetarian tray
    page_bg(c)
    chrome(c, 21, "Khay chay đầy đủ")
    section_title(c, "18 / Khay chay", "Thực đơn chay<br/><font color='#F0835F'>đủ món, dễ ăn.</font>", "Một lựa chọn riêng cho khách hàng cần khẩu phần thanh đạm nhưng vẫn rõ cơ cấu món, canh, trái cây và sữa.", y=720)
    rounded(c, 34, 142, 318, 496, fill=WHITE)
    image_contain(c, meals["vegetarian"], 48, 164, 290, 452, pad=2)
    rounded(c, 374, 350, 182, 288, fill=INK, stroke=HexColor("#476D62"), radius=20)
    c.setFillColor(YELLOW)
    c.setFont("QBA-Bold", 9)
    c.drawString(394, 602, "CẤU TRÚC KHAY CHAY")
    veg_items = [
        ("01", "Món kho rau củ"),
        ("02", "Rau bắp cải xào"),
        ("03", "Nấm và rau xanh"),
        ("04", "Canh rau củ"),
        ("05", "Trái cây tươi"),
        ("06", "Sữa đậu nành"),
    ]
    for i, (num, item) in enumerate(veg_items):
        y = 558 - i * 31
        c.setFillColor([LIME, YELLOW, ORANGE][i % 3])
        c.roundRect(394, y - 8, 26, 18, 9, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 6.4)
        c.drawCentredString(407, y - 2, num)
        c.setFillColor(WHITE)
        c.setFont("QBA-Bold", 9.4)
        c.drawString(430, y - 2, item)
    rounded(c, 374, 144, 182, 176, fill=HexColor("#EEF1EC"))
    c.setFillColor(INK)
    c.setFont("QBA-Bold", 11)
    c.drawString(394, 278, "Gợi ý triển khai")
    para(c, "Khay chay có thể dùng theo lịch đặt trước hoặc theo nhóm lao động cần khẩu phần riêng. Món được giữ tách vị, dễ nhận diện và thuận tiện kiểm soát định lượng.", 394, 252, 138, small)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    chrome(c, 21, "Khay chay đầy đủ")
    c.showPage()

    # 22 - Menu tiers
    page_bg(c)
    chrome(c, 22, "Thực đơn linh hoạt")
    section_title(c, "19 / Thực đơn", "Đổi món theo tuần.<br/><font color='#F0835F'>Điều chỉnh theo nhu cầu.</font>", y=720)
    tiers = [
        (meals["standard"], "Suất tiêu chuẩn", "Cân đối món mặn, rau, canh và tráng miệng"),
        (meals["energy"], "Suất tăng năng lượng", "Linh hoạt định lượng và cách kết hợp món"),
        (meals["expert"], "Suất chuyên gia/sự kiện", "Chú trọng nguyên liệu và cách trình bày"),
    ]
    tier_cards = [(34, 330, 250, 304), (306, 330, 250, 304), (34, 130, 522, 174)]
    for i, (path, name, desc) in enumerate(tiers):
        x, y, w, h = tier_cards[i]
        rounded(c, x, y, w, h, fill=WHITE)
        if i < 2:
            image_cover(c, path, x + 10, y + 102, w - 20, 188, align=(0.5, 0.5))
            text_x, text_y, text_w = x + 16, y + 64, w - 32
        else:
            image_contain(c, path, x + 12, y + 14, 320, h - 28, pad=2)
            text_x, text_y, text_w = x + 356, y + 116, 150
        c.setFillColor([ORANGE, LIME, YELLOW][i])
        c.roundRect(text_x, text_y + 18, 76, 20, 10, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 8)
        c.drawCentredString(text_x + 38, text_y + 25, f"PHƯƠNG ÁN {i + 1}")
        c.setFont("QBA-Bold", 12.4)
        c.drawString(text_x, text_y - 8, name)
        para(c, desc, text_x, text_y - 32, text_w, meal_desc)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 88, "Tên nhóm thực đơn, đơn giá và chu kỳ luân phiên sẽ được xác nhận trước phát hành.")
    chrome(c, 22, "Thực đơn linh hoạt")
    c.showPage()

    # 23-26 - Price menu gallery. Keep these slot aliases separate from the existing
    # project pages so saved edits to the established profile pages remain intact.
    menu_card_style = ParagraphStyle(
        "menu-card-dishes",
        fontName="QBA",
        fontSize=7.45,
        leading=10.15,
        textColor=MUTED,
    )

    def menu_price_page(
        page_alias: int,
        price: str,
        accent,
        samples: list[tuple[str, str, Path, list[str]]],
    ) -> None:
        page_bg(c, HexColor("#F7FAF8"))
        chrome(c, page_alias, "Thực đơn theo đơn giá")
        section_title(
            c,
            "19 / Thực đơn",
            f"Mẫu suất ăn<br/><font color='#{accent.hexval()[2:].upper()}'>{price}</font>",
            "Hình ảnh khay và tên món được giữ nguyên theo website Quốc Bình An.",
            y=690,
        )
        for index, (sample, day, path, dishes) in enumerate(samples):
            x, y, w, h = 34, 452 - index * 158, 522, 144
            premium_card(c, x, y, w, h, radius=20, fill=WHITE, stroke=HexColor("#E0E8E2"))
            rounded(c, x + 12, y + 12, 168, 120, fill=HexColor("#F1F3F0"), stroke=HexColor("#E5E9E6"), radius=14, sw=0.5)
            # A shallow cover crop removes only the neutral studio surround and keeps the tray prominent.
            image_cover(c, path, x + 16, y + 16, 160, 112, align=(0.5, 0.54))
            c.setFillColor(INK)
            c.setFont("QBA-Bold", 11)
            c.drawString(x + 198, y + 112, sample)
            c.setFillColor(GREEN)
            c.setFont("QBA-Bold", 7.2)
            c.drawString(x + 198, y + 98, day.upper())
            pill(c, price, x + 432, y + 106, fill=accent, fg=INK, width=72)
            para(c, "<br/>".join(f"- {dish}" for dish in dishes), x + 198, y + 83, 304, menu_card_style)

    menu_price_page(
        32,
        "23.000Đ",
        ORANGE,
        [
            (
                "MẪU 01 / 06",
                "THỨ 2",
                ASSETS / "menu/qba-23k-mon-ga-luoc-la-chanh-no-milk-v2.png",
                ["Tôm chiên ram hành / Cá hồng kho cà", "Cải chua kho thịt", "Cải ngọt xào", "Canh bầu"],
            ),
            (
                "MẪU 02 / 06",
                "THỨ 3",
                ASSETS / "menu/qba-23k-tue-ca-ba-sa-v3.jpg",
                ["Cá sa ba kho cải chua / Thịt kho mắm ruốc", "Trứng ốp la / Trứng luộc", "Dưa leo ăn sống", "Canh chua rau muống"],
            ),
            (
                "MẪU 03 / 06",
                "THỨ 4",
                ASSETS / "menu/qba-23k-thu-gakho-sa-no-milk-v2.png",
                ["Ếch chiên mắm / Cá lóc kho tiêu", "Khổ hoa kho thịt", "Bắp cải xào", "Canh bí đỏ"],
            ),
        ],
    )
    c.showPage()

    menu_price_page(
        33,
        "24.000Đ",
        LIME,
        [
            (
                "MẪU 04 / 06",
                "THỨ 5",
                ASSETS / "menu/qba-24k-actual-sample-04-web.jpg",
                ["Cơm trắng", "Cá chiên giòn", "Thịt heo xào hành tây cà rốt", "Rau muống xào tỏi", "Canh khoai mỡ"],
            ),
            (
                "MẪU 05 / 06",
                "THỨ 6",
                ASSETS / "menu/qba-24k-actual-sample-05-web.jpg",
                ["Cơm trắng", "Thịt heo xào thơm", "Thịt heo xào sả ớt", "Bắp cải xào cà rốt", "Canh cải xanh"],
            ),
            (
                "MẪU 06 / 06",
                "THỨ 7",
                ASSETS / "menu/qba-24k-actual-sample-06-web.jpg",
                ["Cơm trắng", "Chả cá kho thơm", "Ba rọi kho tiêu", "Canh rau ngót", "Đu đủ chín"],
            ),
        ],
    )
    c.showPage()

    menu_price_page(
        34,
        "25.000Đ",
        YELLOW,
        [
            (
                "MẪU 01 / 06",
                "THỨ 2",
                ASSETS / "menu/qba-25k-actual-mon.jpg",
                ["Đùi gà nướng", "Đậu hũ kho hành", "Dưa leo", "Canh bí đao", "Dưa hấu"],
            ),
            (
                "MẪU 02 / 06",
                "THỨ 3",
                ASSETS / "menu/qba-25k-actual-tue.jpg",
                ["Cá chiên sả ớt", "Bò xào rau cải", "Dưa leo", "Canh bầu thịt bằm"],
            ),
            (
                "MẪU 03 / 06",
                "THỨ 4",
                ASSETS / "menu/qba-25k-actual-wed.jpg",
                ["Cá kèo kho tiêu", "Trứng chiên", "Su su xào", "Canh rau ngót", "Chuối"],
            ),
        ],
    )
    c.showPage()

    menu_price_page(
        35,
        "40.000Đ",
        GREEN,
        [
            (
                "MẪU 01 / 06",
                "THỨ 2",
                ASSETS / "menu/qba-40k-chinese-mon.jpg",
                ["Tôm rim xì dầu kiểu Hoa", "Gà kho nấm đông cô", "Bò xào ớt xanh", "Giá hẹ xào tỏi", "Dưa hấu"],
            ),
            (
                "MẪU 02 / 06",
                "THỨ 3",
                ASSETS / "menu/qba-40k-chinese-tue.jpg",
                ["Thịt viên sốt tương kiểu Hoa", "Gà kho nấm", "Bò xào ớt chuông", "Bắp cải xào xì dầu", "Chôm chôm"],
            ),
            (
                "MẪU 04 / 06",
                "THỨ 5",
                ASSETS / "menu/qba-40k-chinese-thu.jpg",
                ["Cá chiên ngũ vị", "Gà xào sốt cay", "Bò xào ớt chuông", "Cải xanh xào dầu hào", "Nhãn"],
            ),
        ],
    )
    c.showPage()

    # 27-33 - Text-only QBA menu samples. The supplied meal names are retained,
    # while client names, client codes, and source-sheet dates are intentionally omitted.
    def menu_sample_page_start(page_alias: int, sample: str, title: str, accent=GREEN) -> None:
        page_bg(c, HexColor("#F7FAF8"))
        chrome(c, page_alias, "Thực đơn mẫu QBA")
        c.setFillColor(ORANGE)
        c.setFont("QBA-Bold", 8.0)
        c.drawString(34, 752, "19 / THỰC ĐƠN MẪU")
        c.setFillColor(INK)
        c.setFont("QBA-Bold", 21.5)
        c.drawString(34, 718, title)
        c.setFillColor(MUTED)
        c.setFont("QBA", 8.2)
        c.drawString(34, 697, "Danh mục món luân phiên theo ngày, trình bày không kèm tên khách hàng.")
        menu_table_label(c, sample, 426, 746, accent=accent)

    days_7 = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
    days_6 = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"]

    menu_sample_page_start(36, "Mẫu 01 / 07", "Bữa sáng & món Việt", YELLOW)
    menu_table_label(c, "Bữa sáng", 34, 660, accent=YELLOW)
    menu_week_table(
        c,
        34,
        644,
        522,
        days_7,
        [
            ("Món 1", ["Khoai luộc", "Sủi cảo", "Bánh cá đậu xanh", "Bắp luộc", "Bánh đa lợn", "Xôi vị", "Bánh tiêu"], 25),
            ("Món 2", ["Mỳ trộn xá xíu<br/>trứng cút", "Bún riêu", "Bánh cuốn thịt chả", "Mỳ gà tiềm<br/>nấm đông cô", "Bún bò Huế", "Hủ tiếu thập cẩm", "Mỳ xào bò"], 25),
            ("Đồ uống", ["Cà phê sữa", "Tàu hủ", "Sữa đậu nành nóng", "Sữa Fami", "Sữa Milo", "Cà phê", "Sữa mè đen"], 25),
        ],
        accent=YELLOW,
        label_width=64,
        font_size=5.85,
    )
    menu_table_label(c, "Món Việt", 34, 522, accent=GREEN)
    menu_week_table(
        c,
        34,
        506,
        522,
        days_7,
        [
            ("Mặn 1", ["Cá chiên", "Sườn non<br/>kho khóm", "Gà kho sả", "Thịt ba rọi<br/>kho sả", "Cá kho cà", "Cốt lết ram", "Thịt rim tôm"], 33),
            ("Mặn 2", ["Thịt bò xào<br/>sả ớt", "Trứng cuộn", "Cá nấu sốt<br/>thịt bằm", "Khổ qua hầm", "Thịt xào<br/>đậu que", "Trứng hấp", "Tim xào giá hẹ"], 33),
            ("Chay 1", ["Đậu hũ xóc sả", "Chả kho rau củ", "Đậu hũ kho tương<br/>+ rau củ", "Bún đậu hũ", "Đậu hũ chiên<br/>sả ớt", "Bò lát kho sả", "Sườn non kho sả"], 33),
            ("Chay 2", ["Đậu hũ sốt tương", "Đậu hũ xào giá", "Đậu bắp xào<br/>lát chay", "Chả giò", "Nấm đông cô<br/>kho sả", "Nấm xào rau củ", "Chả xào rau củ"], 33),
            ("Đêm 1", ["Sườn non<br/>kho khóm", "Cá chiên", "Hủ tiếu", "Ba rọi chiên<br/>sả ớt", "Tép ram tỏi ớt", "Mỳ bò", "Gà xào sả ớt"], 33),
            ("Đêm 2", ["Thịt bằm<br/>xào cà nấu", "Trứng hấp", "", "Trứng ốp la", "Khổ qua hầm", "", "Thịt xào rau củ"], 33),
        ],
        accent=GREEN,
        label_width=64,
        font_size=5.8,
    )
    c.showPage()

    menu_sample_page_start(37, "Mẫu 02 / 07", "Thực đơn theo ca", ORANGE)
    menu_table_label(c, "Ca sáng", 34, 657, accent=ORANGE)
    menu_week_table(
        c,
        34,
        641,
        522,
        days_7,
        [
            ("Món chính", ["Cá kho", "Sườn chiên<br/>nước mắm", "Gà hấp sốt<br/>nước tương", "Cá diêu hồng<br/>kho cà / cá chiên", "Cốt lết ram", "Thịt kho tôm", "Cá basa kho /<br/>cá biển chiên"], 25),
            ("Món phụ", ["Đậu hũ nhồi", "Trứng xào<br/>khổ qua", "Thịt xào", "Bò xào cần hành", "Chả cá viên chiên<br/>nước mắm", "Tim xào", "Bò xào"], 25),
            ("Rau", ["Cải ngọt xào", "Cải thảo xào", "Dưa leo xào", "Rau muống xào", "Giá hẹ muối chua", "Bầu xào", "Dưa leo xào"], 25),
            ("Canh", ["Canh chua", "Canh bầu", "Canh củ", "Canh xà lách xoong", "Canh chua", "Canh khổ qua", "Canh cải thảo"], 25),
        ],
        accent=ORANGE,
        label_width=54,
        font_size=5.15,
    )
    menu_table_label(c, "Ca chiều", 34, 503, accent=YELLOW)
    menu_week_table(
        c,
        34,
        487,
        522,
        days_7,
        [
            ("Món chính", ["Ba rọi kho<br/>sả ớt", "Gà kho sả", "Cá bạc má<br/>kho hành", "Ba rọi kho sả", "Ếch kho sả ớt<br/>/ cá kho", "Gà chiên<br/>nước mắm", "Sườn chiên<br/>nước mắm"], 25),
            ("Món phụ", ["Chả cá chiên", "Gan heo xào<br/>cần hành", "Khổ qua hầm", "Trứng hấp<br/>thịt bằm", "Cà tím sốt<br/>thịt bằm", "Thịt kho củ", "Đậu hũ kho<br/>nấm thơm"], 25),
            ("Rau", ["Bắp cải xào", "Rau muống xào", "Su su xào cà rốt", "Cải thảo xào", "Đậu que xào", "Cải ngọt luộc", "Cải thảo xào"], 25),
            ("Canh", ["Canh đu đủ", "Canh bí đỏ", "Canh chua", "Canh rau ngót", "Canh bắp cải", "Canh khoai mỡ", "Canh chua"], 25),
        ],
        accent=YELLOW,
        label_width=54,
        font_size=5.15,
    )
    menu_table_label(c, "Ca tối", 34, 349, accent=GREEN)
    menu_week_table(
        c,
        34,
        333,
        522,
        days_7,
        [
            ("Món chính", ["Ba rọi chiên sả", "Gà kho gừng", "Cá diêu hồng kho<br/>/ cá chiên", "Thịt kho tiêu", "Cánh gà chiên bột", "Cá hường chiên", "Cốt lết ram"], 25),
            ("Món phụ", ["Đậu hũ kho<br/>nấm thơm", "Thịt, chả cá xào", "Bò xào cần hành", "Trứng cuộn thịt bằm<br/>/ luộc + kho quẹt", "Cải chua xào thịt", "Khổ qua hầm", "Trứng xào cà"], 25),
            ("Rau", ["Rau muống xào", "Cải ngọt xào", "Bắp cải", "Rau muống xào", "Đậu đũa xào", "Su su xào", "Bắp cải xào"], 25),
            ("Canh", ["Canh chua", "Canh cà chua trứng", "Canh bí đỏ", "Canh chua", "Canh cải thảo", "Canh cải xanh", "Canh chua"], 25),
        ],
        accent=GREEN,
        label_width=54,
        font_size=5.0,
    )
    menu_table_label(c, "Khuya", 34, 195, accent=HexColor("#5BA2B4"))
    menu_week_table(
        c,
        34,
        179,
        522,
        days_7,
        [("Món nước", ["Hủ tiếu sườn<br/>/ cháo sườn", "Bún bò<br/>/ mỳ bò", "Hủ tiếu thập cẩm<br/>/ cháo lòng", "Bún thái<br/>/ mỳ lẩu thái", "Bánh canh giò heo<br/>/ phở gà", "Cháo gà", "Bún riêu cua<br/>/ mỳ thịt, chả"], 38)],
        accent=HexColor("#5BA2B4"),
        label_width=54,
        font_size=5.1,
    )
    c.showPage()

    menu_sample_page_start(38, "Mẫu 03 / 07", "Trưa & tăng ca - phương án A", LIME)
    menu_table_label(c, "Bữa trưa", 34, 657, accent=LIME)
    menu_week_table(
        c,
        34,
        641,
        522,
        days_6,
        [
            ("Món mặn", ["Sườn chua ngọt<br/>/ cá kho cà", "Tôm kho thịt<br/>/ cá đồng chiên", "Đùi gà chiên<br/>nước mắm / cá riêu hồng", "Thịt kho trứng<br/>/ cá nục kho thơm", "Thịt kho tôm<br/>/ cá ngừ kho thơm", "Gà kho lá chanh<br/>/ cá hồng kho cà"], 44),
            ("Xào phụ", ["Mực xào hành cần", "Đậu hũ kho<br/>thơm nấm", "Cải chua xào thịt", "Gỏi gà bắp cải", "Đậu hũ nhồi thịt<br/>sốt cà", "Khổ qua xào trứng"], 31),
            ("Rau", ["Dưa leo + bắp cải", "Cải thảo xào", "Su su", "Giá hẹ muối chua", "Giá xào cải ngọt", "Rau muống xào tỏi"], 28),
            ("Canh", ["Canh chua bạc hà", "Canh rau dền", "Canh rau ngót", "Canh bí đỏ", "Canh bí xanh", "Canh cải thảo"], 28),
            ("Trái cây", ["Theo mùa", "Theo mùa", "Theo mùa", "Theo mùa", "Theo mùa", "Theo mùa"], 25),
        ],
        accent=LIME,
        font_size=6.0,
    )
    menu_table_label(c, "Tăng ca", 34, 444, accent=ORANGE)
    menu_week_table(
        c,
        34,
        428,
        522,
        days_6,
        [
            ("Món mặn", ["Cánh gà chiên<br/>nước mắm / cá chiên", "Bún riêu", "Hủ tiếu", "Thịt xá xíu<br/>/ cá khô đù", "Bún bò", ""], 39),
            ("Xào phụ", ["Khổ qua nhồi thịt", "", "", "Bún gạo xào", "", ""], 27),
            ("Rau", ["Bầu luộc", "", "", "Rau muống xào tỏi", "", ""], 27),
            ("Canh", ["Canh cải xanh", "", "", "Canh cà chua", "", ""], 27),
            ("Trái cây", ["Theo mùa", "", "", "Theo mùa", "", ""], 24),
        ],
        accent=ORANGE,
        font_size=6.0,
    )
    c.showPage()

    menu_sample_page_start(39, "Mẫu 04 / 07", "Trưa & tăng ca - phương án B", YELLOW)
    menu_table_label(c, "Bữa trưa", 34, 657, accent=YELLOW)
    menu_week_table(
        c,
        34,
        641,
        522,
        days_6,
        [
            ("Món mặn", ["Sườn cốt lết<br/>/ cá khô đù chiên", "Bún bò", "Hủ tiếu", "Thịt luộc rau thơm<br/>/ cá khô đù chiên", "Bún riêu", "Sườn chua ngọt<br/>/ cá ngừ kho thơm"], 44),
            ("Xào phụ", ["Bún tươi nước mắm", "", "", "Bún gạo xào", "", ""], 31),
            ("Rau", ["Giá hẹ xào", "", "", "Dưa leo", "", ""], 28),
            ("Canh", ["Rau ngót", "", "", "Canh chua bạc hà", "", ""], 28),
            ("Trái cây", ["Theo mùa", "", "", "Theo mùa", "", ""], 25),
        ],
        accent=YELLOW,
        font_size=6.0,
    )
    menu_table_label(c, "Tăng ca", 34, 444, accent=GREEN)
    menu_week_table(
        c,
        34,
        428,
        522,
        days_6,
        [
            ("Món chính", ["Sườn cốt lết<br/>/ cá khô đù chiên", "Bún bò", "Hủ tiếu", "Thịt luộc rau thơm<br/>/ cá khô đù chiên", "Bún riêu", ""], 39),
            ("Xào phụ", ["Bún tươi nước mắm", "", "", "Bún gạo xào", "", ""], 27),
            ("Rau", ["Giá hẹ xào", "", "", "Dưa leo", "", ""], 27),
            ("Canh", ["Rau ngót", "", "", "Canh chua bạc hà", "", ""], 27),
            ("Trái cây", ["Theo mùa", "", "", "Theo mùa", "", ""], 24),
        ],
        accent=GREEN,
        font_size=6.0,
    )
    c.showPage()

    menu_sample_page_start(40, "Mẫu 05 / 07", "Trưa & tăng ca - phương án C", ORANGE)
    menu_table_label(c, "Bữa trưa", 34, 657, accent=ORANGE)
    menu_week_table(
        c,
        34,
        641,
        522,
        days_6,
        [
            ("Món mặn", ["Gà kho rau răm<br/>/ cá kho cà", "Thịt kho tôm<br/>/ cá hồng kho", "Cánh gà chiên bột<br/>/ cá nục kho cà", "Thịt kho trứng<br/>/ cá kho", "Sườn kho chua ngọt<br/>/ cá biển chiên", "Ba rọi chiên sả<br/>/ cá hồng kho cà"], 44),
            ("Xào phụ", ["Cải chua xào thịt", "Gỏi gà tai heo<br/>chả lụa", "Bò xào ớt chuông", "Đậu hũ chiên sả<br/>xào thập cẩm nấm", "Chả cá chiên sốt tương<br/>tỏi mỡ hành", "Khổ qua xào trứng"], 31),
            ("Rau", ["Bắp cải xào", "Rau muống xào", "Giá hẹ muối chua", "Rau muống xào", "Rau muống xào", "Cải ngọt"], 28),
            ("Canh", ["Bí xanh", "Canh bí xanh", "Canh rau má", "Canh bầu", "Canh chua bạc hà", "Canh rau tơi"], 28),
            ("Trái cây", ["Theo mùa", "Theo mùa", "Theo mùa", "Theo mùa", "Theo mùa", "Theo mùa"], 25),
        ],
        accent=ORANGE,
        font_size=5.85,
    )
    menu_table_label(c, "Tăng ca", 34, 444, accent=LIME)
    menu_week_table(
        c,
        34,
        428,
        522,
        days_6,
        [
            ("Món chính", ["Thịt xá xíu<br/>/ cá khô đù", "Bún bò<br/>/ bún riêu cua", "Hủ tiếu", "Thịt luộc rau thơm<br/>/ cá khô đù chiên", "Bún riêu<br/>/ bún bò", ""], 39),
            ("Xào phụ", ["Trứng ốp la", "", "", "Bún gạo xào", "", ""], 27),
            ("Rau", ["Cải ngọt xào giá", "", "", "Bắp cải", "", ""], 27),
            ("Canh", ["Canh bầu", "", "", "Canh cà chua", "", ""], 27),
            ("Trái cây", ["Theo mùa", "", "", "Theo mùa", "", ""], 24),
        ],
        accent=LIME,
        font_size=6.0,
    )
    c.showPage()

    menu_sample_page_start(41, "Mẫu 06 / 07", "Thực đơn chay theo tuần", GREEN)
    menu_table_label(c, "Buổi sáng", 34, 657, accent=GREEN)
    menu_week_table(
        c,
        34,
        641,
        522,
        days_7,
        [
            ("Món 1", ["Đậu hũ kho khóm", "Ruột heo ram sả ớt", "Đậu hũ tứ xuyên", "Bóng cá sốt tương", "Chả kho tiêu", "Đậu hũ chiên sả", "Heo quay sốt tương"], 43),
            ("Món 2", ["Mướp + ớt + giá<br/>xào nấm", "Bò lát + dưa leo +<br/>cà chua + khóm", "Mỳ xào rau củ<br/>+ chả sợi", "Chả kho dưa leo", "Đậu bắp, đậu bún<br/>sốt thịt bằm", "Bò lát kho củ", "Chả sợi xào cải<br/>+ ớt chuông"], 43),
        ],
        accent=GREEN,
        label_width=64,
        font_size=5.7,
    )
    menu_table_label(c, "Buổi trưa", 34, 514, accent=YELLOW)
    menu_week_table(
        c,
        34,
        498,
        522,
        days_7,
        [
            ("Món 1", ["Heo quay sốt tương", "Sườn non chiên giòn", "Đùi gà kho sả ớt", "Đậu hũ sốc xả ớt", "Cá thu kho cà", "Sườn chay chiên giòn", "Đậu hũ kho tương"], 48),
            ("Món 2", ["Bắp cải + củ đỏ<br/>+ chả kho tương", "Củ quả kho<br/>tương nấm", "Cà tím + khoai tây<br/>sốt thịt bằm", "Rau củ xào nấm", "Đậu hũ xào giá hẹ<br/>+ ớt", "Nấm kho khổ hoa", "Nấm xào cà tím<br/>+ khoai tây"], 48),
        ],
        accent=YELLOW,
        label_width=64,
        font_size=5.7,
    )
    c.showPage()

    menu_sample_page_start(42, "Mẫu 07 / 07", "Sáng, món nước & buổi tối", HexColor("#5BA2B4"))
    menu_table_label(c, "Buổi sáng", 34, 657, accent=HexColor("#5BA2B4"))
    menu_week_table(
        c,
        34,
        641,
        522,
        days_7,
        [
            ("Món 1", ["Sườn kho", "Cá chiên", "Gà kho sả", "Ba rọi chiên", "Cá kho", "Thịt ram tôm", "Thịt kho tôm<br/>/ tôm ram"], 38),
            ("Món 2", ["Cà chua xào trứng", "Khổ qua hầm", "Tim heo xào", "Đậu hũ kho<br/>thơm nấm", "Thịt xào rau củ", "Mề gà xào", "Gan heo xào<br/>hành cần"], 38),
        ],
        accent=HexColor("#5BA2B4"),
        label_width=64,
        font_size=5.8,
    )
    menu_table_label(c, "Món nước", 34, 524, accent=ORANGE)
    menu_week_table(
        c,
        34,
        508,
        522,
        days_7,
        [("Món nước", ["Bún riêu", "Bún bò", "Hủ tiếu", "Bánh canh", "Bún chả cá thịt", "Hủ tiếu sườn", "Gà chiên nước mắm<br/>/ thịt kho củ"], 40)],
        accent=ORANGE,
        label_width=64,
        font_size=5.8,
    )
    menu_table_label(c, "Buổi tối", 34, 427, accent=GREEN)
    menu_week_table(
        c,
        34,
        411,
        522,
        days_7,
        [
            ("Món 1", ["Ba rọi chiên sả", "Gà chiên nước mắm", "Sườn kho coca", "Cá diêu hồng kho<br/>/ gà kho sả", "Cốt lết ram mặn", "Ếch kho sả ớt", "Cá biển chiên<br/>/ ba rọi kho"], 38),
            ("Món 2", ["Tim heo xào<br/>hành cần", "Thịt xào đậu đũa", "Khổ qua hầm", "Bò xào chua ngọt", "Trứng hấp", "Cải chua xào thịt", "Đậu hũ nhồi thịt"], 38),
        ],
        accent=GREEN,
        label_width=64,
        font_size=5.8,
    )
    c.showPage()

    # Expert Chinese-palate menu. Keep the supplied dish names while omitting
    # the source-sheet date and client references, consistent with this section.
    expert_accent = HexColor("#B9823E")
    menu_sample_page_start(44, "Chuyên gia / 01", "Thực đơn chuyên gia", expert_accent)
    c.setFillColor(GREEN)
    c.setFont("QBA-Bold", 8.4)
    c.drawString(34, 679, "KHẨU VỊ TRUNG - THỰC ĐƠN LUÂN PHIÊN 06 NGÀY")
    menu_table_label(c, "Buổi sáng", 34, 660, accent=expert_accent)
    menu_week_table(
        c,
        34,
        644,
        522,
        days_6,
        [
            (
                "Thực đơn",
                [
                    "Hầm bò gốc<br/>Cháo thịt dưa cải sợi<br/>Mì Quảng xào thịt sợi<br/>Salad<br/>Cà phê - trà Voynest",
                    "Bánh bao kẹp thịt<br/>Cháo thịt dưa cải sợi<br/>Miến gà xé<br/>Salad<br/>Cà phê - trà Yufee<br/>Sữa đậu nành",
                    "Xúc xích ốp + chiên<br/>Cháo thịt nấm đông cô<br/>Nui nấu xương<br/>Salad<br/>Sữa tươi + hồng trà",
                    "Bánh xèo<br/>Cháo trứng<br/>Nui nấu xương heo<br/>Salad<br/>Phở + bột cacao nước",
                    "Bánh trứng/lạnh<br/>Cháo khoai lang<br/>Cháo thịt bằm nấm đông cô<br/>Salad<br/>Sữa đậu nành - coffee",
                    "Cơm cuộn<br/>Cháo hạt bắp rau củ<br/>Phở bò<br/>Salad<br/>Sữa bò + hồng trà",
                ],
                89,
            ),
        ],
        accent=expert_accent,
        label_width=64,
        font_size=5.15,
    )
    menu_table_label(c, "Buổi trưa", 34, 517, accent=GREEN)
    menu_week_table(
        c,
        34,
        501,
        522,
        days_6,
        [
            (
                "Món chính",
                [
                    "Cá hấp<br/>Giò heo rang muối Hong Kong<br/>Vịt ba lư mềm tươi<br/>Cải thìa xào thịt bằm",
                    "Gà rô ti<br/>Bò tủ lửa<br/>Cá chiên gỏi chanh<br/>Đậu hũ Tứ Xuyên",
                    "Cá sốt hồng xíu<br/>Mực nướng muối ớt<br/>Cải thìa đậu hũ khô tỏi<br/>Khổ qua xào trứng muối",
                    "Trái cây<br/>Bò roll chiên xù<br/>Cá nướng<br/>Bầu xào tứt mực muối",
                    "Cá thìa lát<br/>Gà cay xào dưa leo<br/>Tôm rim ba rọi<br/>Khoai tây xào thịt bằm",
                    "Tàu hũ<br/>Gà hấp mỡ hành<br/>Thịt heo rim<br/>Trứng cút sốt cà chua",
                ],
                67,
            ),
            (
                "Rau - canh",
                [
                    "Rau xào<br/>Canh súp thịt",
                    "Rau xào<br/>Canh nghêu nấu giấm",
                    "Rau xào<br/>Canh bầu tầm tưa",
                    "Rau xào<br/>Canh củ cải vò viên",
                    "Rau xào<br/>Canh cá thác lác nấu cải xanh nho",
                    "Rau xào<br/>Canh cải thảo nấu đậu hũ trắng",
                ],
                37,
            ),
        ],
        accent=GREEN,
        label_width=64,
        font_size=4.8,
    )
    menu_table_label(c, "Buổi chiều", 34, 347, accent=YELLOW)
    menu_week_table(
        c,
        34,
        331,
        522,
        days_6,
        [
            (
                "Giải khát",
                [
                    "Nước chanh dây<br/>Trái cây theo mùa",
                    "Chè bột đậu nước cốt dừa<br/>Trái cây theo mùa",
                    "Nước mía<br/>Trái cây theo mùa",
                    "Chè đậu đỏ<br/>Trái cây theo mùa",
                    "Nước chanh - bánh khoai lang chanh dây<br/>Trái cây theo mùa",
                    "Nước chanh<br/>Trái cây theo mùa",
                ],
                44,
            ),
        ],
        accent=YELLOW,
        label_width=64,
        font_size=5.1,
    )
    c.showPage()

    menu_sample_page_start(45, "Chuyên gia / 02", "Thực đơn chuyên gia", expert_accent)
    c.setFillColor(GREEN)
    c.setFont("QBA-Bold", 8.4)
    c.drawString(34, 679, "KHẨU VỊ TRUNG - BUỔI TỐI LUÂN PHIÊN 06 NGÀY")
    menu_table_label(c, "Buổi tối", 34, 657, accent=expert_accent)
    menu_week_table(
        c,
        34,
        641,
        522,
        days_6,
        [
            (
                "Món chính",
                [
                    "Cá hấp<br/>Thịt heo nấu không múc mía (băm)<br/>Gà luộc sốt tương tỏi<br/>Trứng xào cà chua",
                    "Cá sốt chua ngọt<br/>Tôm xào hồng xíu<br/>Cà ri gà<br/>Gỏi tai heo trộn dưa leo",
                    "Cá chiên<br/>Sườn hấp cải đông cô<br/>Đậu gà hạt vương chiên sốt<br/>Thịt bằm xào nấm kim châm",
                    "Cá chiên<br/>Vịt tiềm táo đỏ<br/>Đậu sốt Tứ Xuyên<br/>Trứng chiên sốt thịt bằm",
                    "Cá chiên<br/>Mực hấp tàu xì<br/>Heo nướng giòn da kiểu Tàu<br/>Chả giò tôm",
                    "Giò heo om xì dầu<br/>Gà phá lẩu chiên<br/>Thịt hun khói xào cần<br/>Rau xào",
                ],
                95,
            ),
            (
                "Rau - canh",
                [
                    "Rau xào<br/>Canh bí đỏ đậu hào<br/>Trái cây theo mùa",
                    "Rau xào<br/>Canh xương nấu măng tươi<br/>Trái cây theo mùa",
                    "Rau xào<br/>Vịt đậm mềm / hấp nấm châm<br/>Trái cây theo mùa",
                    "Rau xào<br/>Canh bí đỏ nấu nấm<br/>Trái cây theo mùa",
                    "Rau xào<br/>Canh chua sút cáo<br/>Trái cây theo mùa",
                    "Canh rau hẹ nấu huyết heo cải chua<br/>Trái cây theo mùa",
                ],
                55,
            ),
        ],
        accent=GREEN,
        label_width=64,
        font_size=5.35,
    )
    c.showPage()

    def project_page(page_no: int, key: str, company: str, years: str, meals: str, note: str, accent) -> None:
        page_bg(c)
        chrome(c, page_no, "Dự án tiêu biểu")
        project_photo = project_photos.get(key)
        has_project_photo = bool(project_photo and project_photo.exists())
        # The two newly supplied case-study photos replace only the visual placeholder.
        # Keep all existing project copy unchanged as requested.
        visual_only_photo = key in {"royal", "etop"}
        project_subtitle = "Dữ liệu dự án do doanh nghiệp cung cấp; ảnh hiện trường đã được bổ sung để hoàn thiện hồ sơ." if has_project_photo and not visual_only_photo else "Dữ liệu dự án do doanh nghiệp cung cấp; cần bổ sung ảnh và kết quả trước bản chính thức."
        section_title(c, f"20 / Dự án {page_no - 22:02d}", company, project_subtitle, y=720)
        rounded(c, 34, 350, 245, 288, fill=WHITE)
        image_contain(c, logos[key], 52, 410, 209, 188, pad=4)
        c.setFillColor(accent)
        c.rect(52, 382, 82, 6, stroke=0, fill=1)
        if has_project_photo:
            rounded(c, 303, 350, 253, 288, fill=WHITE)
            if key == "etop":
                image_cover(c, project_photo, 303, 430, 253, 160, align=(0.5, 0.7))
            else:
                image_contain(c, project_photo, 303, 430, 253, 160, pad=0)
            c.setFillColor(INK)
            c.setFont("QBA-Bold", 8.2)
            c.drawCentredString(429.5, 398, "HÌNH ẢNH HIỆN TRƯỜNG DỰ ÁN")
        else:
            placeholder(c, 303, 350, 253, 288, "ẢNH DỰ ÁN CẦN BỔ SUNG", "02-04 ảnh ngang tại nhà ăn")
        stat(c, 34, 228, 160, years, "THỜI GIAN ĐỒNG HÀNH", accent)
        stat(c, 208, 228, 160, meals, "QUY MÔ ĐƯỢC CUNG CẤP", YELLOW)
        stat(c, 382, 228, 174, "Bếp tại chỗ", "HÌNH THỨC", LIME)
        para(c, note, 34, 194, 522, project_note)
        c.showPage()

    project_page(23, "royal", "Royal Hoàng Gia", "~20 năm", "600 suất/ngày", "Đây là dấu mốc khởi đầu của Quốc Bình An. Mối quan hệ lâu dài được dùng để kể câu chuyện về sự gắn bó, lắng nghe và thay đổi theo yêu cầu thực tế.", ORANGE)
    project_page(24, "etop", "E-top Việt Nam", "~16 năm", "~5.500 suất/ngày", "Dự án quy mô lớn với mô hình bếp tại chỗ. Hồ sơ mới sẽ làm rõ cách QBA tổ chức nhân sự, thiết bị và nhịp phục vụ theo ca khi có đủ dữ liệu dự án.", LIME)
    project_page(
        26,
        "bellinturf",
        "Công ty TNHH Công Nghiệp Bellinturf Việt Nam",
        "Đang cập nhật",
        "~5.000 suất/ngày",
        "Dự án Bellinturf đã bổ sung ảnh hiện trường tại ấp Long Giang, xã Tân Lập 1, huyện Tân Phước, Tiền Giang. Quy mô do doanh nghiệp cung cấp khoảng 5.000 suất/ngày; các mốc hợp tác sẽ tiếp tục đối chiếu trước bản phát hành.",
        GREEN,
    )

    # 27 - Partners
    page_bg(c)
    chrome(c, 27, "Khách hàng đồng hành")
    section_title(c, "21 / Khách hàng", "Niềm tin được xây dựng<br/><font color='#F0835F'>qua từng ca ăn.</font>", y=720)
    partner_order = [
        ("etop", "E-top Việt Nam"), ("twin", "Twin Kie Việt Nam"), ("royal", "Royal Hoàng Gia"),
        ("jys", "JYS Việt Nam"), ("bellinturf", "Bellinturf Industrial Việt Nam"), ("jintian", "Đông Jintian Việt Nam"),
        ("leow", "Lewo Việt Nam"), ("tahtong", "Dệt Tah Tong Việt Nam"), ("minhtri", "Thép Minh Trị"),
        ("kinhthien", "Công ty TNHH Vật liệu Công nghệ Kỹ thuật Kinh Thiên Việt Nam"),
        ("vinhhung", "Công ty Vĩnh Hưng"),
        ("kangna", "Công ty TNHH Thực nghiệp Dệt Kang Na Việt Nam"),
    ]
    partner_name_style = ParagraphStyle(
        "partner-name",
        fontName="QBA-Bold",
        fontSize=6.15,
        leading=7.2,
        textColor=INK,
        alignment=TA_CENTER,
    )
    for i, (key, name) in enumerate(partner_order):
        col, row = i % 3, i // 3
        x, y = 34 + col * 177, 446 - row * 118
        rounded(c, x, y, 166, 110, fill=WHITE)
        image_contain(c, logos[key], x + 16, y + 38, 134, 60, pad=4)
        para(c, name, x + 10, y + 27, 146, partner_name_style)
    c.setFillColor(MUTED)
    c.setFont("QBA", 7)
    c.drawString(34, 70, "Tên và logo cần được xác nhận quyền công khai trước khi phát hành bản chính thức.")
    chrome(c, 27, "Khách hàng đồng hành")
    c.showPage()

    # 28 - Response commitment
    hero_page_bg(c, hero_bgs, "response", overlay_alpha=0.28)
    chrome(c, 28, "Cam kết phản hồi", dark=True)
    section_title(c, "22 / Đồng hành", "Lắng nghe nhanh.<br/><font color='#FFD569'>Điều chỉnh có trách nhiệm.</font>", dark=True, y=720, width=300)
    hero_corner_logo(c)
    c.setFillColor(YELLOW)
    c.setFont("QBA-Bold", 50)
    c.drawString(34, 548, "15-30")
    c.setFillColor(WHITE)
    c.setFont("QBA-Bold", 16)
    c.drawString(218, 563, "phút")
    c.setFillColor(LIME)
    c.setFont("QBA", 9)
    c.drawString(218, 543, "thời gian phản hồi ban đầu được cung cấp")
    commitments = [
        ("01", "Tiếp nhận", "Bà Trần Thị Thanh Thuỷ là đầu mối chính khi có phản ánh."),
        ("02", "Xác minh", "Kiểm tra ca ăn, món ăn, nhân sự và thông tin tại nhà ăn."),
        ("03", "Điều chỉnh", "Phối hợp xử lý và ghi nhận thay đổi cần thiết cho ca tiếp theo."),
    ]
    for i, (num, title, desc) in enumerate(commitments):
        x = 34 + i * 177
        rounded(c, x, 214, 166, 250, fill=INK_2, stroke=HexColor("#49675F"), radius=18)
        c.setFillColor([LIME, YELLOW, ORANGE][i])
        c.setFont("QBA-Bold", 24)
        c.drawString(x + 16, 411, num)
        c.setFillColor(WHITE)
        c.setFont("QBA-Bold", 12)
        c.drawString(x + 16, 367, title)
        para(c, desc, x + 16, 338, 134, small_dark)
    c.showPage()

    # 29 - Contact
    set_slot_page_alias(c, 29)
    hero_page_bg(c, hero_bgs, "contact", overlay_alpha=0.36)
    image_circle_crop(c, BRAND / "qba-logo-full.jpg", 38, H - 91, 58, LOGO_ICON_CROP)
    c.setFillColor(LIME)
    c.setFont("QBA-Bold", 8)
    c.drawString(108, H - 57, "QUỐC BÌNH AN CATERING")
    final_title = ParagraphStyle("final", fontName="QBA-Bold", fontSize=34, leading=39, textColor=WHITE)
    para(c, "Để Quốc Bình An<br/><font color='#FFD569'>chăm lo từng bữa ăn.</font>", 38, 650, 500, final_title)
    hero_corner_logo(c)
    para(c, "Gửi số lượng suất, số ca và khu vực phục vụ. Đội ngũ sẽ đề xuất mô hình vận hành và thực đơn phù hợp.", 40, 530, 360, body_dark)
    rounded(c, 38, 265, 519, 210, fill=INK_2, stroke=HexColor("#55756C"), radius=20)
    contact_items = [
        ("GIÁM ĐỐC", "Nguyễn Quốc Chinh", "0907 090 572"),
        ("LIÊN HỆ", "Trần Thị Thanh Thuỷ", "0909 843 604"),
        ("EMAIL", "Quốc Bình An Catering", "quocbinhan975@gmail.com"),
    ]
    for i, (label, name, value) in enumerate(contact_items):
        y = 418 - i * 58
        c.setFillColor([LIME, YELLOW, ORANGE][i])
        c.circle(60, y + 2, 7, stroke=0, fill=1)
        c.setFillColor(LIME)
        c.setFont("QBA-Bold", 6.5)
        c.drawString(80, y + 13, label)
        c.setFillColor(WHITE)
        c.setFont("QBA-Bold", 10)
        c.drawString(80, y - 2, name)
        c.setFillColor(HexColor("#D8E5DC"))
        c.setFont("QBA", 8)
        c.drawString(298, y - 2, value)
    pill(c, "Gọi điện • Yêu cầu báo giá", 38, 205, fill=YELLOW, width=190)
    c.setFillColor(LIME)
    c.setFont("QBA", 7.5)
    c.drawString(38, 115, "CÔNG TY TNHH MỘT THÀNH VIÊN QUỐC BÌNH AN • MST 3602666032")
    c.setFillColor(WHITE)
    c.setFont("QBA", 7)
    c.drawString(38, 96, "Nhơn Trạch, Đồng Nai • Địa chỉ đầy đủ sẽ đối chiếu theo giấy đăng ký thay đổi lần 4")
    c.showPage()

    page_count = max(
        [0]
        + [int(item["page"]) for item in PDF_EDITOR_MANIFEST["images"]]
        + [int(item["page"]) for item in PDF_EDITOR_MANIFEST["texts"]]
    )
    write_pdf_editor_manifest(page_count)
    c.save()
    print(OUTPUT)


if __name__ == "__main__":
    build()
