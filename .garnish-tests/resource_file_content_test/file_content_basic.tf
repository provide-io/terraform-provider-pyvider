# Basic file content resource example
resource "pyvider_file_content" "config" {
  filename = "/tmp/pyvider_config.json"
  content  = <<-JSON
    {
      "name": "example-app",
      "version": "1.0.0",
      "description": "Basic configuration file"
    }
  JSON
}

output "file_path" {
  description = "Path to the created file"
  value       = pyvider_file_content.config.filename
}

output "file_hash" {
  description = "SHA256 hash of the file content"
  value       = pyvider_file_content.config.content_hash
}