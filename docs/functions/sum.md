---
page_title: "Function: sum"
description: |-
  Calculates the sum of all numbers in a list with intelligent type conversion
---
# sum (Function)

The `sum` function adds all numbers in a list and returns the total. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, making it ideal for aggregate calculations, budget totals, and resource summation.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Aggregating values from lists is a fundamental operation in infrastructure configuration. The function's automatic type optimization ensures clean results, with whole number totals returned as integers for improved readability and downstream calculations.

## Capabilities

This function enables you to:

- **Aggregate calculations**: Sum multiple values from lists or collections for totals
- **Total calculations**: Calculate totals for costs, quantities, or metrics across resources
- **Accumulation**: Add up values from dynamic lists for flexible configurations
- **Budget summation**: Total multiple budget items or cost centers
- **Resource totals**: Sum resource allocations or usage across multiple sources

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

``sum(numbers)``

## Arguments





## Return Value

Returns the sum of all numbers in the list:
- Returns an integer if the sum is a whole number
- Returns a float if the sum has decimal places
- Returns `0` for empty lists
- Returns `null` if the input is `null`

## Common Patterns

### Cost Totals
```terraform
variable "monthly_expenses" {
  type = list(number)
  default = [1200.50, 800.75, 450.25, 325.00]
}

locals {
  total_monthly_budget = provider::pyvider::sum(var.monthly_expenses)  # 2776.50
}
```

### Resource Aggregation
```terraform
variable "server_specs" {
  type = list(object({
    cpu_cores = number
    memory_gb = number
  }))
  default = [
    { cpu_cores = 4, memory_gb = 16 },
    { cpu_cores = 8, memory_gb = 32 },
    { cpu_cores = 16, memory_gb = 64 }
  ]
}

locals {
  total_cpu = provider::pyvider::sum([for server in var.server_specs : server.cpu_cores])      # 28
  total_memory = provider::pyvider::sum([for server in var.server_specs : server.memory_gb])   # 112
}
```

## Related Components

- **add** (Function) - Add two numbers together
- **max** (Function) - Find the maximum value in a list
- **min** (Function) - Find the minimum value in a list
- **length** (Function) - Get the count of elements in a list

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
