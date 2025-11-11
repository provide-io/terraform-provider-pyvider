---
page_title: "Function: add"
description: |-
  Adds two numbers and returns the result with intelligent integer conversion
---
# add (Function)

The `add` function adds two numbers (integers or floats) and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, ensuring clean numeric output in Terraform configurations.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Type optimization makes results cleaner and more predictable. When adding values that result in whole numbers, the function returns an integer rather than a float, reducing confusion and improving readability in outputs and resource calculations.

## Capabilities

This function enables you to:

- **Arithmetic calculations**: Perform basic addition in Terraform configurations for derived values
- **Counter increments**: Add values to existing counters or indices for dynamic resource naming
- **Resource calculations**: Compute resource counts or sizing values based on base and additional needs
- **Configuration math**: Calculate derived configuration values from multiple inputs
- **Budget calculations**: Sum costs or allocations for financial planning

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

``add(a, b)``

## Arguments





## Return Value

Returns the sum of the two numbers as a number. The return type is automatically optimized:
- If the result is a whole number (e.g., `5.0`), returns an integer (`5`)
- If the result has decimal places (e.g., `5.7`), returns a float (`5.7`)
- Returns `null` if either input is `null`

## Type Optimization

The function automatically converts floating-point results to integers when they represent whole numbers. For example, adding `3.0` and `7.0` returns `10` (an integer), not `10.0` (a float). This ensures cleaner output and more predictable behavior in resource calculations.

## Common Patterns

### Resource Count Calculation
```terraform
variable "base_count" {
  default = 10
}

variable "additional_count" {
  default = 5
}

locals {
  final_count = provider::pyvider::add(var.base_count, var.additional_count)  # 15
}

resource "pyvider_local_directory" "dirs" {
  count = local.final_count
  path  = "/tmp/dir_${count.index}"
}
```

### Budget Summation
```terraform
variable "base_cost" {
  default = 100.50
}

variable "addon_cost" {
  default = 25.75
}

locals {
  total_cost = provider::pyvider::add(var.base_cost, var.addon_cost)  # 126.25
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
