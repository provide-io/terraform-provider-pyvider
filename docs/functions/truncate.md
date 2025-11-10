---
page_title: "Function: truncate"
description: |-
  Truncates text to a specified length with customizable suffix
---
# truncate (Function)

The `truncate` function shortens text to a specified maximum length, adding a suffix (like "...") to indicate truncation. It's useful for creating previews, fitting text into limited display space, and maintaining consistent text lengths across outputs.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Text truncation balances the need to display content with space constraints. The customizable suffix allows you to indicate truncation in a way that fits your use case, from simple ellipses to custom indicators.

## Capabilities

This function enables you to:

- **Text previews**: Create excerpt previews for articles or descriptions in summaries
- **UI constraints**: Fit text into limited display areas without overflow
- **List formatting**: Maintain consistent text lengths in lists for visual alignment
- **Table displays**: Prevent text overflow in table cells for clean layouts
- **Log summaries**: Create shortened log entries for overview displays

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

``truncate(input)``

## Arguments





## Return Value

Returns a truncated string:
- If text is shorter than or equal to max length, returns original text
- If text is longer, returns truncated text with suffix
- Suffix is counted in the max length
- Returns `null` if the input text is `null`

## Common Patterns

### Description Previews
```terraform
variable "article_description" {
  default = "This is a very long article description that needs to be shortened for display in the article list"
}

locals {
  preview = provider::pyvider::truncate(var.article_description, 50)
  # Result: "This is a very long article description that n..."
}
```

### Custom Suffix
```terraform
variable "long_title" {
  default = "Advanced Terraform Provider Development Best Practices"
}

locals {
  truncated = provider::pyvider::truncate(var.long_title, 30, " [more]")
  # Result: "Advanced Terraform Pro [more]"
}
```

## Related Components

- **length** (Function) - Get string length to check if truncation is needed
- **format** (Function) - Format strings with placeholders
- **replace** (Function) - Replace text in strings