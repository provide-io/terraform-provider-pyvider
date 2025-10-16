---
page_title: "Function: to_snake_case"
description: |-
  Converts text to snake_case format with intelligent word separation
---

# to_snake_case (Function)

> Converts text to snake_case format by replacing spaces and other separators with underscores

The `to_snake_case` function converts text to snake_case format, which uses lowercase letters with underscores separating words. It intelligently handles various input formats including camelCase, PascalCase, kebab-case, and space-separated text.

## When to Use This

- **Variable naming**: Convert user input to valid Python/Terraform variable names
- **File naming**: Create consistent snake_case filenames from titles
- **Database columns**: Standardize column names in snake_case format
- **API endpoints**: Convert display names to API-friendly snake_case paths
- **Configuration keys**: Normalize configuration keys to snake_case

**Anti-patterns (when NOT to use):**
- When preserving original case is important
- For display text that should remain readable
- When working with external APIs that expect specific casing

## Quick Start

```terraform
# Convert display text to snake_case
locals {
  page_title = "User Profile Settings"
  snake_name = provider::pyvider::to_snake_case(local.page_title)  # Returns: "user_profile_settings"
}

# Convert camelCase to snake_case
variable "apiEndpointName" {
  default = "getUserData"
}

locals {
  endpoint_snake = provider::pyvider::to_snake_case(var.apiEndpointName)  # Returns: "get_user_data"
}
```

## Examples

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

### Common Use Cases

```terraform
# Database column naming
locals {
  user_fields = ["First Name", "Email Address", "Phone Number"]

  db_columns = [
    for field in local.user_fields :
    provider::pyvider::to_snake_case(field)
  ]
  # Result: ["first_name", "email_address", "phone_number"]
}

# File naming from titles
variable "document_title" {
  default = "Quarterly Sales Report 2024"
}

locals {
  filename = "${provider::pyvider::to_snake_case(var.document_title)}.pdf"  # "quarterly_sales_report_2024.pdf"
}
```

## Signature

`to_snake_case(text: string) -> string`

## Arguments

- **`text`** (string, required) - The text to convert to snake_case. Handles various input formats:
  - `camelCase` (userName)
  - `PascalCase` (UserName)
  - `kebab-case` (user-name)
  - `space separated` (user name)
  - `Mixed-Format_text` (mixed separators)
  - If `null`, returns `null`

## Return Value

Returns the converted string in snake_case format:
- **snake_case**: All lowercase with underscores separating words → `user_profile_data`
- **Empty string**: Returns `""` when input is empty
- **Null**: Returns `null` when input is `null`

## Processing Rules

The function applies these transformations:
1. **Convert to lowercase**: All characters converted to lowercase
2. **Replace separators**: Hyphens (`-`), spaces (` `), and existing underscores remain as underscores
3. **Word boundaries**: CamelCase and PascalCase word boundaries become underscores
4. **Clean up**: Multiple consecutive separators become single underscores
5. **Trim**: Leading and trailing separators are removed

## Related Functions

- [`to_camel_case`](./to_camel_case.md) - Convert to camelCase format
- [`to_kebab_case`](./to_kebab_case.md) - Convert to kebab-case format
- [`upper`](./upper.md) - Convert to uppercase
- [`lower`](./lower.md) - Convert to lowercase
- [`replace`](./replace.md) - Replace specific text patterns