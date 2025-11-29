locals {
  sample_json = jsonencode({
    name  = "Example"
    value = 42
    items = ["apple", "banana", "cherry"]
  })
}

data "pyvider_lens_jq" "example" {
  json_input = local.sample_json
  query      = ".name"
}

output "example_data" {
  description = "Data from pyvider_lens_jq"
  value       = data.pyvider_lens_jq.example.result
}
