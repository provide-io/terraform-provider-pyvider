resource "pyvider_file_content" "example" {
  filename = "/tmp/pyvider_example.txt"
  content  = "This is an example file created by Terraform."
}

output "example_file" {
  description = "The filename and hash of the created file"
  value = {
    filename     = pyvider_file_content.example.filename
    content_hash = pyvider_file_content.example.content_hash
    exists       = pyvider_file_content.example.exists
  }
}
