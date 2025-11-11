---
page_title: "Data Source: pyvider_http_api"
subcategory: "Network"
description: |-
  Makes HTTP requests and processes responses for infrastructure automation
---
# pyvider_http_api (Data Source)

The `pyvider_http_api` data source allows you to make HTTP requests to external APIs and use the responses in your Terraform configurations. It supports various HTTP methods, custom headers, and provides detailed response information including status codes, headers, and timing.

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

## Examples

Explore these examples to see the data source in action:

- **[example.tf](examples/example.tf)** - Basic HTTP GET request
- **[basic.tf](examples/basic.tf)** - Simple API integration patterns
- **[advanced.tf](examples/advanced.tf)** - Complex HTTP operations with custom headers and methods

## Argument Reference

## Schema

### Required

- `url` (String) - 

### Optional

- `method` (String) - 
- `headers` (Dynamic) - 
- `timeout` (String) - 
- `status_code` (String) - 
- `response_body` (String) - 
- `response_time_ms` (String) - 
- `response_headers` (Dynamic) - 
- `header_count` (String) - 
- `content_type` (String) - 
- `error_message` (String) - 


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

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
