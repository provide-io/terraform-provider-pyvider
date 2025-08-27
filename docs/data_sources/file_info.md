---
page_title: "DataSource: pyvider_file_info"
description: |-
  Provides a pyvider_file_info DataSource.
---

# pyvider_file_info (DataSource)

Provides a pyvider_file_info DataSource.

```terraform
data "pyvider_file_info" "example" {
  # Configuration options here
}

output "example_data" {
  description = "Data from pyvider_file_info"
  value       = data.pyvider_file_info.example
}

```

## Argument Reference

## Arguments

- `path` (String, Required) Path to inspect.
- `exists` (String, Computed) Whether path exists.
- `size` (String, Computed) Size in bytes.
- `is_dir` (String, Computed) Is it a directory.
- `is_file` (String, Computed) Is it a regular file.
- `is_symlink` (String, Computed) Is it a symbolic link.
- `modified_time` (String, Computed) Last modification time.
- `access_time` (String, Computed) Last access time.
- `creation_time` (String, Computed) Creation time.
- `permissions` (String, Computed) File permissions.
- `owner` (String, Computed) Owner username, or numeric UID on non-Unix systems.
- `group` (String, Computed) Group name, or numeric GID on non-Unix systems.
- `mime_type` (String, Computed) MIME type.
