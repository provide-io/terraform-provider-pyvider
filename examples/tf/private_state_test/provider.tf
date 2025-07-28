terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}

# The provider requires the encryption key to be set.
provider "pyvider" {}
