---
page_title: "DataSource: pyvider_lens_jq"
description: |-
  Provides a pyvider_lens_jq DataSource.
---

# pyvider_lens_jq (DataSource)

Provides a pyvider_lens_jq DataSource.

```terraform
data "pyvider_lens_jq" "user_names" {
  json_input = jsonencode({
    users = [
      { "name" : "Alice", "active" : true },
      { "name" : "Bob", "active" : false }
    ]
  })
  query = "[.users[] | select(.active == true) | .name]"
}

output "active_user_names" {
  value = data.pyvider_lens_jq.user_names.result
}

```

## Argument Reference

## Arguments

- `json_input` (String, Required)
- `query` (String, Required)
- `result` (String, Computed)
