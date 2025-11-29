resource "pyvider_local_directory" "example" {
  path = "/tmp/pyvider_example_directory"
}

output "example_id" {
  description = "The ID of the pyvider_local_directory resource"
  value       = pyvider_local_directory.example.id
}
