# Verify encryption of private state
resource "pyvider_private_state_verifier" "test" {
  input_value = "sensitive-data"
}

output "basic_verification" {
  value = {
    input           = pyvider_private_state_verifier.test.input_value
    decrypted_token = pyvider_private_state_verifier.test.decrypted_token
    token_matches   = pyvider_private_state_verifier.test.decrypted_token == "SECRET_FOR_SENSITIVE-DATA"
  }
  sensitive = true
}
