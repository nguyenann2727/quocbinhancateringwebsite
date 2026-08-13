#!/usr/bin/env python3
"""Convert a QBA draft export into version-controlled production defaults."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import re
from pathlib import Path


EXTENSIONS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}


def digest(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def safe_id(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("export", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()

    root = args.root.resolve()
    source = args.export.resolve()
    payload = json.loads(source.read_text(encoding="utf-8"))
    if payload.get("type") != "qba-draft-final" or payload.get("version") != 1:
        raise SystemExit("Unsupported QBA draft export")

    asset_dir = root / "assets" / "draft-final"
    asset_dir.mkdir(parents=True, exist_ok=True)

    production_images = []
    manifest_assets = []
    for record in payload.get("imageRecords", []):
        image = dict(record)
        source_value = image.get("dataUrl", "")
        if source_value.startswith("data:"):
            header, encoded = source_value.split(",", 1)
            mime_match = re.match(r"data:([^;,]+);base64$", header)
            if not mime_match:
                raise SystemExit(f"Unsupported image payload for {image.get('id')}")
            mime = mime_match.group(1).lower()
            extension = EXTENSIONS.get(mime) or mimetypes.guess_extension(mime) or ".bin"
            filename = f"{safe_id(image['id'])}{extension}"
            target = asset_dir / filename
            binary = base64.b64decode(encoded, validate=True)
            target.write_bytes(binary)
            image["dataUrl"] = target.relative_to(root).as_posix()
            manifest_assets.append({
                "id": image["id"],
                "path": image["dataUrl"],
                "bytes": len(binary),
                "sha256": digest(binary),
                "mime": mime,
            })
        else:
            target = root / source_value
            if not target.is_file():
                raise SystemExit(f"Missing production asset for {image.get('id')}: {source_value}")
            binary = target.read_bytes()
            manifest_assets.append({
                "id": image["id"],
                "path": source_value,
                "bytes": len(binary),
                "sha256": digest(binary),
                "mime": image.get("type", "image/default"),
            })
        production_images.append(image)

    final_payload = {
        "version": 1,
        "type": "qba-draft-final-production-defaults",
        "sourceExportedAt": payload.get("exportedAt"),
        "sourceViewport": payload.get("source", {}).get("viewport"),
        "contentRecords": payload.get("contentRecords", {}),
        "imageRecords": production_images,
        "frameRecords": payload.get("frameRecords", []),
    }

    js = "window.QBA_DRAFT_FINAL = " + json.dumps(final_payload, ensure_ascii=False, indent=2) + ";\n"
    (root / "draft-final-config.js").write_text(js, encoding="utf-8")
    (root / "image-config.json").write_text(
        json.dumps({"version": 1, "records": production_images, "frameRecords": payload.get("frameRecords", [])}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    source_bytes = source.read_bytes()
    manifest = {
        "version": 1,
        "type": "qba-draft-final-release-manifest",
        "source": {
            "filename": source.name,
            "exportedAt": payload.get("exportedAt"),
            "sha256": digest(source_bytes),
            "bytes": len(source_bytes),
        },
        "counts": {
            "contentRecords": len(payload.get("contentRecords", {})),
            "renderedContent": len(payload.get("renderedContent", [])),
            "imageRecords": len(production_images),
            "frameRecords": len(payload.get("frameRecords", [])),
        },
        "assets": manifest_assets,
    }
    (root / "draft-final-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"Imported {len(final_payload['contentRecords'])} content records")
    print(f"Imported {len(production_images)} image records")
    print(f"Imported {len(final_payload['frameRecords'])} frame records")
    print(f"Wrote {len(manifest_assets)} checksummed production assets")


if __name__ == "__main__":
    main()
