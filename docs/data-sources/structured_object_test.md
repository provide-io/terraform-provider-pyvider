---
page_title: "Data Source: pyvider_structured_object_test"
subcategory: "Test Mode"
description: |-
  Terraform data source for pyvider_structured_object_test
---
# pyvider_structured_object_test (Data Source)

Terraform data source for pyvider_structured_object_test

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

### Required

- `config_name` (String) - 

### Optional

- `metadata` (Dynamic) - 

### Read-Only

- `generated_config` (Dynamic) - 
- `summary` (Dynamic) -

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
