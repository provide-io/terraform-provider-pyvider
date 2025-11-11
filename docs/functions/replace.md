---
page_title: "Function: replace"
description: |-
  Replaces all occurrences of a substring with another string
---
# replace (Function)

The `replace` function searches for all occurrences of a substring within a string and replaces them with a replacement string. It handles null values gracefully and performs global replacement, replacing all occurrences rather than just the first match.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


String replacement is fundamental for text manipulation, configuration templating, and data cleaning. The function's global replacement behavior ensures consistent transformations across entire strings.

## Capabilities

This function enables you to:

- **Text normalization**: Replace unwanted characters or patterns for standardization
- **Path manipulation**: Convert path separators or modify path structures
- **Configuration templating**: Replace placeholders in configuration templates dynamically
- **Data cleaning**: Remove or replace invalid characters from input data
- **URL manipulation**: Modify URLs or endpoints for different environments

## Example Usage

```terraform
locals {
  example_result = upper(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of upper function"
  value       = local.example_result
}

```

## Signature

``replace(str, old, new)``

## Arguments





## Return Value

Returns a new string with all occurrences of the search string replaced:
- Replaces ALL occurrences (global replacement)
- Case-sensitive matching
- Returns the original string if no matches found
- Returns `null` if the input string is `null`
- Empty search string returns original string unchanged

## Common Patterns

### Configuration Templating
```terraform
variable "environment" {
  default = "production"
}

locals {
  template = "Deploying to ENV_PLACEHOLDER environment"
  message = provider::pyvider::replace(local.template, "ENV_PLACEHOLDER", var.environment)
  # Result: "Deploying to production environment"
}
```

### Path Manipulation
```terraform
variable "windows_path" {
  default = "C:\\Program Files\\MyApp"
}

locals {
  unix_path = provider::pyvider::replace(var.windows_path, "\\", "/")
  # Result: "C:/Program Files/MyApp"
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
