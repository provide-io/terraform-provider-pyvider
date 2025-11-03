locals {
  lens_jq_user_data = {
    lens_jq_id    = 123
    lens_jq_name  = "Alice Johnson"
    lens_jq_email = "alice@example.com"
  }

  lens_jq_user_name  = provider::pyvider::lens_jq(local.lens_jq_user_data, ".name")    # "Alice Johnson"
  lens_jq_user_email = provider::pyvider::lens_jq(local.lens_jq_user_data, ".email")   # "alice@example.com"
}

output "lens_jq_user_data" {
  value = {
    name  = local.lens_jq_user_name
    email = local.lens_jq_user_email
  }
}
