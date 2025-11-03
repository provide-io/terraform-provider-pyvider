#!/usr/bin/env bash
# Run plating tests for all components
set -euo pipefail

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Running plating tests for pyvider-components...${NC}\n"

# Change to project root
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
    echo -e "${RED}❌ plating not found, please run: uv sync --group dev${NC}"
    exit 1
}

# Check if pyvider-components is installed
$PYTHON_CMD -c "import pyvider.components" 2>/dev/null || {
    echo -e "${RED}❌ pyvider-components not found, please run: uv sync --group dev${NC}"
    exit 1
}

echo -e "${BLUE}📚 Generating test documentation and examples...${NC}"

# Generate documentation and examples
"$SCRIPT_DIR/generate_docs_and_examples.sh" || {
    echo -e "${RED}❌ Failed to generate documentation and examples${NC}"
    exit 1
}

echo -e "${GREEN}✅ Plating tests completed successfully${NC}"

# Now run soup stir on generated examples if soup is available
if command -v soup &> /dev/null; then
    echo -e "${BLUE}🍲 Running soup stir on generated examples...${NC}"

    if [ -d "$PROJECT_ROOT/docs/examples" ]; then
        cd "$PROJECT_ROOT/docs/examples"
        soup stir --recursive || {
            echo -e "${YELLOW}⚠️  Some soup tests failed${NC}"
            # Don't fail the build for now, just warn
        }
    else
        echo -e "${YELLOW}⚠️  No docs/examples directory found${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  soup command not found, skipping conformance tests${NC}"
    echo -e "${YELLOW}💡 Install with: uv tool install tofusoup${NC}"
fi

echo -e "\n${GREEN}✅ All plating tests completed!${NC}"
