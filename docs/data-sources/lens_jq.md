---
page_title: "Data Source: pyvider_lens_jq"
subcategory: "Lens"
description: |-
  Transforms JSON data using JQ queries with powerful filtering and manipulation
---
# pyvider_lens_jq (Data Source)

The `pyvider_lens_jq` data source allows you to transform JSON data using JQ queries. This enables complex data manipulation, filtering, and extraction from JSON sources such as API responses, configuration files, or structured data within your Terraform configurations.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

## Examples

Explore these examples to see the data source in action:

- **[example.tf](examples/example.tf)** - Basic JQ query usage
- **[basic.tf](examples/basic.tf)** - Simple data transformation patterns
- **[comprehensive.tf](examples/comprehensive.tf)** - Advanced JQ operations and complex transformations

## Argument Reference

## Schema

### Required

- `json_input` (String) - 
- `query` (String) - 

### Read-Only

- `result` (String) - 


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

## Related Components

- **pyvider_lens_jq** (Function) - Use JQ transformations in function calls
- **pyvider_http_api** (Data Source) - Fetch JSON data from APIs for transformation
- **pyvider_file_content** (Resource) - Write transformed JSON to files
- **pyvider_env_variables** (Data Source) - Transform environment variable data

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
