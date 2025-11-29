# Comprehensive env_variables example: Complete feature showcase
# Demonstrates filtering, regex, transformations, sensitive handling, and exclusions
#
# Before running, ensure these environment variables are set:
# export TEST_VAR1="value1"
# export TEST_VAR2="value2"
# export TEST_SENSITIVE_TOKEN="secret123"
# export TEST_EMPTY_VAR=""

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

# Test 4: Filter by regex pattern
data "pyvider_env_variables" "by_regex" {
  # Matches any keys containing 'VAR'
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

output "comprehensive_by_keys_result" {
  description = "Result of filtering by specific keys."
  value       = data.pyvider_env_variables.by_keys.values
}

output "comprehensive_by_prefix_sensitive_result" {
  description = "Result of case-sensitive prefix filtering."
  value       = data.pyvider_env_variables.by_prefix_sensitive.values
}

output "comprehensive_by_prefix_insensitive_result" {
  description = "Result of case-insensitive prefix filtering with transformations."
  value       = data.pyvider_env_variables.by_prefix_insensitive.values
}

output "comprehensive_by_regex_result" {
  description = "Result of regex filtering."
  value       = data.pyvider_env_variables.by_regex.values
}

output "comprehensive_with_sensitive_result" {
  description = "Demonstrates sensitive key handling. The sensitive value should be redacted in CLI output."
  value       = data.pyvider_env_variables.with_sensitive.all_values
  sensitive   = true # Mark the whole output as sensitive for safety
}

output "comprehensive_with_sensitive_nonsensitive_part" {
  description = "The non-sensitive part of the sensitive test."
  value       = data.pyvider_env_variables.with_sensitive.values
}

output "comprehensive_with_sensitive_sensitive_part" {
  description = "The sensitive part of the sensitive test."
  value       = data.pyvider_env_variables.with_sensitive.sensitive_values
  sensitive   = true
}

output "comprehensive_exclude_empty_result" {
  description = "Should only contain TEST_VAR1."
  value       = data.pyvider_env_variables.with_empty.values
}

output "comprehensive_include_empty_result" {
  description = "Should contain both TEST_VAR1 and an empty TEST_EMPTY_VAR."
  value       = data.pyvider_env_variables.without_empty.values
}

output "comprehensive_full_environment_seen_by_provider" {
  description = "A complete dump of the environment as seen by the provider process."
  value       = data.pyvider_env_variables.by_keys.all_environment
  sensitive   = true
}
