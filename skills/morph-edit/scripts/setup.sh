#!/usr/bin/env bash
# One-time setup in the user's project. Installs Playwright + Chromium into ./motion/node_modules
# and faster-whisper (for transcription) into ./motion/.venv.
set -e
MOTION_DIR="${1:-./motion}"
mkdir -p "$MOTION_DIR"/{clips,dist,out,work}
missing=()
case "$(uname -s)" in
  Darwin) OS=mac ;;
  Linux) OS=linux ;;
  *) OS=windows ;;
esac
hint() {  # tool -> install command for this OS
  case "$OS:$1" in
    mac:node) echo "brew install node" ;;
    mac:ffmpeg) echo "brew install ffmpeg" ;;
    mac:python3) echo "brew install python" ;;
    linux:node) echo "sudo apt install nodejs npm   (needs Node 18+; see https://nodejs.org if apt is older)" ;;
    linux:ffmpeg) echo "sudo apt install ffmpeg" ;;
    linux:python3) echo "sudo apt install python3 python3-venv python3-pip" ;;
    windows:*) echo "native Windows is untested: install WSL (wsl --install in PowerShell), open Ubuntu, and run this there" ;;
  esac
}
command -v node >/dev/null || missing+=("node: $(hint node)")
command -v ffmpeg >/dev/null || missing+=("ffmpeg: $(hint ffmpeg)")
command -v python3 >/dev/null || missing+=("python3: $(hint python3)")
if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing tools. Install these, then run setup again:"; printf '  - %s\n' "${missing[@]}"; exit 1
fi
if command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -lt 18 ]; then echo "Node 18 or newer is required (found $(node -v))."; exit 1; fi
python3 -c "import numpy" 2>/dev/null || python3 -m pip install --user numpy || python3 -m pip install --break-system-packages numpy
if [ ! -d "$MOTION_DIR/node_modules/playwright" ]; then
  (cd "$MOTION_DIR" && { [ -f package.json ] || echo '{"private":true}' > package.json; } && npm install --silent playwright && npx playwright install chromium)
fi
if [ ! -d "$MOTION_DIR/.venv" ]; then
  python3 -m venv "$MOTION_DIR/.venv" && "$MOTION_DIR/.venv/bin/pip" install --quiet faster-whisper numpy
fi
ffmpeg -hide_banner -encoders 2>/dev/null | grep -q prores_ks || echo "Note: your ffmpeg has no prores_ks encoder; transparent panel clips will fail."
echo "Ready. Clips go in $MOTION_DIR/clips, renders in $MOTION_DIR/out."
