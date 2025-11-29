locals {
  add_result = provider::pyvider::add(5, 3) # 8
}

output "add_result" {
  value = local.add_result
}
