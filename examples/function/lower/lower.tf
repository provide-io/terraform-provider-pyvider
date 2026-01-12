locals {
  lower_username = provider::pyvider::lower("ADMIN@EXAMPLE.COM") # "admin@example.com"
}

output "lower_username" {
  value = local.lower_username
}
