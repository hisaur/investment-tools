<#
.SYNOPSIS
    Installs the Investment Tools plugin and skills suite into Antigravity globally.
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

# 1. Global Plugin Registration
$PluginsDir = Join-Path $HOME ".gemini\config\plugins"
if (-not (Test-Path $PluginsDir)) {
    New-Item -ItemType Directory -Path $PluginsDir -Force | Out-Null
}
$PluginTarget = Join-Path $PluginsDir "investment-tools"

if (Test-Path $PluginTarget) {
    Write-Host "[OK] Plugin link already exists at: $PluginTarget" -ForegroundColor Green
} else {
    Write-Host "[*] Creating plugin junction: $PluginTarget -> $RepoRoot" -ForegroundColor Yellow
    New-Item -ItemType Junction -Path $PluginTarget -Target $RepoRoot | Out-Null
    Write-Host "[OK] Plugin registered successfully!" -ForegroundColor Green
}

# 2. Individual Skills Registration (Dual Discovery)
$SkillsDir = Join-Path $HOME ".gemini\config\skills"
if (-not (Test-Path $SkillsDir)) {
    New-Item -ItemType Directory -Path $SkillsDir -Force | Out-Null
}

$Skills = @("portfolio-tracker", "stock-deep-dive", "deep-value-hunter")
foreach ($skill in $Skills) {
    $src = Join-Path $RepoRoot "skills\$skill"
    $dest = Join-Path $SkillsDir $skill
    if (Test-Path $dest) {
        Write-Host "[OK] Skill '$skill' already linked at: $dest" -ForegroundColor Green
    } else {
        if (Test-Path $src) {
            Write-Host "[*] Linking skill '$skill' -> $dest" -ForegroundColor Yellow
            New-Item -ItemType Junction -Path $dest -Target $src | Out-Null
            Write-Host "[OK] Skill '$skill' linked successfully!" -ForegroundColor Green
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
        if (-not $cfg.plugins."investment-tools") {
            $cfg.plugins | Add-Member -MemberType NoteProperty -Name "investment-tools" -Value ([PSCustomObject]@{ enabled = $true })
            $cfg | ConvertTo-Json -Depth 20 | Set-Content $ConfigFile -Encoding UTF8
            Write-Host "[OK] Enabled 'investment-tools' in ~/.gemini/config/config.json" -ForegroundColor Green
        } else {
            Write-Host "[OK] 'investment-tools' is already enabled in config.json" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "[WARNING] Could not update config.json: $_" -ForegroundColor Yellow
}

Write-Host "`n[SUCCESS] Investment Tools installation complete!" -ForegroundColor Cyan
Write-Host "Note: Antigravity caches the global skill catalog at IDE startup." -ForegroundColor Yellow
Write-Host "If running inside an active Antigravity session, restart the IDE or open a new window to reload." -ForegroundColor Yellow
