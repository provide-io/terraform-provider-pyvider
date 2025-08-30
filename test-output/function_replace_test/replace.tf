# Replace substring in a string
output "replace_simple" {
  value = provider::pyvider::replace("Hello, World!", "World", "Terraform")
}

output "replace_multiple" {
  value = provider::pyvider::replace("The cat in the hat", "at", "og")
}

output "replace_empty" {
  value = provider::pyvider::replace("Remove spaces", " ", "")
}

output "replace_url" {
  value = provider::pyvider::replace("https://example.com/path", "example.com", "mysite.org")
}