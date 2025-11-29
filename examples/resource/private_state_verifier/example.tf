resource "pyvider_private_state_verifier" "example" {
  input_value = "test-value"
}

output "example_verification" {
  description = "The verification result of the pyvider_private_state_verifier resource"
  value = {
    input           = pyvider_private_state_verifier.example.input_value
    decrypted_token = pyvider_private_state_verifier.example.decrypted_token
  }
  sensitive = true
}
