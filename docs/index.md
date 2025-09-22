---
page_title: "Pyvider Provider"
description: |-
  Terraform provider for pyvider
---

# Pyvider Provider

Terraform provider for pyvider - A Python-based Terraform provider built with the Pyvider framework.

## Example Usage

```terraform
provider "pyvider" {
  # Configuration options
}
```

## Schema

No provider configuration required.

## Resources

- [`pyvider_file_content`](./resource/file_content.md)
- [`pyvider_local_directory`](./resource/local_directory.md)
- [`pyvider_private_state_verifier`](./resource/private_state_verifier.md)
- [`pyvider_timed_token`](./resource/timed_token.md)

## Data Sources

- [`pyvider_env_variables`](./data_source/env_variables.md)
- [`pyvider_file_info`](./data_source/file_info.md)
- [`pyvider_provider_config_reader`](./data_source/provider_config_reader.md)

## Functions

- [`add`](./function/add.md)
- [`divide`](./function/divide.md)
- [`length`](./function/length.md)
- [`max`](./function/max.md)
- [`min`](./function/min.md)
- [`multiply`](./function/multiply.md)
- [`round`](./function/round.md)
- [`subtract`](./function/subtract.md)
- [`sum`](./function/sum.md)