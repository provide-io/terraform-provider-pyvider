---
page_title: "Function: min"
description: |-
  Finds the minimum value in a list of numbers with error handling for empty lists
---

# min (Function)

> Finds the smallest numeric value in a list with null-safe handling and empty list validation

The `min` function returns the smallest value from a list of numbers. It's useful for finding lower bounds, minimum thresholds, or identifying the smallest value in a dataset.

## When to Use This

- **Resource allocation**: Find minimum available capacity
- **Cost optimization**: Identify lowest cost options
- **Performance thresholds**: Determine minimum acceptable values
- **Data analysis**: Find smallest values in datasets
- **Capacity planning**: Identify bottlenecks or constraints

**Anti-patterns (when NOT to use):**
- Empty lists (will raise an error)
- Non-numeric data
- When you need the index of the minimum value, not the value itself

## Quick Start

```terraform
# Find minimum value
locals {
  values = [45, 12, 78, 23, 56]
  smallest = provider::pyvider::min(local.values)  # Returns: 12
}

# Minimum across resource capacities
variable "server_capacities" {
  default = [100, 250, 75, 150]
}

locals {
  min_capacity = provider::pyvider::min(var.server_capacities)  # Returns: 75
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
# Find cheapest pricing option
variable "pricing_tiers" {
  type = list(object({
    name = string
    monthly_cost = number
  }))
  default = [
    { name = "basic", monthly_cost = 29.99 },
    { name = "standard", monthly_cost = 49.99 },
    { name = "premium", monthly_cost = 99.99 }
  ]
}

locals {
  all_prices = [for tier in var.pricing_tiers : tier.monthly_cost]
  cheapest_price = provider::pyvider::min(local.all_prices)  # 29.99
}

# Resource constraint identification
variable "node_resources" {
  type = map(object({
    cpu = number
    memory_gb = number
    storage_gb = number
  }))
  default = {
    node1 = { cpu = 8, memory_gb = 32, storage_gb = 500 }
    node2 = { cpu = 4, memory_gb = 16, storage_gb = 250 }
    node3 = { cpu = 16, memory_gb = 64, storage_gb = 1000 }
  }
}

locals {
  min_cpu = provider::pyvider::min([for node in var.node_resources : node.cpu])          # 4
  min_memory = provider::pyvider::min([for node in var.node_resources : node.memory_gb])  # 16
  min_storage = provider::pyvider::min([for node in var.node_resources : node.storage_gb]) # 250
}
```

## Signature

`min(numbers: list[number]) -> number`

## Arguments

- **`numbers`** (list[number], required) - A list of numbers to find the minimum from. Must not be empty. Returns `null` if the list is `null`.

## Return Value

Returns the smallest number in the list:
- **Minimum value**: The smallest number from the input list
- **Type preservation**: Returns integer if all values are integers, float if any value is a float
- **Null**: Returns `null` if input list is `null`
- **Error**: Raises an error if the list is empty

## Error Handling

```terraform
# Safe minimum with validation
variable "values" {
  type = list(number)
  validation {
    condition     = length(var.values) > 0
    error_message = "Values list cannot be empty for min function."
  }
}

locals {
  safe_min = length(var.values) > 0 ? provider::pyvider::min(var.values) : null
}
```

## Related Functions

- [`max`](./max.md) - Find maximum value in a list
- [`sum`](./sum.md) - Sum all values in a list
- [`length`](./length.md) - Get number of items in list
- [`subtract`](./subtract.md) - Calculate differences