terraform {
  required_version = "= 1.13.0-rc1"

  required_providers {
    pyvider = {
      source  = "provide-io/pyvider"
      version = "0.6.1"
    }
  }
}

provider "pyvider" {}

# Known only after apply, and not refined beyond what core already knows.
resource "terraform_data" "seed" {}

locals {
  # OpenTofu 1.13 `assume*` functions: still unknown at plan time, but refined
  # to "not null, starts with refined:".
  refined = assumestringprefix(assumenotnull(terraform_data.seed.id), "refined:")
}

# `content` is required and not computed, so the planned value is whatever the
# provider echoes back from the config it decoded.
resource "pyvider_file_content" "echo" {
  filename = "${path.module}/refined-unknown.txt"
  content  = local.refined
}

# Through the provider: known at plan only if pyvider decoded the refinement
# from its PlanResourceChange config and encoded it back into the plan.
output "provider_prefix" {
  value = startswith(pyvider_file_content.echo.content, "refined:")
}

output "provider_not_null" {
  value = pyvider_file_content.echo.content != null
}

# Controls.
output "core_prefix" {
  value = startswith(local.refined, "refined:")
}

output "unrefined_prefix" {
  value = startswith(terraform_data.seed.id, "refined:")
}

output "provider_computed_prefix" {
  value = startswith(pyvider_file_content.echo.content_hash, "refined:")
}
