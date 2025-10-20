#
# numeric_functions.tf
#

output "add_result" {
  value = provider::pyvider::add(5, 7)
}

output "subtract_result" {
  value = provider::pyvider::subtract(10, 3)
}

output "multiply_result" {
  value = provider::pyvider::multiply(4, 6)
}

output "divide_result" {
  value = provider::pyvider::divide(20, 4)
}

output "round_number" {
  value = provider::pyvider::round(3.14159, 2)
}

output "min_value" {
  value = provider::pyvider::min([8, 3, 12, 5, 2])
}

output "max_value" {
  value = provider::pyvider::max([8, 3, 12, 5, 2])
}

output "sum_list" {
  value = provider::pyvider::sum([10, 20, 30, 40])
}
