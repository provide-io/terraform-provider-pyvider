locals {
  length_numbers = [1, 2, 3, 4, 5]
  length_result = provider::pyvider::length(local.length_numbers) # 5
}

output "length_results" {
  value = local.length_result
}
