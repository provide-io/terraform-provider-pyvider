---
page_title: "pyvider_file_content Resource"
description: |-
  Manages file content on the local filesystem
---

# pyvider_file_content

Manages file content on the local filesystem.

## Example Usage

```hcl
resource "pyvider_file_content" "example" {
  path    = "/tmp/example.txt"
  content = "Hello, World!"
}
```

## Argument Reference

- `path` - (Required) The file path
- `content` - (Required) The file content

## Attribute Reference

- `id` - The file path
- `exists` - Whether the file exists
