---
page_title: "Function: replace"
description: |-
  Replaces all occurrences of a substring with another string
---
# replace (Function)

The `replace` function searches for all occurrences of a substring within a string and replaces them with a replacement string. It handles null values gracefully and performs global replacement, replacing all occurrences rather than just the first match.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


As in Terraform's built-in `replace`, a `search` argument of more than one character that both starts and ends with a forward slash is treated as a **regular expression** rather than a literal substring, and the replacement may refer to capture groups.

String replacement is fundamental for text manipulation, configuration templating, and data cleaning. The function's global replacement behavior ensures consistent transformations across entire strings.

## Capabilities

This function enables you to:

- **Text normalization**: Replace unwanted characters or patterns for standardization
- **Path manipulation**: Convert path separators or modify path structures
- **Configuration templating**: Replace placeholders in configuration templates dynamically
- **Data cleaning**: Remove or replace invalid characters from input data
- **URL manipulation**: Modify URLs or endpoints for different environments

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

``replace(str, old, new)``

## Arguments





## Return Value

Returns a new string with all occurrences of the search string replaced:
- Replaces ALL occurrences (global replacement)
- Case-sensitive matching
- Returns the original string if no matches found
- Returns `null` if the input string is `null`
- An empty search string matches between every character, so `replace("abc", "", "-")` returns `"-a-b-c-"`

## Regular Expressions

When `search` is wrapped in forward slashes — and is longer than a single `/` — the
text between the slashes is used as a regular expression:

```terraform
locals {
  # /pattern/ is a regular expression, not a literal search
  cleaned = provider::pyvider::replace("hello world", "/w.*d/", "everybody")
  # Result: "hello everybody"

  # $1 and ${name} refer to capture groups from the pattern
  swapped = provider::pyvider::replace("foo-bar", "/(\\w+)-(\\w+)/", "$2-$1")
  # Result: "bar-foo"
}
```

- Use `$$` for a literal `$` in the replacement.
- A reference to a group that did not participate in the match expands to nothing.
- An error is raised if the pattern does not compile.
- A single `/` is not a wrapper, so `replace("a/b", "/", "-")` is still a literal replacement.

## Common Patterns

### Configuration Templating
```terraform
variable "environment" {
  default = "production"
}

locals {
  template = "Deploying to ENV_PLACEHOLDER environment"
  message = provider::pyvider::replace(local.template, "ENV_PLACEHOLDER", var.environment)
  # Result: "Deploying to production environment"
}
```

### Path Manipulation
```terraform
variable "windows_path" {
  default = "C:\\Program Files\\MyApp"
}

locals {
  unix_path = provider::pyvider::replace(var.windows_path, "\\", "/")
  # Result: "C:/Program Files/MyApp"
}
```