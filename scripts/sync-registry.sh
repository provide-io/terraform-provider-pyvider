#!/bin/bash
# Script to trigger Terraform Registry sync for provide-io/pyvider provider

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

echo "🔄 Attempting to sync Terraform Registry for provide-io/pyvider..."

# Try to get provider ID first
PROVIDER_ID=$(curl -s -H "Authorization: Bearer $TFC_ORG_TOKEN" \
    "https://registry.terraform.io/v1/providers/provide-io/pyvider" | \
    jq -r '.data.id' 2>/dev/null)

if [ "$PROVIDER_ID" == "null" ] || [ -z "$PROVIDER_ID" ]; then
    echo "⚠️  Could not find provider ID. Provider might not be registered yet."
    echo "Attempting to use provider ID 7341 (from previous attempts)..."
    PROVIDER_ID="7341"
fi

echo "Provider ID: $PROVIDER_ID"

# Try to trigger a resync
echo -e "\n🔄 Triggering resync..."
RESPONSE=$(curl -s -X POST \
    -H "Authorization: Bearer $TFC_ORG_TOKEN" \
    -H "Content-Type: application/vnd.api+json" \
    "https://registry.terraform.io/v1/providers/$PROVIDER_ID/resync" 2>&1)

echo "Response: $RESPONSE"

# Also try the versions endpoint
echo -e "\n📋 Checking versions endpoint..."
curl -s -H "Authorization: Bearer $TFC_ORG_TOKEN" \
    "https://registry.terraform.io/v1/providers/$PROVIDER_ID/provider-versions" | \
    jq '.data[]? | {version: .attributes.version, platforms: .attributes.platforms}' 2>/dev/null || \
    echo "No versions found"

# Check GitHub webhook status
echo -e "\n🔗 Checking GitHub webhooks..."
gh api repos/provide-io/terraform-provider-pyvider/hooks 2>/dev/null | \
    jq '.[] | {name: .name, active: .active, url: .config.url, events: .events}' || \
    echo "No webhooks configured"

echo -e "\n💡 If sync is not working:"
echo "1. Check https://registry.terraform.io/providers/provide-io/pyvider/settings"
echo "2. Ensure GitHub repository is connected"
echo "3. Try clicking 'Resync' button in the web UI"
echo "4. Verify GPG key is configured in Registry settings"