---
page_title: "Function: subtract"
description: |-
  Terraform function for subtract
---
# subtract (Function)

Terraform function for subtract

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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

``subtract(a, b)``

## Arguments



