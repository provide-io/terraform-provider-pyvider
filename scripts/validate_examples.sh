#!/usr/bin/env bash
# Validate Terraform examples for format and syntax
# This script is maintained in provide-foundry and extracted to provider projects
set -euo pipefail

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Detect provider name from pyproject.toml or environment variable
PROVIDER_NAME="${PROVIDER_NAME:-$(grep '^name = ' "$PROJECT_ROOT/pyproject.toml" 2>/dev/null | cut -d'"' -f2 | sed 's/terraform-provider-//')}"
if [[ -z "$PROVIDER_NAME" ]]; then
    echo "❌ Could not detect provider name. Set PROVIDER_NAME environment variable."
    exit 1
fi

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters for results
TOTAL_FILES=0
PASSED_FILES=0
FAILED_FILES=0
FORMAT_FAILURES=()
VALIDATE_FAILURES=()
PLACEHOLDER_WARNINGS=()

echo -e "${BLUE}🔍 Validating Terraform examples...${NC}\n"

# Find all example directories
EXAMPLES_DIRS=(
    "$PROJECT_ROOT/docs/examples"
    "$PROJECT_ROOT/examples"
)

# Function to check for placeholder values
check_placeholders() {
    local file="$1"
    # Common placeholder patterns
    if grep -qE "(Asdf|PLACEHOLDER|TODO|XXX|dummy|test123|example\.com)" "$file" 2>/dev/null; then
        return 1
    fi
    return 0
}

# Function to validate a single Terraform file
validate_tf_file() {
    local file="$1"
    local dir="$(dirname "$file")"
    local filename="$(basename "$file")"
    local failed=false

    echo -n "  Checking $filename... "

    # Check terraform fmt
    if ! terraform fmt -check "$file" &>/dev/null; then
        FORMAT_FAILURES+=("$file")
        echo -e "${RED}✗ Format${NC}"
        failed=true
    fi

    # Check for placeholder values
    if ! check_placeholders "$file"; then
        PLACEHOLDER_WARNINGS+=("$file")
        echo -e "${YELLOW}⚠ Placeholders${NC}"
    fi

    # For validation, we need to be in the directory with the file
    # and have a minimal provider configuration
    (
        cd "$dir"

        # Create temporary provider config if it doesn't exist
        if [[ ! -f "provider.tf" ]] && [[ ! -f "00_provider.tf" ]]; then
            cat > .provider_temp.tf <<EOF
terraform {
  required_providers {
    ${PROVIDER_NAME} = {
      source = "local/providers/${PROVIDER_NAME}"
      version = ">= 0.0.1"
    }
  }
}

provider "${PROVIDER_NAME}" {}
EOF
            trap "rm -f .provider_temp.tf" EXIT
        fi

        # Initialize if needed (suppress output)
        if [[ ! -d ".terraform" ]]; then
            terraform init -backend=false &>/dev/null || true
        fi

        # Run validate
        if ! terraform validate &>/dev/null; then
            VALIDATE_FAILURES+=("$file")
            echo -e "${RED}✗ Validate${NC}"
            failed=true
            exit 1
        fi
    ) 2>/dev/null

    if [[ "$failed" == "false" ]]; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED_FILES++))
    else
        ((FAILED_FILES++))
    fi

    ((TOTAL_FILES++))
}

# Process all example directories
for dir in "${EXAMPLES_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        echo -e "${BLUE}📂 Scanning $dir${NC}"

        # Find all .tf files
        while IFS= read -r -d '' file; do
            validate_tf_file "$file"
        done < <(find "$dir" -name "*.tf" -type f -print0 2>/dev/null)

        echo ""
    fi
done

# Print summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Validation Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Total files checked: ${TOTAL_FILES}"
echo -e "Passed: ${GREEN}${PASSED_FILES}${NC}"
echo -e "Failed: ${RED}${FAILED_FILES}${NC}"

# Report format failures
if [[ ${#FORMAT_FAILURES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ Format Check Failures:${NC}"
    for file in "${FORMAT_FAILURES[@]}"; do
        echo -e "  • ${file#$PROJECT_ROOT/}"
    done
    echo -e "\n${YELLOW}💡 Fix format issues with: terraform fmt -recursive${NC}"
fi

# Report validation failures
if [[ ${#VALIDATE_FAILURES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ Validation Failures:${NC}"
    for file in "${VALIDATE_FAILURES[@]}"; do
        echo -e "  • ${file#$PROJECT_ROOT/}"
    done
fi

# Report placeholder warnings
if [[ ${#PLACEHOLDER_WARNINGS[@]} -gt 0 ]]; then
    echo -e "\n${YELLOW}⚠️  Files with placeholder values:${NC}"
    for file in "${PLACEHOLDER_WARNINGS[@]}"; do
        echo -e "  • ${file#$PROJECT_ROOT/}"
    done
    echo -e "${YELLOW}Consider replacing with realistic examples${NC}"
fi

# Exit code based on failures
if [[ $FAILED_FILES -gt 0 ]]; then
    echo -e "\n${RED}❌ Validation failed for $FAILED_FILES file(s)${NC}"
    exit 1
else
    echo -e "\n${GREEN}✅ All examples passed validation!${NC}"
    exit 0
fi
