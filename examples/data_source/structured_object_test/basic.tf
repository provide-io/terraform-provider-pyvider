data "pyvider_structured_object_test" "basic" {
  config_name = "my-config"
}

output "basic_generated_config" {
  description = "Generated configuration object with nested attributes"
  value       = data.pyvider_structured_object_test.basic.generated_config
}

output "basic_summary" {
  description = "Summary information with nested details"
  value       = data.pyvider_structured_object_test.basic.summary
}
