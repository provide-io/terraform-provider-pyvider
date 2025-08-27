---
page_title: "DataSource: pyvider_http_api"
description: |-
  Provides a pyvider_http_api DataSource.
---

# pyvider_http_api (DataSource)

Provides a pyvider_http_api DataSource.

```terraform
data "pyvider_http_api" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_http_api"
  value       = data.pyvider_http_api.example
}

```

## Argument Reference

## Arguments

- `url` (String, Required)
- `method` (String, Optional)
- `headers` (String, Optional)
- `timeout` (String, Optional)
- `status_code` (String, Optional)
- `response_body` (String, Optional)
- `response_time_ms` (String, Optional)
- `response_headers` (String, Optional)
- `header_count` (String, Optional)
- `content_type` (String, Optional)
- `error_message` (String, Optional)
