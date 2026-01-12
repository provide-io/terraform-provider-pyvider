```terraform
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.0"  # For development: accepts any version
      # For production, pin to specific version: version = "0.0.12"
    }
  }
}

provider "pyvider" {
  # Provider configuration options
  # Currently no configuration is required
}
```
