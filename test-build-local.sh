#!/usr/bin/env bash
set -euo pipefail

# Local test script to verify PSP build works

echo "🧪 Testing terraform-provider-pyvider PSP build locally..."

# Detect platform
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

case "$OS" in
    darwin)
        PLATFORM="darwin"
        ;;
    linux)
        PLATFORM="linux"
        ;;
    *)
        echo "❌ Unsupported OS: $OS"
        exit 1
        ;;
esac

case "$ARCH" in
    x86_64|amd64)
        ARCH="amd64"
        ;;
    aarch64|arm64)
        ARCH="arm64"
        ;;
    *)
        echo "❌ Unsupported architecture: $ARCH"
        exit 1
        ;;
esac

TARGET="${PLATFORM}_${ARCH}"
echo "🎯 Detected platform: $TARGET"

# Check if flavorpack is available locally
if command -v flavor &> /dev/null; then
    echo "✅ Found flavor command"
    flavor --version
else
    echo "⚠️ flavor not found, trying to use from flavorpack"
    # Try using the local flavorpack
    FLAVORPACK_DIR="../flavorpack"
    if [ -d "$FLAVORPACK_DIR" ]; then
        echo "📦 Found local flavorpack at $FLAVORPACK_DIR"
        export PATH="$FLAVORPACK_DIR/workenv/flavor_${TARGET}/bin:$PATH"
        
        # Source the environment
        if [ -f "$FLAVORPACK_DIR/env.sh" ]; then
            source "$FLAVORPACK_DIR/env.sh"
        fi
    else
        echo "❌ Cannot find flavor command or local flavorpack"
        echo "Please install flavorpack: uv tool install flavorpack"
        exit 1
    fi
fi

# Check for launcher (optional - flavorpack can auto-discover)
LAUNCHER_DIR="../flavorpack/ingredients/bin"
LAUNCHER="$LAUNCHER_DIR/flavor-rs-launcher-${TARGET}"

if [ -f "$LAUNCHER" ]; then
    echo "✅ Found local launcher: $LAUNCHER"
    LAUNCHER_ARGS="--launcher-bin $LAUNCHER"
else
    echo "🔍 Using flavorpack's auto-discovery for launcher"
    LAUNCHER_ARGS=""
fi

# Build the PSP package
VERSION="0.1.0-test"
OUTPUT="terraform-provider-pyvider-${VERSION}-${TARGET}.psp"

echo "🏗️ Building PSP package..."
flavor pack \
    --manifest pyproject.toml \
    --output "$OUTPUT" \
    --key-seed "test123" \
    $LAUNCHER_ARGS

if [ -f "$OUTPUT" ]; then
    echo "✅ Build successful!"
    echo "📦 Package details:"
    ls -la "$OUTPUT"
    
    echo ""
    echo "🔍 Testing package execution:"
    chmod +x "$OUTPUT"
    ./"$OUTPUT" --version || echo "Note: Package may require Terraform environment"
else
    echo "❌ Build failed!"
    exit 1
fi