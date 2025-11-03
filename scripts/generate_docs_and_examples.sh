#!/usr/bin/env bash
# Generate documentation and examples using plating CLI
set -euo pipefail

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}📝 Generating documentation and examples with plating CLI...${NC}"

# Ensure we're in the project root
cd "$PROJECT_ROOT"

# Activate virtual environment if available
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${GREEN}🔧 Activating virtual environment...${NC}"
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Determine which python/plating command to use (CI vs local)
if [ -n "${CI:-}" ]; then
    PYTHON_CMD="uv run python3"
    PLATING_CMD="uv run plating"
else
    PYTHON_CMD="python3"
    PLATING_CMD="plating"
fi

# Check if plating is installed
$PYTHON_CMD -c "import plating" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  plating not found, please run: uv sync --group dev${NC}"
    exit 1
}

# Check if pyvider-components is installed
$PYTHON_CMD -c "import pyvider.components" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  pyvider-components not found, please run: uv sync --group dev${NC}"
    exit 1
}

# Output directory for documentation and examples
OUTPUT_DIR="${PROJECT_ROOT}/docs"
EXAMPLES_DIR="${OUTPUT_DIR}/examples"
GUIDES_DIR="${PROJECT_ROOT}/plating/guides"
GLOBAL_PARTIALS_DIR="${PROJECT_ROOT}/plating/partials"

# Create output directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$EXAMPLES_DIR"

echo -e "${GREEN}🍽️  Running plating to generate documentation and examples...${NC}"

# Build plating command with optional --guides-dir flag
PLATING_ARGS=(
    "plate"
    "--provider-name" "pyvider"
    "--package-name" "pyvider.components"
    "--output-dir" "$OUTPUT_DIR"
    "--generate-examples"
    "--force"
    "--validate"
)

# Add --guides-dir if guides/ directory exists
if [ -d "$GUIDES_DIR" ]; then
    PLATING_ARGS+=("--guides-dir" "$GUIDES_DIR")
fi

# Add --global-partials-dir if global partials directory exists
if [ -d "$GLOBAL_PARTIALS_DIR" ]; then
    PLATING_ARGS+=("--global-partials-dir" "$GLOBAL_PARTIALS_DIR")
fi

# Run plating with generated arguments
# This will:
# 1. Copy guides from guides/ to docs/guides/ (if --guides-dir provided)
# 2. Generate documentation from .plating/docs/ templates
# 3. Inject global headers/footers from partials (if --global-partials-dir provided)
# 4. Copy examples from .plating/examples/ directories
$PLATING_CMD "${PLATING_ARGS[@]}" || {
    echo -e "${RED}❌ Plating failed to generate documentation and examples${NC}"
    exit 1
}

echo -e "${GREEN}✅ Documentation and examples generated successfully${NC}"

# List generated files for verification
echo -e "${GREEN}📂 Generated documentation structure:${NC}"
find "$OUTPUT_DIR" -type f -name "*.md" | head -10
echo ""

echo -e "${GREEN}📂 Generated examples:${NC}"
find "$EXAMPLES_DIR" -type f -name "*.tf" 2>/dev/null | head -10 || echo "Examples will be in: $EXAMPLES_DIR"

echo -e "${GREEN}✨ Done! Documentation and examples are ready in $OUTPUT_DIR${NC}"