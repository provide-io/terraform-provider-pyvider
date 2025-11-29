# Create a simple directory with default permissions.
resource "pyvider_local_directory" "basic_dir" {
  path = "/tmp/pyvider_basic"
}

# Create a directory with specific permissions.
resource "pyvider_local_directory" "secure_dir" {
  path        = "/tmp/pyvider_secure"
  permissions = "0o700" # Only owner can read/write/execute.
}

output "basic_directory_paths" {
  value = {
    basic  = pyvider_local_directory.basic_dir.path
    secure = pyvider_local_directory.secure_dir.path
  }
}

output "basic_secure_dir_permissions" {
  value = pyvider_local_directory.secure_dir.permissions
}
