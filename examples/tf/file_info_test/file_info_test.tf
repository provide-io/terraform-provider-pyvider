#
# pyvider/examples/tf/file_info_test/file_info_test.tf
#

terraform {
  required_providers {
    pyvider = {
      source = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}

provider "pyvider" {
  api_token = "Asdf1asdfasdfasdf"
}

# Create a temporary file to test with
resource "local_file" "test_file" {
  content     = "This is a test file for file_info data source"
  filename    = "/tmp/test_file.txt"
}

# # Test file that exists
# data "pyvider_file_info" "existing_file" {
#   path = local_file.test_file.filename
#   depends_on = [local_file.test_file]
# }

# Test file that doesn't exist
data "pyvider_file_info" "nonexistent_file" {
  path = "/tmp/this_file_does_not_exist.txt"
}

# Test on a directory
data "pyvider_file_info" "directory" {
  path = "/tmp/foo"
}

# output "existing_file_info" {
#   value = {
#     path = data.pyvider_file_info.existing_file.path
#     exists = data.pyvider_file_info.existing_file.exists
#     size = data.pyvider_file_info.existing_file.size
#     is_dir = data.pyvider_file_info.existing_file.is_dir
#     modified_time = data.pyvider_file_info.existing_file.modified_time
#   }
# }

output "nonexistent_file_info" {
  value = {
    path = data.pyvider_file_info.nonexistent_file.path
    exists = data.pyvider_file_info.nonexistent_file.exists
  }
}

output "directory_info" {
  value = {
    path = data.pyvider_file_info.directory.path
    exists = data.pyvider_file_info.directory.exists
    is_dir = data.pyvider_file_info.directory.is_dir
  }
}
