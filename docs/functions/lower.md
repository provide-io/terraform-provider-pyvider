---
page_title: "Function: lower"
description: |-
  Converts a string to lowercase with null-safe handling
---
# lower (Function)

The `lower` function takes a string and returns a new string with all alphabetic characters converted to lowercase. It handles null values gracefully by returning null when the input is null, ensuring safe operation with optional or dynamic string values.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Lowercase conversion is essential for normalizing text input, creating consistent identifiers, and performing case-insensitive operations. The function preserves non-alphabetic characters while transforming all letters to their lowercase equivalents.

## Capabilities

This function enables you to:

- **Case normalization**: Standardize text case for consistent processing
- **Identifier creation**: Create lowercase identifiers from mixed-case input
- **Data consistency**: Normalize user input or imported data to lowercase
- **Comparison operations**: Prepare strings for case-insensitive comparison
- **URL generation**: Create lowercase URL segments from titles

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

``lower(str)``

## Arguments





## Return Value

Returns a new string with all alphabetic characters converted to lowercase:
- Non-alphabetic characters (numbers, symbols, spaces) remain unchanged
- Returns `null` if the input is `null`
- Returns an empty string if the input is an empty string

## Common Patterns

### Identifier Normalization
```terraform
variable "resource_name" {
  default = "MyApplication"
}

locals {
  normalized_name = provider::pyvider::lower(var.resource_name)  # "myapplication"
}
```

### Case-Insensitive Comparison
```terraform
variable "environment" {
  type = string
}

locals {
  is_production = provider::pyvider::lower(var.environment) == "production"
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
