---
page_title: "Resource: pyvider_nested_resource_test"
subcategory: "Test Mode"
description: |-
  Exercises dynamic attributes and nested block lists end to end.
---
# pyvider_nested_resource_test (Resource)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

Exercises dynamic attributes and nested block lists end to end: a `dynamic`

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.

configuration map that Terraform cannot type ahead of apply, and a repeated
`nested_configs` block whose contents are echoed back through a computed
attribute. It exists so the framework's handling of both has something to
prove itself against.

## Example Usage

```terraform
resource "pyvider_nested_resource_test" "example" {
  resource_name = "api-gateway"

  # A dynamic attribute: the shape is not known until apply.
  configuration = {
    region   = "us-west-2"
    replicas = 3
  }

  nested_configs {
    service     = "http"
    port        = 80
    protocol    = "tcp"
    ssl_enabled = false
  }

  nested_configs {
    service     = "https"
    port        = 443
    protocol    = "tcp"
    ssl_enabled = true
  }
}

output "processed" {
  # processed_data echoes the configuration back with a count of the blocks.
  value = pyvider_nested_resource_test.example.processed_data
}

```

## Schema

### Required

- `resource_name` (String)

### Optional

- `configuration` (Dynamic) - Dynamic configuration map

### Read-Only

- `processed_data` (Dynamic) - Processed configuration data
- `resource_id` (String)
- `exists` (Boolean)

### Blocks

- `nested_configs` (Optional, List)


## Import

```bash
terraform import pyvider_nested_resource_test.example <id>
```