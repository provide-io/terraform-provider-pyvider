---
page_title: "Data Source: pyvider_mixed_map_test"
subcategory: "Test Mode"
description: |-
  Terraform data source for pyvider_mixed_map_test
---
# pyvider_mixed_map_test (Data Source)

Terraform data source for pyvider_mixed_map_test

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

## Argument Reference

## Schema

### Optional

- `input_data` (String) - Mixed type map input

### Read-Only

- `processed_data` (String) - Processed mixed map
- `data_hash` (String) - Hash of processed data

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
