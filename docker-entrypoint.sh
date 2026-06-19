#!/bin/sh
set -e

if [ -n "$TWAK_ACCESS_ID" ] && [ -n "$TWAK_HMAC_SECRET" ]; then
  python scripts/twak_bootstrap.py || echo "TWAK bootstrap skipped or failed — check logs"
fi

exec python -m api.server