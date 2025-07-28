---
page_title: "pyvider_jq_cty"
description: |-
  Applies a JQ query to a JSON string and returns the result as a native Terraform value.
---

# pyvider_jq_cty

Applies a JQ query to a JSON string. Unlike the `pyvider_jq` function, this data source returns the result as a native Terraform value (list, object, etc.), avoiding the need for `jsondecode()`. This is the recommended way to perform complex data transformations.

## Example Usage

```hcl
locals {
  input_json = jsonencode({
    users = [{ name = "Alice" }, { name = "Bob" }]
  })
}

data "pyvider_jq_cty" "user_names" {
  json_input = local.input_json
  query      = "[.users[].name]"
}

output "names" {
  # The result is already a list of strings
  value = data.pyvider_jq_cty.user_names.result
}
```

## Schema

### Required

- `json_input` (String) The JSON string to process.
- `query` (String) The JQ query to apply.

### Read-Only

- `result` (Dynamic) The result of the JQ query, returned as a native Terraform value.
