# Read specific environment variables
data "pyvider_env_variables" "specific" {
  keys = ["PATH", "HOME", "USER"]
}

# Read all variables with a prefix
data "pyvider_env_variables" "prefixed" {
  prefix = "TF_"
}

# Read variables matching a regex pattern
data "pyvider_env_variables" "pattern" {
  regex = ".*_TOKEN.*"
  sensitive_keys = ["API_TOKEN", "AUTH_TOKEN"]
}

# Read with transformations
data "pyvider_env_variables" "transformed" {
  prefix           = "app_"
  case_sensitive   = false
  transform_keys   = "lower"
  transform_values = "upper"
  exclude_empty    = true
}

output "specific_vars" {
  description = "Specific environment variables"
  value       = data.pyvider_env_variables.specific.values
}

output "prefixed_vars" {
  description = "Variables with TF_ prefix"
  value       = data.pyvider_env_variables.prefixed.values
}

output "pattern_vars_nonsensitive" {
  description = "Non-sensitive variables matching pattern"
  value       = data.pyvider_env_variables.pattern.values
}

output "pattern_vars_sensitive" {
  description = "Sensitive variables matching pattern"
  value       = data.pyvider_env_variables.pattern.sensitive_values
  sensitive   = true
}

output "transformed_vars" {
  description = "Transformed environment variables"
  value       = data.pyvider_env_variables.transformed.values
}
