---
page_title: "Function: lower"
description: |-
  Convert a string to lowercase.
---
# lower (Function)

Convert a string to lowercase.

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

``lower(str)``

## Arguments



