# Type conversion examples using Pyvider's tostring function
locals {
  number_value = 42
  bool_value   = true
  
  # Convert number to string
  number_as_string = provider::pyvider::tostring(local.number_value)
  
  # Convert boolean to string
  bool_as_string = provider::pyvider::tostring(local.bool_value)
}

output "number_conversion" {
  description = "Number converted to string"
  value = {
    original = local.number_value
    converted = local.number_as_string
    type_check = can(regex("^[0-9]+$", local.number_as_string))
  }
}

output "boolean_conversion" {
  description = "Boolean converted to string"
  value = {
    original = local.bool_value
    converted = local.bool_as_string
    equals_true = local.bool_as_string == "true"
  }
}
