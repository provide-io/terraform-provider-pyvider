---
page_title: "List Resource: pyvider_directory_entry"
subcategory: "File Operations"
description: |-
  Lists files in a directory.
---
# pyvider_directory_entry (List Resource)

Lists files in a directory.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


List resources are queried with `terraform query` from a `.tfquery.hcl` file
rather than planned or applied. The schema below is the `config` block of the
`list` block, not the schema of the managed resource being listed.

## Example Usage

```terraform
# Save as example.tfquery.hcl and run `tofu query`.
list "pyvider_directory_entry" "example" {
  provider = pyvider

  config {
    path = "${path.module}"

    # Only entries ending in this suffix are listed.
    suffix = ".tf"

    # Dotfiles are skipped unless this is set.
    include_hidden = false
  }
}

```

## Schema

### Required

- `path` (String) - Directory to list. Only read.

### Optional

- `suffix` (String) - Only return files ending with this.
- `include_hidden` (Boolean) - Include dotfiles. Defaults to false.
