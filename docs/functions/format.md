---
page_title: "Function: format"
description: |-
  Formats a string template using positional arguments with error handling
---
# format (Function)

The `format` function takes a template string and a list of values, then returns a formatted string with each placeholder replaced by the corresponding value.

~> **Note:** This provider is in pre-release and under active development. Features and APIs may change without notice and it is not intended for production infrastructure.


Two placeholder dialects are supported, and the template chooses between them:

- If the template contains a `%`, it is a **printf** template and is formatted exactly as Terraform's built-in `format` formats it. Braces are literal text, as they are in Terraform.
- Otherwise, the Python-style `{}` and `{0}` placeholders apply. Every other brace is literal, so a JSON template passes through untouched.

Template-based string formatting enables dynamic message construction, configuration generation, and report creation.

## Capabilities

This function enables you to:

- **Message templating**: Create formatted messages with dynamic content for outputs
- **Path construction**: Build complex paths with multiple variables
- **Configuration generation**: Generate configuration strings with parameters
- **Report formatting**: Create formatted reports with data for documentation
- **Query building**: Construct queries with parameters for external systems

## Example Usage

```terraform
locals {
  format_message = provider::pyvider::format("User {} has {} roles.", ["admin", 3])
  # "User admin has 3 roles."
}

output "format_message" {
  value = local.format_message
}

```

## Signature

`format(template: string, values: list[any]) -> string`

## Parameters

- `template` (string, required) - String containing printf verbs or `{}` placeholders. Returns `null` when the template is `null`.
- `values` (list[any], required) - Positional values inserted into the template. A `null` list is treated as empty.

## Returns

A formatted string or `null` when the template is `null`.

## Printf verbs

Supported verbs, with the same meaning they have in Terraform's `format`:

| Verb | Renders |
| --- | --- |
| `%s` | the value as a string |
| `%q` | the value as a quoted, JSON-escaped string |
| `%d` | a whole number in base 10 |
| `%b`, `%o`, `%x`, `%X` | a whole number in base 2, 8 or 16 |
| `%f`, `%e`, `%E`, `%g`, `%G` | a number in fixed, exponent or general form |
| `%t` | a boolean as `true` or `false` |
| `%v` | the value in its natural form; a collection as JSON, a null as `null` |
| `%%` | a literal `%` |

Flags, width and precision work as in Go: `%5s` pads to width 5, `%-10s` pads on the
right, `%08.3f` zero-pads to width 8 with 3 decimal places. An argument can be
selected explicitly with `%[1]s`, which also allows reusing one value more than once.
Width and precision count grapheme clusters, so padding lines up what a reader sees.

```terraform
locals {
  price   = provider::pyvider::format("$%.2f", [12.5])         # "$12.50"
  hex     = provider::pyvider::format("%x", [255])             # "ff"
  padded  = provider::pyvider::format("[%-6s]", ["ok"])        # "[ok    ]"
  twice   = provider::pyvider::format("%[1]s/%[1]s", ["a"])    # "a/a"
  percent = provider::pyvider::format("100%%", [])             # "100%"
}
```

## Notes

- An error is raised when the template needs more values than were supplied, and also when a value is supplied that the template never reaches — an unused value is a mistake worth reporting rather than silently dropping.
- An error is raised when a value cannot be rendered by the verb it is given: `%d` requires a whole number, `%s` requires something convertible to a string, and every verb except `%v` refuses a null.
- Because a `%` always starts a verb, a template that means a literal percent sign must write it as `%%`.

## Common Patterns

### Message Formatting
```terraform
variable "name" {
  default = "Alice"
}

variable "age" {
  default = 30
}

locals {
  message = provider::pyvider::format("Hello {}, you are {} years old!", [var.name, var.age])
  # Result: "Hello Alice, you are 30 years old!"
}
```

### Configuration Generation
```terraform
variable "env" {
  default = "production"
}

variable "service" {
  default = "api"
}

locals {
  log_path = provider::pyvider::format("/var/log/{}/{}.log", [var.env, var.service])
  # Result: "/var/log/production/api.log"
}
```