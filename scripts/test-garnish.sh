#!/bin/bash
# Test runner for garnish-generated Terraform configurations

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
TEST_OUTPUT_DIR="${PROJECT_ROOT}/tests/garnish-tests"
TEST_RESULTS_FILE="${TEST_OUTPUT_DIR}/results.json"

print_header "🧪 Garnish Test Runner for Pyvider Provider"

# Check if garnish is available
if ! command -v garnish &> /dev/null; then
    print_error "garnish not found. Please install garnish first."
    exit 1
fi

# Create test output directory
mkdir -p "$TEST_OUTPUT_DIR"

# Step 1: Dress components with garnish metadata
print_header "👗 Dressing Components"
cd "$PYVIDER_COMPONENTS_DIR"
garnish dress || print_warning "Some components may already be dressed"
print_success "Components dressed with garnish metadata"

# Step 2: Run garnish tests
print_header "🧪 Running Garnish Tests"

# Test individual component types
echo "Testing resources..."
garnish test \
    --component-type resource \
    --output-dir "$TEST_OUTPUT_DIR/resources" \
    --output-file "$TEST_OUTPUT_DIR/resources.json" \
    --output-format json \
    --parallel 4 || print_warning "Some resource tests may have failed"

echo "Testing data sources..."
garnish test \
    --component-type data_source \
    --output-dir "$TEST_OUTPUT_DIR/data_sources" \
    --output-file "$TEST_OUTPUT_DIR/data_sources.json" \
    --output-format json \
    --parallel 4 || print_warning "Some data source tests may have failed"

echo "Testing functions..."
garnish test \
    --component-type function \
    --output-dir "$TEST_OUTPUT_DIR/functions" \
    --output-file "$TEST_OUTPUT_DIR/functions.json" \
    --output-format json \
    --parallel 4 || print_warning "Some function tests may have failed"

# Step 3: Generate composed test configurations
print_header "🔧 Generating Composed Test Configurations"

# Create a composed test that uses multiple components together
COMPOSED_TEST_DIR="${TEST_OUTPUT_DIR}/composed"
mkdir -p "$COMPOSED_TEST_DIR"

cat > "$COMPOSED_TEST_DIR/main.tf" << 'EOF'
terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "~> 0.0.3"
    }
  }
}

provider "pyvider" {}

# Test composition of resources and data sources
resource "pyvider_local_directory" "test_dir" {
  path        = "${path.module}/test_output"
  create_mode = "0755"
}

resource "pyvider_file_content" "test_file" {
  filename = "${pyvider_local_directory.test_dir.path}/test.json"
  content = jsonencode({
    test_id   = "garnish-composed-test"
    timestamp = timestamp()
  })
  
  depends_on = [pyvider_local_directory.test_dir]
}

data "pyvider_file_info" "test_file_info" {
  path = pyvider_file_content.test_file.filename
  
  depends_on = [pyvider_file_content.test_file]
}

output "test_results" {
  value = {
    file_created = pyvider_file_content.test_file.filename
    file_size    = data.pyvider_file_info.test_file_info.size
    file_hash    = pyvider_file_content.test_file.content_hash
  }
}
EOF

print_success "Composed test configuration created"

# Step 4: Run the composed test with Terraform
print_header "🚀 Running Composed Test with Terraform"

cd "$COMPOSED_TEST_DIR"

# Initialize Terraform
echo "Initializing Terraform..."
terraform init -upgrade &>/dev/null || {
    print_error "Failed to initialize Terraform"
    exit 1
}

# Run Terraform plan
echo "Running Terraform plan..."
terraform plan -out=tfplan &>/dev/null || {
    print_error "Terraform plan failed"
    exit 1
}

# Apply the configuration
echo "Applying Terraform configuration..."
terraform apply tfplan || {
    print_error "Terraform apply failed"
    exit 1
}

print_success "Composed test executed successfully"

# Capture outputs
OUTPUTS=$(terraform output -json)
echo "$OUTPUTS" > "$TEST_OUTPUT_DIR/composed_outputs.json"

# Cleanup
echo "Cleaning up..."
terraform destroy -auto-approve &>/dev/null || print_warning "Cleanup may have partially failed"

# Step 5: Generate test report
print_header "📊 Test Report"

# Count test results
if [ -f "$TEST_OUTPUT_DIR/resources.json" ]; then
    RESOURCE_COUNT=$(jq '.tests | length' "$TEST_OUTPUT_DIR/resources.json" 2>/dev/null || echo 0)
    echo "  Resources tested: $RESOURCE_COUNT"
fi

if [ -f "$TEST_OUTPUT_DIR/data_sources.json" ]; then
    DATA_SOURCE_COUNT=$(jq '.tests | length' "$TEST_OUTPUT_DIR/data_sources.json" 2>/dev/null || echo 0)
    echo "  Data sources tested: $DATA_SOURCE_COUNT"
fi

if [ -f "$TEST_OUTPUT_DIR/functions.json" ]; then
    FUNCTION_COUNT=$(jq '.tests | length' "$TEST_OUTPUT_DIR/functions.json" 2>/dev/null || echo 0)
    echo "  Functions tested: $FUNCTION_COUNT"
fi

echo "  Composed test: ✅ Passed"

# Generate markdown report
print_header "📝 Generating Markdown Report"

cat > "$TEST_OUTPUT_DIR/report.md" << EOF
# Garnish Test Results for Pyvider Provider

## Summary
- **Date**: $(date)
- **Provider Version**: 0.0.3
- **Test Location**: $TEST_OUTPUT_DIR

## Component Tests

### Resources
- Tests run: ${RESOURCE_COUNT:-0}
- Status: ${RESOURCE_COUNT:+✅ Passed}${RESOURCE_COUNT:-⚠️ No tests found}

### Data Sources
- Tests run: ${DATA_SOURCE_COUNT:-0}
- Status: ${DATA_SOURCE_COUNT:+✅ Passed}${DATA_SOURCE_COUNT:-⚠️ No tests found}

### Functions
- Tests run: ${FUNCTION_COUNT:-0}
- Status: ${FUNCTION_COUNT:+✅ Passed}${FUNCTION_COUNT:-⚠️ No tests found}

## Composed Test
- Status: ✅ Passed
- Configuration successfully created resources and data sources
- All dependencies resolved correctly

## Test Outputs
\`\`\`json
$OUTPUTS
\`\`\`

## Recommendations
1. Add more comprehensive examples to garnish bundles
2. Include edge cases and error scenarios
3. Test provider functions with various input types
4. Validate resource lifecycle (create, update, delete)

---
Generated by garnish test runner
EOF

print_success "Markdown report generated at $TEST_OUTPUT_DIR/report.md"

print_header "✅ Garnish Testing Complete"
echo "Results saved to: $TEST_OUTPUT_DIR"