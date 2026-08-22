---
page_title: "Function: pyvider_nested_data_processor"
subcategory: "Test Mode"
description: |-
  Parses a JSON string and returns a summarised JSON string.
---
# pyvider_nested_data_processor (Function)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

Parses a JSON string and returns a JSON string carrying the original data

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.

alongside a summary of it. `processing_mode` selects what the summary
contains. Invalid JSON is reported as a function error rather than being
silently treated as empty.

## Example Usage

```terraform
locals {
  payload = jsonencode({
    region   = "us-west-2"
    replicas = 3
  })

  # Returns a JSON string: the original data plus a summary of it.
  analysed = provider::pyvider::pyvider_nested_data_processor(local.payload, "analyze")
}

output "total_keys" {
  value = jsondecode(local.analysed).summary.total_keys
}

```

## Signature

``pyvider_nested_data_processor(input)``

## Arguments



