terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}

# Configure the provider with values that match the 'api' capability schema.
# The framework should dynamically generate a config class from this schema
# and make it available to all components.
provider "pyvider" {
  api_endpoint             = "https://api.example.com/v1"
  api_token                = "my-secret-token-is-very-secret"
  api_timeout              = 60
  api_retries              = 5
  api_insecure_skip_verify = true
  api_headers = {
    "X-Custom-Header" = "Pyvider-E2E-Test"
    "Accept"          = "application/json"
  }
}

# Use our diagnostic data source to read the configuration back.
# If this works, the entire dynamic configuration pipeline is validated.
data "pyvider_provider_config_reader" "test_read" {}

# Output the values to verify they match the inputs.
output "read_api_endpoint" {
  description = "Verifies the api_endpoint was configured correctly."
  value       = data.pyvider_provider_config_reader.test_read.api_endpoint
}

output "read_api_token" {
  description = "Verifies the api_token was configured correctly."
  value       = data.pyvider_provider_config_reader.test_read.api_token
  sensitive   = true
}

output "read_api_timeout" {
  description = "Verifies the api_timeout was configured correctly."
  value       = data.pyvider_provider_config_reader.test_read.api_timeout
}

output "read_api_retries" {
  description = "Verifies the api_retries was configured correctly."
  value       = data.pyvider_provider_config_reader.test_read.api_retries
}

output "read_api_insecure_skip_verify" {
  description = "Verifies the api_insecure_skip_verify was configured correctly."
  value       = data.pyvider_provider_config_reader.test_read.api_insecure_skip_verify
}

output "read_api_headers" {
  description = "Verifies the api_headers were configured correctly."
  value       = data.pyvider_provider_config_reader.test_read.api_headers
}
