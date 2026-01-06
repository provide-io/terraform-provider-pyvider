---
page_title: "Function: min"
description: |-
  Terraform function for min
---
# min (Function)

Terraform function for min

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

``min(numbers)``

## Arguments



