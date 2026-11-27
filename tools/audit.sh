#!/bin/bash
# Accessibility, overflow and screenshot run. Nothing is installed on the host:
# axe-core and the playwright package are installed inside the throwaway container only.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p docs/screenshots
docker run --rm --ipc=host -v "$PWD":/site:ro -v "$PWD/docs/screenshots":/out \
  mcr.microsoft.com/playwright:v1.49.1-noble bash -c '
    set -e; mkdir /tmp/a && cd /tmp/a && npm init -y >/dev/null && npm i --silent --no-audit --no-fund playwright@1.49.1 axe-core@4.10.2 >/dev/null 2>&1
    cp /site/tools/audit.js . && node audit.js; code=$?; chown -R '"$(id -u):$(id -g)"' /out; exit $code'
mv docs/screenshots/og-image.png og-image.png
