<#
.SYNOPSIS
    Installs and syncs the Investment Tools plugin and skills suite into Antigravity globally.
#>
param (
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Installing Investment Tools Suite for Antigravity" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Repository Root: $RepoRoot`n"

# 1. Global Plugin Registration (Physical Mirror Deployment)
# Note: Antigravity's Go runtime ignores NTFS directory junctions on Windows, so we deploy a clean mirror.
$PluginsDir = Join-Path $HOME ".gemini\config\plugins"
if (-not (Test-Path $PluginsDir)) {
    New-Item -ItemType Directory -Path $PluginsDir -Force | Out-Null
}
$PluginTarget = Join-Path $PluginsDir "investment-tools"

# Clean up reparse point / junction if present from older installations
$existing = Get-Item $PluginTarget -ErrorAction SilentlyContinue
if ($existing -and ($existing.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
    cmd /c "rmdir `"$PluginTarget`""
}

Write-Host "[*] Deploying plugin mirror to: $PluginTarget" -ForegroundColor Yellow
robocopy "$RepoRoot" "$PluginTarget" /MIR /XD .git .contextune scratch reports __pycache__ /XF *.pyc *.log /NFL /NDL /NJH /NJS /nc /ns /np | Out-Null
if ($LASTEXITCODE -le 7) {
    Write-Host "[OK] Plugin files synced successfully!" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Robocopy finished with exit code $LASTEXITCODE" -ForegroundColor Yellow
}

# 2. Clean up legacy skill junctions if any
$SkillsDir = Join-Path $HOME ".gemini\config\skills"
if (Test-Path $SkillsDir) {
    foreach ($sk in @("portfolio-tracker", "stock-deep-dive", "deep-value-hunter")) {
        $skPath = Join-Path $SkillsDir $sk
        $skItem = Get-Item $skPath -ErrorAction SilentlyContinue
        if ($skItem -and ($skItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint)) {
            cmd /c "rmdir `"$skPath`""
        }
    }
}

# 3. Enable in Antigravity Configuration
$ConfigFile = Join-Path $HOME ".gemini\config\config.json"
try {
    if (Test-Path $ConfigFile) {
        $cfg = Get-Content $ConfigFile -Raw | ConvertFrom-Json
        if (-not $cfg.plugins) {
            $cfg | Add-Member -MemberType NoteProperty -Name "plugins" -Value ([PSCustomObject]@{})
        }
        if (-not $cfg.plugins."investment-tools" -or -not $cfg.plugins."investment-tools".enabled) {
            $cfg.plugins | Add-Member -MemberType NoteProperty -Name "investment-tools" -Value ([PSCustomObject]@{ enabled = $true }) -Force
            $cfg | ConvertTo-Json -Depth 20 | Set-Content $ConfigFile -Encoding UTF8
            Write-Host "[OK] Enabled 'investment-tools' in ~/.gemini/config/config.json" -ForegroundColor Green
        } else {
            Write-Host "[OK] 'investment-tools' is already enabled in config.json" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "[WARNING] Could not update config.json: $_" -ForegroundColor Yellow
}

Write-Host "`n[SUCCESS] Investment Tools installed and active!" -ForegroundColor Cyan
Write-Host "Discovered Skills:" -ForegroundColor Cyan
Write-Host "  - /portfolio-tracker  (Ghostfolio telemetry, container management, holdings)" -ForegroundColor White
Write-Host "  - /stock-deep-dive    (Fundamental equity valuation, GARP, 10-K analysis)" -ForegroundColor White
Write-Host "  - /deep-value-hunter  (Quantitative Graham & Schloss screener, net-nets)" -ForegroundColor White
