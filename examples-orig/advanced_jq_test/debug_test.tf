output "debug_simple_dict" {
  value = provider::pyvider::lens_jq({ "test" : "value" }, ".test")
}

output "debug_file_content" {
  value = provider::pyvider::lens_jq(jsondecode(file("${path.module}/supply_chain_database.json")), ".suppliers[0].name")
}

locals {
  simple_test = { "test" : "value" }
}

output "debug_local_simple" {
  value = provider::pyvider::lens_jq(local.simple_test, ".test")
}