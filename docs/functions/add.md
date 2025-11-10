---
page_title: "Function: add"
description: |-
  Terraform function for add
---
# add (Function)

Terraform function for add

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


## Example Usage

```terraform
locals {
  example_result = sum(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of sum function"
  value       = local.example_result
}

```

## Signature

``add(a, b)``

## Arguments

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*