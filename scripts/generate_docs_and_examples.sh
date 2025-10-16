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

# Check if plating is installed
if ! command -v plating &> /dev/null; then
    echo -e "${YELLOW}⚠️  plating CLI not found, installing...${NC}"
    pip install plating || {
        echo -e "${RED}❌ Failed to install plating${NC}"
        exit 1
    }
fi

# Check if pyvider-components is installed
python3 -c "import pyvider.components" 2>/dev/null || {
    echo -e "${YELLOW}⚠️  pyvider-components not installed, installing...${NC}"
    pip install pyvider-components || {
        echo -e "${RED}❌ Failed to install pyvider-components${NC}"
        exit 1
    }
}

# Output directory for documentation and examples
OUTPUT_DIR="${PROJECT_ROOT}/docs"
EXAMPLES_DIR="${OUTPUT_DIR}/examples"

# Create output directories
mkdir -p "$OUTPUT_DIR"
mkdir -p "$EXAMPLES_DIR"

echo -e "${GREEN}🍽️  Running plating to generate documentation and examples...${NC}"

# Run plating with --generate-examples flag
# This will:
# 1. Generate documentation from .plating/docs/ templates
# 2. Copy examples from .plating/examples/ directories
plating plate \
    --provider-name pyvider \
    --package-name pyvider.components \
    --output-dir "$OUTPUT_DIR" \
    --generate-examples \
    --force \
    --validate || {
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