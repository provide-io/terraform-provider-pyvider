---
page_title: "Function: min"
description: |-
  Finds the minimum value in a list of numbers with error handling for empty lists
---
# min (Function)

The `min` function finds and returns the smallest number from a list of numbers. It requires at least one number in the list and handles null values gracefully, making it ideal for identifying baseline values, minimum requirements, and cost optimization scenarios.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Minimum value detection is essential for establishing baselines, identifying underutilized resources, and finding optimal configurations. The function preserves numeric types, ensuring accurate representation of both integer and floating-point minimums.

## Capabilities

This function enables you to:

- **Baseline identification**: Find minimum resource requirements for right-sizing
- **Cost optimization**: Identify lowest costs or most efficient configurations
- **Performance analysis**: Determine best-case performance metrics
- **Resource efficiency**: Find underutilized resources for optimization
- **Quality control**: Identify minimum acceptable thresholds

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

``min(numbers)``

## Arguments





## Return Value

Returns the smallest number from the list:
- Works with both integers and floats
- Returns the actual minimum value (preserves type)
- Returns `null` if the input list is `null`

## Common Patterns

### Cost Optimization
```terraform
variable "instance_costs" {
  default = [0.15, 0.25, 0.12, 0.30, 0.18]
}

locals {
  lowest_cost = provider::pyvider::min(var.instance_costs)  # 0.12
}
```

### Baseline Metrics
```terraform
variable "cpu_usage_percent" {
  default = [45, 32, 58, 28, 51]
}

locals {
  minimum_usage = provider::pyvider::min(var.cpu_usage_percent)  # 28
}
```

## Related Components

- **max** (Function) - Find the maximum value in a list
- **sum** (Function) - Calculate the sum of all values in a list
- **length** (Function) - Get the count of elements in a list