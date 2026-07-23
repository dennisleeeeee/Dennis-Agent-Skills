<#
.SYNOPSIS
    Package a M365 Copilot Cowork plugin folder into a sideload-ready .zip with
    forward-slash entry paths (Windows Compress-Archive writes backslashes, which
    Cowork's validator rejects).

.DESCRIPTION
    Zips manifest.json, color.png, outline.png, and the skills/ tree from -PluginDir
    into <PluginDir>/dist/<name>-<Version>.zip. All entries are placed at the package
    root with '/' separators.

.PARAMETER PluginDir
    The plugin bundle folder (contains manifest.json + icons + skills/).

.PARAMETER Version
    Version string used in the output file name. Defaults to the manifest 'version'.

.PARAMETER Name
    Base name for the zip. Defaults to the plugin folder's leaf name.

.EXAMPLE
    ./package-plugin.ps1 -PluginDir "C:\repo\plugin\my-toolkit" -Version 1.0.0
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $PluginDir,
    [string] $Version,
    [string] $Name
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem | Out-Null

$PluginDir = (Resolve-Path $PluginDir).Path
$manifestPath = Join-Path $PluginDir 'manifest.json'
if (-not (Test-Path $manifestPath)) { throw "manifest.json not found in $PluginDir" }
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json

if (-not $Version) { $Version = $manifest.version }
if (-not $Version) { $Version = '1.0.0' }
if (-not $Name)    { $Name = Split-Path $PluginDir -Leaf }

# Collect root files that exist
$rootFiles = @('manifest.json','color.png','outline.png') |
    Where-Object { Test-Path (Join-Path $PluginDir $_) }

$missingIcons = @('color.png','outline.png') | Where-Object { -not (Test-Path (Join-Path $PluginDir $_)) }
if ($missingIcons) { Write-Warning "Missing icon(s): $($missingIcons -join ', '). Run new-icons.ps1 first." }

$entries = @()
foreach ($f in $rootFiles) {
    $entries += [pscustomobject]@{ Path = (Join-Path $PluginDir $f); Name = $f }
}

$skillsRoot = Join-Path $PluginDir 'skills'
if (Test-Path $skillsRoot) {
    Get-ChildItem $skillsRoot -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($PluginDir.Length + 1) -replace '\\', '/'
        $entries += [pscustomobject]@{ Path = $_.FullName; Name = $rel }
    }
}

$distDir = Join-Path $PluginDir 'dist'
New-Item -ItemType Directory -Force -Path $distDir | Out-Null
$zipPath = Join-Path $distDir ("{0}-{1}.zip" -f $Name, $Version)
if (Test-Path $zipPath) { Remove-Item $zipPath -Force }

$fs = [System.IO.File]::Open($zipPath, [System.IO.FileMode]::CreateNew)
try {
    $archive = New-Object System.IO.Compression.ZipArchive($fs, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        foreach ($e in $entries) {
            $entry = $archive.CreateEntry($e.Name, [System.IO.Compression.CompressionLevel]::Optimal)
            $in  = [System.IO.File]::OpenRead($e.Path)
            $out = $entry.Open()
            $in.CopyTo($out)
            $out.Dispose(); $in.Dispose()
        }
    } finally { $archive.Dispose() }
} finally { $fs.Dispose() }

Write-Host "Packaged: $zipPath ($((Get-Item $zipPath).Length) bytes)"
$verify = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
$verify.Entries.FullName | ForEach-Object { Write-Host "  $_" }
$verify.Dispose()
