terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.5"
    }
  }
}

provider "pyvider" {
  provider_testmode = true
  # Add your configuration options here
}
