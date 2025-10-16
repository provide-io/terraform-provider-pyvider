---
page_title: "Function: contains"
description: |-
  Checks if a list contains a specific element with null-safe handling
---

# contains (Function)

> Tests whether a list contains a specific element with null-safe handling and type-aware comparison

The `contains` function searches through a list to determine if it contains a specific element. It performs exact matching and handles null values gracefully, returning a boolean result.

## When to Use This

- **Validation**: Check if required values are present in lists
- **Conditional logic**: Make decisions based on list membership
- **Security checks**: Verify if values are in allowlists or blocklists
- **Feature toggles**: Check if features are enabled in configuration lists
- **Data filtering**: Determine if items meet criteria

**Anti-patterns (when NOT to use):**
- Map/object key checking (use map lookup instead)
- String substring search (use string functions)
- Complex object matching (use custom logic)
- Performance-critical paths with very large lists

## Quick Start

```terraform
# Simple containment check
locals {
  allowed_envs = ["dev", "staging", "production"]
  current_env = "production"
  is_valid_env = provider::pyvider::contains(local.allowed_envs, local.current_env)  # Returns: true
}

# Security validation
locals {
  blocked_ips = ["192.168.1.100", "10.0.0.50"]
  client_ip = "192.168.1.100"
  is_blocked = provider::pyvider::contains(local.blocked_ips, local.client_ip)  # Returns: true
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

  # String contains examples
  sample_text = "The quick brown fox"

  contains_fox = provider::pyvider::contains(local.sample_text, "fox") # Returns: true
  contains_cat = provider::pyvider::contains(local.sample_text, "cat") # Returns: false
  contains_quick = provider::pyvider::contains(local.sample_text, "quick") # Returns: true

  # Map contains examples (checks for keys)
  user_data = {
    username = "alice123"
    email = "alice@example.com"
    active = true
  }

  has_username = provider::pyvider::contains(local.user_data, "username") # Returns: true
  has_password = provider::pyvider::contains(local.user_data, "password") # Returns: false
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
  user_input = {
    name = "John Doe"
    email = "john@example.com"
    age = 25
  }

  # Check if all required fields are present
  missing_fields = [
    for field in local.required_fields :
    field if !provider::pyvider::contains(local.user_input, field)
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
      lists = {
        fruits = local.fruits
        has_apple = local.has_apple
        has_grape = local.has_grape
      }

      strings = {
        text = local.sample_text
        contains_fox = local.contains_fox
        contains_cat = local.contains_cat
        contains_quick = local.contains_quick
      }

      maps = {
        user_data = local.user_data
        has_username = local.has_username
        has_password = local.has_password
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

### Security and Validation



### Configuration Checks



### Feature Toggles



## Signature

`contains(list_to_check: list[any], element: any) -> boolean`

## Arguments

- **`list_to_check`** (list[any], required) - The list to search within. Returns `null` if this value is `null`.
- **`element`** (any, required) - The element to search for. Can be any type (string, number, boolean, etc.).

## Return Value

Returns a boolean indicating whether the element was found:
- `true` if the element exists in the list
- `false` if the element does not exist in the list
- Returns `null` if the input list is `null`
- Uses exact equality comparison (type and value must match)

## Behavior Details

### Type-Sensitive Matching
```terraform
locals {
  mixed_list = [1, "1", true, "true"]

  checks = {
    number_1 = provider::pyvider::contains(local.mixed_list, 1)      # true
    string_1 = provider::pyvider::contains(local.mixed_list, "1")    # true
    bool_true = provider::pyvider::contains(local.mixed_list, true)   # true
    string_true = provider::pyvider::contains(local.mixed_list, "true") # true

    # These are different types, so they don't match
    number_vs_string = provider::pyvider::contains(local.mixed_list, "2") # false ("2" not in list)
  }
}
```

### Null Handling
```terraform
locals {
  list_with_null = ["a", null, "b"]

  checks = {
    has_null = provider::pyvider::contains(local.list_with_null, null)    # true
    null_list = provider::pyvider::contains(null, "value")                # null
  }
}
```

### Empty List Handling
```terraform
locals {
  empty_list = []
  result = provider::pyvider::contains(local.empty_list, "anything")  # false
}
```

## Common Patterns

### Environment Validation
```terraform
variable "environment" {
  type = string
}

locals {
  valid_environments = ["development", "staging", "production"]
  is_valid_env = provider::pyvider::contains(local.valid_environments, var.environment)
}

resource "pyvider_file_content" "env_check" {
  count = local.is_valid_env ? 1 : 0

  filename = "/tmp/environment.txt"
  content  = "Environment ${var.environment} is valid"
}
```

### Feature Toggle Management
```terraform
variable "enabled_features" {
  type = list(string)
  default = ["feature_a", "feature_c"]
}

locals {
  feature_flags = {
    analytics_enabled = provider::pyvider::contains(var.enabled_features, "analytics")
    debug_enabled = provider::pyvider::contains(var.enabled_features, "debug")
    feature_a_enabled = provider::pyvider::contains(var.enabled_features, "feature_a")
  }
}

resource "pyvider_file_content" "feature_config" {
  filename = "/tmp/features.conf"
  content = join("\n", [
    "analytics=${local.feature_flags.analytics_enabled}",
    "debug=${local.feature_flags.debug_enabled}",
    "feature_a=${local.feature_flags.feature_a_enabled}"
  ])
}
```

### Security Allowlist/Blocklist
```terraform
variable "client_ip" {
  type = string
}

variable "allowed_ips" {
  type = list(string)
  default = ["192.168.1.0/24", "10.0.0.100", "203.0.113.50"]
}

variable "blocked_ips" {
  type = list(string)
  default = ["192.168.1.100", "10.0.0.50"]
}

locals {
  is_allowed = provider::pyvider::contains(var.allowed_ips, var.client_ip)
  is_blocked = provider::pyvider::contains(var.blocked_ips, var.client_ip)
  access_granted = local.is_allowed && !local.is_blocked
}

resource "pyvider_file_content" "access_decision" {
  filename = "/tmp/access.log"
  content = join("\n", [
    "Client IP: ${var.client_ip}",
    "Allowed: ${local.is_allowed}",
    "Blocked: ${local.is_blocked}",
    "Access Granted: ${local.access_granted}"
  ])
}
```

### Configuration Validation
```terraform
variable "deployment_strategy" {
  type = string
}

variable "service_tier" {
  type = string
}

locals {
  valid_strategies = ["blue-green", "rolling", "canary"]
  valid_tiers = ["free", "basic", "premium", "enterprise"]

  config_valid = (
    provider::pyvider::contains(local.valid_strategies, var.deployment_strategy) &&
    provider::pyvider::contains(local.valid_tiers, var.service_tier)
  )
}

resource "pyvider_file_content" "deployment_config" {
  count = local.config_valid ? 1 : 0

  filename = "/tmp/deployment.yaml"
  content = join("\n", [
    "strategy: ${var.deployment_strategy}",
    "tier: ${var.service_tier}",
    "validated: true"
  ])
}
```

## Best Practices

### 1. Validate Input Types
```terraform
variable "search_list" {
  type = list(string)
  validation {
    condition     = length(var.search_list) >= 0
    error_message = "Search list must be valid."
  }
}

variable "search_value" {
  type = string
}

locals {
  found = provider::pyvider::contains(var.search_list, var.search_value)
}
```

### 2. Handle Null Cases
```terraform
locals {
  safe_contains = var.optional_list != null ? provider::pyvider::contains(var.optional_list, var.value) : false
}
```

### 3. Use with Conditional Logic
```terraform
locals {
  requires_special_handling = provider::pyvider::contains(var.special_cases, var.current_case)

  processing_mode = local.requires_special_handling ? "special" : "standard"
}
```

### 4. Combine with Other Functions
```terraform
# Check multiple conditions
locals {
  critical_environments = ["production", "staging"]
  is_critical = provider::pyvider::contains(local.critical_environments, var.environment)

  # Use with length for validation
  has_required_tags = provider::pyvider::length(var.tags) > 0
  has_env_tag = provider::pyvider::contains(var.tags, "environment:${var.environment}")

  deployment_ready = local.is_critical ? (local.has_required_tags && local.has_env_tag) : local.has_required_tags
}
```

## Related Functions

- [`length`](./length.md) - Get the size of collections
- [`lookup`](./lookup.md) - Look up values in maps (for key-value searches)
- [`split`](../string_manipulation/split.md) - Split strings to create searchable lists
- [`join`](../string_manipulation/join.md) - Join lists after filtering