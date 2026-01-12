locals {
  max_numbers = [10, 5, 8, 2, 15]
  max_result = provider::pyvider::max(local.max_numbers) # 15
}

output "max_result" {
  value = local.max_result
}
