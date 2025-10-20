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

# Example 1: Length function
locals {
  numbers = [1, 2, 3, 4, 5]
  colors  = ["red", "green", "blue"]
  message = "Hello World"
  config  = { host = "localhost", port = 8080 }

  numbers_length = provider::pyvider::length(local.numbers) # 5
  colors_length  = provider::pyvider::length(local.colors)  # 3
  message_length = provider::pyvider::length(local.message) # 11
  config_length  = provider::pyvider::length(local.config)  # 2
}

# Example 2: Contains function
locals {
  fruits = ["apple", "banana", "cherry"]
  ports  = [80, 443, 8080]

  has_apple  = provider::pyvider::contains(local.fruits, "apple")  # true
  has_grape  = provider::pyvider::contains(local.fruits, "grape")  # false
  has_port80 = provider::pyvider::contains(local.ports, 80)        # true
  has_port22 = provider::pyvider::contains(local.ports, 22)        # false
}

# Example 3: Lookup function
locals {
  settings = {
    database_host = "db.example.com"
    database_port = 5432
    cache_host    = "redis.local"
  }

  db_host      = provider::pyvider::lookup(local.settings, "database_host", "localhost")
  db_port      = provider::pyvider::lookup(local.settings, "database_port", 5432)
  unknown_key  = provider::pyvider::lookup(local.settings, "missing_key", "default")
}

# Example 4: Practical usage
locals {
  servers = ["web1", "web2", "web3"]

  server_count   = provider::pyvider::length(local.servers)
  has_web1       = provider::pyvider::contains(local.servers, "web1")
  needs_scaling  = local.server_count < 5
}

output "collection_examples" {
  value = {
    lengths = {
      numbers = local.numbers_length
      colors  = local.colors_length
      message = local.message_length
      config  = local.config_length
    }
    contains_checks = {
      has_apple  = local.has_apple
      has_grape  = local.has_grape
      has_port80 = local.has_port80
    }
    lookups = {
      db_host     = local.db_host
      db_port     = local.db_port
      unknown_key = local.unknown_key
    }
    practical = {
      server_count  = local.server_count
      has_web1      = local.has_web1
      needs_scaling = local.needs_scaling
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