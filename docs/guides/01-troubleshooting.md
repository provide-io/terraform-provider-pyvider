---
page_title: "Troubleshooting"
guide_order: 3
---

# Troubleshooting

Common issues and solutions for the pyvider Terraform provider.

~> **Note:** This provider is a proof-of-concept. Many issues stem from its experimental nature. For production infrastructure, consider building a custom provider using [pyvider](https://github.com/provide-io/pyvider).

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Configuration Errors](#configuration-errors)
- [Runtime Errors](#runtime-errors)
- [Provider Limitations](#provider-limitations-poc-status)
- [Debug Techniques](#debug-techniques)
- [Getting Help](#getting-help)

---

## Installation Issues

### Provider Not Found

**Problem:** `terraform init` fails with "provider not found" or "provider registry does not have a provider"

**Solutions:**

**If using local development:**
```bash
# 1. Build the provider
cd terraform-provider-pyvider
go build -o terraform-provider-pyvider

# 2. Move to Terraform plugin directory
# macOS/Linux:
mkdir -p ~/.terraform.d/plugins/local/providers/pyvider/0.1.0/darwin_amd64
mv terraform-provider-pyvider ~/.terraform.d/plugins/local/providers/pyvider/0.1.0/darwin_amd64/

# 3. Configure Terraform to use local provider
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = "0.1.0"
    }
  }
}
```

**If provider binary exists but isn't found:**
- Check file permissions: `chmod +x terraform-provider-pyvider`
- Verify plugin directory matches your platform (darwin_amd64, linux_amd64, etc.)
- Ensure version in configuration matches directory structure

---

### Terraform Version Incompatibility

**Problem:** Provider fails to initialize or shows protocol errors

**Solution:**

Check Terraform version compatibility:
```bash
terraform version
# Required: Terraform 1.0+ or OpenTofu 1.0+
```

**Terraform Protocol 6 Required:**
- This provider uses Terraform Plugin Protocol 6
- Requires Terraform 1.0 or later
- Older versions (0.x) are not supported

**Upgrade Terraform:**
```bash
# macOS with Homebrew
brew upgrade terraform

# Or download from terraform.io
```

---

### Permission Denied Errors

**Problem:** "Permission denied" when Terraform tries to execute provider

**Solutions:**

**Make provider executable:**
```bash
chmod +x ~/.terraform.d/plugins/local/providers/pyvider/*/*/terraform-provider-pyvider
```

**Check file ownership:**
```bash
ls -la ~/.terraform.d/plugins/
# Should be owned by your user, not root
```

**Fix ownership if needed:**
```bash
sudo chown -R $USER:$USER ~/.terraform.d/
```

---

### Platform-Specific Installation

**macOS:**
- Use `darwin_amd64` or `darwin_arm64` (Apple Silicon)
- Gatekeeper may block unsigned binaries
- Solution: `xattr -d com.apple.quarantine terraform-provider-pyvider`

**Linux:**
- Use `linux_amd64` or `linux_arm64`
- Ensure executable bit set
- Check SELinux/AppArmor policies if applicable

**Windows:**
- Use `windows_amd64`
- Use backslashes in paths or forward slashes with quotes
- Provider support is experimental on Windows

---

## Configuration Errors

### Invalid Resource Configuration

**Problem:** Resource fails validation with "Missing required argument" or "Invalid attribute"

**Solution:**

Check the resource schema in documentation:

```terraform
# Correct - all required attributes present
resource "pyvider_file_content" "example" {
  path    = "/tmp/example.txt"  # Required
  content = "Hello World"        # Required
}

# Incorrect - missing required attribute
resource "pyvider_file_content" "bad" {
  path = "/tmp/example.txt"
  # ERROR: Missing required attribute 'content'
}
```

**Common issues:**
- Missing required attributes
- Typos in attribute names
- Wrong attribute types (string vs number vs bool)

---

### Provider Configuration Errors

**Problem:** Terraform fails during provider configuration with messages like "Invalid provider configuration" or "Unknown argument"

**Solutions:**

- Verify capability-specific configuration fields. Many resources work without provider-level settings.
- Use `data "pyvider_provider_config_reader"` to validate the effective configuration.
- Ensure environment variables referenced in configuration are set before running Terraform.

---

## Runtime Errors

### File Permission Errors

**Problem:** Operations involving file resources fail with permission errors.

**Solutions:**

- Confirm Terraform has write access to the target path.
- On macOS, ensure the directory allows writing from Terminal (`chmod -R u+w directory`).
- Use relative paths within your Terraform module to avoid accidental restricted directories.

---

### Template Rendering Issues

**Problem:** Dynamic content in resources fails to render or contains unexpected values.

**Solutions:**

- Validate Terraform expressions using `terraform console`.
- Use helper functions like `provider::pyvider::upper` or `provider::pyvider::format` for structured strings.
- Log intermediate values with `terraform console` or temporary outputs.

---

## Provider Limitations (POC Status)

- APIs and schemas may change without notice.
- Error messages emphasize debugging over user-friendly wording.
- Windows support is experimental; prefer macOS or Linux for a smoother experience.

---

## Debug Techniques

- Run Terraform with `TF_LOG=DEBUG` to collect provider logs.
- Use `terraform providers schema -json` to inspect current resource and data source schemas.
- Build the provider locally and run it under a debugger if you are modifying source code.

---

## Getting Help

- Review the [pyvider repository](https://github.com/provide-io/pyvider) for framework documentation.
- Explore component implementations in [pyvider-components](https://github.com/provide-io/pyvider-components).
- Open an issue or discussion in the relevant repository if you uncover a bug or want to share feedback.
