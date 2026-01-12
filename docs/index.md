---
page_title: "Pyvider Provider"
description: |-
  Terraform provider for pyvider
template_output: "index.md"
---

# Pyvider ProviderTerraform provider for pyvider - A Python-based Terraform provider built with the Pyvider framework.

## Example Usage

```terraform
provider "pyvider" {
  # Configuration options
}
```

## Schema

No provider configuration required.

### Resources

- [`pyvider_timed_token`](./resources/timed_token.md)

### Data Sources

- [`pyvider_env_variables`](./data-sources/env_variables.md)
- [`pyvider_nested_data_processor`](./data-sources/nested_data_processor.md)
- [`pyvider_provider_config_reader`](./data-sources/provider_config_reader.md)

### Functions

- [`add`](./functions/add.md)
- [`contains`](./functions/contains.md)
- [`divide`](./functions/divide.md)
- [`format`](./functions/format.md)
- [`format_size`](./functions/format_size.md)
- [`join`](./functions/join.md)
- [`length`](./functions/length.md)
- [`lookup`](./functions/lookup.md)
- [`lower`](./functions/lower.md)
- [`max`](./functions/max.md)
- [`min`](./functions/min.md)
- [`multiply`](./functions/multiply.md)
- [`pluralize`](./functions/pluralize.md)
- [`replace`](./functions/replace.md)
- [`round`](./functions/round.md)
- [`split`](./functions/split.md)
- [`subtract`](./functions/subtract.md)
- [`sum`](./functions/sum.md)
- [`to_camel_case`](./functions/to_camel_case.md)
- [`to_kebab_case`](./functions/to_kebab_case.md)
- [`to_snake_case`](./functions/to_snake_case.md)
- [`tostring`](./functions/tostring.md)
- [`truncate`](./functions/truncate.md)
- [`upper`](./functions/upper.md)

## File Operations

### Resources

- [`pyvider_file_content`](./resources/file_content.md)
- [`pyvider_local_directory`](./resources/local_directory.md)

### Data Sources

- [`pyvider_file_info`](./data-sources/file_info.md)

## Lens

### Data Sources

- [`pyvider_lens_jq`](./data-sources/lens_jq.md)

### Functions

- [`lens_jq`](./functions/lens_jq.md)

## Network

### Data Sources

- [`pyvider_http_api`](./data-sources/http_api.md)

## Test Mode

### Test Resources

- [`pyvider_private_state_verifier`](./resources/private_state_verifier.md)
- [`pyvider_warning_example`](./resources/warning_example.md)

### Test Data Sources

- [`pyvider_mixed_map_test`](./data-sources/mixed_map_test.md)
- [`pyvider_nested_resource_test`](./data-sources/nested_resource_test.md)
- [`pyvider_simple_map_test`](./data-sources/simple_map_test.md)
- [`pyvider_structured_object_test`](./data-sources/structured_object_test.md)
