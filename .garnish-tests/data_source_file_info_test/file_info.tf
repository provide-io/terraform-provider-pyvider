# Create a test file using pyvider's file_content resource
resource "pyvider_file_content" "example" {
  filename = "/tmp/pyvider_file_info_example.txt"
  content  = "Example content for file info testing"
}

# Get information about the created file
data "pyvider_file_info" "example_file" {
  path       = pyvider_file_content.example.filename
  depends_on = [pyvider_file_content.example]
}

# Check a directory
data "pyvider_file_info" "temp_dir" {
  path = "/tmp"
}

# Check a non-existent file
data "pyvider_file_info" "missing" {
  path = "/tmp/does_not_exist_12345.txt"
}

output "file_details" {
  description = "Details about the example file"
  value = {
    path          = data.pyvider_file_info.example_file.path
    exists        = data.pyvider_file_info.example_file.exists
    size          = data.pyvider_file_info.example_file.size
    is_dir        = data.pyvider_file_info.example_file.is_dir
    modified_time = data.pyvider_file_info.example_file.modified_time
  }
}

output "directory_details" {
  description = "Details about the /tmp directory"
  value = {
    path   = data.pyvider_file_info.temp_dir.path
    exists = data.pyvider_file_info.temp_dir.exists
    is_dir = data.pyvider_file_info.temp_dir.is_dir
  }
}

output "missing_file" {
  description = "Information about a non-existent file"
  value = {
    path   = data.pyvider_file_info.missing.path
    exists = data.pyvider_file_info.missing.exists
  }
}
