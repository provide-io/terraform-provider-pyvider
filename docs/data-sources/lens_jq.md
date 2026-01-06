---
page_title: "Data Source: pyvider_lens_jq"
subcategory: "Lens"
description: |-
  Terraform data source for pyvider_lens_jq
---
# pyvider_lens_jq (Data Source)

Terraform data source for pyvider_lens_jq

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
locals {
  sample_json = jsonencode({
    name  = "Example"
    value = 42
    items = ["apple", "banana", "cherry"]
  })
}

data "pyvider_lens_jq" "example" {
  json_input = local.sample_json
  query      = ".name"
}

output "example_data" {
  description = "Data from pyvider_lens_jq"
  value       = data.pyvider_lens_jq.example.result
}

```

## Argument Reference

