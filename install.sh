#!/usr/bin/env sh
# AVM installer for Linux and macOS
# Usage: curl -fsSL https://raw.githubusercontent.com/danil0ws/avm/main/install.sh | sh

set -e

REPO="danil0ws/avm"
BINARY="avm"

# Detect OS
case "$(uname -s)" in
  Linux*)  OS="linux" ;;
  Darwin*) OS="macos" ;;
  *)
    echo "Unsupported OS: $(uname -s)"
    exit 1
    ;;
esac

# Detect arch
case "$(uname -m)" in
  x86_64|amd64)  ARCH="x86_64" ;;
  aarch64|arm64) ARCH="aarch64" ;;
  *)
    echo "Unsupported architecture: $(uname -m)"
    exit 1
    ;;
esac

if [ "$OS" = "linux" ]; then
  TARGET="${ARCH}-unknown-linux-gnu"
elif [ "$OS" = "macos" ]; then
  TARGET="${ARCH}-apple-darwin"
fi

# Determine install directory
if [ -n "$AVM_INSTALL_DIR" ]; then
  INSTALL_DIR="$AVM_INSTALL_DIR"
elif [ -w "/usr/local/bin" ]; then
  INSTALL_DIR="/usr/local/bin"
else
  INSTALL_DIR="$HOME/.local/bin"
fi

mkdir -p "$INSTALL_DIR"

# Get latest release tag
echo "Fetching latest AVM release..."
LATEST=$(curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
  | grep '"tag_name"' | sed 's/.*"tag_name": *"\([^"]*\)".*/\1/')

if [ -z "$LATEST" ]; then
  echo "Could not determine latest release. Check https://github.com/${REPO}/releases"
  exit 1
fi

VERSION="${LATEST#v}"
ARCHIVE="avm-${VERSION}-${TARGET}.tar.gz"
URL="https://github.com/${REPO}/releases/download/${LATEST}/${ARCHIVE}"

echo "Installing AVM ${LATEST} for ${OS}/${ARCH}..."
echo "  From: ${URL}"
echo "  To:   ${INSTALL_DIR}/${BINARY}"

# Download
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

curl -fsSL --progress-bar "$URL" -o "${TMP_DIR}/${ARCHIVE}"

# Verify checksum if SHA256SUMS available
SUMS_URL="https://github.com/${REPO}/releases/download/${LATEST}/SHA256SUMS.txt"
if curl -fsSL "$SUMS_URL" -o "${TMP_DIR}/SHA256SUMS.txt" 2>/dev/null; then
  echo "Verifying checksum..."
  cd "$TMP_DIR"
  if command -v sha256sum > /dev/null 2>&1; then
    grep "$ARCHIVE" SHA256SUMS.txt | sha256sum -c - || { echo "Checksum verification failed!"; exit 1; }
  elif command -v shasum > /dev/null 2>&1; then
    grep "$ARCHIVE" SHA256SUMS.txt | shasum -a 256 -c - || { echo "Checksum verification failed!"; exit 1; }
  fi
  cd - > /dev/null
  echo "  Checksum OK"
fi

# Extract
tar xzf "${TMP_DIR}/${ARCHIVE}" -C "$TMP_DIR"
EXTRACTED_BINARY=$(find "$TMP_DIR" -name "$BINARY" -type f | head -1)

if [ -z "$EXTRACTED_BINARY" ]; then
  echo "Could not find binary in archive"
  exit 1
fi

chmod +x "$EXTRACTED_BINARY"
mv "$EXTRACTED_BINARY" "${INSTALL_DIR}/${BINARY}"

echo ""
echo "AVM ${LATEST} installed successfully!"
echo ""
echo "  Binary: ${INSTALL_DIR}/${BINARY}"
echo ""

# PATH hint
case ":$PATH:" in
  *":${INSTALL_DIR}:"*) ;;
  *)
    echo "Add to your shell profile to use avm:"
    echo "  export PATH=\"${INSTALL_DIR}:\$PATH\""
    echo ""
    ;;
esac

echo "Get started:"
echo "  avm --help"
echo "  avm available node --lts"
echo "  avm install node@22"
