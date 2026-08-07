#!/bin/zsh
set -e

cd "$(dirname "$0")"

PORT=8787
URL="http://127.0.0.1:${PORT}/index.html#services"
PYTHON="/Users/quoc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"

if [ ! -x "$PYTHON" ]; then
  PYTHON="/usr/bin/python3"
fi

if ! /usr/bin/curl -fsI "http://127.0.0.1:${PORT}/index.html" >/dev/null 2>&1; then
  /usr/bin/nohup "$PYTHON" -m http.server "$PORT" --bind 127.0.0.1 > .qba-site-server.log 2>&1 &
  echo $! > .qba-site-server.pid
  sleep 1
fi

/usr/bin/open "$URL"
