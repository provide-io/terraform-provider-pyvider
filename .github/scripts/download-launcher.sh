#!/usr/bin/env bash
set -euo pipefail

# Script to download the appropriate flavor launcher for the current platform

LAUNCHER_VERSION="${LAUNCHER_VERSION:-0.3.0}"
TARGET_PLATFORM="${1:-}"

if [ -z "$TARGET_PLATFORM" ]; then
    echo "❌ Error: Target platform not specified"
    echo "Usage: $0 <platform>"
    echo "Platforms: linux_amd64, linux_arm64, darwin_amd64, darwin_arm64"
    exit 1
fi

echo "📥 Downloading launcher for platform: $TARGET_PLATFORM"

# Construct download URL
BASE_URL="https://github.com/livingstaccato/flavorpack/releases/download"
LAUNCHER_URL="${BASE_URL}/v${LAUNCHER_VERSION}/flavor-rs-launcher-${LAUNCHER_VERSION}-${TARGET_PLATFORM}"

# Create directory for launchers
mkdir -p launchers

# Download the launcher
OUTPUT_FILE="launchers/flavor-rs-launcher-${TARGET_PLATFORM}"
echo "📦 Downloading from: $LAUNCHER_URL"
echo "💾 Saving to: $OUTPUT_FILE"

if command -v curl &> /dev/null; then
    curl -L -f -o "$OUTPUT_FILE" "$LAUNCHER_URL"
elif command -v wget &> /dev/null; then
    wget -O "$OUTPUT_FILE" "$LAUNCHER_URL"
else
    echo "❌ Error: Neither curl nor wget is available"
    exit 1
fi

# Make executable
chmod +x "$OUTPUT_FILE"

# Verify download
if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ Successfully downloaded launcher"
    ls -la "$OUTPUT_FILE"
else
    echo "❌ Error: Failed to download launcher"
    exit 1
fi