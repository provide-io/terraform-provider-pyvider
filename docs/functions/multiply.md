---
page_title: "Function: multiply"
description: |-
  Multiplies two numbers with intelligent integer conversion
---
# multiply (Function)

The `multiply` function multiplies two numbers (integers or floats) and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, ensuring optimal numeric type selection.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Multiplication is fundamental for scaling calculations, resource sizing, and cost projections. The automatic type optimization ensures that results are presented in their most natural form, with whole numbers returned as integers for clarity.

## Capabilities

This function enables you to:

- **Scaling calculations**: Multiply base values by scaling factors for resource sizing
- **Cost projections**: Calculate total costs by multiplying unit prices by quantities
- **Resource allocation**: Determine total resources needed by multiplying per-unit requirements
- **Rate calculations**: Compute totals by multiplying rates by time periods
- **Capacity planning**: Calculate total capacity by multiplying unit capacity by count

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

``multiply(a, b)``

## Arguments





## Return Value

Returns the product as a number. The return type is automatically optimized:
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

### Resource Scaling
```terraform
variable "servers_per_zone" {
  default = 3
}

variable "availability_zones" {
  default = 4
}

locals {
  total_servers = provider::pyvider::multiply(var.servers_per_zone, var.availability_zones)  # 12
}
```

### Cost Calculation
```terraform
variable "instance_price" {
  default = 0.15
}

variable "hours_per_month" {
  default = 730
}

locals {
  monthly_cost = provider::pyvider::multiply(var.instance_price, var.hours_per_month)  # 109.5
}
```