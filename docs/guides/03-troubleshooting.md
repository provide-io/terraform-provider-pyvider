---
page_title: "03) Troubleshooting"
description: "Diagnose and resolve common issues you might hit while experimenting with the pyvider provider."
guide_order: 4
---

# Troubleshooting

Common issues and solutions for the pyvider Terraform provider.

~> **Note:** This provider is in pre-release. Expect API changes, and consider building a custom provider with [Pyvider](https://github.com/provide-io/pyvider) for production needs.

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
# 1. Build the provider (using make or flavor directly)
cd terraform-provider-pyvider
make build

# 2. Move to Terraform plugin directory
# macOS/Linux (adjust version as needed):
mkdir -p ~/.terraform.d/plugins/local/providers/pyvider/0.0.12/darwin_amd64
cp dist/darwin_arm64/terraform-provider-pyvider_v* ~/.terraform.d/plugins/local/providers/pyvider/0.0.12/darwin_amd64/terraform-provider-pyvider

# 3. Configure Terraform to use local provider
terraform {
  required_providers {
    pyvider = {
      source  = "local/providers/pyvider"
      version = ">= 0.0.0"  # For development: accepts any version
      # For production, pin to specific version: version = "~> 0.1"
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

**Debug:**
```bash
terraform validate
# Shows configuration errors before apply
```

---

### Schema Validation Failures

**Problem:** "Invalid value for attribute" or type mismatch errors

**Solutions:**

**String vs Number:**
```terraform
# Correct
resource "pyvider_example" "test" {
  port = 8080        # Number (no quotes)
  name = "test"      # String (with quotes)
}

# Incorrect
resource "pyvider_example" "bad" {
  port = "8080"      # ERROR: Expected number, got string
}
```

**Boolean values:**
```terraform
# Correct
enabled = true       # Boolean (no quotes)

# Incorrect
enabled = "true"     # ERROR: Expected bool, got string
```

**Lists and Maps:**
```terraform
# Correct
tags = {
  Environment = "dev"
  Owner       = "team"
}

files = ["file1.txt", "file2.txt"]

# Incorrect - using wrong brackets
tags = ["key=value"]              # ERROR: Expected map
files = {file = "file1.txt"}      # ERROR: Expected list
```

---

### Attribute Type Mismatches

**Problem:** "Inappropriate value for attribute" errors

**Common Causes:**

1. **Passing computed value where static required:**
   ```terraform
   # May fail if provider expects literal string
   path = data.pyvider_env_variables.vars.value["HOME"]

   # Better - use string interpolation
   path = "${data.pyvider_env_variables.vars.value["HOME"]}/myfile"
   ```

2. **Wrong collection type:**
   ```terraform
   # Check if attribute expects list, set, or map
   # Consult resource documentation
   ```

3. **Null/undefined values:**
   ```terraform
   # Use 'try()' for potentially undefined values
   value = try(var.optional_value, "default")
   ```

---

## Runtime Errors

### File Operations Errors

**Problem:** File resource creation fails

**Common Causes and Solutions:**

**1. Permission Denied:**
```terraform
resource "pyvider_file_content" "test" {
  path    = "/etc/protected.txt"  # ERROR: No write permission
  content = "test"
}

# Solution: Use writable location
resource "pyvider_file_content" "test" {
  path    = "/tmp/test.txt"      # OK: /tmp is writable
  content = "test"
}
```

**2. Directory Doesn't Exist:**
```terraform
resource "pyvider_file_content" "test" {
  path    = "/nonexistent/dir/file.txt"  # ERROR: Parent directory missing
  content = "test"
}

# Solution: Create directory first
resource "pyvider_local_directory" "dir" {
  path = "/tmp/mydir"
}

resource "pyvider_file_content" "test" {
  path    = "${pyvider_local_directory.dir.path}/file.txt"
  content = "test"
}
```

**3. File Already Exists:**
```terraform
# If file exists and content differs, update will fail
# Solution: Remove file first or use different path
```

**4. Invalid Path Characters:**
```terraform
# Windows: Avoid reserved characters < > : " | ? *
# All platforms: Avoid trailing spaces, special characters
path = "/tmp/valid-file-name.txt"  # Good
path = "/tmp/file:name.txt"        # May fail on Windows
```

---

### HTTP/API Errors

**Problem:** `pyvider_http_api` data source fails with network errors

**Common Causes:**

**1. Network Connectivity:**
```terraform
data "pyvider_http_api" "test" {
  url = "https://api.example.com/data"
  # ERROR: Host not reachable
}

# Debug:
# - Check URL is correct
# - Verify DNS resolution: `nslookup api.example.com`
# - Test connectivity: `curl https://api.example.com/data`
```

**2. SSL/TLS Certificate Issues:**
```terraform
# Self-signed certificates may fail validation
# Solution: Use http:// for local testing (not production!)
data "pyvider_http_api" "local" {
  url = "http://localhost:8080/api"
}
```

**3. Authentication Required:**
```terraform
# Some APIs require authentication
# Check if data source supports headers/auth
# Consult data source documentation
```

**4. Rate Limiting:**
```terraform
# API returns 429 Too Many Requests
# Solution: Add delays between applies or reduce refresh frequency
```

---

### State Management Problems

**Problem:** State file errors or drift

**Solutions:**

**1. State file corrupted:**
```bash
# Backup state
cp terraform.tfstate terraform.tfstate.backup

# Inspect state
terraform show

# If corrupted, restore from backup
mv terraform.tfstate.backup terraform.tfstate
```

**2. State drift (resource modified outside Terraform):**
```bash
# Detect drift
terraform plan

# Refresh state to match reality
terraform refresh

# Or import existing resource
terraform import pyvider_file_content.example /path/to/file
```

**3. State locking issues:**
```bash
# If state is locked and process died:
# Manually unlock (use with caution)
terraform force-unlock <lock-id>
```

---

### Validation Errors

**Problem:** Custom validation fails

**Example:**
```terraform
variable "port" {
  type = number
  validation {
    condition     = var.port > 1024 && var.port < 65536
    error_message = "Port must be between 1024 and 65535"
  }
}

# ERROR: Port 80 fails validation
```

**Solution:**
- Read the validation error message carefully
- Adjust input values to meet validation constraints
- Check provider-specific validation rules in documentation

---

## Provider Limitations (Pre-release)

### Understanding Pre-release Status

**This provider is in pre-release**, not recommended for production infrastructure management.

**Current Limitations:**

1. **Limited Resource Types:**
   - Mostly file operations, HTTP calls, and utilities
   - No cloud infrastructure resources (AWS, Azure, GCP)
   - Not suitable for managing production infrastructure

2. **Experimental Features:**
   - Some resources are examples, not production-tested
   - APIs may change in later versions; availability may change or be removed
   - Not all pyvider framework features implemented

3. **Performance:**
   - Not optimized for large-scale deployments
   - May be slower than native providers

4. **Testing:**
   - Test coverage varies by resource
   - Edge cases may not be handled

---

### Known Limitations vs Pyvider Framework

**Provider vs Framework:**

- **terraform-provider-pyvider:** Pre-release provider showing what's possible
- **pyvider framework:** Full framework for building custom providers

**If you need:**
- ✅ Learning pyvider → Use this provider
- ✅ Testing concepts → Use this provider
- ❌ Production infrastructure → Build custom provider with pyvider

**Missing from provider but available in framework:**
- Advanced state management features
- Custom validation logic
- Provider-specific configuration
- Performance optimizations
- Production-grade error handling

---

### When to Build a Custom Provider

**Build your own provider when:**

1. **Production Use Required:**
   - Managing critical infrastructure
   - Need SLAs and support
   - Require specific compliance/security

2. **Custom Logic Needed:**
   - Business-specific resources
   - Custom validation rules
   - Integration with internal APIs

3. **Performance Critical:**
   - Managing 100s+ resources
   - High-frequency updates
   - Large state files

**How to Build:**
- Use [pyvider framework](https://github.com/provide-io/pyvider)
- Reference pyvider-components for examples
- Follow [pyvider documentation](https://foundry.provide.io/pyvider/)

---

## Debug Techniques

### Enable Terraform Debug Logging

**Set TF_LOG environment variable:**

```bash
# Enable detailed logging
export TF_LOG=DEBUG
terraform apply

# Levels: TRACE, DEBUG, INFO, WARN, ERROR
export TF_LOG=TRACE  # Most verbose

# Log to file instead of console
export TF_LOG_PATH=terraform.log
terraform apply
cat terraform.log
```

**What to look for in logs:**
- Provider initialization messages
- Resource creation/update/delete attempts
- Error messages with stack traces
- API request/response details

---

### State Inspection

**View current state:**
```bash
# Show all resources
terraform show

# Show specific resource
terraform state show pyvider_file_content.example

# List all resources
terraform state list
```

**Check state for issues:**
```bash
# Validate state file
terraform validate

# Check for drift
terraform plan

# Refresh state from actual resources
terraform refresh
```

---

### Common Debugging Workflow

1. **Isolate the problem:**
   ```bash
   # Test with minimal configuration
   # Comment out unrelated resources
   # Apply one resource at a time
   ```

2. **Enable logging:**
   ```bash
   export TF_LOG=DEBUG
   terraform apply 2>&1 | tee debug.log
   ```

3. **Check provider logs:**
   - Look for provider initialization errors
   - Check resource-specific error messages
   - Note any warnings

4. **Verify configuration:**
   ```bash
   terraform validate      # Syntax and schema
   terraform fmt -check    # Formatting
   terraform plan         # What will change
   ```

5. **Test manually:**
   ```bash
   # If creating file, try manually:
   touch /tmp/test.txt

   # If calling API, try with curl:
   curl https://api.example.com/endpoint
   ```

---

### Using terraform console

**Interactive testing:**
```bash
terraform console

# Test expressions
> var.example_var
> local.computed_value
> pyvider_file_content.test.path

# Test functions
> file("/tmp/test.txt")
> jsondecode("{\"key\": \"value\"}")
```

---

## Getting Help

### Documentation Resources

- **[Getting Started Tutorial](02-getting-started.md)** - Step-by-step first provider usage
- **[Resource Reference](../index.md#resources)** - Complete resource documentation
- **[Data Sources](../index.md#data-sources)** - Available data sources

### Community Support

**GitHub Issues:**
- [terraform-provider-pyvider issues](https://github.com/provide-io/terraform-provider-pyvider/issues)
- [pyvider framework issues](https://github.com/provide-io/pyvider/issues)

**Before Opening an Issue:**
1. Search existing issues for similar problems
2. Include Terraform version (`terraform version`)
3. Include provider version
4. Provide minimal reproduction configuration
5. Include relevant log output (TF_LOG=DEBUG)
6. Describe expected vs actual behavior

### Reporting Bugs

**Include in bug reports:**
```
- Terraform version: 1.5.0
- Provider version: X.X.X (check VERSION file or releases page)
- Platform: macOS 13.4 (darwin_arm64)
- Configuration: [minimal example]
- Steps to reproduce
- Error message / log output
- Expected behavior
```

---

## Quick Reference

### Most Common Issues

| Problem | Quick Fix |
|---------|-----------|
| Provider not found | Check `~/.terraform.d/plugins/` structure |
| Permission denied | `chmod +x terraform-provider-pyvider` |
| Invalid attribute | Check resource documentation for schema |
| File creation fails | Verify path is writable, directory exists |
| HTTP error | Test URL with `curl` first |
| State locked | `terraform force-unlock <ID>` (caution!) |

### Useful Commands

```bash
# Validation
terraform validate
terraform fmt
terraform plan

# Debugging
export TF_LOG=DEBUG
terraform console

# State management
terraform state list
terraform state show <resource>
terraform refresh

# Cleanup
terraform destroy
rm -rf .terraform terraform.tfstate*
```

---

**Still stuck?** Open an issue on [GitHub](https://github.com/provide-io/terraform-provider-pyvider/issues) with details!

---

*Documentation version: 0.0.19 | Last updated: 2025-11-09*
