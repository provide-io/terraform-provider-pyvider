terraform {
  required_version = ">= 1.0"
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.0.5"
    }
  }
}

provider "pyvider" {}

# Test file content resource
resource "pyvider_file_content" "test_file" {
  filename = "${path.module}/test_output/example.json"
  content = jsonencode({
    test_id   = "plating-comprehensive-test"
    timestamp = timestamp()
    provider  = "pyvider"
  })
}

# Test directory resource
resource "pyvider_local_directory" "test_dir" {
  path        = "${path.module}/test_output"
  create_mode = "0755"
}

# Test data sources
data "pyvider_env_variables" "environment" {
  keys = ["PATH", "HOME", "USER"]
}

data "pyvider_file_info" "test_file_info" {
  path = pyvider_file_content.test_file.filename

  depends_on = [pyvider_file_content.test_file]
}

# Test provider functions
locals {
  # Math functions
  sum_result     = provider::pyvider::add(15, 25)
  divide_result  = provider::pyvider::divide(100, 4)

  # String functions
  upper_result   = provider::pyvider::upper("terraform")
  format_result  = provider::pyvider::format("Hello %s from %s!", ["World", "Pyvider"])

  # Collection functions
  min_result     = provider::pyvider::min([10, 5, 8, 3, 12])
  max_result     = provider::pyvider::max([10, 5, 8, 3, 12])

  # JQ functions
  jq_result      = provider::pyvider::lens_jq(
    jsonencode({name = "test", values = [1, 2, 3]}),
    ".values | length"
  )
}

# Outputs for validation
output "test_results" {
  value = {
    file_created = pyvider_file_content.test_file.filename
    file_size    = data.pyvider_file_info.test_file_info.size
    file_hash    = pyvider_file_content.test_file.content_hash
    dir_created  = pyvider_local_directory.test_dir.path
    env_user     = data.pyvider_env_variables.environment.values["USER"]

    functions = {
      math = {
        sum    = local.sum_result
        divide = local.divide_result
      }
      strings = {
        upper  = local.upper_result
        format = local.format_result
      }
      collections = {
        min = local.min_result
        max = local.max_result
      }
      jq = {
        array_length = local.jq_result
      }
    }
  }
}
