data "pyvider_mixed_map_test" "mixed" {
  input_data = {
    string_value = "hello"
    number_value = 42
    another_str  = "world"
    float_value  = 3.14
  }
}

output "mixed_processed_mixed_data" {
  description = "Map with values processed by type (strings uppercased, numbers incremented)"
  value       = data.pyvider_mixed_map_test.mixed.processed_data
}

output "mixed_data_hash" {
  description = "SHA256 hash of the processed mixed data"
  value       = data.pyvider_mixed_map_test.mixed.data_hash
}
