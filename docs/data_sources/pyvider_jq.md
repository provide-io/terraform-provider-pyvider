---
page_title: "Pyvider Provider: pyvider_jq"
description: |-
  Processes a JSON string with a JQ query.
---

# Data Source: `pyvider_jq`

Applies a [JQ](https://jqlang.github.io/jq/) query to a given JSON input string and returns the result as a string. This is useful for complex data transformations that are difficult to express in HCL.

**Note:** For more direct integration, consider using the `pyvider_jq` **function**, which can operate on native Terraform objects and may not require `jsonencode`/`jsondecode`.

## Example Usage

```hcl
locals {
  input_json = jsonencode({
    users = [
      { "name": "Alice", "active": true },
      { "name": "Bob", "active": false }
    ]
  })
}

data "pyvider_jq" "active_users" {
  json_input = local.input_json
  query      = "[.users[] | select(.active == true) | .name]"
}

output "active_user_names" {
  # The result is a JSON string, so it must be decoded.
  value = jsondecode(data.pyvider_jq.active_users.result)
}
```

## Schema

### Required

*   `json_input` (String) A valid JSON string to be processed.
*   `query` (String) The JQ query to apply to the input.

### Read-Only

*   `result` (String) The result of the JQ query, returned as a string. If the query produces a JSON object or array, this will be a JSON-formatted string.
