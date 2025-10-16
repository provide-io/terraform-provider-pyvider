---
page_title: "Function: lower"
description: |-
  Converts a string to lowercase with null-safe handling
---

# lower (Function)

> Converts all characters in a string to lowercase with null-safe handling

The `lower` function converts all alphabetic characters in a string to lowercase. It's commonly used for case-insensitive comparisons, normalization, and ensuring consistent formatting.

## When to Use This

- **Case-insensitive comparisons**: Normalize strings before comparison
- **Configuration keys**: Create consistent lowercase identifiers
- **Search operations**: Normalize search terms for matching
- **Environment variables**: Process case-insensitive environment names
- **File extensions**: Ensure consistent lowercase extensions

**Anti-patterns (when NOT to use):**
- When case distinction is important (e.g., passwords)
- For display text that requires proper casing
- When working with case-sensitive systems

## Quick Start

```terraform
# Simple lowercase conversion
locals {
  environment = provider::pyvider::lower("PRODUCTION")  # Returns: "production"
}

# Normalize user input
variable "user_input" {
  default = "John.DOE@EXAMPLE.COM"
}

locals {
  normalized_email = provider::pyvider::lower(var.user_input)  # Returns: "john.doe@example.com"
}
```

## Examples

```terraform
# Basic string manipulation function examples

# Case conversion examples
locals {
  original_text = "Hello World"

  uppercase_text = provider::pyvider::upper(local.original_text)    # Returns: "HELLO WORLD"
  lowercase_text = provider::pyvider::lower(local.original_text)    # Returns: "hello world"
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
  original_text = "The quick brown fox jumps over the lazy dog"

  replace_fox = provider::pyvider::replace(local.original_text, "fox", "cat")    # Returns: "The quick brown cat jumps over the lazy dog"
  replace_spaces = provider::pyvider::replace(local.original_text, " ", "_")     # Returns: "The_quick_brown_fox_jumps_over_the_lazy_dog"
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
      original = local.original_text
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
      original = local.original_text
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

### Common Use Cases

```terraform
# Environment configuration
variable "environment_name" {
  default = "STAGING"
}

locals {
  env_lower = provider::pyvider::lower(var.environment_name)
  config_file = "config.${local.env_lower}.json"  # "config.staging.json"
}

# Case-insensitive comparison
variable "user_role" {
  default = "Admin"
}

locals {
  is_admin = provider::pyvider::lower(var.user_role) == "admin"
}

# File extension normalization
variable "filename" {
  default = "Document.PDF"
}

locals {
  extension = provider::pyvider::lower(provider::pyvider::split(".", var.filename)[1])  # "pdf"
  is_pdf = local.extension == "pdf"
}
```

## Signature

`lower(text: string) -> string`

## Arguments

- **`text`** (string, required) - The text to convert to lowercase. If `null`, returns `null`.

## Return Value

Returns the input string with all alphabetic characters converted to lowercase:
- **Lowercase string**: All uppercase letters converted to lowercase
- **Non-alphabetic characters**: Remain unchanged
- **Empty string**: Returns `""`
- **Null**: Returns `null` when input is `null`

## Related Functions

- [`upper`](./upper.md) - Convert to uppercase
- [`to_snake_case`](./to_snake_case.md) - Convert to snake_case format
- [`to_camel_case`](./to_camel_case.md) - Convert to camelCase format
- [`contains`](./contains.md) - Case-sensitive string contains
- [`replace`](./replace.md) - Replace text patterns