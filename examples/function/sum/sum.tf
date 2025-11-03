locals {
  sum_numbers = [10, 5, 8, 2, 15]
  sum_result = provider::pyvider::sum(local.sum_numbers) # 40
}

output "sum_numbers" {
  value = local.sum_result
}
