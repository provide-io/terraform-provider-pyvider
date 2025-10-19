---
page_title: "Function: lens_jq"
description: |-
  Applies jq queries to JSON data for powerful data transformation and extraction
---

# lens_jq (Function)

> Applies jq queries to JSON data and returns transformed results as native objects

The `lens_jq` function enables powerful JSON data transformation using jq query syntax. It applies jq expressions to input data and returns the results as native Terraform objects, making it ideal for complex data manipulation and extraction tasks.

## When to Use This

- **JSON data transformation**: Transform complex JSON structures
- **API response processing**: Extract specific fields from API responses
- **Configuration manipulation**: Modify or extract configuration data
- **Data filtering**: Filter arrays and objects based on criteria
- **Complex data extraction**: Perform advanced queries on nested data

**Anti-patterns (when NOT to use):**
- Simple key access (use direct object access)
- Performance-critical paths (jq has overhead)
- When simpler functions suffice
- Non-JSON data types

## Quick Start

```terraform
# Extract specific field
locals {
  data = {
    users = [
      { name = "Alice", age = 30 },
      { name = "Bob", age = 25 }
    ]
  }
  names = provider::pyvider::lens_jq(".users[].name", local.data)  # Returns: ["Alice", "Bob"]
}

# Filter data
locals {
  filtered_users = provider::pyvider::lens_jq(".users[] | select(.age > 27)", local.data)
}
```

## Examples

### Basic Usage

```terraform
# Basic lens_jq function examples

# Example 1: Simple field extraction
locals {
  user_data = {
    id    = 123
    name  = "Alice Johnson"
    email = "alice@example.com"
  }

  user_name  = provider::pyvider::lens_jq(local.user_data, ".name")
  user_email = provider::pyvider::lens_jq(local.user_data, ".email")
  user_id    = provider::pyvider::lens_jq(local.user_data, ".id")
}

# Example 2: Array operations
locals {
  colors = ["red", "green", "blue", "yellow"]

  first_color = provider::pyvider::lens_jq(local.colors, ".[0]")
  last_color  = provider::pyvider::lens_jq(local.colors, ".[-1]")
  color_count = provider::pyvider::lens_jq(local.colors, "length")
}

# Example 3: Nested field access
locals {
  config = {
    database = {
      host = "localhost"
      port = 5432
    }
    cache = {
      host = "redis.local"
      port = 6379
    }
  }

  db_host    = provider::pyvider::lens_jq(local.config, ".database.host")
  db_port    = provider::pyvider::lens_jq(local.config, ".database.port")
  cache_host = provider::pyvider::lens_jq(local.config, ".cache.host")
}

# Example 4: Simple data transformation
locals {
  users = [
    { name = "Alice", active = true },
    { name = "Bob", active = false },
    { name = "Carol", active = true }
  ]

  active_users = provider::pyvider::lens_jq(local.users, "map(select(.active == true))")
  user_names   = provider::pyvider::lens_jq(local.users, "map(.name)")
}

# Output the results
output "lens_jq_examples" {
  value = {
    user_extraction = {
      name  = local.user_name
      email = local.user_email
      id    = local.user_id
    }
    array_operations = {
      first = local.first_color
      last  = local.last_color
      count = local.color_count
    }
    nested_access = {
      db_host    = local.db_host
      cache_host = local.cache_host
    }
    transformations = {
      active_users = length(local.active_users)
      all_names    = length(local.user_names)
    }
  }
}

```

### Data Transformation



### API Response Processing



### Complex Queries



## Signature

`lens_jq(query: string, data: any) -> any`

## Arguments

- **`query`** (string, required) - The jq expression to apply to the data
- **`data`** (any, required) - The input data to query (typically JSON-like objects)

## Return Value

Returns the result of applying the jq query to the input data. The return type depends on the query:
- Objects, arrays, strings, numbers, or booleans based on the query result
- `null` if the query returns null or if input data is null

## Common jq Query Patterns

### Field Extraction
```terraform
locals {
  config = { database = { host = "localhost", port = 5432 } }
  host = provider::pyvider::lens_jq(".database.host", local.config)  # "localhost"
  port = provider::pyvider::lens_jq(".database.port", local.config)  # 5432
}
```

### Array Processing
```terraform
locals {
  servers = {
    instances = [
      { name = "web-1", status = "running" },
      { name = "web-2", status = "stopped" },
      { name = "db-1", status = "running" }
    ]
  }

  running_servers = provider::pyvider::lens_jq(
    ".instances[] | select(.status == \"running\") | .name",
    local.servers
  )  # ["web-1", "db-1"]
}
```

### Data Transformation
```terraform
locals {
  raw_data = {
    metrics = [
      { service = "api", cpu = 75, memory = 60 },
      { service = "db", cpu = 45, memory = 80 }
    ]
  }

  transformed = provider::pyvider::lens_jq(
    ".metrics | map({name: .service, load: (.cpu + .memory) / 2})",
    local.raw_data
  )  # [{"name": "api", "load": 67.5}, {"name": "db", "load": 62.5}]
}
```

## Related Functions

- [`lookup`](../collection_functions/lookup.md) - Simple key-value lookups
- [`contains`](../collection_functions/contains.md) - Check array membership
- [`length`](../collection_functions/length.md) - Get collection sizes