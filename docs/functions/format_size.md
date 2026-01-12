---
page_title: "Function: format_size"
description: |-
  Format bytes as human-readable size (e.g., "1.5 KB", "2.3 MB").
---
# format_size (Function)

Format bytes as human-readable size (e.g., "1.5 KB", "2.3 MB").

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

``format_size(input)``

## Arguments



