from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import parse_qs, urlparse, urlsplit


ROOT = Path(__file__).resolve().parents[1]
STATE_FILE = ROOT / "editable/hsnl-pdf-editor-state.json"
EDIT_BUTTON_FILE = ROOT / "editable/hsnl-pdf-edit-button.json"
DOWNLOADS = Path.home() / "Downloads"
UPLOADS = ROOT / "editable/hsnl-pdf-editor-uploads"
BUILD_EDITOR_ASSETS = ROOT / "scripts/build_hsnl_pdf_editor_assets.py"
BUILD_WEB_PDF = ROOT / "scripts/build_hsnl_web_pdf.py"
DRAFT_PDF = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01.pdf"
DRAFT_WEB_PDF = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-DRAFT-01-web.pdf"
FINAL_PDF = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL.pdf"
FINAL_WEB_PDF = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL-web.pdf"
WEBSITE_PDF = ROOT / "output/pdf/HSNL-Quoc-Binh-An-Catering-WEBSITE.pdf"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
PROFILE_PDF_MAX_BYTES = 80 * 1024 * 1024
PROFILE_PDF_MAX_REQUEST_BYTES = 112 * 1024 * 1024
PROFILE_PDF_MIME_TYPES = {
    "",
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}
PROFILE_PDF_ALLOWED_ORIGINS = {
    "null",
    "http://127.0.0.1:8787",
    "http://localhost:8787",
}


class EditorHandler(SimpleHTTPRequestHandler):
    # Chromium's PDF viewer seeks forward while the reader scrolls. HTTP/1.1 plus
    # explicit byte-range responses lets later pages load even for large profiles.
    protocol_version = "HTTP/1.1"
    stream_chunk_size = 1024 * 1024

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def handle_one_request(self) -> None:
        try:
            super().handle_one_request()
        except (BrokenPipeError, ConnectionResetError):
            # Browsers can cancel page-image downloads while the editor is reloading.
            pass

    def end_headers(self) -> None:
        path = urlparse(self.path).path.lower()
        if path.endswith(".pdf"):
            # Revalidate rebuilt PDFs without disabling the PDF viewer's range cache.
            self.send_header("Cache-Control", "private, max-age=0, must-revalidate")
            self.send_header("Accept-Ranges", "bytes")
        else:
            self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin", "")
        if origin in PROFILE_PDF_ALLOWED_ORIGINS:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Vary", "Origin")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/health" or parsed.path.startswith("/api/"):
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        self.send_error(HTTPStatus.NOT_FOUND)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/download-images":
            return self.list_download_images()
        if parsed.path == "/api/download-preview":
            return self.download_preview(parsed)
        if parsed.path == "/health":
            return self.send_json({"ok": True, "service": "hsnl-pdf-editor", "status": "ready"}, HTTPStatus.OK)
        if parsed.path.lower().endswith(".pdf"):
            return self.serve_pdf(parsed.path)
        if parsed.path in {"/", ""}:
            self.path = "/editable/hsnl-pdf-editor.html"
        return super().do_GET()

    def do_HEAD(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path.lower().endswith(".pdf"):
            return self.serve_pdf(parsed.path, include_body=False)
        return super().do_HEAD()

    def resolve_static_path(self, raw_path: str) -> Path:
        path = (ROOT / raw_path.lstrip("/")).resolve()
        if not path.is_file() or not path.is_relative_to(ROOT.resolve()):
            raise FileNotFoundError(raw_path)
        return path

    def parse_byte_range(self, raw_range: str, total: int) -> Optional[Tuple[int, int]]:
        # PDF.js issues a single bytes=start-end range. Reject multi-ranges rather
        # than serving an ambiguous multipart response.
        match = re.fullmatch(r"bytes=(\d*)-(\d*)", raw_range.strip())
        if not match:
            return None
        start_text, end_text = match.groups()
        if not start_text and not end_text:
            return None
        if not start_text:
            length = int(end_text)
            if length <= 0:
                return None
            start = max(0, total - length)
            return start, total - 1
        start = int(start_text)
        if start >= total:
            return None
        end = int(end_text) if end_text else total - 1
        return start, min(end, total - 1)

    def serve_pdf(self, raw_path: str, *, include_body: bool = True) -> None:
        try:
            path = self.resolve_static_path(raw_path)
            total = path.stat().st_size
            requested_range = self.headers.get("Range", "")
            byte_range = self.parse_byte_range(requested_range, total) if requested_range else None
            if requested_range and byte_range is None:
                self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
                self.send_header("Content-Range", f"bytes */{total}")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

            start, end = byte_range or (0, total - 1)
            content_length = end - start + 1
            self.send_response(HTTPStatus.PARTIAL_CONTENT if byte_range else HTTPStatus.OK)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'inline; filename="{path.name}"')
            self.send_header("Content-Length", str(content_length))
            if byte_range:
                self.send_header("Content-Range", f"bytes {start}-{end}/{total}")
            self.end_headers()
            if not include_body:
                return
            with path.open("rb") as handle:
                handle.seek(start)
                remaining = content_length
                while remaining:
                    chunk = handle.read(min(self.stream_chunk_size, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)
        except (BrokenPipeError, ConnectionResetError):
            # The PDF viewer may cancel a prefetch after it has received a page.
            return
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, "Không tìm thấy file PDF")
        except ValueError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Range PDF không hợp lệ")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/save-state":
            return self.save_state()
        if parsed.path == "/api/rebuild":
            return self.rebuild_pdf()
        if parsed.path == "/api/edit-button":
            return self.set_edit_button()
        if parsed.path == "/api/import-download-image":
            return self.import_download_image()
        if parsed.path == "/api/upload-image":
            return self.upload_image()
        if parsed.path == "/api/profile-pdf":
            return self.upload_profile_pdf()
        self.send_error(HTTPStatus.NOT_FOUND)

    def safe_slot_id(self, raw_slot_id: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", str(raw_slot_id)).strip("-") or "image"

    def safe_file_stem(self, raw_stem: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", str(raw_stem)).strip("-")[:60] or "upload"

    def upload_extension(self, filename: str, mime: str, data_url_header: str) -> str:
        ext = Path(filename).suffix.lower()
        if ext in IMAGE_EXTENSIONS:
            return ".jpg" if ext == ".jpeg" else ext
        probe = f"{mime} {data_url_header}".lower()
        if "jpeg" in probe or "jpg" in probe:
            return ".jpg"
        if "png" in probe:
            return ".png"
        if "webp" in probe:
            return ".webp"
        if "heic" in probe:
            return ".heic"
        if "heif" in probe:
            return ".heif"
        raise ValueError("File không phải ảnh JPG/PNG/WebP/HEIC được hỗ trợ")

    def safe_download_path(self, raw_path: str) -> Path:
        path = Path(raw_path).expanduser().resolve()
        downloads = DOWNLOADS.resolve()
        if not path.is_file() or not path.is_relative_to(downloads):
            raise ValueError("Chỉ được chọn ảnh trong thư mục Downloads")
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError("File không phải ảnh được hỗ trợ")
        return path

    def list_download_images(self) -> None:
        try:
            files = []
            if DOWNLOADS.exists():
                for path in DOWNLOADS.iterdir():
                    if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                        continue
                    stat = path.stat()
                    encoded = base64.urlsafe_b64encode(str(path).encode("utf-8")).decode("ascii")
                    files.append(
                        {
                            "name": path.name,
                            "path": str(path),
                            "ext": path.suffix.lower(),
                            "size": stat.st_size,
                            "mtime": stat.st_mtime,
                            "preview": f"/api/download-preview?path={encoded}",
                        }
                    )
            files.sort(key=lambda item: item["mtime"], reverse=True)
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
        return self.send_json({"ok": True, "downloads": DOWNLOADS.as_posix(), "images": files[:160]})

    def download_preview(self, parsed) -> None:
        try:
            query = parse_qs(parsed.query)
            encoded = query.get("path", [""])[0]
            raw_path = base64.urlsafe_b64decode(encoded.encode("ascii")).decode("utf-8")
            path = self.safe_download_path(raw_path)
            if path.suffix.lower() in {".heic", ".heif"}:
                return self.send_error(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "HEIC sẽ được chuyển khi bấm chọn")
            mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(path.stat().st_size))
            self.end_headers()
            with path.open("rb") as handle:
                shutil.copyfileobj(handle, self.wfile)
        except Exception as exc:
            return self.send_error(HTTPStatus.BAD_REQUEST, str(exc))

    def save_state(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Payload must be object")
            STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return self.send_json({"ok": True, "path": STATE_FILE.as_posix()})

    def set_edit_button(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            enabled = bool(payload.get("enabled"))
            current = {}
            if EDIT_BUTTON_FILE.exists():
                current = json.loads(EDIT_BUTTON_FILE.read_text(encoding="utf-8"))
            current["enabled"] = enabled
            server_host, server_port = self.server.server_address
            current.setdefault("url", f"http://{server_host}:{server_port}/editable/hsnl-pdf-editor.html?mode=all")
            EDIT_BUTTON_FILE.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)
        return self.send_json({"ok": True, "enabled": enabled, "path": EDIT_BUTTON_FILE.as_posix()})

    def import_download_image(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            source = self.safe_download_path(str(payload.get("path", "")))
            slot_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", str(payload.get("slotId", "image"))).strip("-") or "image"
            safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", source.stem).strip("-")[:60] or "download"
            UPLOADS.mkdir(parents=True, exist_ok=True)
            if source.suffix.lower() in {".heic", ".heif"}:
                target = UPLOADS / f"{slot_id}-{safe_stem}.jpg"
                subprocess.run(["sips", "-s", "format", "jpeg", str(source), "--out", str(target)], check=True)
            else:
                target = UPLOADS / f"{slot_id}-{safe_stem}{source.suffix.lower()}"
                shutil.copy2(source, target)
            return self.send_json(
                {
                    "ok": True,
                    "filename": source.name,
                    "replacement": target.resolve().relative_to(ROOT).as_posix(),
                }
            )
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def upload_image(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        if length > 80 * 1024 * 1024:
            return self.send_json({"ok": False, "error": "Ảnh quá lớn, vui lòng chọn file dưới 80MB"}, HTTPStatus.BAD_REQUEST)
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
            data_url = str(payload.get("dataUrl", ""))
            if "," not in data_url or not data_url.startswith("data:image/"):
                raise ValueError("Dữ liệu ảnh không hợp lệ")
            header, encoded = data_url.split(",", 1)
            source_bytes = base64.b64decode(encoded)
            filename = str(payload.get("filename") or "upload")
            ext = self.upload_extension(filename, str(payload.get("mime") or ""), header)
            slot_id = self.safe_slot_id(str(payload.get("slotId", "image")))
            safe_stem = self.safe_file_stem(Path(filename).stem)
            UPLOADS.mkdir(parents=True, exist_ok=True)
            if ext in {".heic", ".heif"}:
                source = UPLOADS / f"{slot_id}-{safe_stem}{ext}"
                target = UPLOADS / f"{slot_id}-{safe_stem}.jpg"
                source.write_bytes(source_bytes)
                subprocess.run(["sips", "-s", "format", "jpeg", str(source), "--out", str(target)], check=True)
                try:
                    source.unlink()
                except OSError:
                    pass
            else:
                target = UPLOADS / f"{slot_id}-{safe_stem}{ext}"
                target.write_bytes(source_bytes)
            return self.send_json(
                {
                    "ok": True,
                    "filename": filename,
                    "replacement": target.resolve().relative_to(ROOT).as_posix(),
                }
            )
        except Exception as exc:
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def upload_profile_pdf(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0:
            return self.send_json({"ok": False, "error": "Dữ liệu PDF trống"}, HTTPStatus.BAD_REQUEST)
        if length > PROFILE_PDF_MAX_REQUEST_BYTES:
            return self.send_json(
                {"ok": False, "error": "PDF vượt quá dung lượng tối đa 80MB"},
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            )

        temporary_pdf = WEBSITE_PDF.with_suffix(".pdf.uploading")
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            filename = str(payload.get("filename") or "").strip()
            mime = str(payload.get("mime") or "").strip().lower()
            data_url = str(payload.get("dataUrl") or "")

            if Path(filename).suffix.lower() != ".pdf":
                raise ValueError("Chỉ hỗ trợ file PDF")
            if mime not in PROFILE_PDF_MIME_TYPES:
                raise ValueError("Chỉ hỗ trợ file PDF")
            if "," not in data_url:
                raise ValueError("Dữ liệu PDF không hợp lệ")

            header, encoded = data_url.split(",", 1)
            header_parts = header.lower().split(";")
            data_mime = header_parts[0].removeprefix("data:")
            if not header.lower().startswith("data:") or "base64" not in header_parts[1:]:
                raise ValueError("Dữ liệu PDF không hợp lệ")
            if data_mime not in PROFILE_PDF_MIME_TYPES:
                raise ValueError("Dữ liệu PDF không hợp lệ")

            source_bytes = base64.b64decode(encoded, validate=True)
            if not source_bytes:
                raise ValueError("Dữ liệu PDF trống")
            if len(source_bytes) > PROFILE_PDF_MAX_BYTES:
                return self.send_json(
                    {"ok": False, "error": "PDF vượt quá dung lượng tối đa 80MB"},
                    HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                )
            if b"%PDF-" not in source_bytes[:1024]:
                raise ValueError("File không phải PDF hợp lệ")

            WEBSITE_PDF.parent.mkdir(parents=True, exist_ok=True)
            with temporary_pdf.open("wb") as handle:
                handle.write(source_bytes)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_pdf, WEBSITE_PDF)

            stat = WEBSITE_PDF.stat()
            return self.send_json(
                {
                    "ok": True,
                    "path": WEBSITE_PDF.resolve().relative_to(ROOT).as_posix(),
                    "filename": filename,
                    "size": stat.st_size,
                    "updatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(stat.st_mtime)),
                }
            )
        except Exception as exc:
            try:
                temporary_pdf.unlink()
            except OSError:
                pass
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def rebuild_pdf(self) -> None:
        try:
            subprocess.run([sys.executable, str(BUILD_EDITOR_ASSETS)], cwd=ROOT, check=True)
            subprocess.run([sys.executable, str(BUILD_WEB_PDF)], cwd=ROOT, check=True)
            # Keep the downloadable FINAL files in sync with every editor rebuild.
            shutil.copy2(DRAFT_PDF, FINAL_PDF)
            shutil.copy2(DRAFT_WEB_PDF, FINAL_WEB_PDF)
            shutil.copy2(FINAL_WEB_PDF, WEBSITE_PDF)
        except subprocess.CalledProcessError as exc:
            return self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
        return self.send_json(
            {
                "ok": True,
                "pdf": FINAL_PDF.as_posix(),
                "webPdf": FINAL_WEB_PDF.as_posix(),
                "websitePdf": WEBSITE_PDF.as_posix(),
            }
        )

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def parse_port_from_url(raw: str) -> Optional[int]:
    if not raw:
        return None
    try:
        parsed = urlsplit(str(raw))
        return int(parsed.port) if parsed.hostname and parsed.port else None
    except (TypeError, ValueError):
        return None


def read_fallback_ports(preferred_port: int) -> list[int]:
    ports: list[int] = []

    def add_port(value: Optional[int]) -> None:
        if value is None:
            return
        if value < 1 or value > 65535:
            return
        if value not in ports:
            ports.append(value)

    add_port(preferred_port)
    for port in range(preferred_port, preferred_port + 10):
        add_port(port)
    # A previously saved fallback port must never override the standard address.
    if EDIT_BUTTON_FILE.exists():
        try:
            saved = json.loads(EDIT_BUTTON_FILE.read_text(encoding="utf-8"))
            add_port(parse_port_from_url(str(saved.get("url", ""))))
        except Exception:
            pass
    return ports


def main() -> None:
    host = "127.0.0.1"
    try:
        preferred_port = int(os.environ.get("HSNL_EDITOR_PORT", "8791"))
    except ValueError:
        preferred_port = 8791
    ThreadingHTTPServer.allow_reuse_address = True
    server = None
    last_error: Optional[OSError] = None
    for port in read_fallback_ports(preferred_port):
        try:
            server = ThreadingHTTPServer((host, port), EditorHandler)
            break
        except OSError as exc:
            last_error = exc
    if server is None:
        raise SystemExit(f"Không mở được server editor: {last_error}")

    edit_url = f"http://{host}:{port}/editable/hsnl-pdf-editor.html?mode=all"
    pdf_url = f"http://{host}:{port}/output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL.pdf"
    # Preserve the cover-button preference when the local editor restarts.
    # Restarting the server must never bring a deliberately hidden temporary
    # button back onto the exported PDF.
    edit_button_enabled = True
    if EDIT_BUTTON_FILE.exists():
        try:
            existing_button_config = json.loads(EDIT_BUTTON_FILE.read_text(encoding="utf-8"))
            edit_button_enabled = bool(existing_button_config.get("enabled", True))
        except (OSError, json.JSONDecodeError):
            pass
    EDIT_BUTTON_FILE.write_text(
        json.dumps({"enabled": edit_button_enabled, "url": edit_url}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"HSNL PDF editor: {edit_url}")
    print(f"HSNL final PDF: {pdf_url}")
    if "--no-open" not in sys.argv:
        threading.Thread(target=lambda: (time.sleep(0.5), webbrowser.open(edit_url), webbrowser.open(pdf_url)), daemon=True).start()
    server.serve_forever()


if __name__ == "__main__":
    try:
        main()
    except BaseException as exc:
        # LaunchAgent output can be discarded by macOS while a service is
        # starting. Keep a small local diagnostic so failed restarts remain
        # actionable without touching profile content or editor state.
        (ROOT / ".hsnl-editor-launch-error.log").write_text(
            f"{type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        raise
