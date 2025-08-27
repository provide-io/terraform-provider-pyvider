---
page_title: "DataSource: pyvider_provider_config_reader"
description: |-
  Provides a pyvider_provider_config_reader DataSource.
---

# pyvider_provider_config_reader (DataSource)

Provides a pyvider_provider_config_reader DataSource.

```terraform
data "pyvider_provider_config_reader" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_provider_config_reader"
  value       = data.pyvider_provider_config_reader.example
}

```

## Argument Reference

## Arguments

- `api_endpoint` (String, Computed)
- `api_token` (String, Computed)
- `api_timeout` (String, Computed)
- `api_retries` (String, Computed)
- `api_insecure_skip_verify` (String, Computed)
- `api_headers` (String, Computed)
