# This resource will create a secret token in its private state during the plan.
# During the apply, it will read the decrypted token and expose it in the
# `decrypted_token` attribute.

resource "pyvider_private_state_verifier" "verify" {
  input_value = "hello_world"
}

output "input_value" {
  description = "The original input value."
  value       = pyvider_private_state_verifier.verify.input_value
}

output "decrypted_token_from_apply" {
  description = "The secret token that was successfully decrypted during the apply phase."
  value       = pyvider_private_state_verifier.verify.decrypted_token
}
