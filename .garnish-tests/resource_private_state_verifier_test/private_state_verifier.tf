# This resource demonstrates private state encryption.
# It creates a secret token in its private state during the plan phase,
# then decrypts and exposes it during the apply phase.
# Requires PYVIDER_PRIVATE_STATE_SHARED_SECRET environment variable.

resource "pyvider_private_state_verifier" "example" {
  input_value = "hello_world"
}

output "input_value" {
  description = "The original input value"
  value       = pyvider_private_state_verifier.example.input_value
}

output "decrypted_token" {
  description = "The secret token decrypted during apply phase"
  value       = pyvider_private_state_verifier.example.decrypted_token
  sensitive   = true
}
