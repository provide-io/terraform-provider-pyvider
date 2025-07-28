#!/bin/bash
#
# This script sets up a comprehensive set of environment variables
# for testing the pyvider_env_variables data source.
#
# To use:
# 1. Make it executable: chmod +x env_test_vars.sh
# 2. Source it in your shell: source ./env_test_vars.sh
# 3. Run 'tofu plan' or 'tofu apply' in this directory.

echo "Setting up environment variables for Pyvider test..."

# --- Basic Test Variables ---
export TEST_VAR1="Hello"
echo "  - Set TEST_VAR1"

export TEST_VAR2="World"
echo "  - Set TEST_VAR2"

# --- Sensitive Variable ---
export TEST_SENSITIVE_TOKEN="super-secret-token-123-abc-XYZ"
echo "  - Set TEST_SENSITIVE_TOKEN"

# --- Variable for Case-Insensitive Testing ---
export test_var_lower="this key is lowercase"
echo "  - Set test_var_lower"

# --- Variable for Regex Testing ---
export REGEX_TEST_VARX="This matches the regex"
echo "  - Set REGEX_TEST_VARX"

# --- Empty and Special Character Variables ---
export TEST_EMPTY_VAR=""
echo "  - Set TEST_EMPTY_VAR (empty)"

export TEST_VAR_WITH_SPACES="this value has spaces"
echo "  - Set TEST_VAR_WITH_SPACES"

export TEST_VAR_SPECIAL_CHARS="value-with-special-chars!@#\$%^&*()"
echo "  - Set TEST_VAR_SPECIAL_CHARS"

# --- Unset a variable to ensure it's not picked up ---
unset NON_EXISTENT_VAR
echo "  - Unset NON_EXISTENT_VAR"

echo ""
echo "✅ Environment variables are set. You can now run 'tofu plan'."
