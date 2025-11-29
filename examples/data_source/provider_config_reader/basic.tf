# Basic provider configuration reader examples

# Example 1: Read current provider configuration
data "pyvider_provider_config_reader" "current" {}

# Example 2: Simple configuration checks
locals {
  has_endpoint = data.pyvider_provider_config_reader.current.api_endpoint != null
  has_auth     = data.pyvider_provider_config_reader.current.api_token != null
  is_secure    = data.pyvider_provider_config_reader.current.api_insecure_skip_verify != true
}

# Example 3: Create configuration summary file
resource "pyvider_file_content" "config_summary" {
  filename = "/tmp/provider_config_summary.txt"
  content = join("\n", [
    "=== Provider Configuration ===",
    "",
    "Endpoint: ${local.has_endpoint ? "Configured" : "Not configured"}",
    "Authentication: ${local.has_auth ? "Configured" : "Not configured"}",
    "TLS Verification: ${local.is_secure ? "Enabled" : "Disabled"}",
    "",
    "Generated at: ${timestamp()}"
  ])
}

output "provider_config" {
  sensitive = true
  value = {
    has_endpoint = local.has_endpoint
    has_auth     = local.has_auth
    is_secure    = local.is_secure
    timeout      = data.pyvider_provider_config_reader.current.api_timeout
    retries      = data.pyvider_provider_config_reader.current.api_retries
  }
}
