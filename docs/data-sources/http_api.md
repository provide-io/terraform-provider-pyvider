---
page_title: "Data Source: pyvider_http_api"
subcategory: "Network"
description: |-
  Makes HTTP requests and processes responses for infrastructure automation
---
# pyvider_http_api (Data Source)

The `pyvider_http_api` data source allows you to make HTTP requests to external APIs and use the responses in your Terraform configurations. It supports various HTTP methods, custom headers, and provides detailed response information including status codes, headers, and timing.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


This data source bridges the gap between Terraform and external systems, enabling you to fetch dynamic configuration data, validate service availability, and integrate with RESTful APIs. By bringing external data into your infrastructure-as-code workflow, you can create more flexible and environment-aware Terraform configurations that adapt to real-world conditions.

## Capabilities

This data source enables you to:

- **API integration**: Fetch configuration data from external REST APIs and use it in your infrastructure
- **Service discovery**: Query service registries or configuration endpoints to discover available services
- **Health checks**: Verify external services are available before proceeding with deployment
- **Dynamic configuration**: Pull settings from configuration management systems like Consul or etcd
- **Webhook validation**: Test webhook endpoints before setting up integrations
- **Multiple HTTP methods**: Support for GET, POST, PUT, PATCH, DELETE, HEAD, and OPTIONS
- **Custom headers**: Add authentication headers, content-type specifications, and API-specific requirements
- **Response processing**: Access status codes, response bodies, headers, and timing information
- **Timeout control**: Configure request timeouts to handle slow or unresponsive APIs

## Example Usage

```terraform
data "pyvider_http_api" "get_example" {
  url = "https://httpbin.org/get"
}

output "example_data" {
  description = "Data from pyvider_http_api"
  value       = data.pyvider_http_api.get_example
}

```

## More Examples

### Simple API integration patterns

```terraform
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

```

### Complex HTTP operations with custom headers and methods

```terraform
# Advanced HTTP API usage examples

# Example 1: POST request with JSON content type
data "pyvider_http_api" "post_json" {
  url    = "https://httpbin.org/post"
  method = "POST"
  headers = {
    "Content-Type" = "application/json"
    "Accept"       = "application/json"
    "User-Agent"   = "Terraform-Pyvider-Advanced/1.0"
  }
}

# Example 2: PUT request for updates
data "pyvider_http_api" "put_request" {
  url    = "https://httpbin.org/put"
  method = "PUT"
  headers = {
    "Content-Type"  = "application/json"
    "Authorization" = "Bearer fake-token-for-example"
    "X-Request-ID"  = "req-${formatdate("YYYYMMDDhhmmss", timestamp())}"
  }
}

# Example 3: DELETE request
data "pyvider_http_api" "delete_request" {
  url    = "https://httpbin.org/delete"
  method = "DELETE"
  headers = {
    "Authorization" = "Bearer fake-token-for-example"
    "X-Reason"      = "cleanup-operation"
  }
}

# Example 4: PATCH request for partial updates
data "pyvider_http_api" "patch_request" {
  url    = "https://httpbin.org/patch"
  method = "PATCH"
  headers = {
    "Content-Type" = "application/json-patch+json"
    "If-Match"     = "etag-example"
  }
}

# Example 5: OPTIONS request to check allowed methods
data "pyvider_http_api" "options_request" {
  url    = "https://httpbin.org/get"
  method = "OPTIONS"
}

# Example 6: Request with custom timeout for slow APIs
data "pyvider_http_api" "slow_api" {
  url     = "https://httpbin.org/delay/3"
  timeout = 10
  headers = {
    "Accept-Encoding" = "gzip, deflate"
    "Cache-Control"   = "no-cache"
  }
}

# Example 7: Complex headers for API authentication
data "pyvider_http_api" "authenticated_api" {
  url = "https://httpbin.org/bearer"
  headers = {
    "Authorization"     = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.example"
    "X-API-Version"     = "2023-01-01"
    "X-Client-Version"  = "terraform-provider-pyvider/1.0"
    "Accept"            = "application/vnd.api+json"
    "Content-Type"      = "application/vnd.api+json"
    "X-Request-Timeout" = "30"
  }
}

# Example 8: Multiple related API calls
data "pyvider_http_api" "user_profile" {
  url = "https://jsonplaceholder.typicode.com/users/1"
}

# Get posts for the user (using data from first call)
locals {
  advanced_user_data = try(jsondecode(data.pyvider_http_api.user_profile.response_body), {
    id       = 1
    name     = "Unknown"
    username = "unknown"
    email    = "unknown@example.com"
    address = {
      street  = ""
      suite   = ""
      city    = ""
      zipcode = ""
      geo = {
        lat = ""
        lng = ""
      }
    }
    phone   = ""
    website = ""
    company = {
      name        = ""
      catchPhrase = ""
      bs          = ""
    }
  })
}

data "pyvider_http_api" "user_posts" {
  url = "https://jsonplaceholder.typicode.com/posts?userId=${local.advanced_user_data.id}"
}

# Example 9: Error status code handling
data "pyvider_http_api" "not_found" {
  url = "https://httpbin.org/status/404"
}

data "pyvider_http_api" "server_error" {
  url = "https://httpbin.org/status/500"
}

data "pyvider_http_api" "unauthorized" {
  url = "https://httpbin.org/status/401"
}

# Process responses and handle different scenarios
locals {
  # Parse successful responses
  advanced_post_response = try(jsondecode(data.pyvider_http_api.post_json.response_body), {})

  user_posts = try(jsondecode(data.pyvider_http_api.user_posts.response_body), [])

  # Analyze response characteristics
  response_analysis = {
    post_request = {
      status_code   = data.pyvider_http_api.post_json.status_code
      response_time = data.pyvider_http_api.post_json.response_time_ms
      content_type  = data.pyvider_http_api.post_json.content_type
      headers_count = data.pyvider_http_api.post_json.header_count
      success       = data.pyvider_http_api.post_json.status_code >= 200 && data.pyvider_http_api.post_json.status_code < 300
    }

    put_request = {
      status_code   = data.pyvider_http_api.put_request.status_code
      response_time = data.pyvider_http_api.put_request.response_time_ms
      success       = data.pyvider_http_api.put_request.status_code >= 200 && data.pyvider_http_api.put_request.status_code < 300
    }

    delete_request = {
      status_code   = data.pyvider_http_api.delete_request.status_code
      response_time = data.pyvider_http_api.delete_request.response_time_ms
      success       = data.pyvider_http_api.delete_request.status_code >= 200 && data.pyvider_http_api.delete_request.status_code < 300
    }

    patch_request = {
      status_code   = data.pyvider_http_api.patch_request.status_code
      response_time = data.pyvider_http_api.patch_request.response_time_ms
      success       = data.pyvider_http_api.patch_request.status_code >= 200 && data.pyvider_http_api.patch_request.status_code < 300
    }

    options_request = {
      status_code   = data.pyvider_http_api.options_request.status_code
      response_time = data.pyvider_http_api.options_request.response_time_ms
      success       = data.pyvider_http_api.options_request.status_code == 200
    }

    slow_api = {
      status_code   = data.pyvider_http_api.slow_api.status_code
      response_time = data.pyvider_http_api.slow_api.response_time_ms
      timeout_ok    = data.pyvider_http_api.slow_api.response_time_ms <= 10000
      success       = data.pyvider_http_api.slow_api.status_code == 200
    }
  }

  # Error handling examples
  error_scenarios = {
    not_found = {
      status_code = data.pyvider_http_api.not_found.status_code
      is_404      = data.pyvider_http_api.not_found.status_code == 404
      has_error   = data.pyvider_http_api.not_found.error_message != null
    }

    server_error = {
      status_code = data.pyvider_http_api.server_error.status_code
      is_5xx      = data.pyvider_http_api.server_error.status_code >= 500
      has_error   = data.pyvider_http_api.server_error.error_message != null
    }

    unauthorized = {
      status_code = data.pyvider_http_api.unauthorized.status_code
      is_401      = data.pyvider_http_api.unauthorized.status_code == 401
      has_error   = data.pyvider_http_api.unauthorized.error_message != null
    }
  }

  # Performance metrics
  performance_metrics = {
    fastest_response = min([
      for analysis in values(local.response_analysis) :
      analysis.response_time if analysis.response_time != null
    ]...)

    slowest_response = max([
      for analysis in values(local.response_analysis) :
      analysis.response_time if analysis.response_time != null
    ]...)

    average_response_time = sum([
      for analysis in values(local.response_analysis) :
      analysis.response_time if analysis.response_time != null
      ]) / length([
      for analysis in values(local.response_analysis) :
      analysis.response_time if analysis.response_time != null
    ])

    success_rate = (length([
      for analysis in values(local.response_analysis) :
      analysis if analysis.success
    ]) / length(values(local.response_analysis))) * 100
  }
}

# Create comprehensive analysis file
resource "pyvider_file_content" "advanced_api_analysis" {
  filename = "/tmp/http_api_advanced_analysis.json"
  content = jsonencode({
    timestamp = timestamp()

    http_methods_tested = [
      "GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"
    ]

    response_analysis   = local.response_analysis
    error_scenarios     = local.error_scenarios
    performance_metrics = local.performance_metrics

    user_data_example = {
      user_profile     = local.advanced_user_data
      posts_count      = length(local.user_posts)
      first_post_title = length(local.user_posts) > 0 ? local.user_posts[0].title : null
    }

    api_patterns = {
      authentication_tested   = true
      error_handling_tested   = true
      timeout_handling_tested = true
      multiple_methods_tested = true
      json_responses_parsed   = true
    }

    recommendations = [
      local.performance_metrics.success_rate < 100 ? "Some requests failed - check error handling" : null,
      local.performance_metrics.slowest_response > 5000 ? "Consider optimizing slow requests" : null,
      "Always implement proper error handling for production use",
      "Use environment variables for sensitive authentication tokens",
      "Consider implementing retry logic for critical API calls"
    ]
  })
}

# Create a detailed report
resource "pyvider_file_content" "advanced_api_report" {
  filename = "/tmp/http_api_advanced_report.txt"
  content = join("\n", [
    "=== Advanced HTTP API Examples Report ===",
    "",
    "=== HTTP Methods Test Results ===",
    "POST Request: ${local.response_analysis.post_request.success ? "SUCCESS" : "FAILED"} (${local.response_analysis.post_request.status_code}) - ${local.response_analysis.post_request.response_time}ms",
    "PUT Request: ${local.response_analysis.put_request.success ? "SUCCESS" : "FAILED"} (${local.response_analysis.put_request.status_code}) - ${local.response_analysis.put_request.response_time}ms",
    "DELETE Request: ${local.response_analysis.delete_request.success ? "SUCCESS" : "FAILED"} (${local.response_analysis.delete_request.status_code}) - ${local.response_analysis.delete_request.response_time}ms",
    "PATCH Request: ${local.response_analysis.patch_request.success ? "SUCCESS" : "FAILED"} (${local.response_analysis.patch_request.status_code}) - ${local.response_analysis.patch_request.response_time}ms",
    "OPTIONS Request: ${local.response_analysis.options_request.success ? "SUCCESS" : "FAILED"} (${local.response_analysis.options_request.status_code}) - ${local.response_analysis.options_request.response_time}ms",
    "",
    "=== Timeout and Performance ===",
    "Slow API (3s delay): ${local.response_analysis.slow_api.success ? "SUCCESS" : "FAILED"} (${local.response_analysis.slow_api.status_code}) - ${local.response_analysis.slow_api.response_time}ms",
    "Timeout handled correctly: ${local.response_analysis.slow_api.timeout_ok ? "YES" : "NO"}",
    "",
    "=== Error Handling Tests ===",
    "404 Not Found: Status ${local.error_scenarios.not_found.status_code} - Is 404: ${local.error_scenarios.not_found.is_404}",
    "500 Server Error: Status ${local.error_scenarios.server_error.status_code} - Is 5xx: ${local.error_scenarios.server_error.is_5xx}",
    "401 Unauthorized: Status ${local.error_scenarios.unauthorized.status_code} - Is 401: ${local.error_scenarios.unauthorized.is_401}",
    "",
    "=== Performance Summary ===",
    "Success Rate: ${local.performance_metrics.success_rate}%",
    "Fastest Response: ${local.performance_metrics.fastest_response}ms",
    "Slowest Response: ${local.performance_metrics.slowest_response}ms",
    "Average Response Time: ${local.performance_metrics.average_response_time}ms",
    "",
    "=== User Data Example ===",
    "User Name: ${lookup(local.advanced_user_data, "name", "Unknown")}",
    "User Email: ${lookup(local.advanced_user_data, "email", "Unknown")}",
    "Posts Count: ${length(local.user_posts)}",
    length(local.user_posts) > 0 ? "First Post: ${local.user_posts[0].title}" : "No posts found",
    "",
    "=== Content Types Observed ===",
    "POST Response: ${local.response_analysis.post_request.content_type}",
    "Headers Count (POST): ${local.response_analysis.post_request.headers_count}",
    "",
    "Report generated at: ${timestamp()}"
  ])
}

output "advanced_user_data" {
  description = "Results from advanced HTTP API operations"
  value = {
    methods_tested = {
      post    = local.response_analysis.post_request.success
      put     = local.response_analysis.put_request.success
      delete  = local.response_analysis.delete_request.success
      patch   = local.response_analysis.patch_request.success
      options = local.response_analysis.options_request.success
    }

    performance_summary = local.performance_metrics

    error_handling = {
      handled_404 = local.error_scenarios.not_found.is_404
      handled_500 = local.error_scenarios.server_error.is_5xx
      handled_401 = local.error_scenarios.unauthorized.is_401
    }

    data_processing = {
      user_profile_parsed = contains(keys(local.advanced_user_data), "name")
      posts_retrieved     = length(local.user_posts)
      json_parsing_works  = length(local.advanced_post_response) > 0
    }

    files_created = [
      pyvider_file_content.advanced_api_analysis.filename,
      pyvider_file_content.advanced_api_report.filename
    ]
  }
}

```

## Schema

### Required

- `url` (String)

### Optional

- `method` (String)
- `headers` (Map of String)
- `timeout` (Number)
- `status_code` (Number)
- `response_body` (String)
- `response_time_ms` (Number)
- `response_headers` (Map of String)
- `header_count` (Number)
- `content_type` (String)
- `error_message` (String)


## HTTP Methods

The data source supports all standard HTTP methods:

| Method | Purpose | Typical Use Case |
|--------|---------|------------------|
| **GET** | Retrieve data | Fetch configuration, query endpoints (default) |
| **POST** | Send data | Create resources, submit data |
| **PUT** | Update resources | Full resource updates |
| **PATCH** | Partial updates | Modify specific fields |
| **DELETE** | Remove resources | Delete operations |
| **HEAD** | Get headers only | Check resource existence without body |
| **OPTIONS** | Check allowed methods | Discover API capabilities |

## Request Configuration

### Custom Headers

Add headers for authentication, content negotiation, and API requirements:

```terraform
data "pyvider_http_api" "authenticated_request" {
  url = "https://api.example.com/protected"
  headers = {
    "Authorization" = "Bearer ${var.api_token}"
    "User-Agent"    = "Terraform/pyvider-components"
    "Accept"        = "application/json"
    "Content-Type"  = "application/json"
  }
}
```

### Timeout Configuration

Control how long to wait for API responses:

```terraform
data "pyvider_http_api" "slow_api" {
  url     = "https://api.example.com/slow-endpoint"
  timeout = 120  # Wait up to 2 minutes
}
```

## Response Information

The data source provides comprehensive response details:

| Category | Attribute | Type | Description |
|----------|-----------|------|-------------|
| **Status** | `status_code` | number | HTTP status code (200, 404, 500, etc.) |
| **Content** | `response_body` | string | Full response body as string |
| | `content_type` | string | Content-Type header value |
| **Headers** | `response_headers` | map(string) | All response headers as a map |
| | `header_count` | number | Number of response headers |
| **Performance** | `response_time_ms` | number | Response time in milliseconds |
| **Errors** | `error_message` | string | Error description if request failed |

## Response Processing

Process JSON API responses using Terraform's built-in functions:

```terraform
data "pyvider_http_api" "user_data" {
  url = "https://api.example.com/users/1"
}

locals {
  user = jsondecode(data.pyvider_http_api.user_data.response_body)
  user_email = local.user.email
  user_company = local.user.company.name
}
```

## Common Use Patterns

### Configuration Management

Fetch environment-specific configuration from external sources:

```terraform
data "pyvider_http_api" "env_config" {
  url = "https://config.example.com/environments/${var.environment}"
  headers = {
    "Authorization" = "Bearer ${var.config_api_token}"
  }
}

locals {
  config = jsondecode(data.pyvider_http_api.env_config.response_body)
}
```

### Service Discovery

Discover available services from a registry:

```terraform
data "pyvider_http_api" "service_registry" {
  url = "https://consul.example.com/v1/catalog/services"
}

locals {
  services = jsondecode(data.pyvider_http_api.service_registry.response_body)
  has_database = contains(keys(local.services), "database")
}
```

### Health Check Validation

Verify service availability before deployment:

```terraform
data "pyvider_http_api" "health_check" {
  url = "https://api.example.com/health"
}

locals {
  service_healthy = data.pyvider_http_api.health_check.status_code == 200
}
```