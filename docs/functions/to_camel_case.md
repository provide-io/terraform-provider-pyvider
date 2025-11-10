---
page_title: "Function: to_camel_case"
description: |-
  Convert text to camelCase (or PascalCase if upper_first is true).
---
# to_camel_case (Function)

Convert text to camelCase (or PascalCase if upper_first is true).

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*