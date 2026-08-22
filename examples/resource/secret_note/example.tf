resource "pyvider_secret_note" "example" {
  name = "deploy-key"

  # Write-only: sent with the request and never persisted to state. Only the
  # digest below is stored, so a plan cannot compare against the prior value.
  secret_value = "correct-horse-battery-staple"

  # Bump this whenever secret_value changes. Terraform has no prior value to
  # diff against, so this is the only signal that an update is needed.
  secret_version = "1"
}

output "example_digest" {
  description = "Digest of the stored note. The secret itself is never in state."
  value       = pyvider_secret_note.example.digest
}
