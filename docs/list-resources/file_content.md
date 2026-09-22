---
page_title: "List Resource: pyvider_file_content"
subcategory: "File Operations"
description: |-
  Lists files in a directory.
---
# pyvider_file_content (List Resource)

Lists files in a directory.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


List resources are queried with `terraform query` from a `.tfquery.hcl` file
rather than planned or applied. The schema below is the `config` block of the
`list` block, not the schema of the managed resource being listed.

## Example Usage

```terraform
# Save as example.tfquery.hcl and run `terraform query`, which reads these
# files. It arrived in Terraform 1.14, alongside list resources themselves;
# OpenTofu has no query command, so this file is inert under `tofu`.
list "pyvider_file_content" "example" {
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


## Provider linting

`provide-io/pyvider:include-hidden-files` belongs to
`provide-io/pyvider:all` and `provide-io/pyvider:security`.

- **Trigger:** `include_hidden` is explicitly `true`.
- **Remediation:** Set `include_hidden` to `false`.
- **Suppress this rule:**

    ```shell
    PYVIDER_LINT='provide-io/pyvider:all,!provide-io/pyvider:include-hidden-files' tofu validate
    ```