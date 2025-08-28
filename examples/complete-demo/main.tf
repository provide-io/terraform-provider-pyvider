terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source  = "registry.terraform.io/provide-io/pyvider"
      version = "~> 0.0.3"
    }
  }
}

provider "pyvider" {
  # Provider configuration (if any)
}

# Example 1: File content management
resource "pyvider_file_content" "config" {
  filename = "${path.module}/generated/config.json"
  content  = jsonencode({
    name        = "pyvider-demo"
    version     = "1.0.0"
    environment = "test"
    demo        = true
  })
}

# Example 2: Local directory management
resource "pyvider_local_directory" "outputs" {
  path        = "${path.module}/generated/outputs"
  create_mode = "0755"
}

# Example 3: Timed token generation
resource "pyvider_timed_token" "api_token" {
  prefix         = "pvd"
  ttl_seconds    = 3600
  refresh_before = 300
}

# Example 4: Private state verifier
resource "pyvider_private_state_verifier" "verifier" {
  input_value = "test-value-${random_id.test.hex}"
}

# Helper resource for random ID
resource "random_id" "test" {
  byte_length = 4
}

# Data Sources Examples

# Example 1: Read file info
data "pyvider_file_info" "config_info" {
  path = pyvider_file_content.config.filename
  
  depends_on = [pyvider_file_content.config]
}

# Example 2: Read environment variables
data "pyvider_env_variables" "env" {
  filter = "PYVIDER_*"
}

# Example 3: Provider config reader
data "pyvider_provider_config_reader" "config" {
  # Reads the provider's configuration
}

# Outputs
output "file_content_hash" {
  description = "Hash of the created file content"
  value       = pyvider_file_content.config.content_hash
}

output "directory_path" {
  description = "Path of the created directory"
  value       = pyvider_local_directory.outputs.path
}

output "token_value" {
  description = "Generated token value"
  value       = pyvider_timed_token.api_token.token
  sensitive   = true
}

output "token_expires_at" {
  description = "Token expiration timestamp"
  value       = pyvider_timed_token.api_token.expires_at
}

output "file_size" {
  description = "Size of the created file"
  value       = data.pyvider_file_info.config_info.size
}

output "environment_variables" {
  description = "Filtered environment variables"
  value       = data.pyvider_env_variables.env.variables
  sensitive   = true
}