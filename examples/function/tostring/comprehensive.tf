# Basic type conversion function examples

# Example 1: Number to string conversions
locals {
  comprehensive_integer = 42
  comprehensive_float   = 3.14159

  comprehensive_int_string   = provider::pyvider::tostring(local.comprehensive_integer) # "42"
  comprehensive_float_string = provider::pyvider::tostring(local.comprehensive_float)   # "3.14159"
}

# Example 2: Boolean to string conversions
locals {
  comprehensive_is_enabled = true
  comprehensive_is_debug   = false

  comprehensive_enabled_str = provider::pyvider::tostring(local.comprehensive_is_enabled) # "true"
  comprehensive_debug_str   = provider::pyvider::tostring(local.comprehensive_is_debug)   # "false"
}

# Example 3: Lists have no string representation
# `tostring` refuses a collection, the same way Terraform's built-in does, so
# render the elements instead of the container.
locals {
  comprehensive_numbers = [1, 2, 3, 4, 5]
  comprehensive_colors  = ["red", "green", "blue"]

  comprehensive_numbers_str = provider::pyvider::join(", ", local.comprehensive_numbers) # "1, 2, 3, 4, 5"
  comprehensive_colors_str  = provider::pyvider::join(", ", local.comprehensive_colors)  # "red, green, blue"
}

# Example 4: Maps have no string representation either
# Use `jsonencode` when the container itself has to reach a string.
locals {
  comprehensive_config = {
    comprehensive_host = "localhost"
    comprehensive_port = 8080
    comprehensive_ssl  = true
  }

  config_str = jsonencode(local.comprehensive_config) # '{"comprehensive_host":"localhost",...}'
}

# Example 5: Practical use in string interpolation
locals {
  comprehensive_server_port = 8080
  comprehensive_use_ssl     = true

  comprehensive_connection_info = "Server running on port ${provider::pyvider::tostring(local.comprehensive_server_port)} (SSL: ${provider::pyvider::tostring(local.comprehensive_use_ssl)})"
}

# Create output file
resource "pyvider_file_content" "conversion_examples" {
  filename = "/tmp/type_conversion_examples.txt"
  content = join("\n", [
    "Type Conversion Examples",
    "========================",
    "",
    "Integer: ${local.comprehensive_int_string}",
    "Float: ${local.comprehensive_float_string}",
    "Boolean: ${local.comprehensive_enabled_str}",
    "List: ${local.comprehensive_numbers_str}",
    "Map: ${local.config_str}",
    "",
    "Connection: ${local.comprehensive_connection_info}"
  ])
}

output "comprehensive_int_string" {
  value = {
    integer_str = local.comprehensive_int_string
    float_str   = local.comprehensive_float_string
    boolean_str = local.comprehensive_enabled_str
    list_str    = local.comprehensive_numbers_str
    map_str     = local.config_str
    example     = local.comprehensive_connection_info
  }
}
