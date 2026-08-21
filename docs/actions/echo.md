---
page_title: "Action: pyvider_echo"
subcategory: "Test Mode"
description: |-
  Appends a timestamped message to a file, reporting progress per line.
---
# pyvider_echo (Action)

Appends a timestamped message to a file, reporting progress per line.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Actions run as a side effect of an apply. They are either triggered from a
resource's `lifecycle.action_trigger` block or invoked directly.

## Example Usage

```terraform
action "pyvider_echo" "example" {
  config {
    # Configuration options here
  }
}

# Actions run as a side effect of an apply, triggered from a resource:
#
#   lifecycle {
#     action_trigger {
#       events  = [after_create]
#       actions = [action.pyvider_echo.example]
#     }
#   }

```

## Schema

### Required

- `message` (String) - Text to append.
- `path` (String) - File to append to. Created if absent; nothing else is touched.

### Optional

- `repeat` (Number) - How many lines to write. Must be positive.
- `defer` (Boolean) - Defer instead of running, to exercise deferral.
