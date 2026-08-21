---
page_title: "Function: subtract"
description: |-
  Subtracts one number from another with intelligent integer conversion
---
# subtract (Function)

The `subtract` function subtracts the second number from the first and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, providing clean and predictable numeric operations.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Like the add function, subtract optimizes result types to ensure that whole numbers are returned as integers rather than floats. This makes configurations more readable and prevents unnecessary decimal notation in outputs and resource calculations.

## Capabilities

This function enables you to:

- **Arithmetic calculations**: Perform basic subtraction in Terraform configurations
- **Counter decrements**: Subtract values from existing counters or totals
- **Resource calculations**: Compute remaining capacity or available resources
- **Delta calculations**: Calculate differences between baseline and current values
- **Budget calculations**: Determine remaining budget or cost differences

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

``subtract(a, b)``

## Arguments





## Return Value

Returns the difference as a number. The return type is automatically optimized:
- If the result is a whole number, returns an integer
- If the result has decimal places, returns the exact decimal
- Returns `null` if either input is `null`

## Precision

Arithmetic is exact decimal arithmetic, not binary floating point, and carries as many
significant digits as Terraform's own numbers do. That is what a practitioner writing
decimal literals expects:

```terraform
provider::pyvider::add(0.1, 0.2)       # 0.3, not 0.30000000000000004
provider::pyvider::subtract(0.3, 0.1)  # 0.2, not 0.19999999999999998
provider::pyvider::multiply(1.1, 1.1)  # 1.21, not 1.2100000000000002
```

A result too large for a 64-bit float stays a number rather than becoming infinity, and a
division that does not terminate is carried to 155 significant digits rather than 16.

## Common Patterns

### Remaining Capacity Calculation
```terraform
variable "total_capacity" {
  default = 100
}

variable "current_usage" {
  default = 35
}

locals {
  remaining_capacity = provider::pyvider::subtract(var.total_capacity, var.current_usage)  # 65
}
```

### Budget Remaining
```terraform
variable "budget_allocated" {
  default = 5000.00
}

variable "budget_spent" {
  default = 3250.75
}

locals {
  budget_remaining = provider::pyvider::subtract(var.budget_allocated, var.budget_spent)  # 1749.25
}
```