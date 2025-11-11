---
page_title: "Function: lens_jq"
subcategory: "Lens"
description: |-
  Applies jq queries to JSON data for powerful data transformation and extraction
---
# lens_jq (Function)

The `lens_jq` function enables powerful JSON data transformation using jq query syntax. It applies jq expressions to input data and returns the results as native Terraform objects, making it ideal for complex data manipulation and extraction tasks that go beyond simple field access.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


This function bridges the gap between JSON-based APIs and Terraform's native data structures, allowing you to filter, transform, and extract data with the full power of jq. The results are automatically converted to Terraform-native types, enabling seamless integration with the rest of your configuration.

## Capabilities

This function enables you to:

- **JSON data transformation**: Transform complex JSON structures using jq's rich query language
- **API response processing**: Extract specific fields from API responses with precision
- **Configuration manipulation**: Modify or extract configuration data programmatically
- **Data filtering**: Filter arrays and objects based on complex criteria
- **Complex data extraction**: Perform advanced queries on nested data structures

## Example Usage

```terraform
locals {
  example_data = {
    name  = "example"
    value = 42
  }

  example_result = provider::pyvider::lens_jq(local.example_data, ".name")
}

output "function_result" {
  description = "Result of lens_jq function"
  value       = local.example_result
}

```

## Signature

``lens_jq(input)``

## Arguments





## Return Value

Returns the result of applying the jq query to the input data. The return type depends on the query:
- Objects, arrays, strings, numbers, or booleans based on the query result
- `null` if the query returns null or if input data is null
- Results are automatically converted to Terraform-native types

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

## Related Components

- **lookup** (Function) - Simple key-value lookups for basic map access
- **contains** (Function) - Check array membership for simpler containment tests
- **length** (Function) - Get collection sizes

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
