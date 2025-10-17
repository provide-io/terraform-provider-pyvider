---
page_title: "Function: replace"
description: |-
  Replaces all occurrences of a substring with another string
---

# replace (Function)

> Replaces all occurrences of a search string with a replacement string with null-safe handling

The `replace` function searches for all occurrences of a substring within a string and replaces them with a replacement string. It handles null values gracefully and performs global replacement (all occurrences).

## When to Use This

- **Text normalization**: Replace unwanted characters or patterns
- **Path manipulation**: Convert path separators or modify paths
- **Configuration templating**: Replace placeholders in configuration templates
- **Data cleaning**: Remove or replace invalid characters
- **URL manipulation**: Modify URLs or endpoints

**Anti-patterns (when NOT to use):**
- Complex pattern matching (use regex-capable tools)
- Single character replacement in long strings (consider performance)
- Binary data manipulation
- Case-sensitive replacements when case-insensitive is needed

## Quick Start

```terraform
# Simple text replacement
locals {
  template = "Hello PLACEHOLDER, welcome!"
  message = provider::pyvider::replace(local.template, "PLACEHOLDER", "World")  # Returns: "Hello World, welcome!"
}

# Path separator conversion
locals {
  windows_path = "C:\\Program Files\\MyApp"
  unix_path = provider::pyvider::replace(local.windows_path, "\\", "/")  # Returns: "C:/Program Files/MyApp"
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
  template_string = "Hello, {}! You have {} messages."

  formatted_message = provider::pyvider::format(local.template_string, [
    "Alice",
    5
  ])  # Returns: "Hello, Alice! You have 5 messages."

  # Simple template
  simple_format = provider::pyvider::format("User: {}", [
    "admin"
  ])  # Returns: "User: admin"
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
      provider::pyvider::replace(local.user_input, "  ", " "),  # Remove extra spaces
      " ", "_"                                                   # Replace remaining spaces with underscores
    )
  )  # Returns: "mixed_case_text"

  # Create a filename from user input
  filename = provider::pyvider::format("{}.{}", [
    local.cleaned_input,
    "txt"
  ])  # Returns: "mixed_case_text.txt"
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
      user_input = local.user_input
      cleaned = local.cleaned_input
      filename = local.filename
    }
  }
}
```

### Configuration Templating



### Path Manipulation



### Data Cleaning



## Signature

`replace(string: string, search: string, replacement: string) -> string`

## Arguments

- **`string`** (string, required) - The string to search within. Returns `null` if this value is `null`.
- **`search`** (string, required) - The substring to search for. Uses empty string if `null`.
- **`replacement`** (string, required) - The string to replace matches with. Uses empty string if `null`.

## Return Value

Returns a new string with all occurrences of the search string replaced:
- Replaces ALL occurrences (global replacement)
- Case-sensitive matching
- Returns the original string if no matches found
- Returns `null` if the input string is `null`
- Empty search string returns original string unchanged

## Behavior Details

### Global Replacement
```terraform
locals {
  text = "The quick brown fox jumps over the lazy dog"
  result = provider::pyvider::replace(local.text, "the", "THE")  # Returns: "The quick brown fox jumps over THE lazy dog"
}
```

### Empty String Handling
```terraform
locals {
  # Remove all spaces
  no_spaces = provider::pyvider::replace("hello world", " ", "")  # Returns: "helloworld"

  # Add prefix to non-empty string
  prefixed = provider::pyvider::replace("value", "", "prefix-")  # Returns: "value" (no change)
}
```

## Common Patterns

### Configuration Template Processing
```terraform
variable "database_host" {
  type = string
  default = "localhost"
}

variable "database_port" {
  type = string
  default = "5432"
}

locals {
  config_template = "host=;port=;ssl=true"
  config_with_host = provider::pyvider::replace(local.config_template, "", var.database_host)
  final_config = provider::pyvider::replace(local.config_with_host, "", var.database_port)
}

resource "pyvider_file_content" "db_config" {
  filename = "/tmp/database.conf"
  content  = local.final_config
}
```

### URL Endpoint Modification
```terraform
variable "base_url" {
  type = string
  default = "https://api.example.com/v1/users"
}

variable "new_version" {
  type = string
  default = "v2"
}

locals {
  updated_url = provider::pyvider::replace(var.base_url, "/v1/", "/${var.new_version}/")
}
```

### Data Sanitization
```terraform
variable "user_input" {
  type = string
}

locals {
  # Remove potentially dangerous characters
  step1 = provider::pyvider::replace(var.user_input, "<", "")
  step2 = provider::pyvider::replace(local.step1, ">", "")
  sanitized = provider::pyvider::replace(local.step2, "&", "")
}
```

## Best Practices

### 1. Chain Replacements for Multiple Substitutions
```terraform
locals {
  template = " works at  in "
  step1 = provider::pyvider::replace(local.template, "", var.name)
  step2 = provider::pyvider::replace(local.step1, "", var.company)
  final = provider::pyvider::replace(local.step2, "", var.city)
}
```

### 2. Validate Inputs
```terraform
variable "text_to_clean" {
  type = string
  validation {
    condition     = length(var.text_to_clean) > 0
    error_message = "Input text cannot be empty."
  }
}

locals {
  cleaned = provider::pyvider::replace(var.text_to_clean, "bad_pattern", "good_pattern")
}
```

### 3. Handle Null Values
```terraform
locals {
  safe_replace = var.optional_string != null ? provider::pyvider::replace(var.optional_string, "old", "new") : null
}
```

## Related Functions

- [`format`](./format.md) - Format strings with placeholders (alternative to multiple replacements)
- [`split`](./split.md) - Split strings before processing parts
- [`join`](./join.md) - Join strings after replacement
- [`upper`](./upper.md) - Convert case before replacement
- [`lower`](./lower.md) - Convert case before replacement