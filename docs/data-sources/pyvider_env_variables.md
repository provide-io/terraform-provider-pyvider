---
page_title: "Data Source: pyvider_env_variables"
description: |-

---

# Data Source: pyvider_env_variables





## Schema


### Optional

- `keys` (List(String))

- `prefix` (String)

- `regex` (String)

- `exclude_empty` (Bool)

- `transform_keys` (String)

- `transform_values` (String)

- `case_sensitive` (Bool)

- `sensitive_keys` (List(String))


### Read-Only

- `values` (Map(String))

- `sensitive_values` (Map(String)), Sensitive

- `all_values` (Map(String))

- `all_environment` (Map(String))