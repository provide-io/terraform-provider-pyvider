# Basic string manipulation
locals {
  basic_text = "Hello World"

  basic_uppercase = provider::pyvider::upper(local.basic_text)  # "HELLO WORLD"
  basic_lowercase = provider::pyvider::lower(local.basic_text)  # "hello world"
  basic_formatted = provider::pyvider::format("Name: {}", ["Alice"])  # "Name: Alice"
}

output "basic_results" {
  value = {
    upper = local.basic_uppercase
    lower = local.basic_lowercase
    formatted = local.basic_formatted
  }
}
