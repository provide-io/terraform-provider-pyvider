---
page_title: "State Store: pyvider_filesystem_store"
subcategory: "Test Mode"
description: |-
  ``FileSystemStateStore`` with a Terraform configuration schema.
---
# pyvider_filesystem_store (State Store)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

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

    # Directory the state files are kept in. Created if it does not exist.
    path = "${path.module}/tfstate"
  }
}

```

## Schema

### Required

- `path` (String) - Directory holding state for this store; created if absent. A relative path resolves against the provider process's working directory, which is not necessarily the one you ran Terraform from.
