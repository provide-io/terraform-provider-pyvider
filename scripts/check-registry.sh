#!/bin/bash
# Script to check Terraform Registry status for provide-io/pyvider provider

set -euo pipefail

# Source the TFC token
if [ -f ~/code/gh/provide-io/tforg.env ]; then
    source ~/code/gh/provide-io/tforg.env
else
    echo "❌ TFC token file not found at ~/code/gh/provide-io/tforg.env"
    exit 1
fi

if [ -z "${TFC_ORG_TOKEN:-}" ]; then
    echo "❌ TFC_ORG_TOKEN not set"
    exit 1
fi

echo "🔍 Checking Terraform Registry for provide-io/pyvider..."

# Function to check provider info
check_provider() {
    echo -e "\n📦 Provider Info:"
    curl -s -H "Authorization: Bearer $TFC_ORG_TOKEN" \
        "https://registry.terraform.io/v1/providers/provide-io/pyvider" | \
        jq -r '.data | {
            id: .id,
            type: .type,
            name: .attributes.name,
            namespace: .attributes.namespace,
            "full-name": .attributes."full-name",
            "registry-name": .attributes."registry-name",
            published: .attributes."published-at"
        }' 2>/dev/null || echo "Failed to fetch provider info"
}

# Function to list all versions
list_versions() {
    echo -e "\n📋 Published Versions:"
    curl -s -H "Authorization: Bearer $TFC_ORG_TOKEN" \
        "https://registry.terraform.io/v1/providers/provide-io/pyvider/versions" | \
        jq -r '.data[]? | "\(.attributes.version) - Platforms: \(.attributes.platforms | join(", "))"' 2>/dev/null || \
        echo "No versions found or API error"
}

# Function to check specific version
check_version() {
    local version="${1:-}"
    if [ -z "$version" ]; then
        echo "Usage: check_version <version>"
        return 1
    fi
    
    echo -e "\n🔍 Checking version $version:"
    curl -s -H "Authorization: Bearer $TFC_ORG_TOKEN" \
        "https://registry.terraform.io/v1/providers/provide-io/pyvider/versions" | \
        jq --arg v "$version" '.data[]? | select(.attributes.version == $v) | {
            version: .attributes.version,
            platforms: .attributes.platforms,
            published: .attributes."published-at",
            protocols: .attributes.protocols
        }' 2>/dev/null || echo "Version $version not found"
}

# Function to check latest release on GitHub
check_github_releases() {
    echo -e "\n📦 Latest GitHub Releases:"
    gh release list --repo provide-io/terraform-provider-pyvider --limit 3 2>/dev/null || \
        curl -s "https://api.github.com/repos/provide-io/terraform-provider-pyvider/releases" | \
        jq -r '.[:3][] | "\(.tag_name) - \(.published_at) - Assets: \(.assets | length)"'
}

# Main execution
echo "═══════════════════════════════════════════════════"
check_provider
list_versions
check_github_releases

# Check specific version if provided
if [ -n "${1:-}" ]; then
    check_version "$1"
fi

echo "═══════════════════════════════════════════════════"