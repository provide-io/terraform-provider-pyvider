---
page_title: "Function: sum"
description: |-
  Terraform function for sum
---
# sum (Function)

Terraform function for sum

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

``sum(numbers)``

## Arguments



