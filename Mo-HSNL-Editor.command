#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"

PYTHON="/usr/bin/python3"
PORT=""

find_running_port() {
  local candidate
  for candidate in {8791..8800}; do
    # A stale server can answer /health while lacking access to the PDF. Verify
    # a real byte range before reusing it, otherwise start a healthy fallback.
    if /usr/bin/curl -fs "http://127.0.0.1:${candidate}/health" >/dev/null 2>&1 && \
      /usr/bin/curl -fs --range 0-1023 "http://127.0.0.1:${candidate}/output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL.pdf" >/dev/null 2>&1; then
      PORT="$candidate"
      return 0
    fi
  done
  return 1
}

if ! find_running_port; then
  # macOS can stop a detached local server. Keep it in a dedicated Terminal
  # tab instead, so it remains available throughout the editing session.
  /usr/bin/osascript -e "tell application \"Terminal\" to do script \"cd \\\"$PWD\\\" && exec env HSNL_EDITOR_PORT=8792 $PYTHON scripts/serve_hsnl_pdf_editor.py --no-open\""

  for _ in {1..40}; do
    sleep 0.25
    if find_running_port; then
      break
    fi
  done
fi

if [ -z "$PORT" ]; then
  /usr/bin/osascript -e 'display alert "Không thể mở HSNL" message "Máy chủ HSNL không khởi động được. Mở file .hsnl-editor-server.log trong thư mục dự án để xem chi tiết."'
  exit 1
fi

EDITOR_URL="http://127.0.0.1:${PORT}/editable/hsnl-pdf-editor.html?mode=all"
PDF_REVISION="$(/usr/bin/stat -f '%m' output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL.pdf 2>/dev/null || /bin/date +%s)"
PDF_URL="http://127.0.0.1:${PORT}/output/pdf/HSNL-Quoc-Binh-An-Catering-FINAL.pdf?v=${PDF_REVISION}"

/usr/bin/open "$EDITOR_URL"
/usr/bin/open "$PDF_URL"
