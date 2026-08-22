locals {
  payload = jsonencode({
    region   = "us-west-2"
    replicas = 3
  })

  # Returns a JSON string: the original data plus a summary of it.
  analysed = provider::pyvider::pyvider_nested_data_processor(local.payload, "analyze")
}

output "total_keys" {
  value = jsondecode(local.analysed).summary.total_keys
}
