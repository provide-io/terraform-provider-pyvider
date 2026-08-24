---
page_title: "Action: pyvider_wait_for_file"
subcategory: "File Operations"
description: |-
  Blocks until a path exists, reporting progress while it waits.
---
# pyvider_wait_for_file (Action)

Blocks until a path exists, reporting progress while it waits.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Actions run as a side effect of an apply. They are either triggered from a
resource's `lifecycle.action_trigger` block or invoked directly.

## Example Usage

```terraform
action "pyvider_wait_for_file" "example" {
  config {
    # Polled until it exists, or until the timeout elapses.
    path = "${path.module}/ready.marker"

    timeout_seconds = 60
  }
}

# An action runs as a side effect of an apply. Trigger it from a resource:
#
#   resource "pyvider_file_content" "app" {
#     # ...
#     lifecycle {
#       action_trigger {
#         events  = [before_create]
#         actions = [action.pyvider_wait_for_file.example]
#       }
#     }
#   }

```

## Schema

### Required

- `path` (String) - Path to wait for. Only read, never written.

### Optional

- `timeout_seconds` (Number) - How long to wait before failing.
