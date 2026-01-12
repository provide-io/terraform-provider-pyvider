---
page_title: "Function: lookup"
description: |-
  Read a value from a map with an optional default.
---
# lookup (Function)

Fetch a key from a map. Provide a default as the third argument to avoid errors when the key is missing.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
locals {
  lookup_settings = {
    database_host = "db.example.com"
    database_port = 5432
  }
  lookup_db_host = provider::pyvider::lookup(local.lookup_settings, "database_host", "localhost")
  lookup_missing = provider::pyvider::lookup(local.lookup_settings, "missing_key", "default")
}

output "lookup_results" {
  value = {
    found    = local.lookup_db_host
    notfound = local.lookup_missing
  }
}

```

## Signature

`lookup(map_to_search: map[string, any], key: string, options: variadic) -> any`

## Parameters

- `map_to_search` (map[string, any], required) — Map to read. Returns `null` when this is `null`.
- `key` (string, required) — Key to retrieve.
- `options` (variadic, optional) — First value acts as the default result.

## Returns

The matching value, the provided default, or `null` when the map itself is `null`.

## Notes

- Without a default, a missing key raises a `FunctionError`.