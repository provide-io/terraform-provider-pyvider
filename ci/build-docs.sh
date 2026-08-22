#!/usr/bin/env bash
# Generate the provider's registry documentation and examples with plating.
#
# Replaces scripts/build-docs.sh and scripts/generate_docs_and_examples.sh,
# which were deleted in 441584a and left nine Makefile targets pointing at a
# directory that no longer exists -- `make docs` among them, so the provider
# could not rebuild its own documentation at all.
#
# One `plating plate` call does the whole job: it renders every .plating bundle
# in pyvider.components, copies the guides, injects the global partials, writes
# the examples, and rewrites mkdocs.yml's nav to match what it produced.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PLATING="${PLATING:-.venv/bin/plating}"
OUTPUT_DIR="${OUTPUT_DIR:-docs}"
GUIDES_DIR="${GUIDES_DIR:-plating/guides}"
PARTIALS_DIR="${PARTIALS_DIR:-plating/partials}"

if [ ! -x "$PLATING" ]; then
    echo "❌ plating not found at $PLATING -- run: uv sync --group dev" >&2
    exit 1
fi

args=(
    plate
    --provider-name pyvider
    --package-name pyvider.components
    --output-dir "$OUTPUT_DIR"
    --generate-examples
    --force
    --validate
)
[ -d "$GUIDES_DIR" ] && args+=(--guides-dir "$GUIDES_DIR")
[ -d "$PARTIALS_DIR" ] && args+=(--global-partials-dir "$PARTIALS_DIR")

echo "📚 Generating documentation and examples..."
"$PLATING" "${args[@]}"

echo "✅ $(find "$OUTPUT_DIR" -name '*.md' -type f | wc -l | tr -d ' ') pages in $OUTPUT_DIR"
