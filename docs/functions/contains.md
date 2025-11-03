---
page_title: "Function: contains"
description: |-
  Terraform function for contains
---
# contains (Function)

Terraform function for contains

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



