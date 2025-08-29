# Create a file with content using pyvider
resource "pyvider_file_content" "example" {
  filename = "/tmp/pyvider_example.txt"
  content  = "Hello from Pyvider! This file was created by Terraform."
}

# Read the file back to verify (requires local provider)
data "local_file" "verify" {
  filename   = pyvider_file_content.example.filename
  depends_on = [pyvider_file_content.example]
}

output "file_info" {
  description = "Information about the created file"
  value = {
    filename     = pyvider_file_content.example.filename
    exists       = pyvider_file_content.example.exists
    content_hash = pyvider_file_content.example.content_hash
  }
}

output "file_content" {
  description = "Content written to the file"
  value       = pyvider_file_content.example.content
}

output "verification" {
  description = "Verification that file was created correctly"
  value       = data.local_file.verify.content == pyvider_file_content.example.content
}
