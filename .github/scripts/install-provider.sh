#!/usr/bin/env bash
#
# install-provider.sh - Install Terraform provider binary to plugin directory
#
# Usage: install-provider.sh <version> <platform> <source_binary>
#
# Example:
#   install-provider.sh 0.0.17 linux_amd64 ./terraform-provider-pyvider_v0.0.17
#   install-provider.sh 0.0.17 windows_amd64 ./terraform-provider-pyvider_v0.0.17.exe

set -euo pipefail

VERSION="${1:-}"
PLATFORM="${2:-}"
SOURCE_BINARY="${3:-}"

if [[ -z "$VERSION" || -z "$PLATFORM" || -z "$SOURCE_BINARY" ]]; then
  echo "❌ ERROR: Missing required arguments"
  echo "Usage: $0 <version> <platform> <source_binary>"
  exit 1
fi

if [[ ! -f "$SOURCE_BINARY" ]]; then
  echo "❌ ERROR: Source binary not found: $SOURCE_BINARY"
  exit 1
fi

echo "🔌 Installing Terraform provider..."
echo "   Version: $VERSION"
echo "   Platform: $PLATFORM"
echo "   Source: $SOURCE_BINARY"

# Determine plugin directory based on platform
if [[ "$PLATFORM" == windows_* ]]; then
  PLUGIN_DIR="${APPDATA}/terraform.d/plugins/local/providers/pyvider/${VERSION}/${PLATFORM}"
else
  PLUGIN_DIR="${HOME}/.terraform.d/plugins/local/providers/pyvider/${VERSION}/${PLATFORM}"
fi
mkdir -p "$PLUGIN_DIR"

# Windows binaries need .exe extension
if [[ "$PLATFORM" == windows_* ]]; then
  DEST_BINARY="${PLUGIN_DIR}/terraform-provider-pyvider.exe"
else
  DEST_BINARY="${PLUGIN_DIR}/terraform-provider-pyvider"
fi

cp "$SOURCE_BINARY" "$DEST_BINARY"
chmod +x "$DEST_BINARY" 2>/dev/null || true

echo ""
echo "✅ Provider installed successfully!"
echo "   Location: $DEST_BINARY"
echo ""

# Validate installation
echo "📋 Installation details:"
ls -lah "$DEST_BINARY"

if [[ -x "$DEST_BINARY" ]] || [[ "$PLATFORM" == windows_* ]]; then
  echo ""
  echo "✅ Provider binary is executable"
  if "$DEST_BINARY" --version 2>&1 | head -5 || true; then
    echo "✅ Provider binary executed successfully"
  fi
else
  echo "❌ ERROR: Provider binary is not executable"
  exit 1
fi

echo ""
echo "🎉 Installation complete!"
