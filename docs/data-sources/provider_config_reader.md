---
page_title: "Data Source: pyvider_provider_config_reader"
description: |-
  Reads provider configuration settings for dynamic resource management
---
# pyvider_provider_config_reader (Data Source)

The `pyvider_provider_config_reader` data source allows you to read the current provider configuration settings. This enables dynamic resource creation based on provider settings and helps create reusable configurations that adapt to different provider configurations.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This data source provides introspection capabilities for your Terraform provider configuration, allowing you to build adaptive infrastructure code that responds to the current provider context. By accessing provider settings at configuration time, you can implement environment-aware logic, validate configurations, and create more flexible Terraform modules that work across different deployment scenarios.

## Capabilities

This data source enables you to:

- **Dynamic resource configuration**: Adapt resource settings based on provider configuration values
- **Multi-environment deployments**: Use different API endpoints, timeouts, and settings per environment
- **Configuration validation**: Verify provider settings before proceeding with resource creation
- **Debugging and troubleshooting**: Inspect current provider configuration for diagnostics
- **Conditional logic**: Create or configure resources based on provider capabilities and settings
- **Multi-provider scenarios**: Read configuration from different provider instances (aliases)
- **API client configuration**: Configure API clients based on provider endpoint and timeout settings
- **Environment detection**: Determine the current environment based on provider configuration

## Example Usage

```terraform
data "pyvider_provider_config_reader" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_provider_config_reader"
  value       = data.pyvider_provider_config_reader.example
  sensitive   = true
}

```

## Examples

Explore these examples to see the data source in action:

- **[example.tf](examples/example.tf)** - Basic provider configuration reading
- **[basic.tf](examples/basic.tf)** - Simple configuration access patterns

## Argument Reference

## Schema

### Read-Only

- `api_endpoint` (String) - 
- `api_token` (String) - 
- `api_timeout` (String) - 
- `api_retries` (String) - 
- `api_insecure_skip_verify` (String) - 
- `api_headers` (Dynamic) - 


## Provider Configuration Attributes

The data source exposes the following provider configuration settings:

| Category | Attribute | Type | Sensitivity | Description |
|----------|-----------|------|-------------|-------------|
| **Connection** | `api_endpoint` | string | Non-sensitive | The API endpoint URL configured for the provider |
| | `api_timeout` | number | Non-sensitive | Request timeout in seconds |
| | `api_retries` | number | Non-sensitive | Number of retry attempts for failed requests |
| **Authentication** | `api_token` | string | Sensitive | API authentication token |
| | `api_headers` | map(string) | Non-sensitive | Custom headers sent with API requests |
| **Security** | `api_insecure_skip_verify` | bool | Non-sensitive | Whether TLS certificate verification is disabled |

## Common Use Patterns

### Environment-Aware Configuration

Determine the current environment and adjust settings accordingly:

```terraform
data "pyvider_provider_config_reader" "config" {}

locals {
  # Detect environment from API endpoint
  environment = (
    can(regex("staging", data.pyvider_provider_config_reader.config.api_endpoint)) ? "staging" :
    can(regex("prod", data.pyvider_provider_config_reader.config.api_endpoint)) ? "production" :
    "development"
  )

  # Adjust resource settings based on environment
  replica_count = local.environment == "production" ? 3 : 1
  debug_enabled = local.environment == "development"
}
```

### Configuration Validation

Validate provider configuration before resource creation:

```terraform
data "pyvider_provider_config_reader" "config" {}

locals {
  # Verify provider is properly configured
  config_valid = (
    data.pyvider_provider_config_reader.config.api_endpoint != null &&
    data.pyvider_provider_config_reader.config.api_timeout > 0 &&
    data.pyvider_provider_config_reader.config.api_retries >= 0
  )
}
```

### Conditional Resource Creation

Create resources only when specific provider settings are present:

```terraform
data "pyvider_provider_config_reader" "config" {}

# Only create debug resources with longer timeouts
resource "pyvider_file_content" "debug_config" {
  count = data.pyvider_provider_config_reader.config.api_timeout > 60 ? 1 : 0

  filename = "/tmp/debug_enabled.conf"
  content  = "Debug mode enabled"
}
```

### API Client Configuration

Generate API client configuration based on provider settings:

```terraform
data "pyvider_provider_config_reader" "config" {}

resource "pyvider_file_content" "api_client_config" {
  filename = "/tmp/api_client.json"
  content = jsonencode({
    endpoint = data.pyvider_provider_config_reader.config.api_endpoint
    timeout  = data.pyvider_provider_config_reader.config.api_timeout
    retries  = data.pyvider_provider_config_reader.config.api_retries
    headers  = data.pyvider_provider_config_reader.config.api_headers

    # Check if auth is configured without exposing token
    auth_configured = data.pyvider_provider_config_reader.config.api_token != null

    security = {
      tls_verify = !data.pyvider_provider_config_reader.config.api_insecure_skip_verify
    }
  })
}
```

### Multi-Provider Scenarios

Read configuration from different provider instances:

```terraform
# Configure multiple provider instances
provider "pyvider" {
  alias        = "staging"
  api_endpoint = "https://staging-api.example.com"
  api_timeout  = 30
}

provider "pyvider" {
  alias        = "production"
  api_endpoint = "https://api.example.com"
  api_timeout  = 60
}

# Read configuration from each provider
data "pyvider_provider_config_reader" "staging" {
  provider = pyvider.staging
}

data "pyvider_provider_config_reader" "production" {
  provider = pyvider.production
}

# Compare configurations
locals {
  staging_timeout    = data.pyvider_provider_config_reader.staging.api_timeout
  production_timeout = data.pyvider_provider_config_reader.production.api_timeout
  timeout_difference = local.production_timeout - local.staging_timeout
}
```

## Sensitive Data Handling

The `api_token` attribute is marked as sensitive and will not appear in Terraform logs or console output. You can check for its existence without exposing the value:

```terraform
data "pyvider_provider_config_reader" "config" {}

# Safe: Check if token exists
output "auth_configured" {
  value = data.pyvider_provider_config_reader.config.api_token != null
}

# Safe: Expose non-sensitive endpoint
output "provider_endpoint" {
  value = data.pyvider_provider_config_reader.config.api_endpoint
}
```

## Related Components

- **pyvider_env_variables** (Data Source) - Read environment variables used in provider configuration
- **pyvider_http_api** (Data Source) - Make requests using the provider's configured endpoint
- **pyvider_file_content** (Resource) - Create configuration files based on provider settings

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
