---
page_title: "Function: lens_jq"
subcategory: "Lens"
description: |-
  Applies a jq query and returns a native Python object.
---
# lens_jq (Function)

Applies a jq query and returns a native Python object.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
locals {
  example_data = {
    name = "example"
    value = 42
  }

  example_result = provider::pyvider::lens_jq(local.example_data, ".name")
}

output "function_result" {
  description = "Result of lens_jq function"
  value       = local.example_result
}

```

## Signature

``lens_jq(input)``

## Arguments



