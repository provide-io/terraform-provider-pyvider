---
page_title: "Function: lookup"
description: |-
  Performs dynamic key-based lookups in maps with default value support and error handling
---
# lookup (Function)

The `lookup` function searches for a key in a map and returns the corresponding value. It supports optional default values for missing keys and provides clear error messages when keys don't exist and no default is provided, making it essential for safe and robust configuration management.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Dynamic key-based lookups enable flexible configuration patterns where values are resolved at runtime based on variables or computed values. The function's default value support allows graceful degradation when optional keys are missing, while its error handling ensures that required keys are validated during plan time.

## Capabilities

This function enables you to:

- **Configuration management**: Look up configuration values by key for environment-specific settings
- **Data transformation**: Map input values to output values for flexible configurations
- **Environment-specific settings**: Get environment-specific configurations dynamically
- **Resource mapping**: Map resource names to their configurations for scalable infrastructure
- **Dynamic value resolution**: Resolve values based on runtime conditions and variables

## Example Usage

```terraform
locals {
  example_result = length(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of length function"
  value       = local.example_result
}

```

## Signature

``lookup(input)``

## Arguments





## Return Value

Returns the value associated with the key:
- Returns the map value if the key exists
- Returns the default value if the key doesn't exist and a default is provided
- Returns `null` if the input map is `null`
- **Raises an error** if the key doesn't exist and no default is provided

## Error Handling

The function provides clear error messages when a key is not found and no default value is specified. This helps catch configuration errors early during the plan phase. When a default value is provided, the function returns it gracefully for missing keys, enabling optional configuration patterns.

## Common Patterns

### Environment Configuration
```terraform
variable "environment" {
  type = string
}

locals {
  environment_configs = {
    development = {
      database_url = "localhost:5432"
      log_level = "debug"
    }
    production = {
      database_url = "prod-db:5432"
      log_level = "warn"
    }
  }

  current_config = provider::pyvider::lookup(local.environment_configs, var.environment)
  database_url = provider::pyvider::lookup(local.current_config, "database_url")
}
```

### Resource Size Mapping
```terraform
variable "instance_type" {
  type = string
  default = "medium"
}

locals {
  instance_specs = {
    small = { cpu = 1, memory = 2 }
    medium = { cpu = 2, memory = 4 }
    large = { cpu = 4, memory = 8 }
  }

  default_spec = { cpu = 2, memory = 4 }

  selected_spec = provider::pyvider::lookup(local.instance_specs, var.instance_type, local.default_spec)
  cpu_count = provider::pyvider::lookup(local.selected_spec, "cpu")
}
```

### Feature Flag Resolution
```terraform
variable "feature_flags" {
  type = map(bool)
  default = {
    new_ui = true
    analytics = false
  }
}

locals {
  ui_enabled = provider::pyvider::lookup(var.feature_flags, "new_ui", false)
  analytics_enabled = provider::pyvider::lookup(var.feature_flags, "analytics", false)
  experimental_enabled = provider::pyvider::lookup(var.feature_flags, "experimental", false)
}
```

## Best Practices

### Always Provide Defaults for Optional Keys
Always specify a default value when looking up optional configuration keys. This prevents errors and makes your configuration more resilient to missing data.

### Validate Map Structure
For required keys, use variable validation to ensure they exist before attempting lookups. This provides clearer error messages at the variable level.

### Chain Lookups for Complex Data
For nested configurations, perform multiple lookups in sequence rather than trying to access deeply nested paths directly. This provides better error messages and more control over defaults at each level.

## Related Components

- **contains** (Function) - Check if lists contain elements
- **length** (Function) - Get the size of maps