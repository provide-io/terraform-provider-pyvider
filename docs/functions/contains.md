---
page_title: "Function: contains"
description: |-
  Checks if a list contains a specific element with null-safe handling
---
# contains (Function)

The `contains` function searches through a list to determine if it contains a specific element. It performs exact matching and handles null values gracefully, returning a boolean result. This function is essential for validation, conditional logic, and security checks in Terraform configurations.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Type-sensitive matching ensures that both the type and value must match for a positive result. The function handles null values in both the input list and the search element, making it safe to use with optional or dynamic configurations.

## Capabilities

This function enables you to:

- **Validation**: Check if required values are present in lists to ensure configuration correctness
- **Conditional logic**: Make decisions based on list membership for dynamic resource creation
- **Security checks**: Verify if values are in allowlists or blocklists to control access
- **Feature toggles**: Check if features are enabled in configuration lists for conditional features
- **Data filtering**: Determine if items meet criteria before processing

## Example Usage

```terraform
locals {
  example_result = length(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of length function"
  value       = local.example_result
}

```

## Signature

``contains(input)``

## Arguments





## Return Value

Returns a boolean indicating whether the element was found:
- `true` if the element exists in the list
- `false` if the element does not exist in the list
- Returns `null` if the input list is `null`
- Uses exact equality comparison (type and value must match)

## Type-Sensitive Matching

The function performs type-aware comparisons, meaning that values of different types will not match even if they appear similar. For example, the number `1` and the string `"1"` are treated as distinct values. This ensures precise matching in mixed-type lists.

## Common Patterns

### Environment Validation
```terraform
variable "environment" {
  type = string
}

locals {
  valid_environments = ["development", "staging", "production"]
  is_valid_env = provider::pyvider::contains(local.valid_environments, var.environment)
}

resource "pyvider_file_content" "env_check" {
  count = local.is_valid_env ? 1 : 0

  filename = "/tmp/environment.txt"
  content  = "Environment ${var.environment} is valid"
}
```

### Feature Toggle Management
```terraform
variable "enabled_features" {
  type = list(string)
  default = ["feature_a", "feature_c"]
}

locals {
  feature_flags = {
    analytics_enabled = provider::pyvider::contains(var.enabled_features, "analytics")
    debug_enabled = provider::pyvider::contains(var.enabled_features, "debug")
    feature_a_enabled = provider::pyvider::contains(var.enabled_features, "feature_a")
  }
}
```

### Security Allowlist/Blocklist
```terraform
variable "client_ip" {
  type = string
}

variable "allowed_ips" {
  type = list(string)
}

variable "blocked_ips" {
  type = list(string)
}

locals {
  is_allowed = provider::pyvider::contains(var.allowed_ips, var.client_ip)
  is_blocked = provider::pyvider::contains(var.blocked_ips, var.client_ip)
  access_granted = local.is_allowed && !local.is_blocked
}
```

## Related Components

- **length** (Function) - Get the size of collections
- **lookup** (Function) - Look up values in maps for key-value searches
- **split** (Function) - Split strings to create searchable lists
- **join** (Function) - Join lists after filtering