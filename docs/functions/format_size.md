---
page_title: "Function: format_size"
description: |-
  Formats byte values as human-readable file sizes with customizable precision
---
# format_size (Function)

The `format_size` function formats byte values into human-readable strings using appropriate units (B, KB, MB, GB, TB, PB). It automatically selects the most appropriate unit based on the size and allows customizable decimal precision for fine-tuned display control.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


Human-readable size formatting makes technical information accessible to users. The automatic unit selection ensures that sizes are always displayed in the most intuitive format, whether showing a 2 KB config file or a 500 GB database.

## Capabilities

This function enables you to:

- **File size display**: Show file sizes in user-friendly format for outputs and reports
- **Storage reports**: Display storage usage and capacity in readable units
- **Bandwidth monitoring**: Format network transfer amounts for dashboards
- **Memory usage**: Display RAM or cache sizes in appropriate units
- **Progress indicators**: Show download/upload progress with formatted sizes

## Example Usage

```terraform
locals {
  example_result = upper(
    # Function arguments here
  )
}

output "function_result" {
  description = "Result of upper function"
  value       = local.example_result
}

```

## Signature

``format_size(input)``

## Arguments





## Return Value

Returns a human-readable size string:
- Automatically selects appropriate unit (B, KB, MB, GB, TB, PB)
- Formats with specified decimal precision
- Returns `null` if the input is `null`
- Always includes unit suffix

## Common Patterns

### Storage Reports
```terraform
variable "disk_usage_bytes" {
  default = 52428800  # 50 MB
}

locals {
  formatted_usage = provider::pyvider::format_size(var.disk_usage_bytes, 2)
  # Result: "50.00 MB"
}
```

### File Size Display
```terraform
variable "file_sizes" {
  default = [1024, 1048576, 1073741824]
}

locals {
  formatted_sizes = [
    for size in var.file_sizes :
    provider::pyvider::format_size(size)
  ]
  # Result: ["1.0 KB", "1.0 MB", "1.0 GB"]
}
```

## Related Components

- **round** (Function) - Round numeric values for display
- **format** (Function) - Format strings with placeholders
- **tostring** (Function) - Convert numbers to strings