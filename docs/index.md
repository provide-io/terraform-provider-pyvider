---
page_title: "pyvider Provider"
description: |-
  The official Pyvider provider for Terraform/OpenTofu
---

# pyvider Provider

The `pyvider` provider is the official provider for the Pyvider framework, demonstrating Python-based Terraform provider development.

## Example Usage

```hcl
terraform {
  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "~> 0.0"
    }
  }
}

provider "pyvider" {
  # Configuration options
}
```

## Resources

- `pyvider_file_content` - Manages file content
- `pyvider_local_directory` - Manages local directories
- `pyvider_timed_token` - Creates time-limited tokens
- `pyvider_private_state_verifier` - Verifies private state
- `pyvider_warning_example` - Example resource with warnings

## Data Sources

- `pyvider_env_variables` - Read environment variables
- `pyvider_file_info` - Get file information
- `pyvider_provider_config_reader` - Read provider configuration
- `pyvider_jq` - Process data with JQ queries
- `pyvider_jq_cty` - JQ with CTY type handling

## Functions

Provider includes various utility functions for string manipulation, numeric operations, and collection handling.
