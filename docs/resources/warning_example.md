---
page_title: "Resource: pyvider_warning_example"
subcategory: "Test Mode"
description: |-
  Terraform resource for pyvider_warning_example
---
# pyvider_warning_example (Resource)

Terraform resource for pyvider_warning_example

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_warning_example" "example" {
  name = "example_warning"
}

output "example_name" {
  description = "The name of the pyvider_warning_example resource"
  value       = pyvider_warning_example.example.name
}

```

## Argument Reference



## Import

```bash
terraform import pyvider_warning_example.example <id>
```