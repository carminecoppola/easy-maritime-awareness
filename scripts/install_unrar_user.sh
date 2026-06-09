#!/usr/bin/env bash
set -euo pipefail

VERSION="${VERSION:-7.22}"
SOURCE_VERSION="${SOURCE_VERSION:-7.2.6}"
PREFIX="${PREFIX:-$HOME/.local}"
BIN_DIR="$PREFIX/bin"
LIBEXEC_DIR="$PREFIX/libexec/easy-unrar"
TMP_DIR="${TMP_DIR:-$(mktemp -d)}"
METHOD="${METHOD:-binary}"
TARBALL_PATH="${TARBALL_PATH:-}"

cleanup() {
  [[ -n "${TMP_DIR:-}" && -d "$TMP_DIR" ]] && rm -rf "$TMP_DIR"
}
trap cleanup EXIT

usage() {
  cat <<EOF
Install a user-space RAR extractor for EASY.

Modes:
  binary       Install official RARLAB Linux x64 binary bundle (default)
  source       Build unrar from official UnRAR source

Environment overrides:
  VERSION=7.22
  SOURCE_VERSION=7.2.6
  PREFIX=\$HOME/.local
  METHOD=binary|source
  TARBALL_PATH=/path/to/local.tar.gz

Examples:
  scripts/install_unrar_user.sh
  METHOD=source scripts/install_unrar_user.sh
  TARBALL_PATH=\$HOME/Downloads/rarlinux-x64-722.tar.gz scripts/install_unrar_user.sh
EOF
}

download_if_needed() {
  local url="$1"
  local out="$2"

  if [[ -n "$TARBALL_PATH" ]]; then
    cp "$TARBALL_PATH" "$out"
    return 0
  fi

  if command -v curl >/dev/null 2>&1; then
    curl -fL "$url" -o "$out"
    return 0
  fi

  if command -v wget >/dev/null 2>&1; then
    wget -O "$out" "$url"
    return 0
  fi

  echo "Need curl or wget to download $url" >&2
  return 1
}

install_binary_bundle() {
  local compact_version="${VERSION//./}"
  local tarball="$TMP_DIR/rarlinux-x64-${compact_version}.tar.gz"
  local url="https://www.rarlab.com/rar/rarlinux-x64-${compact_version}.tar.gz"

  mkdir -p "$BIN_DIR" "$LIBEXEC_DIR"
  download_if_needed "$url" "$tarball"
  tar -xzf "$tarball" -C "$TMP_DIR"

  cp "$TMP_DIR/rar/unrar" "$BIN_DIR/unrar"
  chmod 0755 "$BIN_DIR/unrar"
  cp "$TMP_DIR/rar/rar" "$BIN_DIR/rar"
  chmod 0755 "$BIN_DIR/rar"
}

install_from_source() {
  local normalized_version="${SOURCE_VERSION}"
  local tarball="$TMP_DIR/unrarsrc-${normalized_version}.tar.gz"
  local url="https://www.rarlab.com/rar/unrarsrc-${normalized_version}.tar.gz"

  mkdir -p "$BIN_DIR" "$LIBEXEC_DIR"
  download_if_needed "$url" "$tarball"
  tar -xzf "$tarball" -C "$TMP_DIR"

  local src_dir
  src_dir="$(find "$TMP_DIR" -maxdepth 1 -type d -name 'unrar*' | head -1)"
  [[ -n "$src_dir" ]] || {
    echo "Could not locate extracted UnRAR source directory" >&2
    exit 2
  }

  make -C "$src_dir"
  cp "$src_dir/unrar" "$BIN_DIR/unrar"
  chmod 0755 "$BIN_DIR/unrar"
}

verify_install() {
  "$BIN_DIR/unrar" >/dev/null 2>&1 || true
  echo "Installed unrar to: $BIN_DIR/unrar"
  echo "Add this to your shell if needed:"
  echo "  export PATH=\"$BIN_DIR:\$PATH\""
  echo "Optional explicit override for EASY:"
  echo "  export RAR_EXTRACTOR=\"$BIN_DIR/unrar\""
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
esac

case "$METHOD" in
  binary)
    install_binary_bundle
    ;;
  source)
    install_from_source
    ;;
  *)
    echo "Unsupported METHOD=$METHOD (expected binary or source)" >&2
    exit 2
    ;;
esac

verify_install
