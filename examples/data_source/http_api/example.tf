# The examples call public test services by default. Point them elsewhere --
# a mirror, or a local server in a test run -- with
# `TF_VAR_api_base_url` / `TF_VAR_json_api_base_url`.
variable "api_base_url" {
  description = "Base URL of an httpbin-compatible service."
  type        = string
  default     = "https://httpbin.org"
}

variable "json_api_base_url" {
  description = "Base URL of a JSONPlaceholder-compatible service."
  type        = string
  default     = "https://jsonplaceholder.typicode.com"
}

data "pyvider_http_api" "get_example" {
  url = "${var.api_base_url}/get"
}

output "example_data" {
  description = "Data from pyvider_http_api"
  value       = data.pyvider_http_api.get_example
}
