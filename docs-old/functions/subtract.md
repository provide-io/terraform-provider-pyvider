---
page_title: "Function: subtract"
description: |-
  Subtracts one number from another with intelligent integer conversion
---

# subtract (Function)

> Performs subtraction of two numeric values with null-safe handling and automatic type optimization

The `subtract` function subtracts the second number from the first number and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers.

## When to Use This

- **Difference calculations**: Calculate differences between values
- **Remaining capacity**: Determine available resources after usage
- **Countdown operations**: Calculate time or quantity remaining
- **Budget analysis**: Calculate remaining budget or overspend
- **Resource depletion**: Track consumption and availability

**Anti-patterns (when NOT to use):**
- Complex mathematical operations (use multiple function calls)
- String operations (use string functions)
- List/array operations (use collection functions)

## Quick Start

```terraform
# Simple subtraction
locals {
  remaining = provider::pyvider::subtract(100, 35)  # Returns: 65
}

# Resource availability
variable "total_capacity" {
  default = 500
}

variable "current_usage" {
  default = 187
}

locals {
  available = provider::pyvider::subtract(var.total_capacity, var.current_usage)  # Returns: 313
}
```

## Examples

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

### Common Use Cases

```terraform
# Budget tracking
variable "budget" {
  type = number
  default = 10000
}

variable "spent" {
  type = number
  default = 3750.50
}

locals {
  remaining_budget = provider::pyvider::subtract(var.budget, var.spent)  # 6249.50
  is_overbudget = local.remaining_budget < 0
}

# Resource capacity management
locals {
  total_memory_gb = 128
  used_memory_gb = 95.5

  free_memory = provider::pyvider::subtract(local.total_memory_gb, local.used_memory_gb)  # 32.5
  memory_percentage_free = provider::pyvider::multiply(
    provider::pyvider::divide(local.free_memory, local.total_memory_gb),
    100
  )
}
```

## Signature

`subtract(a: number, b: number) -> number`

## Arguments

- **`a`** (number, required) - The number to subtract from (minuend). Can be an integer or float. Returns `null` if this value is `null`.
- **`b`** (number, required) - The number to subtract (subtrahend). Can be an integer or float. Returns `null` if this value is `null`.

## Return Value

Returns the difference of `a - b` as a number. The return type is automatically optimized:
- If the result is a whole number (e.g., `5.0`), returns an integer (`5`)
- If the result has decimal places (e.g., `5.75`), returns a float (`5.75`)
- Returns `null` if either input is `null`
- Can return negative numbers when `b > a`

## Related Functions

- [`add`](./add.md) - Add two numbers
- [`multiply`](./multiply.md) - Multiply two numbers
- [`divide`](./divide.md) - Divide two numbers
- [`sum`](./sum.md) - Sum a list of numbers