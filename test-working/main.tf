# Test pyvider functions
locals {
  # String manipulation
  upper_result = provider::pyvider::upper("hello")
  lower_result = provider::pyvider::lower("HELLO")
  
  # Math functions  
  add_result = provider::pyvider::add(5, 7)
  multiply_result = provider::pyvider::multiply(3, 4)
}

output "results" {
  value = {
    upper = local.upper_result
    lower = local.lower_result
    add = local.add_result
    multiply = local.multiply_result
  }
}
