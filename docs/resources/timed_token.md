---
page_title: "Resource: pyvider_timed_token"
description: |-
  Generates time-limited authentication tokens with automatic expiration management
---
# pyvider_timed_token (Resource)

The `pyvider_timed_token` resource creates time-limited authentication tokens that automatically expire after a specified duration. This is useful for generating temporary access credentials, API keys, or session tokens with built-in security through automatic expiration.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

## Examples

Explore these examples to see the resource in action:

- **[example.tf](examples/example.tf)** - Basic timed token generation
- **[basic.tf](examples/basic.tf)** - Simple token creation
- **[cicd.tf](examples/cicd.tf)** - CI/CD pipeline token patterns
- **[comprehensive.tf](examples/comprehensive.tf)** - Advanced token management scenarios

## Argument Reference



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

## Related Components

- **pyvider_private_state_verifier** (Resource) - Verify private state encryption for sensitive token storage
- **pyvider_http_api** (Data Source) - Use tokens for API authentication
- **pyvider_file_content** (Resource) - Write token configuration to files