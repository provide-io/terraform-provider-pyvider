---
page_title: "Data Source: pyvider_http_api"
subcategory: "Network"
description: |-
  Terraform data source for pyvider_http_api
---
# pyvider_http_api (Data Source)

Terraform data source for pyvider_http_api

~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.


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

## Argument Reference

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*