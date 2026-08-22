# Save as example.tfquery.hcl and run `tofu query`.
list "pyvider_secret_note" "example" {
  provider = pyvider

  config {
    # Only notes whose name starts with this are listed.
    name_prefix = "deploy-"

    include_archived = false
  }
}
