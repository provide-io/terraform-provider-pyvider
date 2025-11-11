---
page_title: "Function: tostring"
description: |-
  Explicitly converts values to strings with null-safe handling and boolean normalization
---
# tostring (Function)

The `tostring` function takes any value and converts it to a string representation. It handles different data types appropriately, including special formatting for booleans, and provides null-safe conversion for use in configuration files, templates, and outputs.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Type conversion is essential when working with mixed-type data in Terraform configurations. This function ensures consistent string representation across different value types, making it reliable for template generation, file content creation, and API integration.

## Capabilities

This function enables you to:

- **Template generation**: Convert values for use in string templates and interpolations
- **File content creation**: Prepare values for writing to configuration files
- **Logging and output**: Format values for display or logging in readable form
- **API integration**: Convert values to string format required by external APIs
- **Configuration normalization**: Ensure consistent string representation across configurations

## Example Usage

```terraform
locals {
  example_result = tostring(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of tostring function"
  value       = local.example_result
}

```

## Signature

``tostring(input)``

## Arguments





## Return Value

Returns the string representation of the value:
- **Numbers**: Converted to decimal string representation (e.g., `42` → `"42"`)
- **Booleans**: Converted to lowercase strings (`true` → `"true"`, `false` → `"false"`)
- **Strings**: Returned unchanged
- **Other types**: Converted using standard string representation
- Returns `null` if the input is `null`

## Type-Specific Behavior

The function handles different types appropriately:
- Numbers are converted to their decimal string representation without scientific notation
- Booleans are converted to lowercase "true" or "false" for consistency
- Strings pass through unchanged
- Null values return null rather than the string "null"

## Common Patterns

### Configuration File Generation
```terraform
variable "enabled" {
  type = bool
  default = true
}

variable "port" {
  type = number
  default = 8080
}

locals {
  config_content = "enabled=${provider::pyvider::tostring(var.enabled)}\nport=${provider::pyvider::tostring(var.port)}"
}

resource "pyvider_file_content" "config" {
  filename = "/tmp/app.conf"
  content  = local.config_content
}
```

### Template Processing
```terraform
variable "settings" {
  type = object({
    debug = bool
    timeout = number
    name = string
  })
  default = {
    debug = true
    timeout = 30
    name = "myapp"
  }
}

locals {
  settings_str = {
    for key, value in var.settings :
    key => provider::pyvider::tostring(value)
  }
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
