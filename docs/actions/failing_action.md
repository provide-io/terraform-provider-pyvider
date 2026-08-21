---
page_title: "Action: pyvider_failing_action"
subcategory: "Test Mode"
description: |-
  Fails partway through, so the error path is observable from the CLI.
---
# pyvider_failing_action (Action)

Fails partway through, so the error path is observable from the CLI.

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

- `message` (String)
