---
page_title: "Function: pluralize"
description: |-
  Pluralizes words based on count with support for custom plural forms
---
# pluralize (Function)

The `pluralize` function converts words to their plural form based on a count value. It automatically applies English pluralization rules and allows custom plural forms for irregular words, making it essential for grammatically correct user-facing messages.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Proper pluralization improves the quality of dynamically generated text in reports, notifications, and user interfaces. The function returns singular form for count of 1 and plural form otherwise, with support for custom plural forms to handle irregular words.

## Capabilities

This function enables you to:

- **User interface messages**: Display grammatically correct messages in outputs
- **Report generation**: Create proper text in dynamic reports with counts
- **Notification systems**: Generate contextual notifications with correct grammar
- **Data summaries**: Create readable count descriptions for resources
- **Form validation**: Display appropriate error messages with counts

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

``pluralize(input)``

## Arguments





## Return Value

Returns the singular or plural form based on count:
- Returns singular form for count of 1
- Returns plural form for all other counts (0, 2+, negative, decimals)
- Returns `null` if the word is `null`
- Applies standard English pluralization rules unless custom plural provided

## Common Patterns

### Resource Count Messages
```terraform
variable "server_count" {
  default = 3
}

locals {
  message = "${var.server_count} ${provider::pyvider::pluralize("server", var.server_count)}"
  # Result: "3 servers"
}
```

### Irregular Plurals
```terraform
variable "child_count" {
  default = 2
}

locals {
  description = "${var.child_count} ${provider::pyvider::pluralize("child", var.child_count, "children")}"
  # Result: "2 children"
}
```

## Related Components

- **format** (Function) - Format strings with placeholders
- **tostring** (Function) - Convert numbers to strings
- **length** (Function) - Get counts for pluralization