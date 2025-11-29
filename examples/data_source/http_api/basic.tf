# Make a simple GET request to a public API.
data "pyvider_http_api" "example" {
  url = "https://httpbin.org/get"
  headers = {
    "Accept" = "application/json"
  }
}

output "basic_api_response_status" {
  description = "The HTTP status code of the API response."
  value       = data.pyvider_http_api.example.status_code
}

output "basic_api_response_body_preview" {
  description = "A preview of the response body."
  value       = substr(data.pyvider_http_api.example.response_body, 0, 100)
}
