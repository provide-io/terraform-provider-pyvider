# env_vars_test.tf
# Comprehensive test for the pyvider_env_variables data source.
#
# Before running, ensure these environment variables are set:
# source ./env_test_vars.sh

terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}

provider "pyvider" {
}

# --- Test Cases ---

# Test 1: Filter by a specific list of keys
data "pyvider_env_variables" "by_keys" {
  keys = ["TEST_VAR1", "TEST_VAR2", "TEST_SENSITIVE_TOKEN", "NON_EXISTENT_VAR"]
}

# Test 2: Filter by prefix (case-sensitive)
data "pyvider_env_variables" "by_prefix_sensitive" {
  prefix = "TEST_"
}

# Test 3: Filter by prefix (case-insensitive) and transform keys to lower
data "pyvider_env_variables" "by_prefix_insensitive" {
  prefix           = "test_"
  case_sensitive   = false
  transform_keys   = "lower"
  transform_values = "upper"
}

# Test 4: Filter by regex
data "pyvider_env_variables" "by_regex" {
  # DEFINITIVE FIX: Use a regex that correctly finds keys containing 'VAR'.
  # This pattern matches any characters, followed by 'VAR', followed by any characters.
  regex = ".*VAR.*"
}

# Test 5: Handle sensitive keys correctly
data "pyvider_env_variables" "with_sensitive" {
  keys           = ["TEST_VAR1", "TEST_SENSITIVE_TOKEN"]
  sensitive_keys = ["TEST_SENSITIVE_TOKEN"]
}

# Test 6: Test exclude_empty flag
data "pyvider_env_variables" "with_empty" {
  keys          = ["TEST_VAR1", "TEST_EMPTY_VAR"]
  exclude_empty = true # This is the default, but we're being explicit
}

data "pyvider_env_variables" "without_empty" {
  keys          = ["TEST_VAR1", "TEST_EMPTY_VAR"]
  exclude_empty = false
}


# --- Outputs ---

output "by_keys_result" {
  description = "Result of filtering by specific keys."
  value       = data.pyvider_env_variables.by_keys.values
}

output "by_prefix_sensitive_result" {
  description = "Result of case-sensitive prefix filtering."
  value       = data.pyvider_env_variables.by_prefix_sensitive.values
}

output "by_prefix_insensitive_result" {
  description = "Result of case-insensitive prefix filtering with transformations."
  value       = data.pyvider_env_variables.by_prefix_insensitive.values
}

output "by_regex_result" {
  description = "Result of regex filtering."
  value       = data.pyvider_env_variables.by_regex.values
}

output "with_sensitive_result" {
  description = "Demonstrates sensitive key handling. The sensitive value should be redacted in CLI output."
  value       = data.pyvider_env_variables.with_sensitive.all_values
  sensitive   = true # Mark the whole output as sensitive for safety
}

output "with_sensitive_nonsensitive_part" {
  description = "The non-sensitive part of the sensitive test."
  value       = data.pyvider_env_variables.with_sensitive.values
}

output "with_sensitive_sensitive_part" {
  description = "The sensitive part of the sensitive test."
  value       = data.pyvider_env_variables.with_sensitive.sensitive_values
  sensitive   = true
}

output "exclude_empty_result" {
  description = "Should only contain TEST_VAR1."
  value       = data.pyvider_env_variables.with_empty.values
}

output "include_empty_result" {
  description = "Should contain both TEST_VAR1 and an empty TEST_EMPTY_VAR."
  value       = data.pyvider_env_variables.without_empty.values
}

output "full_environment_seen_by_provider" {
  description = "A complete dump of the environment as seen by the provider process."
  value       = data.pyvider_env_variables.by_keys.all_environment
  sensitive   = true
}
