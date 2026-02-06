#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. install python 3.10+ and retry."
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

pip install -r "$ROOT_DIR/webapp/requirements.txt"

if ! command -v pandoc >/dev/null 2>&1; then
  echo "pandoc not found on PATH. install it before using the app."
  exit 1
fi

if ! command -v anystyle >/dev/null 2>&1; then
  echo "anystyle not found on PATH. install anystyle-cli or set it in the app's Optional section."
fi

cd "$ROOT_DIR"

python -m webapp.app &
APP_PID=$!

if [ "${OPEN_BROWSER:-1}" = "1" ]; then
  sleep 1
  if command -v open >/dev/null 2>&1; then
    open "http://127.0.0.1:5000"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://127.0.0.1:5000"
  else
    echo "open/xdg-open not found. manually visit http://127.0.0.1:5000"
  fi
fi

wait "$APP_PID"
