# Basic numeric operations
locals {
  basic_numbers = [10, 20, 30]

  basic_total = provider::pyvider::sum(local.basic_numbers)  # 60
  basic_average = provider::pyvider::divide(local.basic_total, 3)  # 20
  basic_rounded = provider::pyvider::round(3.14159, 2)  # 3.14
}

output "basic_rounded" {
  value = {
    total = local.basic_total
    average = local.basic_average
    rounded = local.basic_rounded
  }
}
