
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

data "pyvider_file_info" "test" {
  path = "/tmp/foobag"
}

# resource "pyvider_file_content" "test" {
#   count = 2
#   #count = 4
#   filename  = "/tmp/pyvider-test-resource-${count.index}.txt"
#   content = "sup dude 420 ${count.index}\n"
# }

# output "the_file_content" {
#   value = [for i in pyvider_file_content.test : i.content]
# }

variable "complex_demo" {
  default = {
    string_example = "Hello, Pyvider!"
    number_example = 42
    bool_example   = true
    list_example   = ["one", "two", "three"]
    set_example    = ["red", "green", "blue"]  # Fixed: List as default
    map_example = {
      key1 = "value1"
      key2 = "value2"
    }
    tuple_example = [1, "two", true]
    object_example = {
      name    = "test_object"
      enabled = false
      nested = {
        count = 3
        tags  = ["tag1", "tag2"]
      }
    }
    null_example = null
  }
}

locals {
  demo_set = toset(var.complex_demo.set_example)  # Convert to set at runtime
  demo_string = var.complex_demo.string_example
  demo_number = var.complex_demo.number_example
  demo_bool   = var.complex_demo.bool_example
  demo_list   = var.complex_demo.list_example
  demo_map    = var.complex_demo.map_example
  demo_tuple  = var.complex_demo.tuple_example
  demo_object = var.complex_demo.object_example
}

# Debug outputs for testing
output "string_output" {
  value = local.demo_string
}

output "number_output" {
  value = local.demo_number
}

output "bool_output" {
  value = local.demo_bool
}

output "list_output" {
  value = local.demo_list
}

output "set_output" {
  value = local.demo_set
}

output "map_output" {
  value = local.demo_map
}

output "tuple_output" {
  value = local.demo_tuple
}

output "object_output" {
  value = local.demo_object
}

output "file_info" {
  value = data.pyvider_file_info.test
}

# Example usage of the complex variable in a resource
resource "pyvider_file_content" "example" {
  filename = "/tmp/demo_file.txt"
  content  = "dude."
}

# resource "pyvider_file_content" "test" {
#   count = 2
#   #count = 4
#   filename  = "/tmp/pyvider-test-resource-${count.index}.txt"
#   content = "sup dude 420 ${count.index}\n"
# }

