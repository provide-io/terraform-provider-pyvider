locals {
  tostring_integer = 42
  tostring_float   = 3.14159
  tostring_boolean = true

  tostring_int_string   = provider::pyvider::tostring(local.tostring_integer)  # "42"
  tostring_float_string = provider::pyvider::tostring(local.tostring_float)    # "3.14159"
  tostring_bool_string  = provider::pyvider::tostring(local.tostring_boolean)  # "true"
}

output "tostring_boolean" {
  value = {
    integer = local.tostring_int_string
    float   = local.tostring_float_string
    boolean = local.tostring_bool_string
  }
}
