---
page_title: "State Store: pyvider_filesystem_store"
subcategory: "State Storage"
description: |-
  ``FileSystemStateStore`` with a Terraform configuration schema.
---
# pyvider_filesystem_store (State Store)

``FileSystemStateStore`` with a Terraform configuration schema.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


State stores are configured inside the `terraform` block and hold Terraform
state on the provider's behalf. Because the store is loaded before the provider
is configured, its own `provider` block is declared inline.

## Example Usage

```terraform
terraform {
  state_store "pyvider_filesystem_store" {
    provider "pyvider" {}

    # Directory the state files are kept in, relative to the working directory.
    # Created if it does not exist.
    #
    # This has to be a literal. Terraform decodes a `state_store` block with a nil
    # HCL evaluation context, exactly as it does a `backend` block, so `path.module`
    # and every other traversal fail with "Variables may not be used here". State
    # storage is resolved during `init`, before there is a module graph to resolve
    # them against.
    path = "tfstate"
  }
}

```

## Schema

### Required

- `path` (String) - Directory holding state for this store; created if absent. A relative path resolves against the provider process's working directory, which is not necessarily the one you ran Terraform from.
