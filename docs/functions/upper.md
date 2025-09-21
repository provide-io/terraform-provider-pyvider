---
page_title: "upper Function"
description: |-
  Convert string to uppercase
---

# upper Function

Converts a string to uppercase.

## Example Usage

```hcl
output "uppercase" {
  value = provider::pyvider::upper("hello")
}
```

## Signature

```
upper(string) string
```

## Arguments

1. `string` - The string to convert

## Return Value

The uppercase version of the input string.
