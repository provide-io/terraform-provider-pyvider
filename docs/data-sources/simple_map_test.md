---
page_title: "Data Source: pyvider_simple_map_test"
subcategory: "Test Mode"
description: |-
  Terraform data source for pyvider_simple_map_test
---
# pyvider_simple_map_test (Data Source)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

Terraform data source for pyvider_simple_map_test

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
locals {
  example_result = pyvider_nested_data_processor(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of pyvider_nested_data_processor function"
  value       = local.example_result
}

```

## Schema

### Optional

- `input_data` (Map of String) - Simple string map input

### Read-Only

- `processed_data` (Map of String) - Processed string map
- `data_hash` (String) - Hash of processed data
