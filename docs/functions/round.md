---
page_title: "Function: round"
description: |-
  Rounds a number to a specified decimal precision with null-safe handling
---
# round (Function)

The `round` function rounds a number to a specified precision (number of decimal places). It handles null values gracefully and defaults to rounding to the nearest integer when no precision is specified, making it essential for display formatting, currency calculations, and measurement precision.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Rounding is crucial for presenting numeric data in user-friendly formats and ensuring appropriate precision for different contexts. The function's flexible precision control allows you to tailor output to specific requirements, from integer rounding to fine-grained decimal precision.

## Capabilities

This function enables you to:

- **Display formatting**: Round numbers for user-friendly display in outputs and reports
- **Currency calculations**: Round monetary values to appropriate precision (typically 2 decimal places)
- **Percentage calculations**: Round percentages to desired decimal places for clarity
- **Measurement precision**: Round measurements to appropriate accuracy for the context
- **Performance metrics**: Round metrics for cleaner reporting and dashboards

## Example Usage

```terraform
locals {
  example_result = sum(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of sum function"
  value       = local.example_result
}

```

## Signature

``round(number, precision)``

## Arguments





## Return Value

Returns the rounded number:
- When `precision` is `0`: returns an integer
- When `precision` is positive: returns a float with the specified decimal places
- Returns `null` if either input is `null`

## Common Patterns

### Currency Formatting
```terraform
variable "item_costs" {
  type = list(number)
  default = [12.456, 8.923, 15.789]
}

locals {
  total_cost = provider::pyvider::sum(var.item_costs)
  rounded_total = provider::pyvider::round(local.total_cost, 2)  # Round to cents
}

resource "pyvider_file_content" "invoice" {
  filename = "/tmp/invoice.txt"
  content  = "Total: $${local.rounded_total}"
}
```

### Percentage Display
```terraform
variable "successful_requests" {
  default = 847
}

variable "total_requests" {
  default = 1000
}

locals {
  success_rate_raw = provider::pyvider::divide(var.successful_requests, var.total_requests)
  success_rate_pct = provider::pyvider::multiply(local.success_rate_raw, 100)
  success_rate_display = provider::pyvider::round(local.success_rate_pct, 1)  # 84.7
}
```

## Related Components

- **add** (Function) - Add numbers that may need rounding
- **divide** (Function) - Divide numbers and round the results
- **multiply** (Function) - Multiply numbers and round the results
- **sum** (Function) - Sum values and round the total

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
