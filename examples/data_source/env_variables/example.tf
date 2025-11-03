data "pyvider_env_variables" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_env_variables"
  value       = data.pyvider_env_variables.example
  sensitive   = true
}
