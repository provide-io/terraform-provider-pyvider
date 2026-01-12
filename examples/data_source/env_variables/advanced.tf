# Before running, export the following variables:
# export API_URL="https://api.example.com"
# export API_TOKEN="secret-token-value"
# export API_TIMEOUT="60"

# Read all variables with a common prefix
data "pyvider_env_variables" "api_config" {
  prefix         = "API_"
  case_sensitive = true
  sensitive_keys = ["API_TOKEN"]
}

output "advanced_api_endpoint" {
  description = "The API endpoint URL."
  value       = lookup(data.pyvider_env_variables.api_config.values, "API_URL", "https://default.example.com")
}

output "advanced_api_timeout" {
  description = "The configured API timeout."
  value       = lookup(data.pyvider_env_variables.api_config.values, "API_TIMEOUT", "30")
}

output "advanced_api_token_is_sensitive" {
  description = "Demonstrates that the token is in the sensitive_values map."
  value       = "The API token is present in the sensitive outputs."
  sensitive   = true
}
