resource "pyvider_nested_resource_test" "example" {
  resource_name = "complex-test-resource"
  
  # A dynamic map attribute
  configuration = {
    "app_name" = "my_app"
    "replicas" = 3
    "enabled"  = true
    "tags"     = ["web", "api", "production"]
  }
  
  # A list of nested blocks
  nested_configs {
    service  = "web"
    port     = 80
    protocol = "http"
  }

  nested_configs {
    service     = "api" 
    port        = 443
    protocol    = "https"
    ssl_enabled = true
  }
}

output "nested_resource_result" {
  description = "The full state of the created resource."
  value       = pyvider_nested_resource_test.example
}
