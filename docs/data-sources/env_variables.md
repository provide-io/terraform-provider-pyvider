---
page_title: "pyvider_env_variables Data Source"
description: |-
  Read environment variables
---

# pyvider_env_variables

Reads environment variables from the system.

## Example Usage

```hcl
data "pyvider_env_variables" "path" {
  keys = ["PATH", "HOME"]
}

output "path" {
  value = data.pyvider_env_variables.path.values["PATH"]
}
```

## Argument Reference

- `keys` - (Required) List of environment variable names to read

## Attribute Reference

- `values` - Map of environment variable names to their values
