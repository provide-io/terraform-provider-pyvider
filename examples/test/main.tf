terraform {
  required_providers {
    pyvider = {
      source = "local/providers/pyvider"
      version = "0.0.6"
    }
  }
}

provider "pyvider" {}
