locals {
  replace_replace_text = "hello world"
  replace_replaced = provider::pyvider::replace(local.replace_replace_text, "world", "earth")
  # "hello earth"
}

output "replace_replaced" {
  value = local.replace_replaced
}
