---
page_title: "Function: add"
subcategory: "Math"
description: |-
  Terraform function for add
---

# add (Function)

Terraform function for add

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



