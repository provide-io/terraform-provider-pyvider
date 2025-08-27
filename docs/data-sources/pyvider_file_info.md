---
page_title: "Data Source: pyvider_file_info"
description: |-

---

# Data Source: pyvider_file_info





## Schema


### Required

- `path` (String) Path to inspect.


### Read-Only

- `exists` (Bool) Whether path exists.

- `size` (Number) Size in bytes.

- `is_dir` (Bool) Is it a directory.

- `is_file` (Bool) Is it a regular file.

- `is_symlink` (Bool) Is it a symbolic link.

- `modified_time` (String) Last modification time.

- `access_time` (String) Last access time.

- `creation_time` (String) Creation time.

- `permissions` (String) File permissions.

- `owner` (String) Owner username, or numeric UID on non-Unix systems.

- `group` (String) Group name, or numeric GID on non-Unix systems.

- `mime_type` (String) MIME type.