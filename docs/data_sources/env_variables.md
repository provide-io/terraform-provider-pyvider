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

## Arguments

- `keys` (String, Optional)
- `prefix` (String, Optional)
- `regex` (String, Optional)
- `exclude_empty` (String, Optional)
- `transform_keys` (String, Optional)
- `transform_values` (String, Optional)
- `case_sensitive` (String, Optional)
- `sensitive_keys` (String, Optional)
- `values` (String, Computed)
- `sensitive_values` (String, Computed)
- `all_values` (String, Computed)
- `all_environment` (String, Computed)
