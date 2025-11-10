#!/usr/bin/env bash
# Clean all test artifacts from examples directories
# This script is maintained in provide-foundry and extracted to provider projects
set -euo pipefail

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🧹 Cleaning test artifacts from examples..."

# Directories to clean
EXAMPLE_DIRS=(
    "$PROJECT_ROOT/examples"
    "$PROJECT_ROOT/docs/examples"
)

TOTAL_SOUP_DIRS=0
TOTAL_TFSTATE_FILES=0
TOTAL_LOCK_FILES=0
TOTAL_TERRAFORM_DIRS=0

# Count artifacts in each directory
for DIR in "${EXAMPLE_DIRS[@]}"; do
    if [[ -d "$DIR" ]]; then
        SOUP_DIRS=$(find "$DIR" -name ".soup" -type d 2>/dev/null | wc -l | tr -d ' ')
        TFSTATE_FILES=$(find "$DIR" -name "*.tfstate*" -type f 2>/dev/null | wc -l | tr -d ' ')
        LOCK_FILES=$(find "$DIR" -name ".terraform.lock.hcl" -type f 2>/dev/null | wc -l | tr -d ' ')
        TERRAFORM_DIRS=$(find "$DIR" -name ".terraform" -type d 2>/dev/null | wc -l | tr -d ' ')

        TOTAL_SOUP_DIRS=$((TOTAL_SOUP_DIRS + SOUP_DIRS))
        TOTAL_TFSTATE_FILES=$((TOTAL_TFSTATE_FILES + TFSTATE_FILES))
        TOTAL_LOCK_FILES=$((TOTAL_LOCK_FILES + LOCK_FILES))
        TOTAL_TERRAFORM_DIRS=$((TOTAL_TERRAFORM_DIRS + TERRAFORM_DIRS))
    fi
done

echo "Found:"
echo "  - $TOTAL_SOUP_DIRS .soup directories"
echo "  - $TOTAL_TFSTATE_FILES tfstate files"
echo "  - $TOTAL_LOCK_FILES lock files"
echo "  - $TOTAL_TERRAFORM_DIRS .terraform directories"

if [ "$TOTAL_SOUP_DIRS" -eq 0 ] && [ "$TOTAL_TFSTATE_FILES" -eq 0 ] && [ "$TOTAL_LOCK_FILES" -eq 0 ] && [ "$TOTAL_TERRAFORM_DIRS" -eq 0 ]; then
    echo "✅ No test artifacts found - already clean!"
    exit 0
fi

# Clean artifacts in each directory
for DIR in "${EXAMPLE_DIRS[@]}"; do
    if [[ -d "$DIR" ]]; then
        find "$DIR" -name ".soup" -type d -exec rm -rf {} + 2>/dev/null || true
        find "$DIR" -name "*.tfstate*" -type f -delete 2>/dev/null || true
        find "$DIR" -name ".terraform.lock.hcl" -type f -delete 2>/dev/null || true
        find "$DIR" -name ".terraform" -type d -exec rm -rf {} + 2>/dev/null || true
    fi
done

# Show results
echo "✅ Test artifacts cleaned"
for DIR in "${EXAMPLE_DIRS[@]}"; do
    if [[ -d "$DIR" ]]; then
        SIZE=$(du -sh "$DIR" 2>/dev/null | cut -f1 || echo "N/A")
        echo "📊 ${DIR#$PROJECT_ROOT/} size: $SIZE"
    fi
done
