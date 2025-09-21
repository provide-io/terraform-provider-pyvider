terraform {
  required_providers {
    pyvider = {
      source = "local/providers/pyvider"
      version = "0.0.5"
    }
  }
}

provider "pyvider" {}
