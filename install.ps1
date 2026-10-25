# AVM installer for Windows
# Usage: irm https://raw.githubusercontent.com/danil0ws/avm/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo = "danil0ws/avm"
$Binary = "avm.exe"

# Detect arch
$Arch = if ([System.Runtime.InteropServices.RuntimeInformation]::ProcessArchitecture -eq "Arm64") {
    "aarch64"
} else {
    "x86_64"
}
$Target = "${Arch}-pc-windows-msvc"

# Install directory
$InstallDir = if ($env:AVM_INSTALL_DIR) {
    $env:AVM_INSTALL_DIR
} else {
    Join-Path $env:LOCALAPPDATA "AVM\bin"
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

# Get latest release
Write-Host "Fetching latest AVM release..."
$LatestJson = Invoke-RestMethod "https://api.github.com/repos/$Repo/releases/latest"
$Latest = $LatestJson.tag_name
$Version = $Latest.TrimStart("v")

if (-not $Latest) {
    Write-Error "Could not determine latest release. Check https://github.com/$Repo/releases"
    exit 1
}

$Archive = "avm-$Version-$Target.zip"
$Url = "https://github.com/$Repo/releases/download/$Latest/$Archive"

Write-Host "Installing AVM $Latest for Windows/$Arch..."
Write-Host "  From: $Url"
Write-Host "  To:   $InstallDir\$Binary"

# Download
$TmpDir = Join-Path $env:TEMP "avm-install-$(New-Guid)"
New-Item -ItemType Directory -Path $TmpDir | Out-Null

try {
    $ArchivePath = Join-Path $TmpDir $Archive
    Invoke-WebRequest -Uri $Url -OutFile $ArchivePath -UseBasicParsing

    # Verify checksum
    $SumsUrl = "https://github.com/$Repo/releases/download/$Latest/SHA256SUMS.txt"
    try {
        $SumsPath = Join-Path $TmpDir "SHA256SUMS.txt"
        Invoke-WebRequest -Uri $SumsUrl -OutFile $SumsPath -UseBasicParsing
        $ExpectedLine = Get-Content $SumsPath | Where-Object { $_ -match [regex]::Escape($Archive) }
        if ($ExpectedLine) {
            $Expected = ($ExpectedLine -split '\s+')[0].ToLower()
            $Actual = (Get-FileHash $ArchivePath -Algorithm SHA256).Hash.ToLower()
            if ($Expected -ne $Actual) {
                Write-Error "Checksum verification FAILED!`nExpected: $Expected`nActual:   $Actual"
                exit 1
            }
            Write-Host "  Checksum OK"
        }
    } catch {
        Write-Warning "Could not verify checksum (SHA256SUMS.txt unavailable)"
    }

    # Extract
    Expand-Archive -Path $ArchivePath -DestinationPath $TmpDir -Force
    $ExtractedBinary = Get-ChildItem -Path $TmpDir -Recurse -Filter $Binary | Select-Object -First 1

    if (-not $ExtractedBinary) {
        Write-Error "Could not find $Binary in archive"
        exit 1
    }

    Copy-Item $ExtractedBinary.FullName (Join-Path $InstallDir $Binary) -Force

} finally {
    Remove-Item -Path $TmpDir -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "AVM $Latest installed successfully!"
Write-Host ""
Write-Host "  Binary: $InstallDir\$Binary"
Write-Host ""

# Add to PATH for current user if not already there
$CurrentPath = [System.Environment]::GetEnvironmentVariable("PATH", "User")
if ($CurrentPath -notlike "*$InstallDir*") {
    $NewPath = "$InstallDir;$CurrentPath"
    [System.Environment]::SetEnvironmentVariable("PATH", $NewPath, "User")
    Write-Host "Added $InstallDir to your user PATH."
    Write-Host "Restart your terminal to use avm."
} else {
    Write-Host "PATH already includes $InstallDir"
}

Write-Host ""
Write-Host "Get started:"
Write-Host "  avm --help"
Write-Host "  avm available node --lts"
Write-Host "  avm install node@22"
