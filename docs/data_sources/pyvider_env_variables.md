---
page_title: "Pyvider Provider: pyvider_env_variables"
description: |-
  Reads and filters environment variables from the provider's process.
---

# Data Source: `pyvider_env_variables`

Reads environment variables from the provider's execution environment, with powerful filtering and transformation capabilities.

## Example Usage

```hcl
# Read a specific set of environment variables
data "pyvider_env_variables" "specific_vars" {
  keys = ["HOME", "PATH"]
}

# Read all variables with a specific prefix
data "pyvider_env_variables" "docker_vars" {
  prefix = "DOCKER_"
}

output "home_directory" {
  value = data.pyvider_env_variables.specific_vars.values["HOME"]
}
```

## Schema

### Optional

Only one of the following filtering arguments may be used at a time:

*   `keys` (List of String) A specific list of environment variable keys to read.
*   `prefix` (String) A prefix to filter environment variables by.
*   `regex` (String) A regular expression pattern to filter environment variable keys.

Additional options:

*   `exclude_empty` (Boolean) If `true` (the default), variables with empty values are excluded.
*   `case_sensitive` (Boolean) If `true` (the default), prefix and regex matching is case-sensitive.
*   `transform_keys` (String) Transform keys to `"upper"` or `"lower"` case.
*   `transform_values` (String) Transform values to `"upper"` or `"lower"` case.
*   `sensitive_keys` (List of String) A list of keys whose values should be marked as sensitive and placed in the `sensitive_values` attribute.

### Read-Only

*   `values` (Map of String) The map of non-sensitive environment variables found.
*   `sensitive_values` (Map of String, Sensitive) The map of sensitive environment variables found.
*   `all_values` (Map of String) The map of all environment variables found, including sensitive ones.
*   `all_environment` (Map of String) A complete map of all environment variables available to the provider process.
