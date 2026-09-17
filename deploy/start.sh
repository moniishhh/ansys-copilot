#!/bin/sh
set -eu

uvicorn backend.main:app --host 127.0.0.1 --port 8000 &
backend_pid=$!

trap 'kill "$backend_pid" 2>/dev/null || true' INT TERM EXIT
nginx -g 'daemon off;'
