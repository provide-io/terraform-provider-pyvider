# Terraform Provider: Pyvider

The `pyvider` provider is the official, self-hosted provider for the Pyvider framework. It serves as a comprehensive demonstration of the framework's capabilities and provides a suite of utility resources, data sources, and functions that are useful for testing, diagnostics, and general infrastructure tasks.

This provider is built entirely in Python using the `pyvider` framework and packaged using the `pyvider-builder` toolchain.

## Features

* **Utility Resources:** Manage local files and directories (`pyvider_file_content`, `pyvider_local_directory`).
* **Diagnostic Data Sources:** Inspect the provider's environment (`pyvider_env_variables`), read local file metadata (`pyvider_file_info`), and test provider configuration (`pyvider_provider_config_reader`).
* **Powerful Data Transformation:** Process JSON and other data structures using `jq` queries directly within your Terraform configuration (`pyvider_jq`, `pyvider_jq_cty`).
* **Extensive Function Library:** A rich set of functions for string manipulation, numeric operations, and collection handling.

## Installation

1. **Download:** Download the appropriate `terraform-provider-pyvider` binary for your system from the releases page.
2. **Install:** Run the downloaded binary with the `install` command. It will automatically copy itself to the correct Terraform plugin directory.

    ```sh
    ./terraform-provider-pyvider install
    ```

## Example Usage

Configure the provider in your Terraform code. The `pyvider` provider itself has a schema composed from capabilities, such as the `api` capability shown below.

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
  # Example configuration from the 'api' capability
  api_endpoint = "https://api.example.com/v1"
  api_token    = "my-secret-token"
}

# Use a data source from the provider
data "pyvider_env_variables" "path" {
  keys = ["PATH"]
}

output "path_env" {
  value = data.pyvider_env_variables.path.values["PATH"]
}
```
