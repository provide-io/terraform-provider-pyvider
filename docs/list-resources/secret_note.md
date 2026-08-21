---
page_title: "List Resource: pyvider_secret_note"
subcategory: "Test Mode"
description: |-
  Lists the secret notes created in this provider process.
---
# pyvider_secret_note (List Resource)

Lists the secret notes created in this provider process.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


List resources are queried with `terraform query` from a `.tfquery.hcl` file
rather than planned or applied. The schema below is the `config` block of the
`list` block, not the schema of the managed resource being listed.

## Example Usage

```terraform
# Save as example.tfquery.hcl and run `terraform query`.
list "pyvider_secret_note" "example" {
  provider = pyvider

  config {
    # Filter options here
  }
}

```

## Schema

### Optional

- `name_prefix` (String) - Only return notes whose name starts with this.
- `include_archived` (Boolean) - Reserved; accepted and ignored.
