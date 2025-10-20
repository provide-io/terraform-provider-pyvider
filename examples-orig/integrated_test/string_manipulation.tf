#
# string_manipulation.py
#

output "upper_result" {
  value = provider::pyvider::upper("hello world")
}

output "lower_result" {
  value = provider::pyvider::lower("HELLO WORLD")
}

# Format with array parameter
output "format_string" {
  value = provider::pyvider::format("Hello, {0}! Your score is {1}.", ["Terraform", 100])
}

output "join_result" {
  value = provider::pyvider::join("-", ["app", "prod", "v1"])
}

output "replace_result" {
  value = provider::pyvider::replace("Hello, World!", "World", "Terraform")
}

output "split_result" {
  value = provider::pyvider::split(",", "red,green,blue")
}
