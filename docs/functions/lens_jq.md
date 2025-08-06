---
page_title: "Function: lens_jq"
description: |-
  Provides the lens_jq function.
---

# lens_jq (Function)

`pyvider_lens_jq(...)`

Provides the lens_jq function.

```terraform
locals {
  data = {
    items = [
      { "name" : "Laptop", "stock" : 15 },
      { "name" : "Mouse", "stock" : 150 }
    ]
  }
}

output "item_names" {
  value = provider::pyvider::lens_jq(local.data, "[.items[].name]")
}

```

## Arguments

## Arguments

- `json_input` (String, Required)
- `query` (String, Required)
- `result` (String, Computed)
