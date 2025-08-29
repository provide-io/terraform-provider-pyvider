terraform {
  required_providers {
    pyvider = {
      source  = "registry.terraform.io/provide-io/pyvider"
      version = "0.0.3"
    }
  }
}

provider "pyvider" {
  # Provider configuration for tests
}