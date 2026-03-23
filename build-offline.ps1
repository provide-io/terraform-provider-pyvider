# PowerShell script to build PSPF offline using local venv packages
# This bypasses the DNS/network issue by collecting wheels first

Write-Host "Building Pyvider PSPF - Offline Mode"
Write-Host "======================================"

Set-Location "C:\code\terraform-provider-pyvider"

# Step 1: Create wheels directory and collect all installed packages
Write-Host "`nCollecting wheels from venv..."
$wheelsDir = ".\wheels"
if (Test-Path $wheelsDir) {
    Remove-Item $wheelsDir -Recurse -Force
}
New-Item -ItemType Directory -Path $wheelsDir -Force | Out-Null

# Download/copy wheels for all installed packages
Write-Host "Downloading wheels..."
& ".venv\Scripts\pip" download `
    --dest $wheelsDir `
    --no-deps `
    -r <(& ".venv\Scripts\pip" freeze) `
    --no-index `
    --find-links $wheelsDir `
    2>&1 | Select-String "^Collecting\|^Successfully\|ERROR"

Write-Host "Wheels directory ready at: $(Resolve-Path $wheelsDir)"

# Step 2: Set environment for offline build
Write-Host "`nConfiguring offline build environment..."
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONLEGACYWINDOWSSTDIO = "1"

# Tell pip tools to only use local index
$env:PIP_NO_INDEX = "1"
$env:PIP_FIND_LINKS = Resolve-Path $wheelsDir
$env:PIP_INDEX_URL = ""
$env:PIP_EXTRA_INDEX_URL = ""

# For uv: disable network access
$env:UV_INDEX_STRATEGY = "prefer-binary"

Write-Host "Set PIP_FIND_LINKS=$($env:PIP_FIND_LINKS)"

# Step 3: Clean old builds
Write-Host "`nCleaning old builds..."
if (Test-Path "dist\terraform-provider-pyvider.psp") {
    Remove-Item "dist\terraform-provider-pyvider.psp" -Force
}
if (Test-Path "dist\terraform-provider-pyvider.exe") {
    Remove-Item "dist\terraform-provider-pyvider.exe" -Force
}

# Step 4: Build PSPF
Write-Host "`nBuilding PSPF with offline mode..."
Write-Host "Command: flavor pack --launcher-bin <path>"
Write-Host ""

try {
    & "C:\code\provide-io\flavorpack\.venv\Scripts\python.exe" -m flavor pack `
        --launcher-bin "C:\code\provide-io\dist\bin\flavor-go-launcher-windows_arm64.exe" `
        2>&1 | ForEach-Object {
            Write-Host $_
            if ($_ -match "ERROR|error|Failed|failed") {
                Write-Host "^^^ ERROR DETECTED ^^^" -ForegroundColor Red
            }
        }

    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        Write-Host "`nBuild failed with exit code: $exitCode" -ForegroundColor Red
        Write-Host "Checking logs..."
        exit 1
    }
} catch {
    Write-Host "Exception during build: $_" -ForegroundColor Red
    exit 1
}

# Step 5: Verify output
if (Test-Path "dist\terraform-provider-pyvider.exe") {
    $exeSize = (Get-Item "dist\terraform-provider-pyvider.exe").Length / 1MB
    Write-Host "`n✅ SUCCESS!"
    Write-Host "Built: dist\terraform-provider-pyvider.exe ($($exeSize.ToString('F1')) MB)"

    # Check for embedded lazy-packages.zip
    if (Test-Path "lazy-packages.zip") {
        $zipSize = (Get-Item "lazy-packages.zip").Length / 1MB
        Write-Host "Lazy archive: lazy-packages.zip ($($zipSize.ToString('F1')) MB)"
        Write-Host "Archive will be embedded in PSPF"
    }

    # Install to Terraform
    Write-Host "`nInstalling to Terraform plugin directory..."
    $pluginDir = "$env:USERPROFILE\.terraform.d\plugins\local\providers\pyvider\0.3.21\windows_arm64"
    if (-not (Test-Path $pluginDir)) {
        New-Item -ItemType Directory -Path $pluginDir -Force | Out-Null
    }

    Copy-Item "dist\terraform-provider-pyvider.exe" "$pluginDir\terraform-provider-pyvider.exe" -Force
    Write-Host "Installed to: $pluginDir"
    Write-Host "`n✅ Ready for testing with Terraform!"

} else {
    Write-Host "`n❌ FAILED - Build did not produce terraform-provider-pyvider.exe" -ForegroundColor Red
    exit 1
}
