locals {
  format_message = provider::pyvider::format("User {} has {} roles.", ["admin", 3])
  # "User admin has 3 roles."
}

output "format_message" {
  value = local.format_message
}
