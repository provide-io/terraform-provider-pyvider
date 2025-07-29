---
page_title: "Pyvider Provider: pyvider_http_api"
description: |-
  Makes an HTTP request and provides information about the response.
---

# Data Source: `pyvider_http_api`

Makes an HTTP request to a given URL and returns detailed information about the response, including the status code, headers, and body.

## Example Usage

```hcl
data "pyvider_http_api" "ip" {
  url = "https://api.ipify.org?format=json"
}

output "my_public_ip" {
  value = jsondecode(data.pyvider_http_api.ip.response_body).ip
}
```

## Schema

### Required

*   `url` (String) The URL to request.

### Optional

*   `method` (String) The HTTP method to use. Defaults to `"GET"`.
*   `headers` (Map of String) A map of request headers to send.
*   `timeout` (Number) The request timeout in seconds. Defaults to `30`.

### Read-Only

*   `status_code` (Number) The HTTP status code of the response.
*   `response_body` (String) The body of the HTTP response.
*   `response_headers` (Map of String) A map of the response headers.
*   `response_time_ms` (Number) The total request time in milliseconds.
*   `content_type` (String) The value of the `Content-Type` response header.
*   `header_count` (Number) The number of headers in the response.
*   `error_message` (String) A message describing any request error that occurred.
