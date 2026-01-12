data "pyvider_simple_map_test" "example" {
  input_data = {
    key1 = "hello"
    key2 = "world"
    key3 = "test"
  }
}

output "simple_processed_data" {
  description = "Map with all values converted to uppercase"
  value       = data.pyvider_simple_map_test.example.processed_data
}

output "simple_data_hash" {
  description = "SHA256 hash of the processed data"
  value       = data.pyvider_simple_map_test.example.data_hash
}
