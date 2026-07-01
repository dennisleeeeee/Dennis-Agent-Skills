#!/usr/bin/env bash
# Bootstrap a Remotion Video LAB workspace on any device.
# Usage: bash setup.sh "<target-dir>"
set -euo pipefail
TARGET="${1:-remotion-video-lab}"
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$TARGET"
cp -R "$HERE/." "$TARGET/"
rm -f "$TARGET/setup.sh"
cd "$TARGET"
echo "Installing dependencies in $TARGET ..."
npm install
echo "Done. Put a clip at public/sample/source.mp4 then: npm run dev"
