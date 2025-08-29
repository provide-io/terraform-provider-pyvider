resource "pyvider_timed_token" "example" {
  name = "my-secure-resource"
}

output "resource_id" {
  description = "The unique ID of the created timed_token resource"
  value       = pyvider_timed_token.example.id
}

output "token" {
  description = "The generated token (sensitive)"
  value       = pyvider_timed_token.example.token
  sensitive   = true
}

output "expires_at" {
  description = "Token expiration timestamp"
  value       = pyvider_timed_token.example.expires_at
  sensitive   = true
}
