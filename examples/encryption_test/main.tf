resource "pyvider_timed_token" "example" {
  name = "my-secure-resource"
}

output "resource_id" {
  description = "The unique ID of the created timed_token resource."
  value       = pyvider_timed_token.example.id
}
