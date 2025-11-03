---
page_title: "Data Source: pyvider_provider_config_reader"
description: |-
  Terraform data source for pyvider_provider_config_reader
---
# pyvider_provider_config_reader (Data Source)

Terraform data source for pyvider_provider_config_reader

## Example Usage

```terraform
data "pyvider_provider_config_reader" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_provider_config_reader"
  value       = data.pyvider_provider_config_reader.example
  sensitive   = true
}

```

## Argument Reference

