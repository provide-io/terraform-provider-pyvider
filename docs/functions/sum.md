---
page_title: "Function: sum"
description: |-
  Calculates the sum of all numbers in a list with intelligent type conversion
---
# sum (Function)

The `sum` function adds all numbers in a list and returns the total. It handles null values gracefully and automatically converts floating-point results to integers when they represent whole numbers, making it ideal for aggregate calculations, budget totals, and resource summation.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


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
- Returns an exact decimal if the sum has decimal places
- **Raises an error** for an empty list, matching Terraform's `sum`: there is no number the sum of nothing could be, and answering `0` would turn a mistake into a plan
- Returns `null` if the input is `null`

## Precision

The total is accumulated in exact decimal arithmetic rather than binary floating point, so `sum([0.1, 0.2])` is `0.3` rather than `0.30000000000000004`, and a total large enough to overflow a 64-bit float stays a number instead of becoming infinity.

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