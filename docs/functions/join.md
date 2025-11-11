---
page_title: "Function: join"
description: |-
  Joins list elements into a string with a specified delimiter
---
# join (Function)

The `join` function takes a delimiter and a list of values, converts each value to a string, and joins them together with the delimiter. It handles null values gracefully and automatically converts non-string values to strings, making it essential for constructing paths, URLs, and formatted lists.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Joining list elements into strings is a fundamental operation for creating configuration values, building paths, and formatting output. The function's automatic type conversion ensures that you can join lists containing mixed types without explicit conversion.

## Capabilities

This function enables you to:

- **Path construction**: Build file paths from path components with proper separators
- **URL building**: Construct URLs from segments for dynamic resource addressing
- **Configuration strings**: Create comma-separated lists or other delimited formats
- **Command building**: Assemble command-line arguments from parameter lists
- **Display formatting**: Format lists for user display in reports or outputs

## Example Usage

```terraform
locals {
  example_result = upper(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of upper function"
  value       = local.example_result
}

```

## Signature

``join(separator, list)``

## Arguments





## Return Value

Returns a string with all list elements joined by the delimiter:
- Each list element is converted to a string using `tostring()`
- Empty lists return an empty string
- Returns `null` if the input list is `null`
- Uses empty string as delimiter if delimiter is `null`

## Common Patterns

### CSV Generation
```terraform
variable "server_names" {
  type = list(string)
  default = ["web1", "web2", "web3"]
}

locals {
  server_list = provider::pyvider::join(",", var.server_names)
}

resource "pyvider_file_content" "server_config" {
  filename = "/tmp/servers.conf"
  content  = "servers=${local.server_list}"
}
```

### Path Building
```terraform
variable "base_path" {
  default = "var"
}

variable "app_name" {
  default = "myapp"
}

locals {
  log_path = provider::pyvider::join("/", [var.base_path, "log", var.app_name])  # "var/log/myapp"
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
