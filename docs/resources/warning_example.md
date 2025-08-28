---
page_title: "Resource: pyvider_warning_example"
description: |-
  A diagnostic resource to demonstrate framework warnings and errors.
---

# pyvider_warning_example (Resource)

This is a diagnostic resource used to demonstrate and test the framework's ability to generate contextual diagnostics (warnings and errors) during a `terraform plan`.

It showcases two key features:
1.  **Attribute Deprecation:** Using the `old_name` attribute will produce a warning, guiding the user to migrate to the new `name` attribute.
2.  **Mutual Exclusivity:** Providing both `name` and `source_file` will produce an error, as they are mutually exclusive.

## Example Usage

### Correct Usage

This example correctly uses the modern `name` attribute and will not produce any warnings.



### Deprecated Usage

This example uses the deprecated `old_name` attribute. Running `terraform plan` will succeed but will display a warning in the CLI output.



### Invalid Usage (Error)

This configuration is invalid because `name` and `source_file` are mutually exclusive. Running `terraform plan` will fail and display an error message.

```terraform
# This configuration will fail validation.
resource "pyvider_warning_example" "bad_config" {
  name        = "a-direct-name"
  source_file = "/etc/hostname"
}
```

## Argument Reference

