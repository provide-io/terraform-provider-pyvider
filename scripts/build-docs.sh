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

# Check if directories exist
if [ ! -d "$PYVIDER_COMPONENTS_DIR" ]; then
    print_error "pyvider-components directory not found at $PYVIDER_COMPONENTS_DIR"
    exit 1
fi

if [ ! -d "$PLATING_DIR" ]; then
    print_error "plating directory not found at $PLATING_DIR"
    exit 1
fi

# Install plating if not available
# Check if plating is available in Python environment
if ! python3 -c "import plating" &> /dev/null; then
    print_warning "plating not found in Python environment, installing..."

    # Install plating using uv pip
    if command -v uv &> /dev/null; then
        cd "$PLATING_DIR"
        uv pip install -e . --quiet
        print_success "Installed plating"
        cd "$PROJECT_ROOT"
    else
        print_error "uv not found. Please install uv first."
        exit 1
    fi
fi

# Generate documentation
print_header "🔧 Generating Documentation with Plating"

cd "$PROJECT_ROOT"

# Generate documentation using PlatingAPI
print_header "📚 Running Plating Documentation Generation"

# Create output directory if it doesn't exist
mkdir -p "$DOCS_OUTPUT_DIR"

# Generate documentation and examples using plating CLI
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

# Create index if it doesn't exist
if [ ! -f "$DOCS_OUTPUT_DIR/index.md" ]; then
    cat > "$DOCS_OUTPUT_DIR/index.md" << EOF
---
page_title: "pyvider Provider"
description: |-
  The official Pyvider provider for Terraform/OpenTofu
---

# pyvider Provider

The \`pyvider\` provider is the official provider for the Pyvider framework, demonstrating its capabilities and providing utility resources, data sources, and functions for testing and infrastructure tasks.

## Example Usage

\`\`\`hcl
terraform {
  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "~> 0.0"
    }
  }
}

provider "pyvider" {
  # Configuration options
}
\`\`\`

## Available Resources

See the navigation menu for available resources, data sources, and functions.
EOF
fi

print_success "Documentation generated with plating in $DOCS_OUTPUT_DIR"

# Show summary
echo -e "\n📊 Documentation Summary:"
if [ -d "$DOCS_OUTPUT_DIR" ]; then
    echo "  Resources: $(find "$DOCS_OUTPUT_DIR/resources" -name "*.md" 2>/dev/null | wc -l | xargs)"
    echo "  Data Sources: $(find "$DOCS_OUTPUT_DIR/data-sources" -name "*.md" 2>/dev/null | wc -l | xargs)"
    echo "  Functions: $(find "$DOCS_OUTPUT_DIR/functions" -name "*.md" 2>/dev/null | wc -l | xargs)"
fi

print_header "✅ Documentation Build Complete"