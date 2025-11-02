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