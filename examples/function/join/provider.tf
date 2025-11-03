terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
    }
  }
}

provider "pyvider" {
  # No testmode configured
}
