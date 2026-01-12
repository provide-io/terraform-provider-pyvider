---
page_title: "00) Understand the Pyvider Framework"
description: "Get oriented with the ideas behind Pyvider before you dive into the example provider."
guide_order: 1
---

# Understand the Pyvider Framework

Pyvider is a Python framework that implements the Terraform Plugin Protocol v6. Instead of writing Go, you describe providers, resources, and data sources with Python classes, type-safe schemas, and async handlers. This guide gives you the mental model you need before exploring the `pyvider` Terraform provider.

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

## How this repository fits in

- **`terraform-provider-pyvider`** – Prebuilt provider that exposes the example components to Terraform.
- **`pyvider-components`** – The component library this provider imports. Study it to see how individual resources are implemented.
- **`pyvider`** – The framework that turns Python classes into a Terraform provider binary.

Use this repository to learn the flow from framework → components → provider. When you are ready to build something custom, use the tutorials in the Pyvider documentation and copy patterns from `pyvider-components`.

## Next steps

- Move on to [Tour the Example Provider](./01-provider-tour.md) to understand what is shipped.
- Dive into [Getting Started with Pyvider](./02-getting-started.md) when you want to run Terraform locally.
