#!/usr/bin/env bash
# Clean all test artifacts from examples directory
set -euo pipefail

echo "🧹 Cleaning test artifacts from examples..."

# Count before
SOUP_DIRS=$(find examples -name ".soup" -type d 2>/dev/null | wc -l | tr -d ' ')
TFSTATE_FILES=$(find examples -name "*.tfstate*" -type f 2>/dev/null | wc -l | tr -d ' ')
LOCK_FILES=$(find examples -name ".terraform.lock.hcl" -type f 2>/dev/null | wc -l | tr -d ' ')

echo "Found:"
echo "  - $SOUP_DIRS .soup directories"
echo "  - $TFSTATE_FILES tfstate files"
echo "  - $LOCK_FILES lock files"

if [ "$SOUP_DIRS" -eq 0 ] && [ "$TFSTATE_FILES" -eq 0 ] && [ "$LOCK_FILES" -eq 0 ]; then
    echo "✅ No test artifacts found - already clean!"
    exit 0
fi

# Clean
find examples -name ".soup" -type d -exec rm -rf {} + 2>/dev/null || true
find examples -name "*.tfstate*" -type f -delete 2>/dev/null || true
find examples -name ".terraform.lock.hcl" -type f -delete 2>/dev/null || true

# Show results
EXAMPLES_SIZE=$(du -sh examples/ | cut -f1)
echo "✅ Test artifacts cleaned"
echo "📊 Examples directory size: $EXAMPLES_SIZE"
