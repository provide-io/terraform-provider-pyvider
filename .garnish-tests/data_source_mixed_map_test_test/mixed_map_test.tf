# Test mixed type maps with various data types
data "pyvider_mixed_map_test" "mixed_config" {
  input_data = {
    string_value = "hello"
    number_value = 42
    bool_value   = true
    list_value   = ["a", "b", "c"]
    nested_map   = {
      inner_key = "inner_value"
      inner_num = 3.14
    }
  }
}

output "input_data" {
  description = "The input data provided"
  value       = data.pyvider_mixed_map_test.mixed_config.input_data
}

output "processed_data" {
  description = "The processed mixed type data"
  value       = data.pyvider_mixed_map_test.mixed_config.processed_data
}

output "data_hash" {
  description = "Hash of the processed data"
  value       = data.pyvider_mixed_map_test.mixed_config.data_hash
}