---
page_title: "Function: sum"
description: |-
  Calculates the sum of all numbers in a list with intelligent type conversion
---

# sum (Function)

> Calculates the sum of all numeric values in a list with null-safe handling and automatic type optimization

The `sum` function adds all numbers in a list and returns the total. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers.

## When to Use This

- **Aggregate calculations**: Sum multiple values from lists or collections
- **Total calculations**: Calculate totals for costs, quantities, or metrics
- **Accumulation**: Add up values from dynamic lists
- **Budget summation**: Total multiple budget items
- **Resource totals**: Sum resource allocations or usage

**Anti-patterns (when NOT to use):**
- Empty lists without validation (will return 0)
- Non-numeric data (ensure list contains only numbers)
- Single value addition (use `add` for two values)

## Quick Start

```terraform
# Simple sum
locals {
  numbers = [10, 20, 30, 40]
  total = provider::pyvider::sum(local.numbers)  # Returns: 100
}

# Sum with variables
variable "costs" {
  default = [150.50, 75.25, 200.00]
}

locals {
  total_cost = provider::pyvider::sum(var.costs)  # Returns: 425.75
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

### Cost Calculations

```terraform
# Sum up monthly costs
variable "monthly_expenses" {
  type = list(number)
  default = [1200.50, 800.75, 450.25, 325.00]
}

locals {
  total_monthly_budget = provider::pyvider::sum(var.monthly_expenses)  # 2776.50

  # Calculate quarterly total
  quarterly_costs = [
    local.total_monthly_budget,
    2950.25,
    3150.75
  ]
  quarterly_total = provider::pyvider::sum(local.quarterly_costs)
}
```

### Resource Totals

```terraform
# Aggregate server resources
variable "server_specs" {
  type = list(object({
    cpu_cores = number
    memory_gb = number
    storage_gb = number
  }))
  default = [
    { cpu_cores = 4, memory_gb = 16, storage_gb = 100 },
    { cpu_cores = 8, memory_gb = 32, storage_gb = 200 },
    { cpu_cores = 16, memory_gb = 64, storage_gb = 500 }
  ]
}

locals {
  total_cpu = provider::pyvider::sum([for server in var.server_specs : server.cpu_cores])      # 28
  total_memory = provider::pyvider::sum([for server in var.server_specs : server.memory_gb])   # 112
  total_storage = provider::pyvider::sum([for server in var.server_specs : server.storage_gb]) # 800
}
```

## Signature

`sum(numbers: list[number]) -> number`

## Arguments

- **`numbers`** (list[number], required) - A list of numbers to sum. Can contain integers and floats. Returns `null` if the list is `null`. Returns `0` for empty lists.

## Return Value

Returns the sum of all numbers in the list as a number. The return type is automatically optimized:
- If the result is a whole number (e.g., `15.0`), returns an integer (`15`)
- If the result has decimal places (e.g., `15.75`), returns a float (`15.75`)
- Returns `null` if the input list is `null`
- Returns `0` for empty lists

## Common Patterns

### Budget Totaling
```terraform
variable "monthly_costs" {
  type = list(number)
  default = [1200.00, 800.50, 450.25, 300.00]
}

locals {
  total_monthly_budget = provider::pyvider::sum(var.monthly_costs)
}

resource "pyvider_file_content" "budget_summary" {
  filename = "/tmp/budget.txt"
  content  = "Total monthly budget: $${local.total_monthly_budget}"
}
```

### Resource Aggregation
```terraform
variable "server_cpu_cores" {
  type = list(number)
  default = [4, 8, 16, 2]
}

locals {
  total_cpu_capacity = provider::pyvider::sum(var.server_cpu_cores)
}
```

### Dynamic Calculation
```terraform
locals {
  usage_metrics = [
    var.app1_cpu_usage,
    var.app2_cpu_usage,
    var.app3_cpu_usage
  ]
  total_cpu_usage = provider::pyvider::sum(local.usage_metrics)
}
```

## Best Practices

### 1. Validate List Contents
```terraform
variable "values" {
  type = list(number)
  validation {
    condition     = length(var.values) > 0
    error_message = "Values list cannot be empty."
  }
}

locals {
  total = provider::pyvider::sum(var.values)
}
```

### 2. Handle Null Lists
```terraform
locals {
  safe_total = var.optional_values != null ? provider::pyvider::sum(var.optional_values) : 0
}
```

## Related Functions

- [`add`](./add.md) - Add two numbers
- [`max`](./max.md) - Find maximum value in a list
- [`min`](./min.md) - Find minimum value in a list
- [`round`](./round.md) - Round the result to specific precision