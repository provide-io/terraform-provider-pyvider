---
page_title: "Pyvider Provider"
description: |-
  The Pyvider provider offers a suite of utilities for diagnostics, data transformation, and local resource management, serving as a reference implementation for the Pyvider framework.
---

# Pyvider Provider

The `pyvider` provider is the official, self-hosted provider for the Pyvider framework. It serves as a comprehensive demonstration of the framework's capabilities and provides a suite of utility resources, data sources, and functions that are useful for testing, diagnostics, and general infrastructure tasks.

This provider is built entirely in Python using the `pyvider` framework and packaged using the `pyvider-builder` toolchain.

## Example Usage

```hcl
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}

provider "pyvider" {
  # Configuration for the provider is composed from 'capabilities'.
  # This example uses attributes from the built-in 'api' capability.
  api_endpoint             = "https://api.example.com/v1"
  api_token                = "my-secret-token-is-very-secret"
  api_timeout              = 60
  api_retries              = 5
  api_insecure_skip_verify = true
  api_headers = {
    "X-Custom-Header" = "Pyvider-E2E-Test"
    "Accept"          = "application/json"
  }
}
```

## Schema

### Optional

*   `api_endpoint` (String) The base URL of the API endpoint (e.g., 'https://api.example.com').
*   `api_token` (String, Sensitive) The authentication token (e.g., Bearer token) for API requests.
*   `api_timeout` (Number) Request timeout in seconds for API calls.
*   `api_retries` (Number) The maximum number of retries for failed API requests.
*   `api_insecure_skip_verify` (Boolean) If true, bypasses TLS certificate verification. Use with caution.
*   `api_headers` (Map of String) A map of custom HTTP headers to send with every API request.
