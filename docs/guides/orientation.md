---
page_title: "Understand the Pyvider Framework"
description: "Get oriented with the ideas behind Pyvider and how to build Terraform providers in Python."
guide_order: 1
---

# Understand the Pyvider Framework

Pyvider is a Python framework that implements the Terraform Plugin Protocol v6. Instead of writing Go, you describe providers, resources, and data sources with Python classes, type-safe schemas, and async handlers. This guide gives you the mental model you need to build Terraform providers with Pyvider.


~> **Note:** This provider is currently in POC (proof-of-concept) status and under active development. Features and APIs may change without notice. Not intended for production infrastructure.

## Key ideas in Pyvider

- **Pure Python implementation** – Providers are regular Python packages. Pyvider handles the wire protocol and lifecycle interactions with Terraform.
- **Decorator-based registration** – Use decorators such as `@register_provider` and `@register_resource` to expose capabilities without manual boilerplate.
- **Schema definitions** – Define resource and data source schemas with expressive helpers (`s_resource`, `a_str`, `a_int`, and friends) that map to Terraform types.
- **Async execution model** – Resource operations (`create`, `read`, `update`, `delete`) and data source fetches can run concurrently with `asyncio`, keeping providers responsive.

## Components that make up a provider

| Concept | Pyvider term | Terraform equivalent | Purpose |
| --- | --- | --- | --- |
| Provider | `BaseProvider` subclass | Provider plugin entrypoint | Handles configuration and wires capabilities |
| Capability | Module of components | Logical feature area (e.g. file operations) | Groups related resources/data sources |
| Resource | `BaseResource` subclass | `resource "…" "…" {}` | Manages infrastructure objects or local effects |
| Data Source | `BaseDataSource` subclass | `data "…" "…" {}` | Reads or calculates information for configurations |
| Function | Decorated Python callable | `provider::pyvider::upper()` | Adds reusable helpers directly to Terraform |

The [pyvider-components](https://github.com/provide-io/pyvider-components) repository supplies a rich library of these building blocks. This provider bundles them so you can experiment from Terraform without writing any Python.

## What happens when Terraform calls the provider

1. Terraform launches the compiled provider binary.
2. The binary loads your Python package and registers all Pyvider components.
3. When Terraform evaluates configuration blocks, Pyvider calls your async handlers.
4. Python code returns structured objects (`State`, `Diagnostics`), and Pyvider translates them back to Terraform's protocol messages.

Because Pyvider speaks the same protocol as the official Go SDK, anything you build behaves like a native provider.

## How the Pyvider ecosystem fits together

- **`pyvider`** – The core framework that turns Python classes into a Terraform provider binary.
- **`pyvider-components`** – This component library providing example resources, data sources, and functions. Study these to see how components are implemented.
- **`terraform-provider-pyvider`** – Reference implementation provider that bundles pyvider-components for demonstration purposes.

Use the components in this library as templates when building your own providers. Each component demonstrates best practices for schema definition, async handlers, validation, and error handling.

## Next steps

- Continue to [Build Your Own Provider](./build-your-own.md) to create a custom provider for your infrastructure.
- Explore the component source code in this repository to understand implementation patterns.

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*