---
page_title: "Resource: pyvider_secret_note"
subcategory: "Test Mode"
description: |-
  Terraform resource for pyvider_secret_note
---
# pyvider_secret_note (Resource)

Terraform resource for pyvider_secret_note

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_secret_note" "example" {
  # Configuration options here
}

output "example_id" {
  description = "The ID of the pyvider_secret_note resource"
  value       = pyvider_secret_note.example.id
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