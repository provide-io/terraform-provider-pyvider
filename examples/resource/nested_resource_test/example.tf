resource "pyvider_nested_resource_test" "example" {
  resource_name = "api-gateway"

  # A dynamic attribute: the shape is not known until apply.
  configuration = {
    region   = "us-west-2"
    replicas = 3
  }

  nested_configs {
    service     = "http"
    port        = 80
    protocol    = "tcp"
    ssl_enabled = false
  }

  nested_configs {
    service     = "https"
    port        = 443
    protocol    = "tcp"
    ssl_enabled = true
  }
}

output "processed" {
  # processed_data echoes the configuration back with a count of the blocks.
  value = pyvider_nested_resource_test.example.processed_data
}
