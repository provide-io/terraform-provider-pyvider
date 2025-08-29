# Test pyvider functions
locals {
  # String manipulation
  upper_result = provider::pyvider::upper("hello world")
  lower_result = provider::pyvider::lower("HELLO WORLD")
  
  # Math functions  
  add_result = provider::pyvider::add(5, 7)
  multiply_result = provider::pyvider::multiply(3, 4)
}

output "string_functions" {
  value = {
    upper = local.upper_result
    lower = local.lower_result
  }
}

output "math_functions" {
  value = {
    add = local.add_result
    multiply = local.multiply_result
  }
}