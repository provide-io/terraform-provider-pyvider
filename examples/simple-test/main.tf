terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source  = "registry.terraform.io/provide-io/pyvider"
      version = "0.0.3"
    }
  }
}

provider "pyvider" {}

# Simple file with static content
resource "pyvider_file_content" "simple" {
  filename = "./test.txt"
  content  = "Hello World from Pyvider"
}

output "file_path" {
  value = pyvider_file_content.simple.filename
}

output "file_hash" {
  value = pyvider_file_content.simple.content_hash
}