# Composed example using multiple garnish components
# This demonstrates how garnish examples can work together

terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source  = "registry.terraform.io/provide-io/pyvider"
      version = "~> 0.0.3"
    }
  }
}

provider "pyvider" {}

# Variables that can be shared across garnish examples
variable "app_name" {
  description = "Application name"
  type        = string
  default     = "garnish-demo"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "testing"
}

# Include file_content garnish example
module "file_content_basic" {
  source = "../../pyvider-components/src/pyvider/components/resources/file_content.garnish/examples"
  
  # The basic.tf example creates a config.json file
}

# Include local_directory garnish example
resource "pyvider_local_directory" "output_dir" {
  path        = "${path.module}/outputs"
  create_mode = "0755"
}

# Create a file in the directory (composing resources)
resource "pyvider_file_content" "manifest" {
  filename = "${pyvider_local_directory.output_dir.path}/manifest.json"
  content = jsonencode({
    app_name    = var.app_name
    environment = var.environment
    created_at  = timestamp()
    components  = ["file_content", "local_directory", "file_info"]
  })
  
  depends_on = [pyvider_local_directory.output_dir]
}

# Use file_info data source to read the created file
data "pyvider_file_info" "manifest_info" {
  path = pyvider_file_content.manifest.filename
  
  depends_on = [pyvider_file_content.manifest]
}

# Environment variables data source
data "pyvider_env_variables" "pyvider_env" {
  filter = "PYVIDER_*"
}

# Timed token resource
resource "pyvider_timed_token" "api_token" {
  prefix         = substr(var.app_name, 0, 3)
  ttl_seconds    = 3600
  refresh_before = 300
}

# Private state verifier
resource "pyvider_private_state_verifier" "state_check" {
  input_value = "${var.app_name}-${var.environment}"
}

# Outputs that combine results from multiple garnish components
output "composition_summary" {
  description = "Summary of all composed components"
  value = {
    directories = {
      output_dir = pyvider_local_directory.output_dir.path
    }
    files = {
      manifest = {
        path = pyvider_file_content.manifest.filename
        hash = pyvider_file_content.manifest.content_hash
        size = data.pyvider_file_info.manifest_info.size
      }
    }
    tokens = {
      api_token_expires = pyvider_timed_token.api_token.expires_at
    }
    environment = {
      variables = keys(data.pyvider_env_variables.pyvider_env.variables)
    }
    verification = {
      state_verified = pyvider_private_state_verifier.state_check.verified
    }
  }
}