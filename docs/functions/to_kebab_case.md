---
page_title: "Function: to_kebab_case"
description: |-
  Converts text to kebab-case format with intelligent word separation
---
# to_kebab_case (Function)

The `to_kebab_case` function converts text to kebab-case format, which uses lowercase letters with hyphens separating words. It intelligently handles various input formats to create clean, URL-friendly identifiers commonly used in web development and CSS.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Kebab case is the standard format for URLs, CSS class names, HTML attributes, and command-line flags. The function's intelligent word separation ensures proper conversion from any common text format while maintaining readability.

## Capabilities

This function enables you to:

- **URL slugs**: Create URL-friendly slugs from titles or descriptions
- **CSS classes**: Generate kebab-case class names from descriptive text
- **HTML attributes**: Create valid HTML attribute names
- **Command-line flags**: Generate CLI flag names from descriptions
- **Resource naming**: Create kebab-case resource names for cloud providers

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

``to_kebab_case(input)``

## Arguments





## Return Value

Returns a new string in kebab-case format:
- All letters converted to lowercase
- Words separated by hyphens
- Returns `null` if the input is `null`
- Handles various input formats (camelCase, snake_case, PascalCase, spaces)

## Common Patterns

### URL Slug Generation
```terraform
variable "page_title" {
  default = "User Profile Settings"
}

locals {
  url_slug = provider::pyvider::to_kebab_case(var.page_title)  # "user-profile-settings"
}
```

### CSS Class Naming
```terraform
locals {
  component_names = ["Primary Button", "Navigation Menu", "Footer Links"]

  css_classes = [
    for name in local.component_names :
    provider::pyvider::to_kebab_case(name)
  ]
  # Result: ["primary-button", "navigation-menu", "footer-links"]
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
