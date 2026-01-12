---
page_title: "Resource: pyvider_file_content"
subcategory: "File Operations"
description: |-
  Terraform resource for pyvider_file_content
---
# pyvider_file_content (Resource)

Terraform resource for pyvider_file_content

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_file_content" "example" {
  filename = "/tmp/pyvider_example.txt"
  content  = "This is an example file created by Terraform."
}

output "example_file" {
  description = "The filename and hash of the created file"
  value = {
    filename     = pyvider_file_content.example.filename
    content_hash = pyvider_file_content.example.content_hash
    exists       = pyvider_file_content.example.exists
  }
}

```

## Argument Reference



## Import

```bash
terraform import pyvider_file_content.example <id>
```