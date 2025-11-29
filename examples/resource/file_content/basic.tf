# Create a simple file with specified content.
resource "pyvider_file_content" "readme" {
  filename = "/tmp/pyvider_readme.txt"
  content  = "This file was created by Terraform."
}

output "basic_readme_details" {
  description = "Details about the created file."
  value = {
    filename     = pyvider_file_content.readme.filename
    exists       = pyvider_file_content.readme.exists
    content_hash = pyvider_file_content.readme.content_hash
  }
}
