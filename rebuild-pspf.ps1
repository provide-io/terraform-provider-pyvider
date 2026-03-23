# PowerShell script to rebuild the PSPF with lazy loading
# Run this from an elevated PowerShell prompt with network access

Write-Host "Building Pyvider PSPF with Lazy Loading System"
Write-Host "================================================"

# Set working directory
Set-Location "C:\code\terraform-provider-pyvider"

# Clean old build
Write-Host "`nCleaning old builds..."
if (Test-Path "dist\terraform-provider-pyvider.exe") {
    Remove-Item "dist\terraform-provider-pyvider.exe" -Force
}
if (Test-Path "dist\terraform-provider-pyvider.psp") {
    Remove-Item "dist\terraform-provider-pyvider.psp" -Force
}

# Ensure lazy-packages.zip exists
Write-Host "Checking lazy-packages.zip..."
if (-not (Test-Path "lazy-packages.zip")) {
    Write-Host "Building lazy-packages.zip..."
    & "C:\code\terraform-provider-pyvider\.venv\Scripts\python.exe" `
        "C:\code\pyvider\scripts\build-lazy-packages.py" `
        --output "lazy-packages.zip"
}

$lazySize = (Get-Item "lazy-packages.zip").Length / 1MB
Write-Host "  Lazy archive: $($lazySize.ToString('F1')) MB"

# Build PSPF with flavor pack
Write-Host "`nBuilding PSPF..."
Write-Host "This may take 2-5 minutes..."

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONLEGACYWINDOWSSTDIO = "1"

# Run the build
& "C:\code\provide-io\flavorpack\.venv\Scripts\python.exe" -m flavor pack `
    --launcher-bin "C:\code\provide-io\dist\bin\flavor-go-launcher-windows_arm64.exe"

# Check result
if (Test-Path "dist\terraform-provider-pyvider.exe") {
    $exeSize = (Get-Item "dist\terraform-provider-pyvider.exe").Length / 1MB
    Write-Host "`nSUCCESS!"
    Write-Host "Built: dist\terraform-provider-pyvider.exe ($($exeSize.ToString('F1')) MB)"

    # Copy to terraform plugin directory
    Write-Host "`nInstalling to Terraform..."
    $pluginDir = "$env:USERPROFILE\.terraform.d\plugins\local\providers\pyvider\0.3.21\windows_arm64"
    if (-not (Test-Path $pluginDir)) {
        New-Item -ItemType Directory -Path $pluginDir -Force | Out-Null
    }

    Copy-Item "dist\terraform-provider-pyvider.exe" `
        "$pluginDir\terraform-provider-pyvider.exe" -Force
    Copy-Item "lazy-packages.zip" `
        "$pluginDir\lazy-packages.zip" -Force

    Write-Host "Installed to: $pluginDir"
    Write-Host "`nReady to test with Terraform!"
    Write-Host "Run: terraform plan"
} else {
    Write-Host "FAILED - Build did not produce terraform-provider-pyvider.exe"
    exit 1
}
