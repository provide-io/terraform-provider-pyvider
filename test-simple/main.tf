terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source = "registry.terraform.io/provide-io/pyvider"
      version = "0.0.3"
    }
  }
}

provider "pyvider" {
  # Provider configuration
}

# Create a simple file
resource "pyvider_file_content" "test" {
  filename = "${path.module}/test-output.txt"
  content  = "Hello from Pyvider Provider!\nVersion: 0.0.3\nTime: ${timestamp()}"
}

output "file_created" {
  description = "Path to the created file"
  value       = pyvider_file_content.test.filename
}

output "file_hash" {
  description = "Hash of the file content"
  value       = pyvider_file_content.test.content_hash
}