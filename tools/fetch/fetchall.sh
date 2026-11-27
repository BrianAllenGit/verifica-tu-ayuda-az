#!/bin/bash
# Usage: fetchall.sh <urls.txt> <outdir>   (lines: name url). Docker only, nothing installed on the host.
set -euo pipefail
URLS=$(realpath "$1"); OUT=$(realpath "$2"); HERE=$(cd "$(dirname "$0")" && pwd)
docker run --rm -v "$HERE":/w:ro -v "$OUT":/out -v "$URLS":/urls.txt:ro mcr.microsoft.com/playwright:v1.49.1-noble \
  sh -c "cd /tmp && npm i playwright@1.49.1 >/dev/null 2>&1 && cp /w/dump.mjs . && while read n u; do echo \"== \$n \$u\"; node dump.mjs \"\$u\" \"\$n\" || echo FAILED \$n; done < /urls.txt; chown -R $(id -u):$(id -g) /out"
