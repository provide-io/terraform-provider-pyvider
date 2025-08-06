---
page_title: "DataSource: pyvider_env_variables"
description: |-
  Provides a pyvider_env_variables DataSource.
---

# pyvider_env_variables (DataSource)

Provides a pyvider_env_variables DataSource.

```terraform
# Read specific environment variables
data "pyvider_env_variables" "by_keys" {
  keys = ["HOME", "PATH"]
}

# Read all environment variables with a specific prefix
data "pyvider_env_variables" "by_prefix" {
  prefix = "PYVIDER_"
}

output "home_directory" {
  value = data.pyvider_env_variables.by_keys.values["HOME"]
}

output "pyvider_vars" {
  value = data.pyvider_env_variables.by_prefix.values
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
