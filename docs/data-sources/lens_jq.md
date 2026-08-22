---
page_title: "Data Source: pyvider_lens_jq"
subcategory: "Lens"
description: |-
  Transforms JSON data using JQ queries with powerful filtering and manipulation
---
# pyvider_lens_jq (Data Source)

The `pyvider_lens_jq` data source allows you to transform JSON data using JQ queries. This enables complex data manipulation, filtering, and extraction from JSON sources such as API responses, configuration files, or structured data within your Terraform configurations.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


This data source brings the full power of the JQ language to your Terraform workflows, enabling sophisticated JSON transformations that would be difficult or impossible with built-in Terraform functions alone. Whether you're reshaping API responses, extracting nested values, performing aggregations, or implementing complex filtering logic, JQ queries provide a concise and expressive way to manipulate JSON data at configuration time.

## Capabilities

This data source enables you to:

- **JSON data transformation**: Process complex JSON structures from APIs, files, or configuration sources
- **Data extraction**: Pull specific values from deeply nested JSON documents with simple queries
- **Configuration processing**: Transform configuration formats between different systems or schemas
- **API response filtering**: Extract only the relevant data from large or complex API responses
- **Data validation**: Check JSON structure, validate required fields, and ensure data quality
- **Array operations**: Map, filter, sort, group, and aggregate array data
- **Object reshaping**: Restructure JSON objects to match desired schemas
- **Statistical operations**: Calculate sums, averages, counts, and other aggregations
- **Pattern matching**: Use regex and conditions to filter and select data
- **Deep transformations**: Combine multiple JQ operations for complex multi-step processing

## Example Usage

```terraform
locals {
  sample_json = jsonencode({
    name  = "Example"
    value = 42
    items = ["apple", "banana", "cherry"]
  })
}

data "pyvider_lens_jq" "example" {
  json_input = local.sample_json
  query      = ".name"
}

output "example_data" {
  description = "Data from pyvider_lens_jq"
  value       = data.pyvider_lens_jq.example.result
}

```

## More Examples

### Simple data transformation patterns

```terraform
# Use the lens_jq data source to extract a field from a JSON object.
data "pyvider_lens_jq" "user_extract" {
  json_input = jsonencode({
    user = {
      name  = "John Doe"
      email = "john@example.com"
    }
  })
  query = ".user.name"
}

output "basic_extracted_name" {
  description = "The name extracted from the JSON input."
  value       = data.pyvider_lens_jq.user_extract.result
}

```

### Advanced JQ operations and complex transformations

```terraform
# Comprehensive lens_jq example: Complex jq queries and data transformations
# Demonstrates the full range of jq capabilities: filtering, projecting, transforming

locals {
  # Sample data for demonstrating the jq function.
  # The function can accept raw Terraform objects directly.
  comprehensive_sample_data_for_func = {
    comprehensive_items = [
      { "name" : "Laptop", "stock" : 15, "tags" : ["electronics", "sale"], "price" : 999 },
      { "name" : "Mouse", "stock" : 150, "tags" : ["electronics", "accessory"], "price" : 25 },
      { "name" : "Keyboard", "stock" : 75, "tags" : ["electronics", "accessory"], "price" : 75 },
      { "name" : "Monitor", "stock" : 25, "tags" : ["electronics"], "price" : 350 }
    ],
    "store_location" : "Warehouse A",
    "last_updated" : "2025-06-25T10:00:00Z"
  }

  # Sample data for demonstrating the jq data source.
  # The data source requires a valid JSON string as input.
  sample_json_string_for_ds = jsonencode({
    users = [
      { "name" : "Alice", "id" : "a1", "roles" : ["admin", "editor"], "active" : true },
      { "name" : "Bob", "id" : "b2", "roles" : ["viewer"], "active" : true },
      { "name" : "Charlie", "id" : "c3", "roles" : ["editor"], "active" : false }
    ],
    "metadata" = { "timestamp" : "2025-06-25T12:00:00Z", "source" : "test-data" }
  })
}

# ===================================================================
# Example 1: Simple Field Extraction (Result is a primitive)
# ===================================================================
output "comprehensive_field_extraction" {
  description = "Example 1: Extracts the 'store_location' field."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, ".store_location")
}

# ===================================================================
# Example 2: Array Indexing (Result is a primitive)
# ===================================================================
output "comprehensive_array_indexing" {
  description = "Example 2: Extracts the name of the first item in the 'items' array."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, ".comprehensive_items[0].name")
}

# ===================================================================
# Example 3: Array Projection (Result is a list)
# ===================================================================
output "comprehensive_array_projection" {
  description = "Example 3: Creates a new array containing only the names of all items."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[].name]")
}

# ===================================================================
# Example 4: Filtering an Array (Result is a list of objects)
# ===================================================================
output "comprehensive_array_filtering" {
  description = "Example 4: Filters for items tagged as 'accessory'."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[] | select(.tags[] == \"accessory\")]")
}

# ===================================================================
# Example 5: Filtering and Projecting (Result is a list)
# ===================================================================
output "comprehensive_filter_and_project" {
  description = "Example 5: Filters for 'accessory' items and returns only their names."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[] | select(.tags[] == \"accessory\") | .name]")
}

# ===================================================================
# Example 6: Creating a New Object (Result is an object)
# ===================================================================
output "comprehensive_create_object" {
  description = "Example 6: Creates a custom stock report object."
  value = provider::pyvider::lens_jq(
    local.comprehensive_sample_data_for_func,
    "{ report_date: .last_updated, inventory: [ .comprehensive_items[] | { item: .name, quantity: .stock, is_electronic: (.tags[] | contains(\"electronics\")) } ] }"
  )
}

# ===================================================================
# Example 7: Complex Filtering (Result is a list of objects)
# ===================================================================
output "comprehensive_complex_filter" {
  description = "Example 7: Finds items on sale with stock less than 20."
  value       = provider::pyvider::lens_jq(local.comprehensive_sample_data_for_func, "[.comprehensive_items[] | select((.tags[] == \"sale\") and .stock < 20)]")
}

# ===================================================================
# Example 8: Using the lens_jq Data Source
# ===================================================================
data "pyvider_lens_jq" "get_active_admins" {
  json_input = local.sample_json_string_for_ds
  query      = ".users[] | select(.active == true and (.roles[] | contains(\"admin\"))) | .name"
}

output "comprehensive_data_source_result" {
  description = "Example 8: Result from the lens_jq data source."
  # The data source returns a string. Since the query result is a primitive ("Alice"),
  # we do not need jsondecode() here. If the query returned a list or object, we would.
  value = data.pyvider_lens_jq.get_active_admins.result
}

# ===================================================================
# Real-world pattern: Dynamic configuration filtering
# ===================================================================
data "pyvider_lens_jq" "filter_active_users" {
  json_input = local.sample_json_string_for_ds
  query      = "[.users[] | select(.active == true)] | length"
}

output "comprehensive_active_users_count" {
  description = "Count of active users using jq aggregation"
  value       = data.pyvider_lens_jq.filter_active_users.result
}

```

## Schema

### Required

- `json_input` (String)
- `query` (String)

### Read-Only

- `result` (Dynamic)


## JQ Query Language Reference

The data source uses the JQ query language for JSON processing. Here are the key operations:

### Basic Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `.field` | Extract a field | `.name` returns `"Alice"` from `{"name": "Alice"}` |
| `.nested.field` | Extract nested field | `.user.email` |
| `.[0]` | Get array element by index | `.[0]` gets first element |
| `.[]` | Iterate over array/object | `.users[]` iterates all users |

### Array Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `map(expr)` | Transform each element | `map(.name)` extracts all names |
| `select(cond)` | Filter elements | `select(.active)` keeps active items |
| `length` | Get array/object length | `length` returns count |
| `sort_by(.field)` | Sort by field value | `sort_by(.age)` sorts by age |
| `add` | Sum array of numbers | `map(.count) \| add` |
| `unique` | Remove duplicates | `unique` |
| `group_by(.field)` | Group elements | `group_by(.department)` |

### Filtering and Conditions

| Operation | Description | Example |
|-----------|-------------|---------|
| `select(.field == "value")` | Filter by exact match | `select(.role == "admin")` |
| `select(.field > 10)` | Numeric comparison | `select(.age > 18)` |
| `select(.field \| test("pattern"))` | Regex matching | `select(.email \| test("@example.com"))` |

### Data Manipulation

| Operation | Description | Example |
|-----------|-------------|---------|
| `{new_key: .old_key}` | Reshape objects | `{username: .name, id: .user_id}` |
| `to_entries` / `from_entries` | Convert objects to/from arrays | `to_entries \| map(...) \| from_entries` |
| `keys` | Get object keys | `keys` returns `["name", "age"]` |

## Common Use Patterns

### Extract Specific Fields

Transform objects to extract only needed fields:

```terraform
data "pyvider_lens_jq" "extract_names" {
  json_input = jsonencode(var.users)
  query = ".[] | .name"
}
```

### Filter and Transform

Select items matching criteria and reshape them:

```terraform
data "pyvider_lens_jq" "active_admins" {
  json_input = jsonencode(var.users)
  query = ".[] | select(.active and .role == \"admin\") | {name, email}"
}
```

### Statistical Operations

Calculate aggregations and summaries:

```terraform
data "pyvider_lens_jq" "user_stats" {
  json_input = jsonencode(var.users)
  query = "{total: length, active: [.[] | select(.active)] | length}"
}
```

### Complex Nested Processing

Process nested structures with multiple transformations:

```terraform
data "pyvider_lens_jq" "department_summary" {
  json_input = jsonencode(var.company_data)
  query = ".departments | map({
    name: .name,
    employee_count: .employees | length,
    avg_salary: (.employees | map(.salary) | add / length)
  })"
}
```

## Integration with HTTP APIs

Transform API responses for use in Terraform configurations:

```terraform
# Fetch data from API
data "pyvider_http_api" "github_repos" {
  url = "https://api.github.com/users/octocat/repos"
}

# Transform and filter the response
data "pyvider_lens_jq" "repo_summary" {
  json_input = data.pyvider_http_api.github_repos.response_body
  query = "map(select(.private == false)) | map({
    name: .name,
    language: .language,
    stars: .stargazers_count
  }) | sort_by(.stars) | reverse"
}
```

## Configuration Management

Process environment-specific configurations:

```terraform
# Read environment variables
data "pyvider_env_variables" "config" {
  prefix = "APP_"
}

# Transform to application config format
data "pyvider_lens_jq" "app_config" {
  json_input = jsonencode(data.pyvider_env_variables.config.values)
  query = "to_entries | map({
    key: (.key | sub(\"APP_\"; \"\") | ascii_downcase),
    value: .value
  }) | from_entries"
}
```

## Advanced JQ Patterns

### Grouping and Aggregation

```jq
group_by(.department) | map({
  department: .[0].department,
  count: length,
  avg_salary: (map(.salary) | add / length)
})
```

### Conditional Transformations

```jq
map(if .active then {name, role} else {name, status: "inactive"} end)
```

### Date Processing

```jq
map(.created_at | strptime("%Y-%m-%d") | strftime("%m/%d/%Y"))
```

### Deep Merging

```jq
reduce .[] as $item ({}; . * $item)
```