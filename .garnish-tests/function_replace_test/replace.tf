# Example of string replacement
locals {
  template_string = "Hello, {name}! Welcome to {platform}."
  config_path     = "/home/user/old_config/settings.yaml"
  log_message     = "Error: Connection failed. Error: Timeout. Error: Retry exhausted."
}

# Replace placeholders in template
output "personalized_message" {
  description = "Replace template placeholders"
  value = provider::pyvider::replace(
    provider::pyvider::replace(local.template_string, "{name}", "Alice"),
    "{platform}", "Terraform"
  )
}

# Update configuration path
output "updated_config_path" {
  description = "Replace old path with new"
  value       = provider::pyvider::replace(local.config_path, "old_config", "new_config")
}

# Clean up repeated text
output "cleaned_log" {
  description = "Remove duplicate 'Error:' prefix"
  value       = provider::pyvider::replace(local.log_message, "Error: ", "")
}

# Compare with Terraform's built-in replace
output "comparison" {
  description = "Compare Pyvider replace with Terraform's replace"
  value = {
    pyvider_result   = provider::pyvider::replace("hello world", "world", "terraform")
    terraform_result = replace("hello world", "world", "terraform")
    results_match    = provider::pyvider::replace("hello world", "world", "terraform") == replace("hello world", "world", "terraform")
  }
}
