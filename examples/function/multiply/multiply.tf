locals {
  multiply_result = provider::pyvider::multiply(4, 3) # 12
}

output "multiply_result" {
  value = local.multiply_result
}
