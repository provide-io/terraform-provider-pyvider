terraform {
  required_version = "= 1.13.0-beta1"

  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "0.6.0"
    }
  }
}

# TofuSoup drives a real init/apply/show/convergence/destroy lifecycle here.
# The configuration is intentionally side-effect-free and provider-only; the
# seven validation RPCs are proven separately by the explicit direct driver.
provider "pyvider" {}
