---
page_title: "Pyvider Provider"
description: |-
  Terraform provider for pyvider
template_output: "index.md"
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

### Resources

- [`pyvider_timed_token`](./resources/timed_token/)

### Data Sources

- [`pyvider_env_variables`](./data-sources/env_variables/)
- [`pyvider_nested_data_processor`](./data-sources/nested_data_processor/)
- [`pyvider_provider_config_reader`](./data-sources/provider_config_reader/)

### Functions

- [`add`](./functions/add/)
- [`contains`](./functions/contains/)
- [`divide`](./functions/divide/)
- [`format`](./functions/format/)
- [`format_size`](./functions/format_size/)
- [`join`](./functions/join/)
- [`length`](./functions/length/)
- [`lookup`](./functions/lookup/)
- [`lower`](./functions/lower/)
- [`max`](./functions/max/)
- [`min`](./functions/min/)
- [`multiply`](./functions/multiply/)
- [`pluralize`](./functions/pluralize/)
- [`replace`](./functions/replace/)
- [`round`](./functions/round/)
- [`split`](./functions/split/)
- [`subtract`](./functions/subtract/)
- [`sum`](./functions/sum/)
- [`to_camel_case`](./functions/to_camel_case/)
- [`to_kebab_case`](./functions/to_kebab_case/)
- [`to_snake_case`](./functions/to_snake_case/)
- [`tostring`](./functions/tostring/)
- [`truncate`](./functions/truncate/)
- [`upper`](./functions/upper/)

## File Operations

### Resources

- [`pyvider_file_content`](./resources/file_content/)
- [`pyvider_local_directory`](./resources/local_directory/)

### Data Sources

- [`pyvider_file_info`](./data-sources/file_info/)

## Lens

### Data Sources

- [`pyvider_lens_jq`](./data-sources/lens_jq/)

### Functions

- [`lens_jq`](./functions/lens_jq/)

## Network

### Data Sources

- [`pyvider_http_api`](./data-sources/http_api/)

## Test Mode

### Test Resources

- [`pyvider_private_state_verifier`](./resources/private_state_verifier/)
- [`pyvider_warning_example`](./resources/warning_example/)

### Test Data Sources

- [`pyvider_mixed_map_test`](./data-sources/mixed_map_test/)
- [`pyvider_nested_resource_test`](./data-sources/nested_resource_test/)
- [`pyvider_simple_map_test`](./data-sources/simple_map_test/)
- [`pyvider_structured_object_test`](./data-sources/structured_object_test/)
