# Example demonstrating diagnostic warnings for deprecated attributes

# This resource uses the modern 'name' attribute - no warnings
resource "pyvider_warning_example" "modern" {
  name = "modern-resource"
}

# This resource uses the deprecated 'old_name' attribute - produces warning
resource "pyvider_warning_example" "deprecated" {
  old_name = "legacy-resource"
}

output "modern_resource_name" {
  description = "Name of the modern resource"
  value       = pyvider_warning_example.modern.name
}

output "deprecated_resource_name" {
  description = "Name of the deprecated resource (migrated from old_name)"
  value       = pyvider_warning_example.deprecated.name
}
