---
page_title: "List Resource: pyvider_secret_note"
subcategory: "Test Mode"
description: |-
  Lists the secret notes created in this provider process.
---
# pyvider_secret_note (List Resource)

> **Test-mode only.** This component is registered `test_only`, so a provider
> started normally does not publish it: it is absent from
> `terraform providers schema` and cannot be referenced from a configuration.
> It is served only when the provider process is launched with
> `PYVIDER_TESTMODE=true`, which is how the conformance suite exercises it.
> Documented here so the behaviour it demonstrates is discoverable, not
> because it is available to a published provider's users.

Lists the secret notes created in this provider process.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


List resources are queried with `terraform query` from a `.tfquery.hcl` file
rather than planned or applied. The schema below is the `config` block of the
`list` block, not the schema of the managed resource being listed.

## Example Usage

```terraform
# Save as example.tfquery.hcl and run `tofu query`.
list "pyvider_secret_note" "example" {
  provider = pyvider

  config {
    # Only notes whose name starts with this are listed.
    name_prefix = "deploy-"

    include_archived = false
  }
}

```

## Schema

### Optional

- `name_prefix` (String) - Only return notes whose name starts with this.
- `include_archived` (Boolean) - Reserved; accepted and ignored.
