---
page_title: "Function: to_snake_case"
description: |-
  Converts text to snake_case format with intelligent word separation
---
# to_snake_case (Function)

The `to_snake_case` function converts text to snake_case format, which uses lowercase letters with underscores separating words. It intelligently handles various input formats including camelCase, PascalCase, kebab-case, and space-separated text, making it ideal for creating consistent identifiers.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Snake case is widely used in Python, Terraform variables, database columns, and file naming. The function's intelligent word separation ensures clean conversions from any common text format, preserving readability while adhering to snake_case conventions.

## Capabilities

This function enables you to:

- **Variable naming**: Convert user input to valid Python/Terraform variable names
- **File naming**: Create consistent snake_case filenames from titles or descriptions
- **Database columns**: Standardize column names in snake_case format
- **API endpoints**: Convert display names to API-friendly snake_case paths
- **Configuration keys**: Normalize configuration keys to snake_case for consistency

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

``to_snake_case(input)``

## Arguments





## Return Value

Returns a new string in snake_case format:
- All letters converted to lowercase
- Words separated by underscores
- Returns `null` if the input is `null`
- Handles various input formats (camelCase, PascalCase, kebab-case, spaces)

## Common Patterns

### Database Column Naming
```terraform
locals {
  user_fields = ["First Name", "Email Address", "Phone Number"]

  db_columns = [
    for field in local.user_fields :
    provider::pyvider::to_snake_case(field)
  ]
  # Result: ["first_name", "email_address", "phone_number"]
}
```

### File Naming from Titles
```terraform
variable "document_title" {
  default = "Quarterly Sales Report 2024"
}

locals {
  filename = "${provider::pyvider::to_snake_case(var.document_title)}.pdf"  # "quarterly_sales_report_2024.pdf"
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
