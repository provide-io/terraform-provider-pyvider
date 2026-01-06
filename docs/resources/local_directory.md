---
page_title: "Resource: pyvider_local_directory"
subcategory: "File Operations"
description: |-
  Terraform resource for pyvider_local_directory
---
# pyvider_local_directory (Resource)

Terraform resource for pyvider_local_directory

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_local_directory" "example" {
  path = "/tmp/pyvider_example_directory"
}

output "example_id" {
  description = "The ID of the pyvider_local_directory resource"
  value       = pyvider_local_directory.example.id
}

```

## Argument Reference



## Import

```bash
terraform import pyvider_local_directory.example <id>
```