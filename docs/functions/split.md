---
page_title: "Function: split"
description: |-
  Splits a string into a list using a specified delimiter
---

# split (Function)

> Divides a string into a list of substrings using a specified delimiter with null-safe handling

The `split` function takes a delimiter and a string, then returns a list of substrings created by splitting the original string at each occurrence of the delimiter. It handles null values gracefully and edge cases like empty strings.

## When to Use This

- **Path parsing**: Split file paths into components
- **CSV processing**: Parse comma-separated values
- **Configuration parsing**: Split delimited configuration strings
- **Tag processing**: Split tag strings into individual tags
- **Data extraction**: Extract values from structured strings

**Anti-patterns (when NOT to use):**
- Complex parsing (use proper parsers for JSON, XML, etc.)
- Single character extraction (use string indexing)
- Binary data splitting
- When delimiter doesn't exist in string (returns single-element list)

## Quick Start

```terraform
# Simple CSV splitting
locals {
  csv_data = "apple,banana,cherry"
  fruits = provider::pyvider::split(",", local.csv_data)  # Returns: ["apple", "banana", "cherry"]
}

# Path splitting
locals {
  file_path = "/var/log/myapp/error.log"
  path_parts = provider::pyvider::split("/", local.file_path)  # Returns: ["", "var", "log", "myapp", "error.log"]
}
```

## Examples

### Basic Usage

```terraform
# Basic string manipulation function examples

# Case conversion examples
locals {
  case_original_text = "Hello World"

  uppercase_text = provider::pyvider::upper(local.case_original_text)    # Returns: "HELLO WORLD"
  lowercase_text = provider::pyvider::lower(local.case_original_text)    # Returns: "hello world"
}

# String formatting examples
locals {
  template_string = "Hello, {name}! You have {count} messages."

  formatted_message = provider::pyvider::format(local.template_string, {
    name = "Alice"
    count = 5
  })  # Returns: "Hello, Alice! You have 5 messages."

  # Simple template
  simple_format = provider::pyvider::format("User: {user}", {
    user = "admin"
  })  # Returns: "User: admin"
}

# String joining examples
locals {
  word_list = ["apple", "banana", "cherry"]

  comma_separated = provider::pyvider::join(local.word_list, ", ")     # Returns: "apple, banana, cherry"
  pipe_separated = provider::pyvider::join(local.word_list, " | ")     # Returns: "apple | banana | cherry"
  no_separator = provider::pyvider::join(local.word_list, "")          # Returns: "applebananacherry"
}

# String splitting examples
locals {
  csv_data = "apple,banana,cherry,date"

  split_by_comma = provider::pyvider::split(local.csv_data, ",")       # Returns: ["apple", "banana", "cherry", "date"]

  # Split with limit
  path_string = "/home/user/documents/file.txt"
  split_path = provider::pyvider::split(local.path_string, "/")        # Returns: ["", "home", "user", "documents", "file.txt"]
}

# String replacement examples
locals {
  replacement_original_text = "The quick brown fox jumps over the lazy dog"

  replace_fox = provider::pyvider::replace(local.replacement_original_text, "fox", "cat")    # Returns: "The quick brown cat jumps over the lazy dog"
  replace_spaces = provider::pyvider::replace(local.replacement_original_text, " ", "_")     # Returns: "The_quick_brown_fox_jumps_over_the_lazy_dog"
}

# Combined string operations
locals {
  user_input = "  MiXeD cAsE tExT  "

  # Clean and normalize user input
  cleaned_input = provider::pyvider::lower(
    provider::pyvider::replace(
      provider::pyvider::replace(user_input, "  ", " "),  # Remove extra spaces
      " ", "_"                                            # Replace remaining spaces with underscores
    )
  )  # Returns: "mixed_case_text"

  # Create a filename from user input
  filename = provider::pyvider::format("{base}.{ext}", {
    base = local.cleaned_input
    ext = "txt"
  })  # Returns: "mixed_case_text.txt"
}

# Output results for verification
output "string_manipulation_examples" {
  value = {
    case_conversion = {
      original = local.case_original_text
      uppercase = local.uppercase_text
      lowercase = local.lowercase_text
    }

    formatting = {
      template = local.template_string
      formatted = local.formatted_message
      simple = local.simple_format
    }

    joining = {
      words = local.word_list
      comma_separated = local.comma_separated
      pipe_separated = local.pipe_separated
      no_separator = local.no_separator
    }

    splitting = {
      csv_original = local.csv_data
      csv_split = local.split_by_comma
      path_original = local.path_string
      path_split = local.split_path
    }

    replacement = {
      original = local.replacement_original_text
      fox_to_cat = local.replace_fox
      spaces_to_underscores = local.replace_spaces
    }

    combined_operations = {
      user_input = user_input
      cleaned = local.cleaned_input
      filename = local.filename
    }
  }
}
```

### Path Processing



### Configuration Parsing



### Tag Processing



## Signature

`split(delimiter: string, string: string) -> list[string]`

## Arguments

- **`delimiter`** (string, required) - The string to split on. Uses empty string if `null` (splits into individual characters).
- **`string`** (string, required) - The string to split. Returns `null` if this value is `null`.

## Return Value

Returns a list of strings created by splitting the input:
- Empty string returns an empty list `[]`
- String without delimiter returns a single-element list `["original_string"]`
- Returns `null` if the input string is `null`
- Empty delimiter splits into individual characters

## Behavior Details

### Empty String Handling
```terraform
locals {
  empty_result = provider::pyvider::split(",", "")  # Returns: []
  single_item = provider::pyvider::split(",", "single")  # Returns: ["single"]
}
```

### Leading/Trailing Delimiters
```terraform
locals {
  leading = provider::pyvider::split(",", ",apple,banana")  # Returns: ["", "apple", "banana"]
  trailing = provider::pyvider::split(",", "apple,banana,")  # Returns: ["apple", "banana", ""]
}
```

## Common Patterns

### Environment Variable Processing
```terraform
variable "path_env" {
  type = string
  default = "/usr/bin:/usr/local/bin:/opt/bin"
}

locals {
  path_directories = provider::pyvider::split(":", var.path_env)
}

resource "pyvider_file_content" "path_config" {
  filename = "/tmp/paths.txt"
  content = join("\n", [
    "Available paths:",
    for path in local.path_directories : "- ${path}"
  ])
}
```

### Configuration List Processing
```terraform
variable "allowed_hosts" {
  type = string
  default = "web1.example.com,web2.example.com,api.example.com"
}

locals {
  host_list = provider::pyvider::split(",", var.allowed_hosts)
}
```

### Filename Extension Extraction
```terraform
variable "filename" {
  type = string
  default = "document.backup.pdf"
}

locals {
  filename_parts = provider::pyvider::split(".", var.filename)
  file_extension = length(local.filename_parts) > 1 ? local.filename_parts[length(local.filename_parts) - 1] : ""
}
```

## Best Practices

### 1. Validate Input
```terraform
variable "csv_input" {
  type = string
  validation {
    condition     = length(var.csv_input) > 0
    error_message = "Input cannot be empty."
  }
}

locals {
  csv_items = provider::pyvider::split(",", var.csv_input)
}
```

### 2. Handle Edge Cases
```terraform
locals {
  safe_split = var.input_string != null && var.input_string != "" ? provider::pyvider::split(",", var.input_string) : []
}
```

## Related Functions

- [`join`](./join.md) - Join lists into strings (opposite operation)
- [`replace`](./replace.md) - Replace text patterns before splitting
- [`format`](./format.md) - Format strings with placeholders