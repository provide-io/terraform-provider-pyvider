---
page_title: "Function: divide"
description: |-
  Divides one number by another with intelligent integer conversion
---
# divide (Function)

The `divide` function divides the first number by the second and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, providing clean division operations for Terraform configurations.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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
- If the result has decimal places, returns the exact decimal
- Returns `null` if either input is `null`
- Dividing a non-zero number by `0` returns a signed infinity (`+Inf` or
  `-Inf`), matching Terraform's own `/` operator
- **Raises an error** when dividing `0` by `0`, which is undefined

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