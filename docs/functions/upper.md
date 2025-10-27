---
page_title: "Function: upper"
description: |-
  Converts a string to uppercase with null-safe handling
---

# upper (Function)

> Converts all characters in a string to uppercase with null-safe handling

The `upper` function takes a string and returns a new string with all alphabetic characters converted to uppercase. It handles null values gracefully by returning null when the input is null.

## When to Use This

- **Case normalization**: Standardize text case for comparisons
- **Display formatting**: Format text for headers or emphasis
- **Data consistency**: Normalize user input or imported data
- **Configuration values**: Standardize environment or configuration strings
- **Search operations**: Normalize text for case-insensitive matching

**Anti-patterns (when NOT to use):**
- Preserving original case formatting (use original string)
- Binary data or non-text content
- When case sensitivity is required
- Passwords or security-sensitive strings

## Quick Start

```terraform
# Simple case conversion
locals {
  environment = "production"
  env_upper = provider::pyvider::upper(local.environment)  # Returns: "PRODUCTION"
}

# Normalizing user input
variable "region_name" {
  default = "us-west-2"
}

locals {
  region_normalized = provider::pyvider::upper(var.region_name)  # Returns: "US-WEST-2"
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

### Configuration Normalization



### Text Processing



### Null Handling



## Signature

`upper(input_str: string) -> string`

## Arguments

- **`input_str`** (string, required) - The string to convert to uppercase. Returns `null` if this value is `null`.

## Return Value

Returns a new string with all alphabetic characters converted to uppercase:
- Non-alphabetic characters (numbers, symbols, spaces) remain unchanged
- Returns `null` if the input is `null`
- Returns an empty string if the input is an empty string

## Common Patterns

### Environment Variables
```terraform
variable "env" {
  type = string
  default = "dev"
}

locals {
  environment_upper = provider::pyvider::upper(var.env)
}

resource "pyvider_file_content" "config" {
  filename = "/tmp/app_config.env"
  content  = "ENVIRONMENT=${local.environment_upper}"
}
```

### Header Formatting
```terraform
variable "service_name" {
  type = string
}

locals {
  header_text = provider::pyvider::upper(var.service_name)
}

resource "pyvider_file_content" "header" {
  filename = "/tmp/service_header.txt"
  content  = "=== ${local.header_text} SERVICE ==="
}
```

### Case-Insensitive Comparisons
```terraform
variable "user_input" {
  type = string
}

locals {
  normalized_input = provider::pyvider::upper(var.user_input)
  is_production = local.normalized_input == "PRODUCTION"
}
```

## Best Practices

### 1. Handle Null Values
```terraform
locals {
  safe_upper = var.optional_string != null ? provider::pyvider::upper(var.optional_string) : null
}
```

### 2. Validate Input Type
```terraform
variable "text_input" {
  type = string
  validation {
    condition     = can(regex("^[a-zA-Z0-9_-]*$", var.text_input))
    error_message = "Input must contain only alphanumeric characters, underscores, and hyphens."
  }
}

locals {
  normalized_text = provider::pyvider::upper(var.text_input)
}
```

## Related Functions

- [`lower`](./lower.md) - Convert string to lowercase
- [`format`](./format.md) - Format strings with placeholders
- [`replace`](./replace.md) - Replace text patterns in strings
- [`split`](./split.md) - Split strings into lists
- [`join`](./join.md) - Join lists into strings