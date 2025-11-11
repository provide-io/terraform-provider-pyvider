---
page_title: "Function: divide"
description: |-
  Divides one number by another with intelligent integer conversion
---
# divide (Function)

The `divide` function divides the first number by the second and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, providing clean division operations for Terraform configurations.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Division operations are essential for calculating ratios, averages, and per-unit values. The function's type optimization ensures that evenly divisible results are returned as integers, while preserving decimal precision when needed for accurate calculations.

## Capabilities

This function enables you to:

- **Ratio calculations**: Compute ratios and proportions between values
- **Average calculations**: Calculate averages by dividing sums by counts
- **Per-unit values**: Determine per-unit costs or allocations
- **Capacity distribution**: Divide total capacity across multiple units
- **Rate conversions**: Convert between different time-based rates

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

``divide(a, b)``

## Arguments





## Return Value

Returns the quotient as a number. The return type is automatically optimized:
- If the result is a whole number, returns an integer
- If the result has decimal places, returns a float
- Returns `null` if either input is `null`

## Common Patterns

### Average Calculation
```terraform
variable "total_cost" {
  default = 1200
}

variable "num_servers" {
  default = 4
}

locals {
  cost_per_server = provider::pyvider::divide(var.total_cost, var.num_servers)  # 300
}
```

### Ratio Calculation
```terraform
variable "successful_requests" {
  default = 950
}

variable "total_requests" {
  default = 1000
}

locals {
  success_rate = provider::pyvider::divide(var.successful_requests, var.total_requests)  # 0.95
}
```

## Related Components

- **add** (Function) - Add two numbers together
- **subtract** (Function) - Subtract one number from another
- **multiply** (Function) - Multiply two numbers together
- **round** (Function) - Round division results to specific precision

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
