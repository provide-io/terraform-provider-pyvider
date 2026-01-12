# Permissions example: Directory creation with various permission modes
# Demonstrates default permissions, custom permissions, and nested structures

# --- Test Case 1: Create a directory with default permissions ---
resource "pyvider_local_directory" "test_default_perms" {
  path = "/tmp/pyvider_test_dir_default"
}

output "permissions_default_perms_output" {
  description = "Details of the directory created with default permissions."
  value = {
    id          = pyvider_local_directory.test_default_perms.id
    path        = pyvider_local_directory.test_default_perms.path
    permissions = pyvider_local_directory.test_default_perms.permissions
    file_count  = pyvider_local_directory.test_default_perms.file_count
  }
}

# --- Test Case 2: Create a directory with custom permissions ---
resource "pyvider_local_directory" "test_custom_perms" {
  path        = "/tmp/pyvider_test_dir_custom"
  permissions = "0o777"
}

output "permissions_custom_perms_output" {
  description = "Details of the directory created with custom permissions."
  value = {
    id          = pyvider_local_directory.test_custom_perms.id
    path        = pyvider_local_directory.test_custom_perms.path
    permissions = pyvider_local_directory.test_custom_perms.permissions
    file_count  = pyvider_local_directory.test_custom_perms.file_count
  }
}

# --- Test Case 3: Create a nested directory structure ---
resource "pyvider_local_directory" "test_nested_dir" {
  path = "/tmp/pyvider_test_nested/a/b/c"
}

output "permissions_nested_dir_output" {
  description = "Details of a nested directory structure."
  value       = pyvider_local_directory.test_nested_dir.id
}
