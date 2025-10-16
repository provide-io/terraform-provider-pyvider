---
page_title: "Function: length"
description: |-
  Returns the length of lists, maps, or strings with null-safe handling
---

# length (Function)

> Returns the number of elements in a collection (list, map, or string) with null-safe handling

The `length` function counts the number of elements in a collection and returns the count as an integer. It works with lists, maps (dictionaries), and strings, handling null values gracefully.

## When to Use This

- **Validation**: Check if collections have expected sizes
- **Conditional logic**: Make decisions based on collection size
- **Loop bounds**: Determine iteration limits
- **Resource scaling**: Scale resources based on collection size
- **Capacity planning**: Assess data volume

**Anti-patterns (when NOT to use):**
- Empty checks (use direct comparison: `collection != null && collection != []`)
- Performance-critical paths with very large collections
- When you only need to know if collection is empty (use boolean checks)

## Quick Start

```terraform
# List length
locals {
  servers = ["web1", "web2", "web3"]
  server_count = provider::pyvider::length(local.servers)  # Returns: 3
}

# Map length
locals {
  config = {
    host = "localhost"
    port = 8080
    ssl  = true
  }
  config_keys = provider::pyvider::length(local.config)  # Returns: 3
}

# String length
locals {
  message = "Hello World"
  char_count = provider::pyvider::length(local.message)  # Returns: 11
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

### Validation and Conditional Logic



### Resource Scaling



### Collection Analysis



## Signature

`length(collection: list|map|string) -> number`

## Arguments

- **`collection`** (list|map|string, required) - The collection to measure. Can be a list, map/object, or string. Returns `null` if this value is `null`.

## Return Value

Returns the count of elements as an integer:
- **Lists**: Number of elements in the list
- **Maps/Objects**: Number of key-value pairs
- **Strings**: Number of characters (including spaces)
- Returns `null` if the input is `null`
- Returns `0` for empty collections

## Behavior with Different Types

### Lists
```terraform
locals {
  empty_list = []
  small_list = ["a", "b"]
  mixed_list = [1, "text", true, null]

  counts = {
    empty = provider::pyvider::length(local.empty_list)   # 0
    small = provider::pyvider::length(local.small_list)   # 2
    mixed = provider::pyvider::length(local.mixed_list)   # 4
  }
}
```

### Maps/Objects
```terraform
locals {
  empty_map = {}
  user_data = {
    name  = "Alice"
    email = "alice@example.com"
    age   = 30
  }

  counts = {
    empty = provider::pyvider::length(local.empty_map)    # 0
    user  = provider::pyvider::length(local.user_data)    # 3
  }
}
```

### Strings
```terraform
locals {
  empty_string = ""
  simple_text = "hello"
  with_spaces = "hello world"
  unicode_text = "🚀 rocket"

  counts = {
    empty   = provider::pyvider::length(local.empty_string)  # 0
    simple  = provider::pyvider::length(local.simple_text)   # 5
    spaces  = provider::pyvider::length(local.with_spaces)   # 11
    unicode = provider::pyvider::length(local.unicode_text)  # 8
  }
}
```

## Common Patterns

### Validation
```terraform
variable "required_tags" {
  type = list(string)
  validation {
    condition     = provider::pyvider::length(var.required_tags) > 0
    error_message = "At least one tag is required."
  }
}

variable "user_config" {
  type = map(string)
  validation {
    condition     = provider::pyvider::length(var.user_config) <= 10
    error_message = "Configuration cannot have more than 10 keys."
  }
}
```

### Conditional Resource Creation
```terraform
variable "backup_servers" {
  type = list(string)
  default = []
}

locals {
  needs_load_balancer = provider::pyvider::length(var.backup_servers) > 1
}

resource "pyvider_file_content" "load_balancer_config" {
  count = local.needs_load_balancer ? 1 : 0

  filename = "/tmp/load_balancer.conf"
  content  = "Servers: ${provider::pyvider::join(",", var.backup_servers)}"
}
```

### Dynamic Scaling
```terraform
variable "applications" {
  type = list(object({
    name = string
    port = number
  }))
}

locals {
  app_count = provider::pyvider::length(var.applications)
  min_instances = provider::pyvider::max([local.app_count, 2])
}

resource "pyvider_local_directory" "app_dirs" {
  count = local.min_instances
  path  = "/tmp/app_${count.index + 1}"
}
```

### Size-based Configuration
```terraform
variable "dataset" {
  type = list(string)
}

locals {
  data_size = provider::pyvider::length(var.dataset)
  processing_mode = local.data_size > 1000 ? "batch" : "realtime"
  worker_count = local.data_size > 100 ? 4 : 1
}

resource "pyvider_file_content" "processing_config" {
  filename = "/tmp/processing.conf"
  content = join("\n", [
    "mode=${local.processing_mode}",
    "workers=${local.worker_count}",
    "data_size=${local.data_size}"
  ])
}
```

## Best Practices

### 1. Null Safety
```terraform
locals {
  safe_length = var.optional_list != null ? provider::pyvider::length(var.optional_list) : 0
}
```

### 2. Meaningful Validation
```terraform
variable "server_list" {
  type = list(string)
  validation {
    condition = (
      provider::pyvider::length(var.server_list) >= 1 &&
      provider::pyvider::length(var.server_list) <= 10
    )
    error_message = "Server list must contain between 1 and 10 servers."
  }
}
```

### 3. Performance Considerations
```terraform
# Cache length for multiple uses
locals {
  items_count = provider::pyvider::length(var.large_dataset)
  needs_pagination = local.items_count > 100
  batch_size = local.items_count > 1000 ? 50 : 10
}
```

## Related Functions

- [`contains`](./contains.md) - Check if a list contains an element
- [`lookup`](./lookup.md) - Look up values in maps
- [`max`](../numeric_functions/max.md) - Find maximum length
- [`min`](../numeric_functions/min.md) - Find minimum length