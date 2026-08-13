#!/usr/bin/env python3
"""Build the public QBA static site from an explicit runtime allowlist."""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PUBLIC_PDF = Path("output/pdf/HSNL-Quoc-Binh-An-Catering-WEBSITE.pdf")
ROOT_FILES = (
    Path("index.html"),
    Path("styles.css"),
    Path("script.js"),
    Path("i18n.js"),
    Path("draft-final-config.js"),
    Path("draft-final-manifest.json"),
    Path("image-config.json"),
    Path("robots.txt"),
)
SCAN_FILES = tuple(path for path in ROOT_FILES if path.suffix in {".html", ".css", ".js", ".json"})
ASSET_LIMIT = 25 * 1024 * 1024
RUNTIME_REF = re.compile(r"(?:assets|output/pdf)/[^\"'`()<>\\\s]+")


def clean_reference(raw: str) -> Path:
    value = unquote(raw).split("?", 1)[0].split("#", 1)[0]
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe runtime reference: {raw}")
    return path


def collect_runtime_files() -> set[Path]:
    files = set(ROOT_FILES)
    for relative in SCAN_FILES:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"Missing required source file: {relative}")
        text = source.read_text(encoding="utf-8")
        for match in RUNTIME_REF.finditer(text):
            files.add(clean_reference(match.group(0)))

    # The public document is intentionally the only PDF shipped at runtime.
    pdf_refs = {path for path in files if path.parts[:2] == ("output", "pdf")}
    if pdf_refs != {PUBLIC_PDF}:
        rendered = ", ".join(str(path) for path in sorted(pdf_refs)) or "none"
        raise RuntimeError(f"Unexpected public PDF references: {rendered}")
    return files


def main() -> int:
    runtime_files = collect_runtime_files()
    missing = sorted(path for path in runtime_files if not (ROOT / path).is_file())
    if missing:
        print("Missing runtime files:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        return 1

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    for relative in sorted(runtime_files):
        source = ROOT / relative
        destination = DIST / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    oversized = sorted(
        path.relative_to(DIST)
        for path in DIST.rglob("*")
        if path.is_file() and path.stat().st_size >= ASSET_LIMIT
    )
    if oversized:
        print("Cloudflare-incompatible assets (25 MiB or larger):", file=sys.stderr)
        for path in oversized:
            print(f"  - {path}", file=sys.stderr)
        return 1

    largest = max((path for path in DIST.rglob("*") if path.is_file()), key=lambda path: path.stat().st_size)
    print(f"Built {len(runtime_files)} public files in {DIST}")
    print(f"Largest asset: {largest.relative_to(DIST)} ({largest.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
