---
page_title: "Resource: pyvider_timed_token"
description: |-
  Generates time-limited authentication tokens with automatic expiration management
---
# pyvider_timed_token (Resource)

The `pyvider_timed_token` resource creates time-limited authentication tokens that automatically expire after a specified duration. This is useful for generating temporary access credentials, API keys, or session tokens with built-in security through automatic expiration.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


This resource demonstrates time-based credential management within Terraform, showcasing how to generate secure, ephemeral tokens with built-in expiration. The tokens are stored securely using Terraform's private state encryption and can be used for temporary API access, session management, automated workflows, and testing scenarios that require time-limited authentication.

## Capabilities

This resource enables you to:

- **Temporary API access**: Generate short-lived tokens for external integrations and API authentication
- **Session management**: Create time-limited session tokens for application workflows
- **Secure automation**: Provide temporary credentials for CI/CD pipelines and automated processes
- **Token rotation**: Implement automatic token refresh and rotation strategies
- **Testing and development**: Generate test tokens with predictable expiration for development environments
- **Private state encryption**: Store tokens securely using Terraform's private state encryption
- **Automatic expiration**: Tokens expire automatically without manual cleanup
- **Unique token generation**: Each token has a unique UUID-based identifier

## Prerequisites

This resource keeps encrypted private state, which the provider will not do
without a shared secret. Supply one before applying, or the first apply fails
with `Private state shared secret not configured`:

```bash
export PYVIDER_PRIVATE_STATE_SHARED_SECRET="a-long-random-value"
```

`private_state_shared_secret` in `pyvider.toml` does the same thing. Keep the
value stable across runs -- private state written under one secret cannot be
read back under another.

## Example Usage

```terraform
resource "pyvider_timed_token" "simple_token" {
  name = "test-token"
}

output "example_token_id" {
  description = "The ID of the pyvider_timed_token resource"
  value       = pyvider_timed_token.simple_token.id
  sensitive   = true
}

```

## More Examples

### Simple token creation

```terraform
# Generate a timed token
resource "pyvider_timed_token" "example" {
  name = "demo-token"
}

output "basic_token_info" {
  value = {
    token_id   = pyvider_timed_token.example.id
    expires_at = pyvider_timed_token.example.expires_at
  }
  sensitive = true
}

```

### CI/CD pipeline token patterns

```terraform
# CI/CD pipeline with temporary tokens

# Generate short-lived token for CI pipeline
resource "pyvider_timed_token" "ci_deploy_token" {
  name = "cicd-deploy-token"
}

# Generate token for automated tests
resource "pyvider_timed_token" "test_runner_token" {
  name = "test-runner-token"
}

# Create config file with tokens
resource "pyvider_file_content" "ci_config" {
  filename = "/tmp/ci_config.env"
  content = provider::pyvider::join("\n", [
    "DEPLOY_TOKEN=${pyvider_timed_token.ci_deploy_token.token}",
    "TEST_TOKEN=${pyvider_timed_token.test_runner_token.token}",
    "EXPIRES_AT=${pyvider_timed_token.ci_deploy_token.expires_at}"
  ])
}

output "cicd_ci_tokens" {
  value = {
    deploy_token_expires = pyvider_timed_token.ci_deploy_token.expires_at
    test_token_expires   = pyvider_timed_token.test_runner_token.expires_at
    config_file          = pyvider_file_content.ci_config.filename
  }
  sensitive = true
}

```

### Advanced token management scenarios

```terraform
# Basic timed token examples

# Example 1: Simple token generation
resource "pyvider_timed_token" "simple" {
  name = "basic-example-token"
}

# Example 2: Token for API integration
resource "pyvider_timed_token" "api_auth" {
  name = "api-integration-token"
}

# Create configuration file with token metadata
resource "pyvider_file_content" "api_config" {
  filename = "/tmp/api_config.json"
  content = jsonencode({
    authentication = {
      token_id   = pyvider_timed_token.api_auth.id
      token_name = pyvider_timed_token.api_auth.name
      expires_at = pyvider_timed_token.api_auth.expires_at
      # Note: actual token value is sensitive and not exposed in config
    }
    api_endpoint    = "https://api.example.com/v1"
    timeout_seconds = 30
  })
}

# Example 3: Multiple tokens for different services
resource "pyvider_timed_token" "database" {
  name = "database-service-token"
}

resource "pyvider_timed_token" "cache" {
  name = "cache-service-token"
}

# Summary file
resource "pyvider_file_content" "token_summary" {
  filename = "/tmp/token_summary.txt"
  content = join("\n", [
    "=== Token Summary ===",
    "",
    "Simple Token:",
    "  ID: ${pyvider_timed_token.simple.id}",
    "  Name: ${pyvider_timed_token.simple.name}",
    "  Expires: ${pyvider_timed_token.simple.expires_at}",
    "",
    "API Token:",
    "  ID: ${pyvider_timed_token.api_auth.id}",
    "  Expires: ${pyvider_timed_token.api_auth.expires_at}",
    "",
    "Service Tokens:",
    "  Database: ${pyvider_timed_token.database.id}",
    "  Cache: ${pyvider_timed_token.cache.id}",
  ])
}

output "comprehensive_basic_token_examples" {
  description = "Information about created tokens (sensitive values excluded)"
  sensitive   = true
  value = {
    simple_token = {
      id         = pyvider_timed_token.simple.id
      name       = pyvider_timed_token.simple.name
      expires_at = pyvider_timed_token.simple.expires_at
    }
    api_token = {
      id         = pyvider_timed_token.api_auth.id
      name       = pyvider_timed_token.api_auth.name
      expires_at = pyvider_timed_token.api_auth.expires_at
    }
    service_tokens = {
      database = pyvider_timed_token.database.name
      cache    = pyvider_timed_token.cache.name
    }
  }
}

```

## Schema

### Required

- `name` (String)

### Read-Only

- `id` (String)
- `token` (String)
- `expires_at` (String)


## Computed Attributes

The resource provides the following computed attributes:

| Attribute | Type | Sensitivity | Description |
|-----------|------|-------------|-------------|
| `id` | string | Non-sensitive | Unique token identifier in format `timed-token-id-{uuid}` |
| `token` | string | Sensitive | The actual token value in format `token-{uuid}` |
| `expires_at` | string | Non-sensitive | Expiration timestamp in ISO 8601 format (UTC) |

## Token Lifecycle

The resource manages the complete lifecycle of time-limited tokens:

### 1. Creation
- Generates a unique token ID with UUID format: `timed-token-id-{uuid}`
- Creates a secure token string: `token-{uuid}`
- Sets expiration time to 1 hour from creation
- Stores sensitive token data in encrypted private state

### 2. Reading
- Returns current token and expiration information
- Automatically decrypts private state for secure access
- Maintains token validity status

### 3. Expiration
- Tokens expire automatically after the specified duration
- No cleanup required - tokens are self-invalidating
- Expiration time is stored in ISO 8601 format for easy parsing

### 4. Deletion
- Removes token from Terraform state
- No additional provider-side cleanup required

## Token Format Reference

| Component | Format | Example | Notes |
|-----------|--------|---------|-------|
| **ID** | `timed-token-id-{uuid}` | `timed-token-id-123e4567-e89b-12d3-a456-426614174000` | Unique identifier |
| **Token** | `token-{uuid}` | `token-123e4567-e89b-12d3-a456-426614174000` | Actual token value (sensitive) |
| **Expiration** | ISO 8601 | `2025-11-08T15:30:00Z` | UTC timestamp |

## Security Features

### Sensitive Data Protection

The `token` attribute is marked as sensitive and will not appear in Terraform logs or console output:

```terraform
resource "pyvider_timed_token" "secure_token" {
  name = "production-api-key"
}

# Safe: Check if token exists
output "token_available" {
  value = pyvider_timed_token.secure_token.token != null
}

# Safe: Show expiration time
output "token_expires_at" {
  value = pyvider_timed_token.secure_token.expires_at
}
```

### Private State Encryption

The resource uses Terraform's private state encryption to securely store:
- The actual token value
- Expiration timestamp
- Internal token metadata

## Common Use Patterns

### Token Rotation Strategy

```terraform
# Create multiple tokens for rotation
resource "pyvider_timed_token" "primary" {
  name = "primary-token"
}

resource "pyvider_timed_token" "backup" {
  name = "backup-token"
}

# Application config with fallback
resource "pyvider_file_content" "app_config" {
  filename = "/app/config/tokens.json"
  content = jsonencode({
    primary_token = {
      value = pyvider_timed_token.primary.token
      expires_at = pyvider_timed_token.primary.expires_at
    }
    backup_token = {
      value = pyvider_timed_token.backup.token
      expires_at = pyvider_timed_token.backup.expires_at
    }
  })
}
```

### Environment-Specific Tokens

```terraform
variable "environment" {
  type = string
}

resource "pyvider_timed_token" "env_token" {
  name = "${var.environment}-api-token"
}
```

### Integration with External Systems

```terraform
resource "pyvider_timed_token" "webhook_token" {
  name = "webhook-authentication"
}

# Use token for API authentication
data "pyvider_http_api" "register_webhook" {
  url    = "https://api.example.com/webhooks"
  method = "POST"
  headers = {
    "Authorization" = "Bearer ${pyvider_timed_token.webhook_token.token}"
  }
}
```

## Import

```bash
terraform import pyvider_timed_token.example <id>
```