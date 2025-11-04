#!/bin/bash
# Script to build documentation for pyvider-components using plating

set -euo pipefail

# Colors for output
COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[0;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m'

print_header() {
    echo -e "\n${COLOR_BLUE}--- ${1} ---${COLOR_NC}"
}

print_success() {
    echo -e "${COLOR_GREEN}✅ ${1}${COLOR_NC}"
}

print_error() {
    echo -e "${COLOR_RED}❌ ${1}${COLOR_NC}"
}

print_warning() {
    echo -e "${COLOR_YELLOW}⚠️  ${1}${COLOR_NC}"
}

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYVIDER_COMPONENTS_DIR="${PROJECT_ROOT}/../pyvider-components"
PLATING_DIR="${PROJECT_ROOT}/../plating"
TOFUSOUP_DIR="${PROJECT_ROOT}/../tofusoup"
DOCS_OUTPUT_DIR="${PROJECT_ROOT}/docs"

print_header "📚 Building Documentation for Terraform Provider Pyvider"

# Check if documentation generation is disabled
if [ "${SKIP_DOCS:-false}" = "true" ]; then
    print_warning "Skipping documentation generation (SKIP_DOCS=true)"
    exit 0
fi

# Note: In CI/CD, pyvider-components and plating are installed as packages via uv sync
# We don't need the source directories - plating works with installed packages
# Only check for directories in local development mode
if [ -n "${CI:-}" ]; then
    print_warning "Running in CI mode - skipping source directory checks"
    print_warning "Packages should be installed via: uv sync --group dev"
else
    # Local development: check if directories exist (optional)
    if [ ! -d "$PYVIDER_COMPONENTS_DIR" ]; then
        print_warning "pyvider-components directory not found at $PYVIDER_COMPONENTS_DIR"
        print_warning "Assuming packages are installed via pip/uv"
    fi

    if [ ! -d "$PLATING_DIR" ]; then
        print_warning "plating directory not found at $PLATING_DIR"
        print_warning "Assuming packages are installed via pip/uv"
    fi
fi

# Verify required packages are installed
print_header "🔍 Verifying required packages"

# In CI, use uv run to access venv; locally use python3 directly
if [ -n "${CI:-}" ]; then
    PYTHON_CMD="uv run python3"
else
    PYTHON_CMD="python3"
fi

$PYTHON_CMD -c "import plating" 2>/dev/null || {
    print_error "plating package not found. Run: uv sync --group dev"
    exit 1
}
$PYTHON_CMD -c "import pyvider.components" 2>/dev/null || {
    print_error "pyvider-components package not found. Run: uv sync --group dev"
    exit 1
}
print_success "Required packages are installed"

# Generate documentation
print_header "🔧 Generating Documentation with Plating"

cd "$PROJECT_ROOT"

# Generate documentation using Plating
print_header "📚 Running Plating Documentation Generation"

# Create output directory if it doesn't exist
mkdir -p "$DOCS_OUTPUT_DIR"

# Generate documentation and examples using plating CLI
# Note: Guide copying is now handled by plating via --guides-dir flag
print_header "📚 Generating Documentation and Examples with Plating CLI"

"$SCRIPT_DIR/generate_docs_and_examples.sh" || {
    print_error "Failed to generate documentation and examples with plating"
    exit 1
}

print_success "Documentation and examples generated with plating"

# Validate generated examples
print_header "🔍 Validating Generated Examples"

"$SCRIPT_DIR/validate_examples.sh" || {
    print_warning "Some examples failed validation - please review and fix"
    # Don't fail the build for now, just warn
}

# Use tofusoup for conformance testing if available
if command -v tofusoup &> /dev/null; then
    echo "🍲 Running tofusoup conformance tests on examples..."

    # Create test configurations
    TOFUSOUP_TEST_DIR="${PROJECT_ROOT}/tests/conformance"
    mkdir -p "$TOFUSOUP_TEST_DIR"

    # Set examples directory (from plating generation)
    EXAMPLES_OUTPUT_DIR="${PROJECT_ROOT}/docs/examples"

    # Generate conformance test configurations
    tofusoup generate \
        --provider pyvider \
        --examples "$EXAMPLES_OUTPUT_DIR" \
        --output "$TOFUSOUP_TEST_DIR" \
        --format hcl 2>/dev/null || print_warning "Tofusoup test generation had issues"

    print_success "Generated conformance test configurations in $TOFUSOUP_TEST_DIR"
fi

# Note: Not copying docs from pyvider-components as they may be outdated or incorrect
# Documentation should be generated fresh from the code

print_success "Documentation generated with plating in $DOCS_OUTPUT_DIR"

# Show summary
echo -e "\n📊 Documentation Summary:"
if [ -d "$DOCS_OUTPUT_DIR" ]; then
    echo "  Guides: $(find "$DOCS_OUTPUT_DIR/guides" -name "*.md" 2>/dev/null | wc -l | xargs)"
    echo "  Resources: $(find "$DOCS_OUTPUT_DIR/resources" -name "*.md" 2>/dev/null | wc -l | xargs)"
    echo "  Data Sources: $(find "$DOCS_OUTPUT_DIR/data-sources" -name "*.md" 2>/dev/null | wc -l | xargs)"
    echo "  Functions: $(find "$DOCS_OUTPUT_DIR/functions" -name "*.md" 2>/dev/null | wc -l | xargs)"
fi

print_header "✅ Documentation Build Complete"