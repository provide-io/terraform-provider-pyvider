---
page_title: "pyvider_file_content"
description: |-
  Manages the content of a file on the local filesystem.
---

# pyvider_file_content

Manages the content of a file on the local filesystem. This resource can create, update, and delete files.

## Example Usage

```hcl
resource "pyvider_file_content" "config" {
  filename = "/etc/myapp/config.json"
  content  = jsonencode({
    setting = "value"
  })
}
```

## Schema

### Required

- `filename` (String) The path to the file to manage.
- `content` (String) The content to write to the file.

### Read-Only

- `exists` (Boolean) Whether the file exists after being managed.
- `content_hash` (String) The SHA-256 hash of the file's content.
