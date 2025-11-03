resource "pyvider_warning_example" "example" {
  name = "example_warning"
}

output "example_name" {
  description = "The name of the pyvider_warning_example resource"
  value       = pyvider_warning_example.example.name
}
