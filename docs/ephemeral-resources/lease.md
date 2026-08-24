---
page_title: "Ephemeral Resource: pyvider_lease"
subcategory: "Coordination"
description: |-
  Holds a lease on a file for as long as Terraform needs it.
---
# pyvider_lease (Ephemeral Resource)

Holds a lease on a file for as long as Terraform needs it.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Ephemeral resources are opened during an operation and closed when it ends.
Their values are never written to state, so they can only be consumed by
write-only attributes, provider configuration, or other ephemeral values.

## Example Usage

```terraform
ephemeral "pyvider_lease" "example" {
  name = "deploy-lock"

  # The lease file is created when the lease opens and removed when it closes.
  path = "${path.module}/deploy.lease"

  # How long the lease is good for before Terraform must renew it.
  ttl_seconds = 300
}

# Ephemeral values cannot be persisted. Consume them from a write-only
# attribute, a provider block, or another ephemeral resource -- never from an
# output or a normal resource argument.

```

## Schema

### Required

- `name` (String) - Identifier for the lease.
- `path` (String) - Lease file to hold. Created on open and removed on close.

### Optional

- `ttl_seconds` (Number) - Lease duration before Terraform must renew.

### Read-Only

- `lease_id` (String) - Identifier issued when the lease opened.
- `expires_at` (String) - When the current lease expires (UTC).
