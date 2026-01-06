---
page_title: "Function: format"
description: |-
  Format a template string with positional arguments.
---
# format (Function)

Substitute `{}` placeholders in a template with values. Inputs are coerced to strings, letting you mix strings, numbers, and booleans safely.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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

- `template` (string, required) — String containing `{}` placeholders. Returns `null` when the template is `null`.
- `values` (list[any], required) — Positional values inserted into the template. A `null` list is treated as empty.

## Returns

A formatted string or `null` when the template is `null`.

## Notes

- An error is raised if the number of values does not match the number of placeholders.