---
page_title: "Function: split"
description: |-
  Splits a string into a list using a specified delimiter
---
# split (Function)

The `split` function takes a delimiter and a string, then returns a list of substrings created by splitting the original string at each occurrence of the delimiter. It handles null values gracefully and edge cases like empty strings, making it ideal for parsing delimited data.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


String splitting is essential for processing configuration values, parsing paths, and extracting data from formatted strings. The function's predictable behavior with edge cases ensures robust handling of various input scenarios.

## Capabilities

This function enables you to:

- **Path parsing**: Split file paths into components for analysis or manipulation
- **CSV processing**: Parse comma-separated values into individual elements
- **Configuration parsing**: Split delimited configuration strings into lists
- **Tag processing**: Split tag strings into individual tags for iteration
- **Data extraction**: Extract values from structured strings

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

``split(str, delimiter)``

## Arguments





## Return Value

Returns a list of strings created by splitting the input:
- Empty string returns an empty list `[]`
- String without delimiter returns a single-element list
- Returns `null` if the input string is `null`
- Empty delimiter splits into individual characters

## Common Patterns

### Environment Variable Processing
```terraform
variable "path_env" {
  type = string
  default = "/usr/local/bin:/usr/bin:/bin"
}

locals {
  path_dirs = provider::pyvider::split(":", var.path_env)
  # Result: ["/usr/local/bin", "/usr/bin", "/bin"]
}
```

### CSV Data Parsing
```terraform
variable "server_list" {
  default = "web1,web2,web3,db1"
}

locals {
  servers = provider::pyvider::split(",", var.server_list)
  # Result: ["web1", "web2", "web3", "db1"]
}
```

## Related Components

- **join** (Function) - Join lists into strings using delimiters
- **contains** (Function) - Check if results contain specific elements
- **length** (Function) - Get the count of split elements

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
