locals {
  format_size_default_display = provider::pyvider::format_size(10240)        # "10.0 KB"
  format_size_precise_display = provider::pyvider::format_size(123456789, 2) # "117.74 MB"
}

output "format_size_precise_display" {
  value = {
    default = local.format_size_default_display
    precise = local.format_size_precise_display
  }
}
