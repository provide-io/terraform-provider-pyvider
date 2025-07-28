---
page_title: "pyvider_env_variables"
description: |-
  Reads and filters environment variables available to the provider process.
---

# pyvider_env_variables

Reads and filters environment variables available to the provider process. This is useful for dynamically configuring resources based on the execution environment.

## Example Usage

```hcl
data "pyvider_env_variables" "aws_config" {
  prefix = "AWS_"
}

output "aws_region" {
  value = data.pyvider_env_variables.aws_config.values["AWS_REGION"]
}
```

## Schema

### Optional

- `keys` (List of String) A specific list of environment variable keys to read.
- `prefix` (String) A prefix to filter environment variables by.
- `regex` (String) A regex pattern to filter environment variable keys.
- `exclude_empty` (Boolean) If true (default), variables with empty values are excluded.
- `transform_keys` (String) Transform keys to 'upper' or 'lower' case.
- `transform_values` (String) Transform values to 'upper' or 'lower' case.
- `case_sensitive` (Boolean) Whether prefix/regex matching is case-sensitive (default: true).
- `sensitive_keys` (List of String) A list of keys whose values should be marked as sensitive.

### Read-Only

- `values` (Map of String) The map of non-sensitive environment variables found.
- `sensitive_values` (Map of String, Sensitive) The map of sensitive environment variables found.
- `all_values` (Map of String) The map of all environment variables found, including sensitive ones.
- `all_environment` (Map of String) A complete map of all environment variables available to the provider process.
