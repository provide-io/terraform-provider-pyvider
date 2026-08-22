---
page_title: "Resource: pyvider_secret_note"
subcategory: "Test Mode"
description: |-
  Terraform resource for pyvider_secret_note
---
# pyvider_secret_note (Resource)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

Terraform resource for pyvider_secret_note

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_secret_note" "example" {
  name = "deploy-key"

  # Write-only: sent with the request and never persisted to state. Only the
  # digest below is stored, so a plan cannot compare against the prior value.
  secret_value = "correct-horse-battery-staple"

  # Bump this whenever secret_value changes. Terraform has no prior value to
  # diff against, so this is the only signal that an update is needed.
  secret_version = "1"
}

output "example_digest" {
  description = "Digest of the stored note. The secret itself is never in state."
  value       = pyvider_secret_note.example.digest
}

```

## Schema

### Required

- `name` (String) - Identifier for the note.
- `secret_value` (String) - Never persisted to state; only the digest is.

### Optional

- `secret_version` (String) - Change this to tell the provider secret_value changed. Write-only values are absent from prior state, so a change to one cannot be detected by comparison.

### Read-Only

- `digest` (String) - Digest derived from secret_value.


## Import

```bash
terraform import pyvider_secret_note.example <id>
```