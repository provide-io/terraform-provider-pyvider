---
page_title: "Data Source: pyvider_env_variables"
description: |-
  Terraform data source for pyvider_env_variables
---
# pyvider_env_variables (Data Source)

Terraform data source for pyvider_env_variables

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*