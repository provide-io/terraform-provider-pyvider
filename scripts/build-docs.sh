#!/bin/bash
# Script to build documentation for pyvider-components using garnish

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
GARNISH_DIR="${PROJECT_ROOT}/../garnish"
TOFUSOUP_DIR="${PROJECT_ROOT}/../tofusoup"
DOCS_OUTPUT_DIR="${PROJECT_ROOT}/docs"

print_header "📚 Building Documentation for Terraform Provider Pyvider"

# Check if directories exist
if [ ! -d "$PYVIDER_COMPONENTS_DIR" ]; then
    print_error "pyvider-components directory not found at $PYVIDER_COMPONENTS_DIR"
    exit 1
fi

if [ ! -d "$GARNISH_DIR" ]; then
    print_error "garnish directory not found at $GARNISH_DIR"
    exit 1
fi

# Install garnish if not available
if ! command -v garnish &> /dev/null; then
    print_warning "garnish not found in PATH, installing..."
    
    # Install garnish using uv pip
    if command -v uv &> /dev/null; then
        cd "$GARNISH_DIR"
        uv pip install -e . --quiet
        print_success "Installed garnish"
    else
        print_error "uv not found. Please install uv first."
        exit 1
    fi
fi

# Generate documentation
print_header "🔧 Generating Documentation with Garnish"

cd "$PYVIDER_COMPONENTS_DIR"

# Check for garnish command
GARNISH_CMD=""
if command -v garnish &> /dev/null; then
    GARNISH_CMD="garnish"
elif [ -f "$GARNISH_DIR/src/garnish/cli.py" ]; then
    GARNISH_CMD="python $GARNISH_DIR/src/garnish/cli.py"
else
    print_error "Cannot find garnish executable or CLI script"
    exit 1
fi

# Run garnish to generate docs
print_header "🍽️ Running Garnish"

# Create output directory if it doesn't exist
mkdir -p "$DOCS_OUTPUT_DIR"

# Generate documentation for resources
if [ -d "$PYVIDER_COMPONENTS_DIR/src/pyvider_components/resources" ]; then
    echo "📦 Generating resource documentation..."
    $GARNISH_CMD generate \
        --source "$PYVIDER_COMPONENTS_DIR/src/pyvider_components/resources" \
        --output "$DOCS_OUTPUT_DIR/resources" \
        --type resource || print_warning "Resource docs generation had issues"
fi

# Generate documentation for data sources
if [ -d "$PYVIDER_COMPONENTS_DIR/src/pyvider_components/data_sources" ]; then
    echo "📊 Generating data source documentation..."
    $GARNISH_CMD generate \
        --source "$PYVIDER_COMPONENTS_DIR/src/pyvider_components/data_sources" \
        --output "$DOCS_OUTPUT_DIR/data_sources" \
        --type data-source || print_warning "Data source docs generation had issues"
fi

# Generate documentation for functions
if [ -d "$PYVIDER_COMPONENTS_DIR/src/pyvider_components/functions" ]; then
    echo "🔧 Generating function documentation..."
    $GARNISH_CMD generate \
        --source "$PYVIDER_COMPONENTS_DIR/src/pyvider_components/functions" \
        --output "$DOCS_OUTPUT_DIR/functions" \
        --type function || print_warning "Function docs generation had issues"
fi

# Generate example Terraform configurations from garnish examples
print_header "🧪 Generating Example Terraform Configurations"

EXAMPLES_OUTPUT_DIR="${PROJECT_ROOT}/examples"
mkdir -p "$EXAMPLES_OUTPUT_DIR"

# Use garnish to generate example TF files
if command -v garnish &> /dev/null; then
    echo "📝 Generating Terraform examples from documentation..."
    
    # Extract and build examples from resource docs
    if [ -d "$DOCS_OUTPUT_DIR/resources" ]; then
        for doc in "$DOCS_OUTPUT_DIR/resources"/*.md; do
            if [ -f "$doc" ]; then
                resource_name=$(basename "$doc" .md)
                garnish extract-examples \
                    --input "$doc" \
                    --output "$EXAMPLES_OUTPUT_DIR/resources/${resource_name}.tf" \
                    --format terraform 2>/dev/null || true
            fi
        done
    fi
    
    # Extract and build examples from data source docs  
    if [ -d "$DOCS_OUTPUT_DIR/data_sources" ]; then
        for doc in "$DOCS_OUTPUT_DIR/data_sources"/*.md; do
            if [ -f "$doc" ]; then
                data_source_name=$(basename "$doc" .md)
                garnish extract-examples \
                    --input "$doc" \
                    --output "$EXAMPLES_OUTPUT_DIR/data_sources/${data_source_name}.tf" \
                    --format terraform 2>/dev/null || true
            fi
        done
    fi
fi

# Use tofusoup for conformance testing if available
if command -v tofusoup &> /dev/null; then
    echo "🍲 Running tofusoup conformance tests on examples..."
    
    # Create test configurations
    TOFUSOUP_TEST_DIR="${PROJECT_ROOT}/tests/conformance"
    mkdir -p "$TOFUSOUP_TEST_DIR"
    
    # Generate conformance test configurations
    tofusoup generate \
        --provider pyvider \
        --examples "$EXAMPLES_OUTPUT_DIR" \
        --output "$TOFUSOUP_TEST_DIR" \
        --format hcl 2>/dev/null || print_warning "Tofusoup test generation had issues"
    
    print_success "Generated conformance test configurations in $TOFUSOUP_TEST_DIR"
fi

# Copy any existing handwritten docs
if [ -d "$PYVIDER_COMPONENTS_DIR/docs" ]; then
    echo "📄 Copying existing documentation..."
    cp -r "$PYVIDER_COMPONENTS_DIR/docs/"* "$DOCS_OUTPUT_DIR/" 2>/dev/null || true
fi

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

print_success "Documentation generated in $DOCS_OUTPUT_DIR"

# Show summary
echo -e "\n📊 Documentation Summary:"
if [ -d "$DOCS_OUTPUT_DIR" ]; then
    echo "  Resources: $(find "$DOCS_OUTPUT_DIR/resources" -name "*.md" 2>/dev/null | wc -l)"
    echo "  Data Sources: $(find "$DOCS_OUTPUT_DIR/data_sources" -name "*.md" 2>/dev/null | wc -l)"
    echo "  Functions: $(find "$DOCS_OUTPUT_DIR/functions" -name "*.md" 2>/dev/null | wc -l)"
fi

print_header "✅ Documentation Build Complete"