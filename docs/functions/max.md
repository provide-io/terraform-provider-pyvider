---
page_title: "Function: max"
description: |-
  Finds the maximum value in a list of numbers with error handling for empty lists
---
# max (Function)

The `max` function finds and returns the largest number from a list of numbers. It requires at least one number in the list and handles null values gracefully, making it essential for capacity planning, performance optimization, and identifying peak values.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Finding maximum values is critical for many infrastructure decisions, from determining peak resource requirements to identifying bottlenecks. The function works with both integers and floats, returning results in their natural numeric form.

## Capabilities

This function enables you to:

- **Capacity planning**: Find maximum resource requirements to ensure adequate provisioning
- **Performance optimization**: Identify peak performance values for tuning and optimization
- **Scaling decisions**: Determine maximum load or usage to guide auto-scaling policies
- **Budget planning**: Find highest costs or allocations for worst-case planning
- **Quality metrics**: Identify best performance indicators from measurement sets

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

``max(numbers)``

## Arguments





## Return Value

Returns the largest number from the list:
- Works with both integers and floats
- Returns the actual maximum value (preserves type)
- Returns `null` if the input list is `null`

## Common Patterns

### Peak Resource Identification
```terraform
variable "memory_usage_gb" {
  default = [2.5, 8.1, 4.3, 12.7, 6.2]
}

locals {
  peak_memory = provider::pyvider::max(var.memory_usage_gb)  # 12.7
}
```

### Performance Metrics
```terraform
variable "response_times_ms" {
  default = [250, 180, 520, 195, 275]
}

locals {
  slowest_response = provider::pyvider::max(var.response_times_ms)  # 520
}
```

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
