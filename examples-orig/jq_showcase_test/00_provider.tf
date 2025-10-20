terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}

provider "pyvider" {
  api_token = "placeholder-token"
}
