# Pyvider Provider Examples

This directory contains examples demonstrating the capabilities of the Pyvider provider for Terraform/OpenTofu.

## Examples

### 1. Complete Demo (`complete-demo/`)
A comprehensive example showcasing various resources and data sources:
- File content management
- Directory creation
- Timed token generation
- Private state verification
- Environment variable reading
- File information retrieval

### 2. Functions Demo (`functions-demo/`)
Demonstrates the provider functions available in Terraform 1.8+:
- String manipulation (upper, lower, reverse, replace)
- Numeric operations (sum, mean)
- Collection operations (concatenate)
- Type conversion
- JQ lens for JSON processing

## Running the Examples

### Prerequisites
1. Install Terraform or OpenTofu
2. Ensure the Pyvider provider is available (version ~> 0.0.3)

### Complete Demo
```bash
cd complete-demo
terraform init
terraform plan
terraform apply
```

This will:
- Create a JSON configuration file
- Set up a local directory
- Generate a timed token
- Read file information and environment variables

### Functions Demo
```bash
cd functions-demo
terraform init
terraform plan
terraform apply
```

This will:
- Demonstrate various provider functions
- Create a JSON file with all function results
- Show how to use JQ expressions for JSON processing

## Provider Functions

The Pyvider provider includes several utility functions:

| Function | Description | Example |
|----------|-------------|---------|
| `upper(string)` | Convert to uppercase | `provider::pyvider::upper("hello")` |
| `lower(string)` | Convert to lowercase | `provider::pyvider::lower("HELLO")` |
| `reverse(string)` | Reverse a string | `provider::pyvider::reverse("hello")` |
| `replace(string, old, new)` | Replace text | `provider::pyvider::replace("hello world", "world", "terraform")` |
| `sum(list)` | Sum of numbers | `provider::pyvider::sum([1, 2, 3])` |
| `mean(list)` | Mean of numbers | `provider::pyvider::mean([1, 2, 3])` |
| `concatenate(list1, list2)` | Concatenate lists | `provider::pyvider::concatenate(["a"], ["b"])` |
| `to_int(string)` | Convert to integer | `provider::pyvider::to_int("42")` |
| `lens_jq(json, query)` | JQ query on JSON | `provider::pyvider::lens_jq(json, ".field")` |

## Testing with Garnish

The examples can be tested using the garnish tool:

```bash
# From the terraform-provider-pyvider directory
garnish test --output-format markdown
```

This will run all example configurations and verify they work correctly.

## Contributing

To add new examples:
1. Create a new directory under `examples/`
2. Add a `main.tf` file with your example configuration
3. Include appropriate comments and outputs
4. Update this README with details about your example

## License

These examples are part of the Pyvider provider project and follow the same Apache-2.0 license.