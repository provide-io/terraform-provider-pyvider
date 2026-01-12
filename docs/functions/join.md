---
page_title: "Function: join"
description: |-
  Join a list of strings with a delimiter.
---
# join (Function)

Join a list of strings with a delimiter.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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

``join(separator, list)``

## Arguments



