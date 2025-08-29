# Simple GET request
data "pyvider_http_api" "get_request" {
  url    = "https://httpbin.org/get"
  method = "GET"
  headers = {
    "User-Agent" = "Pyvider/1.0"
  }
  timeout = 10
}

# GET request with query parameters
data "pyvider_http_api" "get_with_params" {
  url    = "https://httpbin.org/get?param1=value1&param2=value2"
  method = "GET"
  headers = {
    "User-Agent" = "Pyvider/1.0"
  }
  timeout = 10
}

output "get_response" {
  description = "GET request response details"
  value = {
    status_code      = data.pyvider_http_api.get_request.status_code
    content_type     = data.pyvider_http_api.get_request.content_type
    response_time_ms = data.pyvider_http_api.get_request.response_time_ms
    header_count     = data.pyvider_http_api.get_request.header_count
  }
}

output "get_response_body" {
  description = "Parsed GET response body"
  value       = jsondecode(data.pyvider_http_api.get_request.response_body)
}

output "params_response" {
  description = "GET request with params response"
  value = {
    status_code = data.pyvider_http_api.get_with_params.status_code
    args        = jsondecode(data.pyvider_http_api.get_with_params.response_body).args
  }
}
