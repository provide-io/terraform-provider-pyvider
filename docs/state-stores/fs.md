---
page_title: "State Store: pyvider_fs"
subcategory: "Test Mode"
description: |-
  ``FileSystemStateStore`` with a Terraform configuration schema.
---
# pyvider_fs (State Store)

``FileSystemStateStore`` with a Terraform configuration schema.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


State stores are configured inside the `terraform` block and hold Terraform
state on the provider's behalf. Because the store is loaded before the provider
is configured, its own `provider` block is declared inline.

## Example Usage

```terraform
terraform {
  state_store "pyvider_fs" {
    provider "pyvider" {}

    # Configuration options here
  }
}

```

## Schema

### Required

- `path` (String) - Directory holding state for this store; created if absent. A relative path resolves against the provider process's working directory, which is not necessarily the one you ran Terraform from.
