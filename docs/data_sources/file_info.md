---
page_title: "DataSource: pyvider_file_info"
description: |-
  Provides a pyvider_file_info DataSource.
---

# pyvider_file_info (DataSource)

Provides a pyvider_file_info DataSource.

```terraform
# Get information about an existing file
data "pyvider_file_info" "bash_profile" {
  path = "~/.bash_profile"
}

# Check for a non-existent file
data "pyvider_file_info" "nonexistent" {
  path = "/tmp/this_file_does_not_exist.txt"
}

output "bash_profile_exists" {
  value = data.pyvider_file_info.bash_profile.exists
}

output "bash_profile_size" {
  value = data.pyvider_file_info.bash_profile.size
}

output "nonexistent_exists" {
  value = data.pyvider_file_info.nonexistent.exists
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
