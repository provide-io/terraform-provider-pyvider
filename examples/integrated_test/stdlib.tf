locals {
  sample_list = ["a", "b", "c"]
  sample_map = {
    "key1" = "value1"
    "key2" = "value2"
  }
  sample_string = "hello"
}

# --- length() ---
output "length_of_list" {
  value = provider::pyvider::length(local.sample_list)
}
output "length_of_map" {
  value = provider::pyvider::length(local.sample_map)
}
output "length_of_string" {
  value = provider::pyvider::length(local.sample_string)
}

# --- contains() ---
output "contains_true" {
  value = provider::pyvider::contains(local.sample_list, "b")
}
output "contains_false" {
  value = provider::pyvider::contains(local.sample_list, "z")
}

# --- lookup() ---
output "lookup_success" {
  value = provider::pyvider::lookup(local.sample_map, "key1", "default")
}
output "lookup_with_default" {
  value = provider::pyvider::lookup(local.sample_map, "missing_key", "default_value_returned")
}

# --- tostring() ---
output "tostring_from_number" {
  value = provider::pyvider::tostring(123.45)
}
output "tostring_from_bool" {
  value = provider::pyvider::tostring(true)
}
