---
page_title: "Pyvider Provider: pyvider_local_directory"
description: |-
  Manages a directory on the local filesystem.
---

# Resource: `pyvider_local_directory`

Ensures a directory exists at a given path with specified permissions.

## Example Usage

```hcl
resource "pyvider_local_directory" "app_data" {
  path        = "/var/data/my_app"
  permissions = "0o750"
}
```

## Schema

### Required

*   `path` (String) The absolute path of the directory to manage.

### Optional

*   `permissions` (String) The permissions for the directory in octal format. Must be prefixed with `0o` (e.g., `"0o755"`). Defaults to `"0o755"`.

### Read-Only

*   `id` (String) The absolute path of the managed directory.
*   `file_count` (Number) The number of files within the directory (non-recursive).
