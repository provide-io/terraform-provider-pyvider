---
page_title: "pyvider_jq"
description: |-
  Applies a JQ query and returns the result as a JSON string.
---

# Function: pyvider_jq

Applies a JQ query to the given input data. This function **always** returns a valid JSON string. For results that are lists or objects, you must use Terraform's built-in `jsondecode()` function to use the result.

For more complex transformations where you want a native Terraform value returned directly, prefer using the `pyvider_jq_cty` data source.

## Example Usage

```hcl
output "user_names" {
  value = jsondecode(provider::pyvider::pyvider_jq(
    {
      users = [{ name = "Alice" }, { name = "Bob" }]
    },
    "[.users[].name]"
  ))
}
```

## Signature

`pyvider_jq(input_data, query) -> String`

### Arguments

- `input_data` (Any) The data structure to process.
- `query` (String) The JQ query string to apply.
