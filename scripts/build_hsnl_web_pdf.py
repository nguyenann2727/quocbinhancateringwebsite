#!/usr/bin/env python3
"""Create a compact, image-based PDF for website/flipbook viewing."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01.pdf"
OUTPUT = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01-web.pdf"
FALLBACK_PDFTOPPM = [
    Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm"),
    Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"),
    Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/bin/pdftoppm"),
    Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm"),
]


def main() -> None:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        for fallback in FALLBACK_PDFTOPPM:
            if fallback.exists():
                pdftoppm = str(fallback)
                break
    if not pdftoppm:
        raise RuntimeError("Không tìm thấy pdftoppm để tạo bản PDF nhẹ.")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hsnl-qba-web-") as temp_dir:
        prefix = Path(temp_dir) / "page"
        subprocess.run(
            [
                pdftoppm,
                "-jpeg",
                "-r",
                "120",
                "-jpegopt",
                "quality=80,optimize=y,progressive=y",
                str(SOURCE),
                str(prefix),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )

        images = sorted(Path(temp_dir).glob("page-*.jpg"))
        if not images:
            raise RuntimeError("Không tạo được ảnh trang từ PDF nguồn.")

        pdf = canvas.Canvas(str(OUTPUT), pagesize=A4, pageCompression=1)
        pdf.setTitle("Hồ sơ năng lực Quốc Bình An Catering - Bản website")
        pdf.setAuthor("Quốc Bình An Catering")
        for image in images:
            pdf.drawImage(str(image), 0, 0, width=A4[0], height=A4[1])
            pdf.showPage()
        pdf.save()

    print(OUTPUT)


if __name__ == "__main__":
    main()
