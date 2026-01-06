---
page_title: "02) Getting Started with Pyvider"
description: "Step-by-step tutorial for installing and using the pyvider Terraform provider for the first time."
guide_order: 3
---

# Getting Started with pyvider Terraform Provider

**Time to Complete:** 10-15 minutes

This tutorial will guide you through your first use of the pyvider Terraform provider, from installation to creating your first resources.

-> **Note:** New to Pyvider? Start with 00) [Understand the Pyvider Framework](./00-pyvider-orientation.md) and 01) [Tour the Example Provider](./01-provider-tour.md) for the foundational concepts this tutorial builds on.

---

## What You'll Learn

By the end of this tutorial, you will:

- ✅ Install and configure the pyvider provider
- ✅ Create your first file resource
- ✅ Use a data source to read content
- ✅ Understand basic provider workflows
- ✅ Know where to go next

---

## Prerequisites

Before starting, ensure you have:

- **Terraform** 1.0 or later ([Install Terraform](https://www.terraform.io/downloads))
- **pyvider provider binary** ([Download latest release](https://github.com/provide-io/terraform-provider-pyvider/releases))
- Basic familiarity with Terraform concepts (providers, resources, data sources)

### Verify Terraform Installation

```bash
terraform version
# Should output: Terraform v1.x.x
```

---

## Step 1: Install the Provider

### Option A: Automatic Installation (Recommended)

The provider will be automatically installed when you run `terraform init` if properly configured.

### Option B: Manual Installation

1. **Download the provider binary:**

```bash
# Download latest release for your platform
# Example for macOS:
curl -LO https://github.com/provide-io/terraform-provider-pyvider/releases/latest/download/terraform-provider-pyvider_darwin_amd64.zip

# Unzip
unzip terraform-provider-pyvider_darwin_amd64.zip
```

2. **Install to Terraform plugins directory:**

```bash
# Create plugins directory (adjust version as needed)
mkdir -p ~/.terraform.d/plugins/local/providers/pyvider/0.0.12/darwin_amd64/

# Move binary
mv terraform-provider-pyvider ~/.terraform.d/plugins/local/providers/pyvider/0.0.12/darwin_amd64/

# Make executable
chmod +x ~/.terraform.d/plugins/local/providers/pyvider/0.0.12/darwin_amd64/terraform-provider-pyvider
```

### Note

Adjust paths for your platform (linux_amd64, windows_amd64, etc.)

---

## Step 2: Create Your First Configuration

Create a new directory for this tutorial:

```bash
mkdir pyvider-tutorial
cd pyvider-tutorial
```

Create a file named `main.tf`:

```terraform
# main.tf

terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.0"  # For development: accepts any version
      # For production, pin to specific version: version = "~> 0.1"
    }
  }
}

# Configure the pyvider provider
provider "pyvider" {
  # Provider configuration (if needed)
  # Most resources work without additional provider config
}

# Create a simple text file
resource "pyvider_file_content" "greeting" {
  filename = "${path.module}/hello.txt"

  content = <<-EOT
    Hello from pyvider!

    This file was created by Terraform using the pyvider provider.
    Current timestamp: ${timestamp()}
  EOT

  # File permissions (Unix-style)
  mode = "0644"
}

# Output the file path
output "greeting_file" {
  value       = pyvider_file_content.greeting.filename
  description = "Path to the created greeting file"
}
```

---

## Step 3: Initialize Terraform

Initialize your Terraform working directory:

```bash
terraform init
```

**Expected Output:**
```
Initializing the backend...

Initializing provider plugins...
- Finding local/providers/pyvider versions...
- Installing local/providers/pyvider vX.X.X...
- Installed local/providers/pyvider vX.X.X (unauthenticated)

Terraform has been successfully initialized!
```

---

## Step 4: Preview Changes

See what Terraform will create:

```bash
terraform plan
```

**Expected Output:**
```
Terraform will perform the following actions:

  # pyvider_file_content.greeting will be created
  + resource "pyvider_file_content" "greeting" {
      + content  = (known after apply)
      + id       = (known after apply)
      + mode     = "0644"
      + filename = "./hello.txt"
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

---

## Step 5: Apply Configuration

Create the resources:

```bash
terraform apply
```

**Terraform will prompt for confirmation. Type `yes` and press Enter.**

**Expected Output:**
```
pyvider_file_content.greeting: Creating...
pyvider_file_content.greeting: Creation complete after 0s [id=hello.txt]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.

Outputs:

greeting_file = "./hello.txt"
```

---

## Step 6: Verify the Resource

Check that the file was created:

```bash
cat hello.txt
```

**Expected Output:**
```
Hello from pyvider!

This file was created by Terraform using the pyvider provider.
Current timestamp: 2025-10-30T15:39:55Z
```

---

## Step 7: Use a Data Source

Now let's read file information using a data source. Add to your `main.tf`:

```terraform
# Read file metadata
data "pyvider_file_info" "greeting_info" {
  path = pyvider_file_content.greeting.filename
}

# Output the file information
output "greeting_info" {
  value = {
    size         = data.pyvider_file_info.greeting_info.size
    exists       = data.pyvider_file_info.greeting_info.exists
    is_directory = data.pyvider_file_info.greeting_info.is_directory
  }
  description = "Metadata about the greeting file"
}
```

Apply the changes:

```bash
terraform apply
```

**Expected Output:**
```
...
Outputs:

greeting_file = "./hello.txt"
greeting_info = {
  "exists"       = true
  "is_directory" = false
  "size"         = 123
}
```

---

## Step 8: Update a Resource

Let's update the file content. Modify the `pyvider_file_content.greeting` resource:

```terraform
resource "pyvider_file_content" "greeting" {
  filename = "${path.module}/hello.txt"

  content = <<-EOT
    Hello from pyvider!

    This file was UPDATED by Terraform.
    Current timestamp: ${timestamp()}

    pyvider makes Terraform providers easy to build and use!
  EOT

  mode = "0644"
}
```

Apply the changes:

```bash
terraform apply
```

Terraform will detect the change and update the file:

```
pyvider_file_content.greeting: Refreshing state... [id=hello.txt]

Terraform will perform the following actions:

  # pyvider_file_content.greeting will be updated in-place
  ~ resource "pyvider_file_content" "greeting" {
      ~ content  = <<-EOT
            Hello from pyvider!

          - This file was created by Terraform using the pyvider provider.
          + This file was UPDATED by Terraform.
            Current timestamp: 2025-10-30T15:42:18Z
          +
          + pyvider makes Terraform providers easy to build and use!
        EOT
        id       = "hello.txt"
        # (2 unchanged attributes hidden)
    }

Plan: 0 to add, 1 to change, 0 to destroy.
```

---

## Step 9: Clean Up

Destroy the resources:

```bash
terraform destroy
```

Type `yes` when prompted.

**Expected Output:**
```
pyvider_file_content.greeting: Destroying... [id=hello.txt]
pyvider_file_content.greeting: Destruction complete after 0s

Destroy complete! Resources: 1 destroyed.
```

Verify the file is gone:

```bash
ls hello.txt
# Should output: No such file or directory
```

---

## What You've Learned

Congratulations! You've successfully:

✅ Installed and configured the pyvider provider
✅ Created a resource with Terraform
✅ Used a data source to read data
✅ Updated a resource in-place
✅ Destroyed resources with Terraform

---

## Next Steps

### Explore More Components

The pyvider provider includes resources, data sources, and functions. See the [provider documentation](../index.md) for the complete list of available components.

### Build Your Own Provider

Interested in building Terraform providers with Python?

- **[pyvider Framework](https://foundry.provide.io/pyvider/):** Build providers in Python
- **[pyvider-components](https://foundry.provide.io/pyvider-components/):** Example component library for learning and reference
- **[Building Providers Guide](https://foundry.provide.io/pyvider/guides/building-components/):** Complete guide

---

## Troubleshooting

Having issues? See our comprehensive **[Troubleshooting Guide](./03-troubleshooting.md)** for solutions to common problems:

- **[Installation Issues](./03-troubleshooting.md#installation-issues)** - Provider not found, permissions, platform-specific
- **[Configuration Errors](./03-troubleshooting.md#configuration-errors)** - Validation, schema, type mismatches
- **[Runtime Errors](./03-troubleshooting.md#runtime-errors)** - File operations, HTTP/API, state management
- **[Debug Techniques](./03-troubleshooting.md#debugging-techniques)** - TF_LOG, state inspection, terraform console
- **[Getting Help](./03-troubleshooting.md#getting-help)** - Community support and issue reporting

### Quick Fixes

**Provider Not Found:**
```bash
# Verify installation and re-initialize
terraform init -upgrade
```

**Permission Denied:**
```bash
# Check directory permissions
ls -la $(dirname /path/to/file)
```

**Need More Help?** → **[Full Troubleshooting Guide](./03-troubleshooting.md)**

---

## Complete Example

Here's the complete `main.tf` with all features:

```terraform
terraform {
  required_version = ">= 1.0"

  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      # For local development, use the installed version
      # For production, specify: version = "~> 0.0"
    }
  }
}

provider "pyvider" {
  # Provider configuration
}

# Create a file with dynamic content
resource "pyvider_file_content" "greeting" {
  filename = "${path.module}/hello.txt"

  content = <<-EOT
    Hello from pyvider!

    This file was created at: ${timestamp()}
    Terraform version: ${terraform.version}

    pyvider makes Terraform providers easy!
  EOT

  mode = "0644"
}

# Read file metadata
data "pyvider_file_info" "greeting_info" {
  path = pyvider_file_content.greeting.filename
}

# Outputs
output "greeting_file" {
  value       = pyvider_file_content.greeting.filename
  description = "Path to the greeting file"
}

output "greeting_info" {
  value = {
    size         = data.pyvider_file_info.greeting_info.size
    exists       = data.pyvider_file_info.greeting_info.exists
    is_directory = data.pyvider_file_info.greeting_info.is_directory
  }
  description = "Metadata about the greeting file"
}
```

---

## Additional Resources

- **[Provider Reference](../index.md):** Complete resource and data source reference
- **[pyvider Documentation](https://foundry.provide.io/pyvider/):** Provider framework docs
- **[Terraform Documentation](https://www.terraform.io/docs):** Official Terraform docs
- **[Community Support](https://github.com/provide-io/terraform-provider-pyvider/discussions):** Get help

---

## Feedback

Was this tutorial helpful? Have suggestions for improvement?

- 📝 [Report documentation issues](https://github.com/provide-io/terraform-provider-pyvider/issues)
- 💬 [Join the discussion](https://github.com/provide-io/terraform-provider-pyvider/discussions)
- ⭐ [Star the project](https://github.com/provide-io/terraform-provider-pyvider)

---

**Tutorial Version:** 1.0
**Last Updated:** October 30, 2025
**Terraform Version:** 1.0+
**Provider Version:** 1.0+
