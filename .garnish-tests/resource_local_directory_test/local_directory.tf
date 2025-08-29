# Create a directory with default permissions
resource "pyvider_local_directory" "example" {
  path = "/tmp/pyvider_example_dir"
}

# Create a directory with custom permissions
resource "pyvider_local_directory" "custom_perms" {
  path        = "/tmp/pyvider_custom_dir"
  permissions = "0o755"
}

# Create a nested directory structure
resource "pyvider_local_directory" "nested" {
  path = "/tmp/pyvider_nested/deep/structure"
}

output "example_directory" {
  description = "Details of the example directory"
  value = {
    path        = pyvider_local_directory.example.path
    permissions = pyvider_local_directory.example.permissions
    file_count  = pyvider_local_directory.example.file_count
  }
}

output "custom_directory" {
  description = "Details of the custom permissions directory"
  value = {
    path        = pyvider_local_directory.custom_perms.path
    permissions = pyvider_local_directory.custom_perms.permissions
  }
}

output "nested_directory" {
  description = "Path of the nested directory structure"
  value       = pyvider_local_directory.nested.path
}
