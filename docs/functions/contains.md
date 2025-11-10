---
page_title: "Function: contains"
description: |-
  Terraform function for contains
---
# contains (Function)

Terraform function for contains

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


## Example Usage

```terraform
locals {
  example_result = length(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of length function"
  value       = local.example_result
}

```

## Signature

``contains(input)``

## Arguments

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*