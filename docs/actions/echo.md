---
page_title: "Action: pyvider_echo"
subcategory: "Test Mode"
description: |-
  Appends a timestamped message to a file, reporting progress per line.
---
# pyvider_echo (Action)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

Appends a timestamped message to a file, reporting progress per line.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Actions run as a side effect of an apply. They are either triggered from a
resource's `lifecycle.action_trigger` block or invoked directly.

## Example Usage

```terraform
action "pyvider_echo" "example" {
  config {
    message = "deployment finished"
    path    = "${path.module}/deploy.log"

    # Write the line this many times, reporting progress as it goes.
    repeat = 3
  }
}

# An action runs as a side effect of an apply. Trigger it from a resource:
#
#   resource "pyvider_file_content" "app" {
#     # ...
#     lifecycle {
#       action_trigger {
#         events  = [after_create]
#         actions = [action.pyvider_echo.example]
#       }
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
