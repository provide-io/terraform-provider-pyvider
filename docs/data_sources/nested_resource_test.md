---
page_title: "Resource: pyvider_nested_resource_test"
description: |-
  A diagnostic resource for testing nested block and dynamic attribute handling.
---

# pyvider_nested_resource_test (Resource)

This is a diagnostic resource used to test and validate the framework's ability to correctly handle complex, nested data structures within a resource's state.

It accepts a dynamic `configuration` map and a list of `nested_configs` blocks. The resource's primary function is to process this nested data and reflect it in its computed attributes, confirming that the framework's data marshalling and state management are working correctly for complex schemas.

## Example Usage

```terraform
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

```

## Argument Reference

## Arguments

- `resource_name` (String, Required)
- `configuration` (String, Optional) Dynamic configuration map
- `processed_data` (String, Computed) Processed configuration data
- `resource_id` (String, Computed)
- `exists` (String, Computed)
