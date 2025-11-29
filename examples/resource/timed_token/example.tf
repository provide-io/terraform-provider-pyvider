resource "pyvider_timed_token" "simple_token" {
  name = "test-token"
}

output "example_token_id" {
  description = "The ID of the pyvider_timed_token resource"
  value       = pyvider_timed_token.simple_token.id
  sensitive   = true
}
