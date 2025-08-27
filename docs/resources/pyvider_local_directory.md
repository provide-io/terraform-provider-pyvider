---
page_title: "Resource: pyvider_local_directory"
description: |-

---

# Resource: pyvider_local_directory





## Schema


### Required

- `path` (String) The path of the directory to manage.


### Read-Only

- `permissions` (String) The permissions for the directory in octal format. Must start with '0o' (e.g., '0o755').

- `id` (String) The absolute path of the directory.

- `file_count` (Number) The number of files in the directory.
