# This resource uses the modern 'name' attribute and should
# produce no warnings.
resource "pyvider_warning_example" "good" {
  name = "modern-resource"
}

# This resource uses the deprecated 'old_name' attribute.
# Running `terraform plan` on this configuration should display
# a warning message in the output.
resource "pyvider_warning_example" "deprecated" {
  old_name = "legacy-resource"
}

output "good_resource_name" {
  value = pyvider_warning_example.good.name
}

output "deprecated_resource_name" {
  value = pyvider_warning_example.deprecated.name
}
