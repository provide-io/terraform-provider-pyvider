---
page_title: "Data Source: pyvider_file_info"
subcategory: "File Operations"
description: |-
  Terraform data source for pyvider_file_info
---
# pyvider_file_info (Data Source)

Terraform data source for pyvider_file_info

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
data "pyvider_file_info" "target_file" {
  path = "/tmp/example_file.txt"
}

output "example_data" {
  description = "Data from pyvider_file_info"
  value       = data.pyvider_file_info.target_file
}

```

## Argument Reference

