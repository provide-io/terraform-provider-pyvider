---
page_title: "Function: replace"
description: |-
  Replace all occurrences of a substring.
---
# replace (Function)

Replace all occurrences of a substring.

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

``replace(str, old, new)``

## Arguments



