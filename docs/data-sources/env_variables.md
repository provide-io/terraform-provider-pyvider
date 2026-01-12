---
page_title: "Data Source: pyvider_env_variables"
description: |-
  Terraform data source for pyvider_env_variables
---
# pyvider_env_variables (Data Source)

Terraform data source for pyvider_env_variables

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
data "pyvider_env_variables" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_env_variables"
  value       = data.pyvider_env_variables.example
  sensitive   = true
}

```

## Argument Reference

