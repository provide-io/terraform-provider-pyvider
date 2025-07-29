---
page_title: "pyvider_local_directory"
description: |-
  Manages a directory on the local filesystem.
---

# pyvider_local_directory

Manages a directory on the local filesystem. This resource can create directories with specific permissions.

## Example Usage

```hcl
resource "pyvider_local_directory" "app_data" {
  path        = "/var/data/my_app"
  permissions = "0o750"
}
```

## Schema

### Required

- `path` (String) The path of the directory to manage.

### Optional

- `permissions` (String) The permissions for the directory in octal format. Must start with '0o' (e.g., '0o755'). Defaults to `0o755`.

### Read-Only

- `id` (String) The absolute path of the directory.
- `file_count` (Number) The number of files in the directory.
