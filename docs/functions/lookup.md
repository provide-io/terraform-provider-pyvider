---
page_title: "Function: lookup"
description: |-
  Performs dynamic key-based lookups in maps with default value support and error handling
---

# lookup (Function)

> Retrieves values from maps using dynamic keys with optional default values and comprehensive error handling

The `lookup` function searches for a key in a map and returns the corresponding value. It supports default values for missing keys and provides clear error messages when keys don't exist and no default is provided.

## When to Use This

- **Configuration management**: Look up configuration values by key
- **Data transformation**: Map input values to output values
- **Environment-specific settings**: Get environment-specific configurations
- **Resource mapping**: Map resource names to their configurations
- **Dynamic value resolution**: Resolve values based on runtime conditions

**Anti-patterns (when NOT to use):**
- Static key access (use direct map access: `map.key`)
- List element access (use list indexing)
- Complex nested object traversal (use multiple lookups or path functions)
- When key existence is uncertain without proper error handling

## Quick Start

```terraform
# Simple lookup
locals {
  region_configs = {
    us-east-1 = "config-east"
    us-west-2 = "config-west"
    eu-west-1 = "config-europe"
  }
  current_region = "us-west-2"
  config = provider::pyvider::lookup(local.region_configs, local.current_region)  # Returns: "config-west"
}

# Lookup with default
locals {
  environment_ports = {
    development = 3000
    staging = 4000
  }
  current_env = "production"
  port = provider::pyvider::lookup(local.environment_ports, local.current_env, 8080)  # Returns: 8080 (default)
}
```

## Examples

### Basic Usage

```terraform
# Basic collection function examples

# Length function examples
locals {
  # List length examples
  number_list = [1, 2, 3, 4, 5]
  string_list = ["apple", "banana", "cherry"]
  empty_list = []

  number_list_length = provider::pyvider::length(local.number_list)    # Returns: 5
  string_list_length = provider::pyvider::length(local.string_list)    # Returns: 3
  empty_list_length = provider::pyvider::length(local.empty_list)      # Returns: 0

  # String length examples
  short_string = "Hello"
  long_string = "The quick brown fox jumps over the lazy dog"
  empty_string = ""

  short_string_length = provider::pyvider::length(local.short_string)  # Returns: 5
  long_string_length = provider::pyvider::length(local.long_string)    # Returns: 43
  empty_string_length = provider::pyvider::length(local.empty_string)  # Returns: 0

  # Map length examples
  simple_map = {
    name = "Alice"
    age = 30
    city = "New York"
  }
  empty_map = {}

  simple_map_length = provider::pyvider::length(local.simple_map)      # Returns: 3
  empty_map_length = provider::pyvider::length(local.empty_map)        # Returns: 0
}

# Contains function examples
locals {
  # List contains examples
  fruits = ["apple", "banana", "cherry", "date"]

  has_apple = provider::pyvider::contains(local.fruits, "apple")       # Returns: true
  has_grape = provider::pyvider::contains(local.fruits, "grape")       # Returns: false

  # Number list contains examples
  numbers = [1, 2, 3, 4, 5]

  has_three = provider::pyvider::contains(local.numbers, 3)            # Returns: true
  has_ten = provider::pyvider::contains(local.numbers, 10)             # Returns: false

  # Mixed type list examples
  mixed_list = ["apple", "banana", 123, true]

  has_banana = provider::pyvider::contains(local.mixed_list, "banana") # Returns: true
  has_false = provider::pyvider::contains(local.mixed_list, false)     # Returns: false
}

# Lookup function examples
locals {
  # Simple map lookup
  config_map = {
    database_host = "db.example.com"
    database_port = 5432
    debug_mode = true
  }

  db_host = provider::pyvider::lookup(local.config_map, "database_host", "localhost")     # Returns: "db.example.com"
  cache_ttl = provider::pyvider::lookup(local.config_map, "cache_ttl", 3600)             # Returns: 3600 (default)
  ssl_enabled = provider::pyvider::lookup(local.config_map, "ssl_enabled", false)        # Returns: false (default)

  # Nested map lookup
  nested_config = {
    server = {
      host = "api.example.com"
      port = 8080
    }
    database = {
      host = "db.example.com"
      port = 5432
    }
  }

  server_info = provider::pyvider::lookup(local.nested_config, "server", {})
  cache_info = provider::pyvider::lookup(local.nested_config, "cache", { enabled = false })
}

# Combined collection operations
locals {
  # User management example
  users = [
    { name = "Alice", role = "admin", active = true },
    { name = "Bob", role = "user", active = true },
    { name = "Charlie", role = "user", active = false }
  ]

  total_users = provider::pyvider::length(local.users)

  # Check if we have any admin users
  roles = [for user in local.users : user.role]
  has_admin = provider::pyvider::contains(local.roles, "admin")

  # Environment configuration with defaults
  env_defaults = {
    environment = "development"
    log_level = "info"
    max_connections = 100
    timeout_seconds = 30
  }

  # Simulated environment variables (would come from actual env vars)
  env_vars = {
    environment = "production"
    log_level = "warn"
  }

  # Build final configuration with defaults
  final_env = provider::pyvider::lookup(local.env_vars, "environment", local.env_defaults.environment)
  final_log_level = provider::pyvider::lookup(local.env_vars, "log_level", local.env_defaults.log_level)
  final_max_conn = provider::pyvider::lookup(local.env_vars, "max_connections", local.env_defaults.max_connections)
  final_timeout = provider::pyvider::lookup(local.env_vars, "timeout_seconds", local.env_defaults.timeout_seconds)
}

# Validation examples
locals {
  # Input validation using collection functions
  required_fields = ["name", "email", "password"]
  provided_fields = ["name", "email", "age"]

  # Check if all required fields are present
  missing_fields = [
    for field in local.required_fields :
    field if !provider::pyvider::contains(local.provided_fields, field)
  ]

  has_all_required = provider::pyvider::length(local.missing_fields) == 0
}

# Output results for verification
output "collection_function_examples" {
  value = {
    length_operations = {
      lists = {
        numbers = {
          data = local.number_list
          length = local.number_list_length
        }
        strings = {
          data = local.string_list
          length = local.string_list_length
        }
        empty = {
          data = local.empty_list
          length = local.empty_list_length
        }
      }

      strings = {
        short = {
          data = local.short_string
          length = local.short_string_length
        }
        long = {
          data = local.long_string
          length = local.long_string_length
        }
        empty = {
          data = local.empty_string
          length = local.empty_string_length
        }
      }

      maps = {
        simple = {
          data = local.simple_map
          length = local.simple_map_length
        }
        empty = {
          data = local.empty_map
          length = local.empty_map_length
        }
      }
    }

    contains_operations = {
      string_lists = {
        fruits = local.fruits
        has_apple = local.has_apple
        has_grape = local.has_grape
      }

      number_lists = {
        numbers = local.numbers
        has_three = local.has_three
        has_ten = local.has_ten
      }

      mixed_lists = {
        mixed_list = local.mixed_list
        has_banana = local.has_banana
        has_false = local.has_false
      }
    }

    lookup_operations = {
      simple_lookups = {
        db_host = local.db_host
        cache_ttl = local.cache_ttl
        ssl_enabled = local.ssl_enabled
      }

      nested_lookups = {
        server_info = local.server_info
        cache_info = local.cache_info
      }
    }

    combined_operations = {
      user_management = {
        total_users = local.total_users
        has_admin = local.has_admin
      }

      configuration = {
        environment = local.final_env
        log_level = local.final_log_level
        max_connections = local.final_max_conn
        timeout = local.final_timeout
      }

      validation = {
        required_fields = local.required_fields
        missing_fields = local.missing_fields
        has_all_required = local.has_all_required
      }
    }
  }
}
```

### Configuration Management



### Environment-Specific Settings



### Error Handling



## Signature

`lookup(map_to_search: map[string, any], key: string, default?: any) -> any`

## Arguments

- **`map_to_search`** (map[string, any], required) - The map to search within. Returns `null` if this value is `null`.
- **`key`** (string, required) - The key to look up in the map.
- **`default`** (any, optional) - The value to return if the key is not found. If not provided and key is missing, an error is raised.

## Return Value

Returns the value associated with the key:
- Returns the map value if the key exists
- Returns the default value if the key doesn't exist and a default is provided
- Returns `null` if the input map is `null`
- **Raises an error** if the key doesn't exist and no default is provided

## Error Handling

### Missing Key Without Default
```terraform
# This will cause an error
locals {
  config = { dev = "localhost" }
  # Error: Invalid key for map lookup: key "prod" does not exist in the map
  # bad_lookup = provider::pyvider::lookup(local.config, "prod")
}

# Safe lookup with default
locals {
  config = { dev = "localhost" }
  safe_lookup = provider::pyvider::lookup(local.config, "prod", "default-host")
}
```

### Null Map Handling
```terraform
locals {
  null_map_result = provider::pyvider::lookup(null, "any_key")  # Returns: null
}
```

## Behavior Details

### Key Existence Check
```terraform
locals {
  test_map = {
    existing_key = "value"
    empty_value = ""
    null_value = null
  }

  results = {
    exists = provider::pyvider::lookup(local.test_map, "existing_key")     # "value"
    empty = provider::pyvider::lookup(local.test_map, "empty_value")       # ""
    null_val = provider::pyvider::lookup(local.test_map, "null_value")     # null
    missing = provider::pyvider::lookup(local.test_map, "missing", "default") # "default"
  }
}
```

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
      cache_ttl = 60
    }
    staging = {
      database_url = "staging-db:5432"
      log_level = "info"
      cache_ttl = 300
    }
    production = {
      database_url = "prod-db:5432"
      log_level = "warn"
      cache_ttl = 3600
    }
  }

  current_config = provider::pyvider::lookup(local.environment_configs, var.environment)
  database_url = provider::pyvider::lookup(local.current_config, "database_url")
  log_level = provider::pyvider::lookup(local.current_config, "log_level")
}

resource "pyvider_file_content" "app_config" {
  filename = "/tmp/app.conf"
  content = join("\n", [
    "database_url=${local.database_url}",
    "log_level=${local.log_level}",
    "environment=${var.environment}"
  ])
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
    small = {
      cpu = 1
      memory = 2
      storage = 20
    }
    medium = {
      cpu = 2
      memory = 4
      storage = 50
    }
    large = {
      cpu = 4
      memory = 8
      storage = 100
    }
  }

  default_spec = {
    cpu = 2
    memory = 4
    storage = 50
  }

  selected_spec = provider::pyvider::lookup(local.instance_specs, var.instance_type, local.default_spec)
  cpu_count = provider::pyvider::lookup(local.selected_spec, "cpu")
  memory_gb = provider::pyvider::lookup(local.selected_spec, "memory")
}
```

### Feature Flag Resolution
```terraform
variable "feature_flags" {
  type = map(bool)
  default = {
    new_ui = true
    analytics = false
    beta_features = false
  }
}

locals {
  # Look up feature flags with safe defaults
  ui_enabled = provider::pyvider::lookup(var.feature_flags, "new_ui", false)
  analytics_enabled = provider::pyvider::lookup(var.feature_flags, "analytics", false)
  beta_enabled = provider::pyvider::lookup(var.feature_flags, "beta_features", false)

  # Additional features not in config default to false
  experimental_enabled = provider::pyvider::lookup(var.feature_flags, "experimental", false)
}

resource "pyvider_file_content" "feature_config" {
  filename = "/tmp/features.json"
  content = jsonencode({
    ui_version = local.ui_enabled ? "new" : "classic"
    analytics = local.analytics_enabled
    beta = local.beta_enabled
    experimental = local.experimental_enabled
  })
}
```

### Multi-level Configuration Lookup
```terraform
variable "region" {
  type = string
}

variable "environment" {
  type = string
}

locals {
  regional_configs = {
    "us-east-1" = {
      development = { endpoint = "dev-east.example.com", replicas = 1 }
      production = { endpoint = "prod-east.example.com", replicas = 3 }
    }
    "us-west-2" = {
      development = { endpoint = "dev-west.example.com", replicas = 1 }
      production = { endpoint = "prod-west.example.com", replicas = 3 }
    }
  }

  default_config = { endpoint = "default.example.com", replicas = 1 }

  # Two-level lookup with defaults
  region_config = provider::pyvider::lookup(local.regional_configs, var.region, {})
  final_config = provider::pyvider::lookup(local.region_config, var.environment, local.default_config)

  endpoint = provider::pyvider::lookup(local.final_config, "endpoint")
  replicas = provider::pyvider::lookup(local.final_config, "replicas")
}
```

## Best Practices

### 1. Always Provide Defaults for Optional Keys
```terraform
locals {
  # Good - provides sensible defaults
  timeout = provider::pyvider::lookup(var.config, "timeout", 30)
  retries = provider::pyvider::lookup(var.config, "retries", 3)

  # Avoid - could cause errors if keys don't exist
  # risky_value = provider::pyvider::lookup(var.config, "optional_key")
}
```

### 2. Validate Map Structure
```terraform
variable "configuration" {
  type = map(string)
  validation {
    condition = (
      provider::pyvider::contains(keys(var.configuration), "required_key1") &&
      provider::pyvider::contains(keys(var.configuration), "required_key2")
    )
    error_message = "Configuration must contain required_key1 and required_key2."
  }
}

locals {
  value1 = provider::pyvider::lookup(var.configuration, "required_key1")
  value2 = provider::pyvider::lookup(var.configuration, "required_key2")
}
```

### 3. Use Descriptive Error Handling
```terraform
locals {
  # Create meaningful defaults
  database_config = provider::pyvider::lookup(
    var.database_configs,
    var.environment,
    {
      host = "localhost"
      port = 5432
      database = "default_db"
    }
  )
}
```

### 4. Chain Lookups for Complex Data
```terraform
locals {
  # First lookup: get environment config
  env_config = provider::pyvider::lookup(var.all_configs, var.environment)

  # Second lookup: get service config within environment
  service_config = provider::pyvider::lookup(local.env_config, var.service_name)

  # Third lookup: get specific values
  port = provider::pyvider::lookup(local.service_config, "port", 8080)
  replicas = provider::pyvider::lookup(local.service_config, "replicas", 1)
}
```

## Related Functions

- [`contains`](./contains.md) - Check if lists contain elements
- [`length`](./length.md) - Get the size of maps
- [`keys`](https://terraform.io/docs/language/functions/keys.html) - Get map keys (Terraform built-in)
- [`values`](https://terraform.io/docs/language/functions/values.html) - Get map values (Terraform built-in)