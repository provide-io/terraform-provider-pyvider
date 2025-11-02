---
page_title: "Pyvider Provider"
description: |-
  Terraform provider for pyvider
---

# Pyvider Provider

Terraform provider for pyvider - A Python-based Terraform provider built with the Pyvider framework.

!!! warning "Proof of Concept & Functionality Test"
    **This provider is currently a proof-of-concept and basic functionality test.**

    It demonstrates the capabilities of the [pyvider framework](https://github.com/provide-io/pyvider)
    for building Terraform providers in Python, using components from
    [pyvider-components](https://github.com/provide-io/pyvider-components).

    **Current Status:**

    - ✅ Functional proof-of-concept
    - ✅ Demonstrates pyvider capabilities
    - ✅ 100+ example resources/data sources/functions
    - ⚠️ Not intended for production workloads
    - ⚠️ APIs may change as pyvider evolves

    **Use this provider for:**

    - Learning pyvider framework capabilities
    - Testing pyvider-based provider development
    - Exploring Terraform provider patterns
    - Proof-of-concept work

    **For production infrastructure:**
    Consider building a custom provider using [pyvider](https://github.com/provide-io/pyvider)
    tailored to your specific needs.

---

## Part of the provide.io Ecosystem

This project is part of a larger ecosystem of tools for Python and Terraform development.

**[View Ecosystem Overview →](https://docs.provide.io/provide-foundation/ecosystem/)**

Understand how provide-foundation, pyvider, flavorpack, and other projects work together.

---

## When to Use This Provider

**✅ Use for learning and testing:**

- Learning how to build Terraform providers in Python
- Studying provider implementation patterns
- Testing and diagnostics
- Proof-of-concept work
- Exploring 100+ example implementations

**❌ Not for production:**

- Critical infrastructure management
- Long-term production configurations
- Systems requiring stable APIs
- Production workloads

**For production:** Build a custom provider with [pyvider](https://github.com/provide-io/pyvider), or use established providers (AWS, Azure, etc.) for real infrastructure.

## Getting Started

New to the pyvider provider? Start with our step-by-step tutorial:

**[→ Getting Started Tutorial](getting-started.md)** - Create your first resources in 10-15 minutes

## Need Help?

**Having issues?** Check our comprehensive troubleshooting guide:

- **[Troubleshooting Guide](troubleshooting.md)** - Solutions to common problems
  - Installation issues (provider not found, permissions)
  - Configuration errors (validation, schema, types)
  - Runtime errors (file operations, HTTP/API, state)
  - Debug techniques (TF_LOG, state inspection)

**Want to learn more?**
- [Common Patterns](how-to-guides/common-patterns.md) - Frequently used configurations
- [pyvider Framework Docs](https://docs.provide.io/pyvider/) - Build your own provider

**Have questions?**
- [GitHub Discussions](https://github.com/provide-io/terraform-provider-pyvider/discussions) - Community support
- [GitHub Issues](https://github.com/provide-io/terraform-provider-pyvider/issues) - Report bugs

## Example Usage

```terraform
provider "pyvider" {
  # Configuration options
}
```

## Schema

No provider configuration required.

## Resources

- [`pyvider_adorner`](./resources/adorner.md)
- [`pyvider_file_content`](./resources/file_content.md)
- [`pyvider_local_directory`](./resources/local_directory.md)
- [`pyvider_private_state_verifier`](./resources/private_state_verifier.md)
- [`pyvider_readme`](./resources/readme.md)
- [`pyvider_timed_token`](./resources/timed_token.md)
- [`pyvider_warning_example`](./resources/warning_example.md)

## Data Sources

- [`pyvider_env_variables`](./data-sources/env_variables.md)
- [`pyvider_file_info`](./data-sources/file_info.md)
- [`pyvider_http_api`](./data-sources/http_api.md)
- [`pyvider_lens_jq`](./data-sources/lens_jq.md)
- [`pyvider_provider_config_reader`](./data-sources/provider_config_reader.md)

## Functions

- [`add`](./functions/add.md)
- [`contains`](./functions/contains.md)
- [`divide`](./functions/divide.md)
- [`format`](./functions/format.md)
- [`format_size`](./functions/format_size.md)
- [`join`](./functions/join.md)
- [`length`](./functions/length.md)
- [`lens_jq`](./functions/lens_jq.md)
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
