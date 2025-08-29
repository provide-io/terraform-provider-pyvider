# Read the provider configuration
# This data source reads the configuration passed to the provider block
data "pyvider_provider_config_reader" "config" {}

output "provider_api_endpoint" {
  description = "The configured API endpoint"
  value       = data.pyvider_provider_config_reader.config.api_endpoint
}

output "provider_api_timeout" {
  description = "The configured API timeout"
  value       = data.pyvider_provider_config_reader.config.api_timeout
}

output "provider_api_retries" {
  description = "The configured number of API retries"
  value       = data.pyvider_provider_config_reader.config.api_retries
}

output "provider_api_headers" {
  description = "The configured API headers"
  value       = data.pyvider_provider_config_reader.config.api_headers
}

output "provider_insecure_skip_verify" {
  description = "Whether TLS verification is skipped"
  value       = data.pyvider_provider_config_reader.config.api_insecure_skip_verify
}

# Note: api_token is sensitive and should be handled carefully
output "has_api_token" {
  description = "Whether an API token is configured"
  value       = data.pyvider_provider_config_reader.config.api_token != null
  sensitive   = true
}
