---
page_title: "Function: format"
description: |-
  Formats a string template using positional arguments with error handling
---
# format (Function)

The `format` function takes a template string with placeholders and a list of values, then returns a formatted string with the placeholders replaced by the corresponding values. It automatically converts values to strings and provides clear error messages for formatting issues.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Template-based string formatting enables dynamic message construction, configuration generation, and report creation. The function's automatic type conversion and positional substitution make it simple to combine static text with dynamic values.

## Capabilities

This function enables you to:

- **Message templating**: Create formatted messages with dynamic content for outputs
- **Path construction**: Build complex paths with multiple variables
- **Configuration generation**: Generate configuration strings with parameters
- **Report formatting**: Create formatted reports with data for documentation
- **Query building**: Construct queries with parameters for external systems

## Example Usage

```terraform
locals {
  format_message = provider::pyvider::format("User {} has {} roles.", ["admin", 3])
  # "User admin has 3 roles."
}

output "format_message" {
  value = local.format_message
}

```

## Signature

`format(template: string, values: list[any]) -> string`

## Parameters

- `template` (string, required) - String containing `{}` placeholders. Returns `null` when the template is `null`.
- `values` (list[any], required) - Positional values inserted into the template. A `null` list is treated as empty.

## Returns

A formatted string or `null` when the template is `null`.

## Notes

- An error is raised if the number of values does not match the number of placeholders.

## Common Patterns

### Message Formatting
```terraform
variable "name" {
  default = "Alice"
}

variable "age" {
  default = 30
}

locals {
  message = provider::pyvider::format("Hello {}, you are {} years old!", [var.name, var.age])
  # Result: "Hello Alice, you are 30 years old!"
}
```

### Configuration Generation
```terraform
variable "env" {
  default = "production"
}

variable "service" {
  default = "api"
}

locals {
  log_path = provider::pyvider::format("/var/log/{}/{}.log", [var.env, var.service])
  # Result: "/var/log/production/api.log"
}
```

## Related Components

- **join** (Function) - Join lists with delimiters
- **tostring** (Function) - Convert values to strings explicitly
- **concat** (Built-in) - Concatenate strings without formatting

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
