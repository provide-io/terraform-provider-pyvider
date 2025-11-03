# Basic type conversion
locals {
  basic_number = 42
  basic_boolean = true
  basic_list = [1, 2, 3]

  basic_num_str = provider::pyvider::tostring(local.basic_number)  # "42"
  basic_bool_str = provider::pyvider::tostring(local.basic_boolean)  # "true"
  basic_list_str = provider::pyvider::tostring(local.basic_list)  # "[1, 2, 3]"
}

output "basic_list_str" {
  value = {
    number = local.basic_num_str
    boolean = local.basic_bool_str
    list = local.basic_list_str
  }
}
