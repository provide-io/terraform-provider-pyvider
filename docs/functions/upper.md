---
page_title: "Function: upper"
description: |-
  Converts a string to uppercase with null-safe handling
---
# upper (Function)

The `upper` function takes a string and returns a new string with all alphabetic characters converted to uppercase. It handles null values gracefully by returning null when the input is null, making it safe for use with optional or dynamic string values.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Case conversion is fundamental for text normalization and comparison operations. Converting text to uppercase ensures consistent formatting for configuration values, environment variables, and case-insensitive matching scenarios.

## Capabilities

This function enables you to:

- **Case normalization**: Standardize text case for comparisons and consistency
- **Display formatting**: Format text for headers or emphasis in outputs
- **Data consistency**: Normalize user input or imported data to uppercase
- **Configuration values**: Standardize environment or configuration strings
- **Search operations**: Normalize text for case-insensitive matching

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

``upper(str)``

## Arguments





## Return Value

Returns a new string with all alphabetic characters converted to uppercase:
- Non-alphabetic characters (numbers, symbols, spaces) remain unchanged
- Returns `null` if the input is `null`
- Returns an empty string if the input is an empty string

## Common Patterns

### Environment Variables
```terraform
variable "env" {
  type = string
  default = "dev"
}

locals {
  environment_upper = provider::pyvider::upper(var.env)
}

resource "pyvider_file_content" "config" {
  filename = "/tmp/app_config.env"
  content  = "ENVIRONMENT=${local.environment_upper}"
}
```

### Header Formatting
```terraform
variable "service_name" {
  default = "api gateway"
}

locals {
  service_header = provider::pyvider::upper(var.service_name)  # "API GATEWAY"
}
```

## Related Components

- **lower** (Function) - Convert strings to lowercase
- **to_snake_case** (Function) - Convert to snake_case format
- **to_camel_case** (Function) - Convert to camelCase format
- **to_kebab_case** (Function) - Convert to kebab-case format

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
