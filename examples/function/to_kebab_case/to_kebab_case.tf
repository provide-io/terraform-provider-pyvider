locals {
  to_kebab_case_to_kebab_case_text = "HelloWorld"
  to_kebab_case_kebab = provider::pyvider::to_kebab_case(local.to_kebab_case_to_kebab_case_text)
  # "hello-world"
}

output "to_kebab_case_kebab" {
  value = local.to_kebab_case_kebab
}
