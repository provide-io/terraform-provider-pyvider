---
page_title: "Function: contains"
description: |-
  Terraform function for contains
---
# contains (Function)

Terraform function for contains

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

``contains(input)``

## Arguments



