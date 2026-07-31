<#
.SYNOPSIS
    Generate placeholder Cowork plugin icons: color.png (192x192) and outline.png
    (32x32, transparent). Branded with an accent color and a simple document glyph.

.PARAMETER PluginDir
    Folder to write color.png and outline.png into.

.PARAMETER AccentColor
    Hex color for the color.png background (default Microsoft blue #0078D4).

.EXAMPLE
    ./new-icons.ps1 -PluginDir "C:\repo\plugin\my-toolkit" -AccentColor "#0078D4"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string] $PluginDir,
    [string] $AccentColor = '#0078D4'
)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing | Out-Null
$PluginDir = (Resolve-Path $PluginDir).Path
$accent = [System.Drawing.ColorTranslator]::FromHtml($AccentColor)

function New-RoundedPath([int]$x,[int]$y,[int]$w,[int]$h,[int]$r){
    $p = New-Object System.Drawing.Drawing2D.GraphicsPath
    $d = $r * 2
    $p.AddArc($x, $y, $d, $d, 180, 90)
    $p.AddArc($x + $w - $d, $y, $d, $d, 270, 90)
    $p.AddArc($x + $w - $d, $y + $h - $d, $d, $d, 0, 90)
    $p.AddArc($x, $y + $h - $d, $d, $d, 90, 90)
    $p.CloseFigure()
    return $p
}

# ---- color.png 192x192 ----
$bmp = New-Object System.Drawing.Bitmap 192,192
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$g.Clear([System.Drawing.Color]::Transparent)
$g.FillPath((New-Object System.Drawing.SolidBrush $accent), (New-RoundedPath 8 8 176 176 34))
$g.FillPath([System.Drawing.Brushes]::White, (New-RoundedPath 58 44 76 104 10))
$pen = New-Object System.Drawing.Pen $accent, 7
$pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.EndCap   = [System.Drawing.Drawing2D.LineCap]::Round
foreach ($y in 66,84,102,120) { $g.DrawLine($pen, 72, $y, 120, $y) }
$g.Dispose()
$bmp.Save((Join-Path $PluginDir 'color.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

# ---- outline.png 32x32 (white on transparent) ----
$o = New-Object System.Drawing.Bitmap 32,32
$go = [System.Drawing.Graphics]::FromImage($o)
$go.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$go.Clear([System.Drawing.Color]::Transparent)
$wpen = New-Object System.Drawing.Pen ([System.Drawing.Color]::White), 2.2
$wpen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
$go.DrawPath($wpen, (New-RoundedPath 8 5 16 22 3))
$lp = New-Object System.Drawing.Pen ([System.Drawing.Color]::White), 1.8
$lp.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$lp.EndCap   = [System.Drawing.Drawing2D.LineCap]::Round
foreach ($y in 11,16,21) { $go.DrawLine($lp, 12, $y, 20, $y) }
$go.Dispose()
$o.Save((Join-Path $PluginDir 'outline.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$o.Dispose()

Write-Host "Icons written to $PluginDir : color.png (192x192), outline.png (32x32)"
