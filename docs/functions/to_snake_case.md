---
page_title: "Function: to_snake_case"
description: |-
  Convert text to snake_case using provide-foundation utilities.
---
# to_snake_case (Function)

Convert text to snake_case using provide-foundation utilities.

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

``to_snake_case(input)``

## Arguments



