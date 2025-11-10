---
page_title: "Function: to_camel_case"
description: |-
  Converts text to camelCase format with intelligent word separation
---
# to_camel_case (Function)

The `to_camel_case` function converts text to camelCase format, where the first word starts with a lowercase letter and subsequent words start with uppercase letters, with no separators between words. It intelligently handles various input formats for seamless conversion.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Camel case is the standard naming convention in JavaScript, Java, and many other programming languages. The function's smart word detection ensures proper capitalization regardless of whether the input is snake_case, kebab-case, or space-separated text.

## Capabilities

This function enables you to:

- **JavaScript identifiers**: Convert text to valid JavaScript variable names
- **API field names**: Standardize JSON field names in camelCase format
- **Configuration keys**: Normalize configuration to camelCase for JavaScript/JSON
- **Code generation**: Generate camelCase identifiers programmatically
- **Data transformation**: Convert between naming conventions

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

``to_camel_case(input)``

## Arguments





## Return Value

Returns a new string in camelCase format:
- First word starts with lowercase letter
- Subsequent words start with uppercase letter
- No separators between words
- Returns `null` if the input is `null`

## Common Patterns

### API Field Mapping
```terraform
locals {
  database_fields = ["user_id", "email_address", "created_at"]

  api_fields = [
    for field in local.database_fields :
    provider::pyvider::to_camel_case(field)
  ]
  # Result: ["userId", "emailAddress", "createdAt"]
}
```

### JavaScript Configuration
```terraform
variable "config_keys" {
  default = ["max retry count", "timeout seconds", "enable logging"]
}

locals {
  js_config = {
    for key in var.config_keys :
    provider::pyvider::to_camel_case(key) => "value"
  }
}
```

## Related Components

- **to_snake_case** (Function) - Convert to snake_case format
- **to_kebab_case** (Function) - Convert to kebab-case format
- **upper** (Function) - Convert to uppercase
- **lower** (Function) - Convert to lowercase