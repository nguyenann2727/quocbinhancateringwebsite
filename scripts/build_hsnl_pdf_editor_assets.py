from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01.pdf"
PAGES_DIR = ROOT / "editable/hsnl-pdf-pages"
BUILD_SCRIPT = ROOT / "scripts/build_hsnl_qba_full.py"


def find_pdftoppm() -> str:
    candidates = [
        Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pdftoppm"),
        Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"),
        Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/bin/pdftoppm"),
        Path("/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/native/poppler/poppler/bin/pdftoppm"),
    ]
    for bundled in candidates:
        if bundled.exists():
            return str(bundled)
    found = shutil.which("pdftoppm")
    if found:
        return found
    raise RuntimeError("Không tìm thấy pdftoppm để render trang PDF.")


def main() -> None:
    subprocess.run([sys.executable, str(BUILD_SCRIPT)], cwd=ROOT, check=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    for path in PAGES_DIR.glob("page-*.jpg"):
        path.unlink()
    for path in PAGES_DIR.glob("raw-*.jpg"):
        path.unlink()

    prefix = PAGES_DIR / "raw"
    subprocess.run(
        [
            find_pdftoppm(),
            "-jpeg",
            "-r",
            "144",
            "-jpegopt",
            "quality=88,optimize=y,progressive=y",
            str(PDF),
            str(prefix),
        ],
        cwd=ROOT,
        check=True,
    )

    rendered = sorted(PAGES_DIR.glob("raw-*.jpg"), key=lambda item: int(item.stem.split("-")[-1]))
    for index, path in enumerate(rendered, start=1):
        path.rename(PAGES_DIR / f"page-{index:02d}.jpg")

    print(ROOT / "editable/hsnl-pdf-editor.html")


if __name__ == "__main__":
    main()
