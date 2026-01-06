---
page_title: "Resource: pyvider_nested_resource_test"
subcategory: "Test Mode"
description: |-
  Terraform resource for pyvider_nested_resource_test
---
# pyvider_nested_resource_test (Resource)

Terraform resource for pyvider_nested_resource_test

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
locals {
  example_result = pyvider_nested_data_processor(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of pyvider_nested_data_processor function"
  value       = local.example_result
}

```

## Argument Reference



## Import

```bash
terraform import pyvider_nested_resource_test.example <id>
```