# Read a specific environment variable by key.
# Before running, export a variable: export MY_APP_USERNAME="admin"
data "pyvider_env_variables" "user" {
  keys = ["MY_APP_USERNAME"]
}

output "basic_username" {
  description = "The username read from the environment."
  value       = lookup(data.pyvider_env_variables.user.values, "MY_APP_USERNAME", "not_set")
}
