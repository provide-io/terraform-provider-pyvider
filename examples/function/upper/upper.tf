locals {
  upper_shout = provider::pyvider::upper("hello world") # "HELLO WORLD"
}

output "upper_shout" {
  value = local.upper_shout
}
