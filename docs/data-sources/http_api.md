---
page_title: "Data Source: pyvider_http_api"
subcategory: "Network"
description: |-
  Terraform data source for pyvider_http_api
---
# pyvider_http_api (Data Source)

Terraform data source for pyvider_http_api

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

