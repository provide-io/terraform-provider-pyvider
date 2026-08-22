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
