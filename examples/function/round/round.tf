locals {
  round_to_int = provider::pyvider::round(3.7, 0)         # 4
  round_to_decimal = provider::pyvider::round(3.14159, 2) # 3.14
}

output "round_to_int" {
  value = {
    to_int     = local.round_to_int
    to_decimal = local.round_to_decimal
  }
}
