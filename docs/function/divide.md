---
page_title: "Function: divide"
description: |-
  Divides two numbers with division-by-zero protection and intelligent type conversion
---

# divide (Function)

> Performs division of two numeric values with null-safe handling, division-by-zero protection, and automatic type optimization

The `divide` function divides the first number by the second number and returns the result. It includes division-by-zero protection, handles null values gracefully, and automatically converts floating-point results to integers when they represent whole numbers.

## When to Use This

- **Rate calculations**: Calculate rates, ratios, or averages
- **Resource allocation**: Distribute resources evenly
- **Percentage calculations**: Convert values to percentages
- **Unit conversions**: Convert between different units
- **Performance metrics**: Calculate per-unit metrics

**Anti-patterns (when NOT to use):**
- Division by potentially zero values without error handling
- Complex mathematical operations (use multiple function calls)
- Integer division when you need exact integer results (check result type)
- String operations (use string functions)

## Quick Start

```terraform
# Simple division
locals {
  average = provider::pyvider::divide(100, 4)  # Returns: 25
}

# Rate calculation
variable "total_requests" {
  default = 1000
}

variable "time_period" {
  default = 60  # seconds
}

locals {
  requests_per_second = provider::pyvider::divide(var.total_requests, var.time_period)  # Returns: 16.67
}
```

## Examples

### Basic Usage

```terraform
# Basic numeric function examples

# Addition examples
locals {
  simple_add = provider::pyvider::add(5, 3)      # Returns: 8
  float_add = provider::pyvider::add(2.5, 1.5)   # Returns: 4
  mixed_add = provider::pyvider::add(10, 2.3)    # Returns: 12.3
}

# Subtraction examples
locals {
  simple_subtract = provider::pyvider::subtract(10, 4)    # Returns: 6
  float_subtract = provider::pyvider::subtract(5.5, 2.1)  # Returns: 3.4
  negative_result = provider::pyvider::subtract(3, 7)     # Returns: -4
}

# Multiplication examples
locals {
  simple_multiply = provider::pyvider::multiply(4, 3)     # Returns: 12
  float_multiply = provider::pyvider::multiply(2.5, 4)    # Returns: 10
  zero_multiply = provider::pyvider::multiply(5, 0)       # Returns: 0
}

# Division examples
locals {
  simple_divide = provider::pyvider::divide(12, 3)        # Returns: 4
  float_divide = provider::pyvider::divide(10, 3)         # Returns: 3.333...
  precise_divide = provider::pyvider::divide(15, 3)       # Returns: 5
}

# List operations
locals {
  numbers = [10, 5, 8, 2, 15]

  list_sum = provider::pyvider::sum(local.numbers)         # Returns: 40
  list_min = provider::pyvider::min(local.numbers)         # Returns: 2
  list_max = provider::pyvider::max(local.numbers)         # Returns: 15
}

# Rounding examples
locals {
  round_to_int = provider::pyvider::round(3.7, 0)         # Returns: 4
  round_to_decimal = provider::pyvider::round(3.14159, 2) # Returns: 3.14
  round_negative = provider::pyvider::round(-2.6, 0)      # Returns: -3
}

# Output results for verification
output "numeric_examples" {
  value = {
    addition = {
      simple = local.simple_add
      float = local.float_add
      mixed = local.mixed_add
    }
    subtraction = {
      simple = local.simple_subtract
      float = local.float_subtract
      negative = local.negative_result
    }
    multiplication = {
      simple = local.simple_multiply
      float = local.float_multiply
      zero = local.zero_multiply
    }
    division = {
      simple = local.simple_divide
      float = local.float_divide
      precise = local.precise_divide
    }
    list_operations = {
      sum = local.list_sum
      min = local.list_min
      max = local.list_max
    }
    rounding = {
      to_int = local.round_to_int
      to_decimal = local.round_to_decimal
      negative = local.round_negative
    }
  }
}
```

### Rate Calculations

```terraform
# Performance rate calculations
variable "total_requests" {
  type = number
  default = 50000
}

variable "time_period_seconds" {
  type = number
  default = 3600  # 1 hour
}

locals {
  requests_per_second = provider::pyvider::divide(var.total_requests, var.time_period_seconds)  # 13.89

  # Calculate average response time
  total_response_time_ms = 125000
  average_response_time = provider::pyvider::divide(local.total_response_time_ms, var.total_requests)  # 2.5ms
}
```

### Resource Distribution

```terraform
# Distribute resources across environments
variable "total_cpu_cores" {
  type = number
  default = 64
}

variable "environment_count" {
  type = number
  default = 4
}

locals {
  # Equal distribution
  cpu_per_environment = provider::pyvider::divide(var.total_cpu_cores, var.environment_count)  # 16

  # Safe division with validation
  safe_cpu_allocation = var.environment_count > 0 ?
    provider::pyvider::divide(var.total_cpu_cores, var.environment_count) :
    0
}
```

## Signature

`divide(a: number, b: number) -> number`

## Arguments

- **`a`** (number, required) - The dividend (number to be divided). Can be an integer or float. Returns `null` if this value is `null`.
- **`b`** (number, required) - The divisor (number to divide by). Can be an integer or float. Returns `null` if this value is `null`. **Cannot be zero** - will raise an error.

## Return Value

Returns the quotient of `a / b` as a number. The return type is automatically optimized:
- If the result is a whole number (e.g., `4.0`), returns an integer (`4`)
- If the result has decimal places (e.g., `4.75`), returns a float (`4.75`)
- Returns `null` if either input is `null`
- **Raises an error** if the divisor (`b`) is zero

## Error Handling

### Division by Zero
```terraform
# This will cause an error
locals {
  # Error: Division by zero
  # bad_result = provider::pyvider::divide(10, 0)
}

# Safe division with check
variable "divisor" {
  type = number
}

locals {
  safe_result = var.divisor != 0 ? provider::pyvider::divide(100, var.divisor) : null
}
```

### Null Safety
```terraform
locals {
  # These all return null
  result1 = provider::pyvider::divide(null, 5)     # null
  result2 = provider::pyvider::divide(10, null)    # null
  result3 = provider::pyvider::divide(null, null)  # null
}
```

## Common Patterns

### Average Calculation
```terraform
variable "total_value" {
  type = number
}

variable "count" {
  type = number
}

locals {
  average = var.count > 0 ? provider::pyvider::divide(var.total_value, var.count) : 0
}

resource "pyvider_file_content" "stats" {
  filename = "/tmp/average.txt"
  content  = "Average value: ${local.average}"
}
```

### Resource Per Unit
```terraform
variable "total_memory_gb" {
  type = number
}

variable "instance_count" {
  type = number
}

locals {
  memory_per_instance = var.instance_count > 0 ? provider::pyvider::divide(var.total_memory_gb, var.instance_count) : 0
}
```

## Best Practices

### 1. Always Check for Zero Division
```terraform
variable "numerator" {
  type = number
}

variable "denominator" {
  type = number
  validation {
    condition     = var.denominator != 0
    error_message = "Denominator cannot be zero."
  }
}

locals {
  result = provider::pyvider::divide(var.numerator, var.denominator)
}
```

### 2. Handle Edge Cases
```terraform
locals {
  safe_division = var.total > 0 && var.count > 0 ? provider::pyvider::divide(var.total, var.count) : 0
}
```

## Related Functions

- [`add`](./add.md) - Add two numbers
- [`subtract`](./subtract.md) - Subtract two numbers
- [`multiply`](./multiply.md) - Multiply two numbers
- [`round`](./round.md) - Round division results to specific precision