terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.5"
    }
  }
}

provider "pyvider" {
  # This component is registered `test_only`. Start the
  # provider with PYVIDER_TESTMODE=true in its environment,
  # or it will not publish the component at all.
  # Add your configuration options here
}
