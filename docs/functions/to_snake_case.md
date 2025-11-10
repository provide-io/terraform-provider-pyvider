---
page_title: "Function: to_snake_case"
description: |-
  Convert text to snake_case using provide-foundation utilities.
---
# to_snake_case (Function)

Convert text to snake_case using provide-foundation utilities.

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

``to_snake_case(input)``

## Arguments

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*