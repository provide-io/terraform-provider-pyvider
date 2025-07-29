---
page_title: "Pyvider Provider: pyvider_file_content"
description: |-
  Manages the content of a file on the local filesystem.
---

# Resource: `pyvider_file_content`

Manages the content of a file at a given path. If the file does not exist, it will be created. If it exists, its content will be overwritten.

## Example Usage

```hcl
resource "pyvider_file_content" "config" {
  filename = "/etc/myapp/config.json"
  content  = jsonencode({
    api_key = "example-key"
    retries = 3
  })
}
```

## Schema

### Required

*   `filename` (String) The absolute path to the file to manage.
*   `content` (String) The content to write to the file.

### Read-Only

*   `exists` (Boolean) `true` if the file exists after the operation.
*   `content_hash` (String) The SHA-256 hash of the file's content.
