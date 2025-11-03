locals {
  min_numbers = [10, 5, 8, 2, 15]
  min_result = provider::pyvider::min(local.min_numbers) # 2
}

output "min_result" {
  value = local.min_result
}
