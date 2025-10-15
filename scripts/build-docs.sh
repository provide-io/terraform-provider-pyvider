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

# Generate documentation using Python PlatingAPI
echo "📝 Generating documentation with PlatingAPI..."

python3 -c "
import sys
import asyncio
sys.path.append('$PYVIDER_COMPONENTS_DIR/src')

from pathlib import Path
from plating import Plating, PlatingContext

async def generate_docs():
    try:
        # Create plating context with provider name
        context = PlatingContext(provider_name='pyvider')
        api = Plating(context, 'pyvider.components')

        output_dir = Path('$DOCS_OUTPUT_DIR')

        # Generate all documentation
        print('Generating documentation with plating...')
        result = await api.plate(output_dir, validate_markdown=False, force=True)

        if result.success:
            print(f'Successfully generated {result.files_generated} documentation files')
            print(f'Processed {result.bundles_processed} component bundles')
        else:
            print('Documentation generation failed:')
            for error in result.errors:
                print(f'  - {error}')
            sys.exit(1)

    except Exception as e:
        print(f'Error generating documentation: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Run async function
asyncio.run(generate_docs())
" || {
    print_error "Failed to generate documentation with plating"
    exit 1
}

# Example generation with plating (simplified approach)
print_header "🧪 Creating Example Terraform Configurations"

EXAMPLES_OUTPUT_DIR="${PROJECT_ROOT}/examples"
mkdir -p "$EXAMPLES_OUTPUT_DIR"

# Create basic examples directory structure
mkdir -p "$EXAMPLES_OUTPUT_DIR/resources"
mkdir -p "$EXAMPLES_OUTPUT_DIR/data-sources"
mkdir -p "$EXAMPLES_OUTPUT_DIR/functions"

echo "📝 Creating basic example configurations..."

# Create a comprehensive example that demonstrates multiple components
cat > "$EXAMPLES_OUTPUT_DIR/comprehensive.tf" << 'EOF'
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "~> 0.0.5"
    }
  }
}

provider "pyvider" {}

# Example resources
resource "pyvider_file_content" "example" {
  filename = "example.json"
  content = jsonencode({
    message = "Hello from Pyvider"
    timestamp = timestamp()
  })
}

resource "pyvider_local_directory" "example_dir" {
  path        = "./example-output"
  create_mode = "0755"
}

# Example data sources
data "pyvider_env_variables" "current" {
  keys = ["USER", "HOME", "PATH"]
}

data "pyvider_file_info" "example_info" {
  path = pyvider_file_content.example.filename
  depends_on = [pyvider_file_content.example]
}

# Example function usage
locals {
  math_examples = {
    sum = provider::pyvider::add(10, 20)
    division = provider::pyvider::divide(100, 5)
  }

  string_examples = {
    upper = provider::pyvider::upper("terraform")
    formatted = provider::pyvider::format("Hello %s!", ["World"])
  }

  collection_examples = {
    minimum = provider::pyvider::min([5, 2, 8, 1])
    maximum = provider::pyvider::max([5, 2, 8, 1])
  }
}

# Outputs
output "examples" {
  value = {
    file_path = pyvider_file_content.example.filename
    directory_path = pyvider_local_directory.example_dir.path
    current_user = data.pyvider_env_variables.current.values["USER"]
    file_size = data.pyvider_file_info.example_info.size
    math_results = local.math_examples
    string_results = local.string_examples
    collection_results = local.collection_examples
  }
}
EOF

print_success "Comprehensive example created at $EXAMPLES_OUTPUT_DIR/comprehensive.tf"

# TODO: Extract examples from plating-generated documentation when that feature is available
# For now, we rely on the comprehensive example above

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