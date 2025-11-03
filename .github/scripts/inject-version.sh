#!/usr/bin/env bash
#
# inject-version.sh - Inject version constraint into provider.tf files
#
# Usage: inject-version.sh <version> <provider.tf>
#
# This script handles both cases:
# 1. provider.tf has no version constraint (inserts it)
# 2. provider.tf has existing version constraint (replaces it)
#
# The version constraint uses exact matching (not >=) for test stability.

set -euo pipefail

VERSION="${1:-}"
PROVIDER_FILE="${2:-provider.tf}"

if [[ -z "$VERSION" ]]; then
  echo "❌ ERROR: Version argument required"
  echo "Usage: $0 <version> [provider.tf]"
  exit 1
fi

if [[ ! -f "$PROVIDER_FILE" ]]; then
  echo "❌ ERROR: Provider file not found: $PROVIDER_FILE"
  exit 1
fi

echo "🔧 Injecting version constraint: $VERSION"
echo "   File: $PROVIDER_FILE"

# Check if version constraint already exists
if grep -q 'version\s*=' "$PROVIDER_FILE"; then
  echo "   Replacing existing version constraint..."

  # Replace existing version constraint (handles both >= and exact versions)
  sed -i.bak \
    's/version\s*=\s*"[^"]*"/version = "'"$VERSION"'"/' \
    "$PROVIDER_FILE"
else
  echo "   Inserting new version constraint..."

  # Insert version constraint after source line
  # This works on both GNU sed (Linux) and BSD sed (macOS)
  sed -i.bak \
    '/source[[:space:]]*=[[:space:]]*"local\/providers\/pyvider"/a\
      version = "'"$VERSION"'"
' \
    "$PROVIDER_FILE"
fi

# Remove backup file
rm -f "${PROVIDER_FILE}.bak"

# Validate that version was injected
echo ""
echo "📋 Updated provider configuration:"
grep -A 2 "required_providers" "$PROVIDER_FILE" | head -8
echo ""

if ! grep -q "version.*$VERSION" "$PROVIDER_FILE"; then
  echo "❌ ERROR: Failed to inject version constraint"
  echo "   Expected: version = \"$VERSION\""
  exit 1
fi

echo "✅ Version constraint successfully injected: $VERSION"
