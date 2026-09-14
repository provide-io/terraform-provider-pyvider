terraform {
  required_version = "= 1.13.0-beta1"

  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "0.5.0"
    }
  }
}

provider "pyvider" {
  api_insecure_skip_verify = true
}

resource "pyvider_local_directory" "lint_target" {
  path        = "${path.module}/world-writable"
  permissions = "0o777"
}

# Validation inspects only configuration. It must never contact this endpoint.
data "pyvider_http_api" "lint_target" {
  url     = "http://127.0.0.1/provider-lint-proof"
  method  = "GET"
  headers = {}
  timeout = 30
}

ephemeral "pyvider_lease" "lint_target" {
  name        = "provider-lint-proof"
  path        = "${path.module}/proof.lease"
  ttl_seconds = 3601
}
