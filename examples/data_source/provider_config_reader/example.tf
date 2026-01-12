data "pyvider_provider_config_reader" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_provider_config_reader"
  value       = data.pyvider_provider_config_reader.example
  sensitive   = true
}
