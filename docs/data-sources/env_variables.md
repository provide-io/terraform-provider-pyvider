---
page_title: "DataSource: pyvider_env_variables"
description: |-
  Provides a pyvider_env_variables DataSource.
---

# pyvider_env_variables (DataSource)

Provides a pyvider_env_variables DataSource.

```terraform
data "pyvider_env_variables" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_env_variables"
  value       = data.pyvider_env_variables.example
}

```

## Argument Reference

