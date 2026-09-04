# Save as example.tfquery.hcl and run `tofu query`.
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
