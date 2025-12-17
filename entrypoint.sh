#!/bin/sh
set -eu

# If OPENAI_API_KEY isn't set, try to load it from /app/api-key.txt (copied into the image).
if [ -z "${OPENAI_API_KEY:-}" ]; then
  if [ -f /app/api-key.txt ]; then
    # Strip possible Windows CRLF.
    OPENAI_API_KEY="$(tr -d '\r\n' < /app/api-key.txt)"
    export OPENAI_API_KEY
  fi
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000


