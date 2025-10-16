---
page_title: "Function: add"
description: |-
  Adds two numbers and returns the result with intelligent integer conversion
---

# add (Function)

> Performs addition of two numeric values with null-safe handling and automatic type optimization

The `add` function adds two numbers (integers or floats) and returns the result. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers.

## When to Use This

- **Arithmetic calculations**: Perform basic addition in Terraform configurations
- **Counter increments**: Add values to existing counters or indices
- **Resource calculations**: Compute resource counts or sizing values
- **Configuration math**: Calculate derived configuration values
- **Budget calculations**: Sum costs or allocations

**Anti-patterns (when NOT to use):**
- Complex mathematical operations (use multiple function calls)
- String concatenation (use `join` or template interpolation)
- List/array operations (use collection functions)
- Boolean logic (use conditional expressions)

## Quick Start

```terraform
# Simple addition
locals {
  total_servers = provider::pyvider::add(3, 5)  # Returns: 8
}

# Adding with variables
variable "base_count" {
  default = 10
}

variable "additional_count" {
  default = 5
}

locals {
  final_count = provider::pyvider::add(var.base_count, var.additional_count)  # Returns: 15
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

### Resource Calculations

```terraform
# Resource calculation examples using numeric functions

# Calculate total CPU cores across instances
variable "instance_types" {
  type = list(object({
    name  = string
    cores = number
    count = number
  }))
  default = [
    { name = "web", cores = 2, count = 3 },
    { name = "api", cores = 4, count = 2 },
    { name = "db", cores = 8, count = 1 }
  ]
}

locals {
  # Calculate cores per instance type
  web_total_cores = provider::pyvider::multiply(
    var.instance_types[0].cores,
    var.instance_types[0].count
  )  # 2 * 3 = 6

  api_total_cores = provider::pyvider::multiply(
    var.instance_types[1].cores,
    var.instance_types[1].count
  )  # 4 * 2 = 8

  db_total_cores = provider::pyvider::multiply(
    var.instance_types[2].cores,
    var.instance_types[2].count
  )  # 8 * 1 = 8

  # Sum all cores
  all_core_counts = [
    local.web_total_cores,
    local.api_total_cores,
    local.db_total_cores
  ]
  total_cores = provider::pyvider::sum(local.all_core_counts)  # 6 + 8 + 8 = 22
}

# Memory allocation calculations
variable "base_memory_gb" {
  type    = number
  default = 4
}

variable "memory_multiplier" {
  type    = number
  default = 1.5
}

locals {
  # Calculate memory per instance type
  web_memory_per_instance = provider::pyvider::multiply(
    var.base_memory_gb,
    var.memory_multiplier
  )  # 4 * 1.5 = 6

  # Round to nearest GB
  web_memory_rounded = provider::pyvider::round(local.web_memory_per_instance, 0)  # 6

  # Calculate total memory for web tier
  web_total_memory = provider::pyvider::multiply(
    local.web_memory_rounded,
    var.instance_types[0].count
  )  # 6 * 3 = 18
}

# Storage calculations
variable "base_storage_gb" {
  type    = number
  default = 100
}

variable "additional_storage_gb" {
  type    = number
  default = 50
}

locals {
  # Calculate storage per instance
  storage_per_instance = provider::pyvider::add(
    var.base_storage_gb,
    var.additional_storage_gb
  )  # 100 + 50 = 150

  # Calculate total storage needed
  total_instances = provider::pyvider::sum([
    var.instance_types[0].count,
    var.instance_types[1].count,
    var.instance_types[2].count
  ])  # 3 + 2 + 1 = 6

  total_storage = provider::pyvider::multiply(
    local.storage_per_instance,
    local.total_instances
  )  # 150 * 6 = 900
}

# Cost calculations
variable "cost_per_core_hour" {
  type    = number
  default = 0.05
}

variable "hours_per_month" {
  type    = number
  default = 730
}

locals {
  # Calculate monthly compute cost
  cost_per_core_month = provider::pyvider::multiply(
    var.cost_per_core_hour,
    var.hours_per_month
  )  # 0.05 * 730 = 36.5

  total_monthly_compute_cost = provider::pyvider::multiply(
    local.cost_per_core_month,
    local.total_cores
  )  # 36.5 * 22 = 803

  # Round to nearest dollar
  monthly_cost_rounded = provider::pyvider::round(local.total_monthly_compute_cost, 0)  # 803
}

# Create resource allocation summary
resource "pyvider_file_content" "resource_summary" {
  filename = "/tmp/resource_allocation.txt"
  content = join("\n", [
    "=== Resource Allocation Summary ===",
    "",
    "CPU Allocation:",
    "  Web tier: ${local.web_total_cores} cores (${var.instance_types[0].count} × ${var.instance_types[0].cores})",
    "  API tier: ${local.api_total_cores} cores (${var.instance_types[1].count} × ${var.instance_types[1].cores})",
    "  DB tier: ${local.db_total_cores} cores (${var.instance_types[2].count} × ${var.instance_types[2].cores})",
    "  Total: ${local.total_cores} cores",
    "",
    "Memory Allocation:",
    "  Web tier total: ${local.web_total_memory} GB",
    "  Per instance: ${local.web_memory_rounded} GB",
    "",
    "Storage Allocation:",
    "  Per instance: ${local.storage_per_instance} GB",
    "  Total instances: ${local.total_instances}",
    "  Total storage: ${local.total_storage} GB",
    "",
    "Cost Estimation:",
    "  Cost per core/month: $${local.cost_per_core_month}",
    "  Monthly compute cost: $${local.monthly_cost_rounded}",
    "",
    "Generated: ${timestamp()}"
  ])
}

# Output the calculations
output "resource_calculations" {
  value = {
    cpu = {
      web_cores = local.web_total_cores
      api_cores = local.api_total_cores
      db_cores = local.db_total_cores
      total_cores = local.total_cores
    }
    memory = {
      web_total_gb = local.web_total_memory
      per_instance_gb = local.web_memory_rounded
    }
    storage = {
      per_instance_gb = local.storage_per_instance
      total_instances = local.total_instances
      total_storage_gb = local.total_storage
    }
    cost = {
      monthly_compute = local.monthly_cost_rounded
      per_core_month = local.cost_per_core_month
    }
  }
}
```

### Configuration Math



### Null Handling



## Signature

`add(a: number, b: number) -> number`

## Arguments

- **`a`** (number, required) - The first number to add. Can be an integer or float. Returns `null` if this value is `null`.
- **`b`** (number, required) - The second number to add. Can be an integer or float. Returns `null` if this value is `null`.

## Return Value

Returns the sum of `a` and `b` as a number. The return type is automatically optimized:
- If the result is a whole number (e.g., `5.0`), returns an integer (`5`)
- If the result has decimal places (e.g., `5.7`), returns a float (`5.7`)
- Returns `null` if either input is `null`

## Behavior Details

### Null Safety
```terraform
locals {
  # These all return null
  result1 = provider::pyvider::add(null, 5)     # null
  result2 = provider::pyvider::add(3, null)     # null
  result3 = provider::pyvider::add(null, null)  # null
}
```

### Type Optimization
```terraform
locals {
  # Integer results when possible
  int_result = provider::pyvider::add(3, 7)      # 10 (integer)
  int_from_float = provider::pyvider::add(3.0, 7.0)  # 10 (integer, not 10.0)

  # Float results when necessary
  float_result = provider::pyvider::add(3.5, 2.1)    # 5.6 (float)
  mixed_result = provider::pyvider::add(3, 2.5)      # 5.5 (float)
}
```

### Precision Considerations
```terraform
locals {
  # Be aware of floating-point precision
  precise_calc = provider::pyvider::add(0.1, 0.2)  # May be 0.30000000000000004

  # Use round() for display if needed
  rounded_result = provider::pyvider::round(
    provider::pyvider::add(0.1, 0.2),
    2
  )  # 0.30
}
```

## Common Patterns

### Counter Increments
```terraform
variable "current_index" {
  type    = number
  default = 0
}

locals {
  next_index = provider::pyvider::add(var.current_index, 1)
}

resource "pyvider_file_content" "indexed_file" {
  filename = "/tmp/file_${local.next_index}.txt"
  content  = "This is file number ${local.next_index}"
}
```

### Resource Scaling
```terraform
variable "base_instances" {
  type    = number
  default = 2
}

variable "additional_instances" {
  type    = number
  default = 3
}

locals {
  total_instances = provider::pyvider::add(var.base_instances, var.additional_instances)
}

# Use in resource count
resource "pyvider_local_directory" "instance_dirs" {
  count = local.total_instances
  path  = "/tmp/instance_${count.index + 1}"
}
```

### Budget Calculations
```terraform
variable "base_cost" {
  type = number
}

variable "additional_features_cost" {
  type = number
}

locals {
  total_budget = provider::pyvider::add(var.base_cost, var.additional_features_cost)
}

resource "pyvider_file_content" "budget_report" {
  filename = "/tmp/budget.txt"
  content = join("\n", [
    "Budget Calculation:",
    "Base Cost: $${var.base_cost}",
    "Additional Features: $${var.additional_features_cost}",
    "Total Budget: $${local.total_budget}"
  ])
}
```

## Error Handling

### Type Errors
```terraform
# These will cause errors at runtime
locals {
  # Error: Cannot add string and number
  # bad_result = provider::pyvider::add("hello", 5)

  # Error: Cannot add boolean and number
  # bad_result2 = provider::pyvider::add(true, 3)
}
```

### Handling Invalid Inputs
```terraform
variable "user_input_a" {
  type = any
}

variable "user_input_b" {
  type = any
}

locals {
  # Safely convert to numbers first
  safe_a = try(tonumber(var.user_input_a), 0)
  safe_b = try(tonumber(var.user_input_b), 0)

  safe_result = provider::pyvider::add(local.safe_a, local.safe_b)
}
```

## Performance Considerations

- **Lightweight operation**: Addition is extremely fast and has minimal overhead
- **Memory efficient**: No memory allocation for the calculation itself
- **Type conversion**: Minimal overhead for integer optimization
- **Null checking**: Fast null validation before calculation

## Best Practices

### 1. Input Validation
```terraform
variable "count_a" {
  type = number
  validation {
    condition     = var.count_a >= 0
    error_message = "Count must be non-negative."
  }
}

variable "count_b" {
  type = number
  validation {
    condition     = var.count_b >= 0
    error_message = "Count must be non-negative."
  }
}

locals {
  total_count = provider::pyvider::add(var.count_a, var.count_b)
}
```

### 2. Null-Safe Calculations
```terraform
# Provide defaults for potentially null values
locals {
  safe_total = provider::pyvider::add(
    coalesce(var.optional_value_a, 0),
    coalesce(var.optional_value_b, 0)
  )
}
```

### 3. Complex Calculations
```terraform
# Break down complex calculations
locals {
  subtotal_1 = provider::pyvider::add(var.base_cost, var.feature_cost)
  subtotal_2 = provider::pyvider::add(var.license_cost, var.support_cost)
  grand_total = provider::pyvider::add(local.subtotal_1, local.subtotal_2)
}
```

## Related Functions

- [`subtract`](./subtract.md) - Subtract two numbers
- [`multiply`](./multiply.md) - Multiply two numbers
- [`divide`](./divide.md) - Divide two numbers
- [`sum`](./sum.md) - Add multiple numbers from a list
- [`round`](./round.md) - Round the result to specific precision