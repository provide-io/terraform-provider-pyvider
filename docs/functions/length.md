---
page_title: "Function: length"
description: |-
  Terraform function for length
---
# length (Function)

Terraform function for length

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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

``length(input)``

## Arguments



