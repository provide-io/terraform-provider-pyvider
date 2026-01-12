locals {
  truncate_truncate_text = "Very long text that needs truncation"
  truncate_truncated = provider::pyvider::truncate(local.truncate_truncate_text, 10)  # "Very lo..."
  truncate_custom_suffix = provider::pyvider::truncate(local.truncate_truncate_text, 10, ">>")  # "Very long>>"
}

output "truncate_custom_suffix" {
  value = {
    default = local.truncate_truncated
    custom  = local.truncate_custom_suffix
  }
}
