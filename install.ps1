#Requires -Version 5.1
<#
.SYNOPSIS
    Install RPG Maker Agent Skills for Claude Code, Codex, and Cursor.
.DESCRIPTION
    Downloads and installs the rpgmaker-agent-skills pack into your
    agent's skills directory. Installs both skills/ (for agent invocation)
    and scripts/ (Python helper scripts for validation, dialog, etc.).
.PARAMETER Version
    Release version to install. Default: "latest" (main branch).
.EXAMPLE
    .\install.ps1
    .\install.ps1 -Version "v1.0.0"
#>
param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

$Repo = "nightquill/rpgmaker-agent-skills"

Write-Host "RPG Maker Agent Skills Installer"
Write-Host ""
Write-Host "Install location:"
Write-Host "  1) Global: ~/.claude/skills/ (default)"
Write-Host "  2) Local:  ./.claude/skills/ (current project)"
Write-Host ""

$Choice = Read-Host "Choose [1/2]"

if ($Choice -eq "2") {
    $BaseDir = Join-Path (Get-Location).Path ".claude"
} else {
    $BaseDir = Join-Path $env:USERPROFILE ".claude"
}

$SkillsTarget = Join-Path $BaseDir "skills"
$ScriptsTarget = Join-Path $BaseDir "rpgmaker-scripts"

# Build download URL
if ($Version -eq "latest") {
    $Url = "https://github.com/$Repo/archive/refs/heads/main.zip"
} else {
    $Url = "https://github.com/$Repo/archive/refs/tags/$Version.zip"
}

# Create temp directory
$TmpDir = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null

try {
    Write-Host ""
    Write-Host "Downloading from $Url..."

    $ZipPath = Join-Path $TmpDir "pack.zip"
    Invoke-WebRequest -Uri $Url -OutFile $ZipPath -UseBasicParsing

    Write-Host "Extracting..."
    $ExtractDir = Join-Path $TmpDir "extracted"
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractDir -Force

    # The archive extracts to a subdirectory named <repo>-<branch>
    # Get that directory
    $ExtractedRoot = Get-ChildItem -Path $ExtractDir -Directory | Select-Object -First 1

    if (-not $ExtractedRoot) {
        Write-Error "Failed to find extracted content in archive."
        exit 1
    }

    $PackRoot = $ExtractedRoot.FullName

    # Install skills
    if (-not (Test-Path $SkillsTarget)) {
        New-Item -ItemType Directory -Path $SkillsTarget -Force | Out-Null
    }
    $SkillsSource = Join-Path $PackRoot "skills"
    Copy-Item -Path (Join-Path $SkillsSource "*") -Destination $SkillsTarget -Recurse -Force
    Write-Host "Installed skills to: $SkillsTarget"

    # Install scripts and schemas
    if (-not (Test-Path $ScriptsTarget)) {
        New-Item -ItemType Directory -Path $ScriptsTarget -Force | Out-Null
    }
    $ScriptsSource = Join-Path $PackRoot "scripts"
    $SchemasSource = Join-Path $PackRoot "schemas"
    Copy-Item -Path $ScriptsSource -Destination $ScriptsTarget -Recurse -Force
    Copy-Item -Path $SchemasSource -Destination $ScriptsTarget -Recurse -Force
    Write-Host "Installed scripts to: $(Join-Path $ScriptsTarget 'scripts')"
    Write-Host "Installed schemas to: $(Join-Path $ScriptsTarget 'schemas')"

    Write-Host ""
    Write-Host "Done! Restart your agent to pick up the new skills."
    Write-Host ""
    Write-Host "To use helper scripts:"
    Write-Host "  cd $ScriptsTarget; `$env:PYTHONPATH='.'; python scripts/validate_project.py --project C:\path\to\your\project"
    Write-Host ""
    Write-Host "Available skills:"
    Get-ChildItem -Path $SkillsTarget -Directory -Filter "rpgmaker-*" | ForEach-Object {
        Write-Host "  - $($_.Name)"
    }

} finally {
    # Clean up temp directory
    if (Test-Path $TmpDir) {
        Remove-Item -Path $TmpDir -Recurse -Force
    }
}
