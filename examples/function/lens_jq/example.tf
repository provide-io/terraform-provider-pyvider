locals {
  example_data = {
    name = "example"
    value = 42
  }

  example_result = provider::pyvider::lens_jq(local.example_data, ".name")
}

output "function_result" {
  description = "Result of lens_jq function"
  value       = local.example_result
}
