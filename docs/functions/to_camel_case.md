---
page_title: "Function: to_camel_case"
description: |-
  Convert text to camelCase (or PascalCase if upper_first is true).
---
# to_camel_case (Function)

Convert text to camelCase (or PascalCase if upper_first is true).

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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

``to_camel_case(input)``

## Arguments



