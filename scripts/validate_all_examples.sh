#!/usr/bin/env bash
# Validate all generated examples by running terraform init, plan, and apply
set -euo pipefail

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Counters
TOTAL_EXAMPLES=0
PASSED_EXAMPLES=0
FAILED_EXAMPLES=0
INIT_FAILURES=()
PLAN_FAILURES=()
APPLY_FAILURES=()

echo -e "${BLUE}🔍 Validating All Generated Examples${NC}\n"

cd "$PROJECT_ROOT"

# Find all example directories (those with main.tf)
while IFS= read -r example_dir; do
    ((TOTAL_EXAMPLES++))

    example_name="${example_dir#$PROJECT_ROOT/docs/examples/}"
    echo -ne "  [${TOTAL_EXAMPLES}] ${example_name}... "

    (
        cd "$example_dir"

        # Clean any previous state
        rm -rf .terraform .terraform.lock.hcl terraform.tfstate terraform.tfstate.backup 2>/dev/null || true

        # Initialize
        if ! timeout 30 terraform init -backend=false &>/dev/null; then
            echo -e "${RED}✗ init${NC}"
            INIT_FAILURES+=("$example_name")
            exit 1
        fi

        # Validate
        if ! timeout 15 terraform validate &>/dev/null; then
            echo -e "${RED}✗ validate${NC}"
            PLAN_FAILURES+=("$example_name")
            exit 1
        fi

        # Plan
        if ! timeout 30 terraform plan -out=tfplan &>/dev/null; then
            echo -e "${RED}✗ plan${NC}"
            PLAN_FAILURES+=("$example_name")
            exit 1
        fi

        # Apply (since no remote connections, should be safe)
        if ! timeout 30 terraform apply -auto-approve tfplan &>/dev/null; then
            echo -e "${RED}✗ apply${NC}"
            APPLY_FAILURES+=("$example_name")
            exit 1
        fi

        # Destroy to clean up
        timeout 30 terraform destroy -auto-approve &>/dev/null || true

        # Clean up
        rm -rf .terraform .terraform.lock.hcl terraform.tfstate terraform.tfstate.backup tfplan 2>/dev/null || true

    ) && {
        echo -e "${GREEN}✓${NC}"
        ((PASSED_EXAMPLES++))
    } || {
        ((FAILED_EXAMPLES++))
    }

done < <(find "$PROJECT_ROOT/docs/examples" -type f -name "main.tf" -exec dirname {} \; | sort -u)

# Print summary
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📊 Validation Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Total examples: ${TOTAL_EXAMPLES}"
echo -e "Passed: ${GREEN}${PASSED_EXAMPLES}${NC}"
echo -e "Failed: ${RED}${FAILED_EXAMPLES}${NC}"

# Report failures
if [[ ${#INIT_FAILURES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ Init Failures (${#INIT_FAILURES[@]}):${NC}"
    for example in "${INIT_FAILURES[@]}"; do
        echo -e "  • $example"
    done
fi

if [[ ${#PLAN_FAILURES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ Plan Failures (${#PLAN_FAILURES[@]}):${NC}"
    for example in "${PLAN_FAILURES[@]}"; do
        echo -e "  • $example"
    done
fi

if [[ ${#APPLY_FAILURES[@]} -gt 0 ]]; then
    echo -e "\n${RED}❌ Apply Failures (${#APPLY_FAILURES[@]}):${NC}"
    for example in "${APPLY_FAILURES[@]}"; do
        echo -e "  • $example"
    done
fi

# Exit code
if [[ $FAILED_EXAMPLES -gt 0 ]]; then
    echo -e "\n${RED}❌ ${FAILED_EXAMPLES} example(s) failed validation${NC}"
    exit 1
else
    echo -e "\n${GREEN}✅ All ${PASSED_EXAMPLES} examples passed validation!${NC}"
    exit 0
fi
