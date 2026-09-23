# Save as example.tfquery.hcl and run `terraform query`, which reads these
# files. It arrived in Terraform 1.14, alongside list resources themselves;
# OpenTofu has no query command, so this file is inert under `tofu`.
list "pyvider_secret_note" "example" {
  provider = pyvider

  config {
    # Only notes whose name starts with this are listed.
    name_prefix = "deploy-"

    include_archived = false
  }
}
