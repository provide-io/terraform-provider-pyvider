---
page_title: "Function: length"
description: |-
  Returns the length of lists, maps, or strings with null-safe handling
---
# length (Function)

The `length` function counts the number of elements in a collection and returns the count as an integer. It works seamlessly with lists, maps (dictionaries), and strings, handling null values gracefully to prevent errors in dynamic configurations.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This versatile function is fundamental for validation, conditional logic, and resource scaling. Whether you need to determine loop bounds, validate collection sizes, or make decisions based on data volume, `length` provides a reliable and type-agnostic way to measure your data.

## Capabilities

This function enables you to:

- **Validation**: Check if collections have expected sizes to enforce constraints
- **Conditional logic**: Make decisions based on collection size for dynamic behavior
- **Loop bounds**: Determine iteration limits for resource creation
- **Resource scaling**: Scale resources based on collection size automatically
- **Capacity planning**: Assess data volume to optimize performance

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

``length(input)``

## Arguments





## Return Value

Returns the count of elements as an integer:
- **Lists**: Number of elements in the list
- **Maps/Objects**: Number of key-value pairs
- **Strings**: Number of characters (including spaces)
- Returns `null` if the input is `null`
- Returns `0` for empty collections

## Behavior with Different Types

The function adapts its behavior based on the input type. For lists, it counts all elements including null values. For maps, it counts key-value pairs regardless of value types. For strings, it counts all characters including whitespace and Unicode characters.

## Common Patterns

### Validation
```terraform
variable "required_tags" {
  type = list(string)
  validation {
    condition     = provider::pyvider::length(var.required_tags) > 0
    error_message = "At least one tag is required."
  }
}

variable "user_config" {
  type = map(string)
  validation {
    condition     = provider::pyvider::length(var.user_config) <= 10
    error_message = "Configuration cannot have more than 10 keys."
  }
}
```

### Conditional Resource Creation
```terraform
variable "backup_servers" {
  type = list(string)
  default = []
}

locals {
  needs_load_balancer = provider::pyvider::length(var.backup_servers) > 1
}

resource "pyvider_file_content" "load_balancer_config" {
  count = local.needs_load_balancer ? 1 : 0

  filename = "/tmp/load_balancer.conf"
  content  = "Servers: ${provider::pyvider::join(",", var.backup_servers)}"
}
```

### Dynamic Scaling
```terraform
variable "applications" {
  type = list(object({
    name = string
    port = number
  }))
}

locals {
  app_count = provider::pyvider::length(var.applications)
  min_instances = provider::pyvider::max([local.app_count, 2])
}

resource "pyvider_local_directory" "app_dirs" {
  count = local.min_instances
  path  = "/tmp/app_${count.index + 1}"
}
```

## Related Components

- **contains** (Function) - Check if a list contains an element
- **lookup** (Function) - Look up values in maps
- **max** (Function) - Find maximum value
- **min** (Function) - Find minimum value

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
