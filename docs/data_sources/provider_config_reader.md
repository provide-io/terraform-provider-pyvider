---
page_title: "DataSource: pyvider_provider_config_reader"
description: |-
  Provides a pyvider_provider_config_reader DataSource.
---

# pyvider_provider_config_reader (DataSource)

Provides a pyvider_provider_config_reader DataSource.

```terraform
# This data source reads the configuration from the provider block.
# It is useful for diagnostics and for passing provider-level
# settings to other resources.

provider "pyvider" {
  api_endpoint = "https://api.example.com"
  api_token    = "my-secret-token"
}

data "pyvider_provider_config_reader" "config" {}

output "provider_api_endpoint" {
  value = data.pyvider_provider_config_reader.config.api_endpoint
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
