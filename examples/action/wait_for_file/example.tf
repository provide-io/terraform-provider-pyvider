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
