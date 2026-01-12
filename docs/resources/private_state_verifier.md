---
page_title: "Resource: pyvider_private_state_verifier"
subcategory: "Test Mode"
description: |-
  Terraform resource for pyvider_private_state_verifier
---
# pyvider_private_state_verifier (Resource)

Terraform resource for pyvider_private_state_verifier

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


## Example Usage

```terraform
resource "pyvider_private_state_verifier" "example" {
  input_value = "test-value"
}

output "example_verification" {
  description = "The verification result of the pyvider_private_state_verifier resource"
  value = {
    input           = pyvider_private_state_verifier.example.input_value
    decrypted_token = pyvider_private_state_verifier.example.decrypted_token
  }
  sensitive = true
}

```

## Argument Reference



## Import

```bash
terraform import pyvider_private_state_verifier.example <id>
```