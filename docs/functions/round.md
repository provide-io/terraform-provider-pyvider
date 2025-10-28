---
page_title: "Function: round"
description: |-
  Rounds a number to a specified decimal precision with null-safe handling
---

# round (Function)

> Rounds a numeric value to a specified number of decimal places with null-safe handling

The `round` function rounds a number to a specified precision (number of decimal places). It handles null values gracefully and defaults to rounding to the nearest integer when no precision is specified.

## When to Use This

- **Display formatting**: Round numbers for user-friendly display
- **Currency calculations**: Round monetary values to appropriate precision
- **Percentage calculations**: Round percentages to desired decimal places
- **Measurement precision**: Round measurements to appropriate accuracy
- **Performance metrics**: Round metrics for cleaner reporting

**Anti-patterns (when NOT to use):**
- Financial calculations requiring exact precision (use appropriate decimal libraries)
- When exact floating-point values are critical
- Integer-only operations (unnecessary overhead)

## Quick Start

```terraform
# Round to nearest integer
locals {
  price = 19.847
  rounded_price = provider::pyvider::round(local.price, 0)  # Returns: 20
}

# Round to 2 decimal places (currency)
locals {
  calculation_result = 123.456789
  currency_amount = provider::pyvider::round(local.calculation_result, 2)  # Returns: 123.46
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

### Currency Formatting



### Percentage Calculations



### Measurement Precision



## Signature

`round(number: number, precision?: number) -> number`

## Arguments

- **`number`** (number, required) - The number to round. Can be an integer or float. Returns `null` if this value is `null`.
- **`precision`** (number, optional) - The number of decimal places to round to. Defaults to `0` (round to nearest integer). Returns `null` if this value is `null`.

## Return Value

Returns the rounded number:
- When `precision` is `0`: returns an integer
- When `precision` is positive: returns a float with the specified decimal places
- Returns `null` if either input is `null`

## Common Patterns

### Currency Rounding
```terraform
variable "item_costs" {
  type = list(number)
  default = [12.456, 8.923, 15.789]
}

locals {
  total_cost = provider::pyvider::sum(var.item_costs)
  rounded_total = provider::pyvider::round(local.total_cost, 2)
}

resource "pyvider_file_content" "invoice" {
  filename = "/tmp/invoice.txt"
  content  = "Total: $${local.rounded_total}"
}
```

### Percentage Display
```terraform
variable "completed_tasks" {
  type = number
}

variable "total_tasks" {
  type = number
}

locals {
  raw_percentage = provider::pyvider::multiply(
    provider::pyvider::divide(var.completed_tasks, var.total_tasks),
    100
  )
  display_percentage = provider::pyvider::round(local.raw_percentage, 1)
}
```

### Measurement Precision
```terraform
locals {
  precise_measurement = 2.718281828
  engineering_precision = provider::pyvider::round(local.precise_measurement, 3)  # 2.718
  display_precision = provider::pyvider::round(local.precise_measurement, 1)      # 2.7
}
```

## Best Practices

### 1. Choose Appropriate Precision
```terraform
locals {
  # Currency: 2 decimal places
  price = provider::pyvider::round(var.raw_price, 2)

  # Percentages: 1-2 decimal places
  percentage = provider::pyvider::round(var.raw_percentage, 1)

  # Display metrics: 0-1 decimal places
  metric = provider::pyvider::round(var.raw_metric, 0)
}
```

### 2. Handle Null Values
```terraform
locals {
  safe_rounded = var.optional_value != null ? provider::pyvider::round(var.optional_value, 2) : null
}
```

## Related Functions

- [`add`](./add.md) - Add numbers (often rounded afterward)
- [`subtract`](./subtract.md) - Subtract numbers (often rounded afterward)
- [`multiply`](./multiply.md) - Multiply numbers (often rounded afterward)
- [`divide`](./divide.md) - Divide numbers (often rounded afterward)