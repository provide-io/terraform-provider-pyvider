terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.0"
    }
  }
}

provider "pyvider" {
  # Add your configuration options here
}
