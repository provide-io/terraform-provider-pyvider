# Save as example.tfquery.hcl and run `terraform query`, which reads these
# files. It arrived in Terraform 1.14, alongside list resources themselves;
# OpenTofu has no query command, so this file is inert under `tofu`.
list "pyvider_file_content" "example" {
  provider = pyvider

  config {
    path = "${path.module}"

    # Only entries ending in this suffix are listed.
    suffix = ".tf"

    # Dotfiles are skipped unless this is set.
    include_hidden = false
  }
}
