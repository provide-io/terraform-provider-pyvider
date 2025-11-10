# Advanced file_info example: File validation and conditional logic
# Demonstrates checking file existence, directory detection, and metadata access

# Create a temporary file to test with
resource "local_file" "test_file" {
  content  = "This is a test file for file_info data source"
  filename = "/tmp/test_file.txt"
}

# Test file that exists - access all metadata
data "pyvider_file_info" "existing_file" {
  path       = local_file.test_file.filename
  depends_on = [local_file.test_file]
}

# Test file that doesn't exist - useful for conditional logic
data "pyvider_file_info" "nonexistent_file" {
  path = "/tmp/this_file_does_not_exist.txt"
}

# Test on a directory
data "pyvider_file_info" "directory" {
  path = "/tmp"
}

# Output for existing file - shows all available metadata
output "advanced_existing_file_info" {
  value = {
    path          = data.pyvider_file_info.existing_file.path
    exists        = data.pyvider_file_info.existing_file.exists
    size          = data.pyvider_file_info.existing_file.size
    is_dir        = data.pyvider_file_info.existing_file.is_dir
    is_file       = data.pyvider_file_info.existing_file.is_file
    modified_time = data.pyvider_file_info.existing_file.modified_time
  }
}

# Output for non-existent file - useful for validation
output "advanced_nonexistent_file_info" {
  value = {
    path   = data.pyvider_file_info.nonexistent_file.path
    exists = data.pyvider_file_info.nonexistent_file.exists
  }
}

# Output for directory - distinguish between files and directories
output "advanced_directory_info" {
  value = {
    path   = data.pyvider_file_info.directory.path
    exists = data.pyvider_file_info.directory.exists
    is_dir = data.pyvider_file_info.directory.is_dir
  }
}

# Real-world pattern: Validation and error handling
locals {
  advanced_file_validation = {
    advanced_is_valid       = data.pyvider_file_info.existing_file.exists && data.pyvider_file_info.existing_file.is_file
    advanced_is_directory   = data.pyvider_file_info.directory.is_dir
    advanced_file_is_recent = can(timeadd(data.pyvider_file_info.existing_file.modified_time, "24h"))
  }
}

output "advanced_validation_summary" {
  value = local.advanced_file_validation
}
