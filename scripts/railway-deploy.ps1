# EchoTrader Railway deploy - sets secrets from .env and deploys via CLI.
# Requires: railway login (run once in an interactive terminal)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Railway = Join-Path $env:APPDATA "npm\railway.cmd"
Set-Location $ProjectRoot

function Invoke-Railway {
    param([Parameter(Mandatory)][string[]]$RailwayArgs)
    $output = & $Railway @RailwayArgs 2>&1 | Out-String
    if ($LASTEXITCODE -ne 0) {
        throw "railway $($RailwayArgs -join ' ') failed: $output"
    }
    return $output.Trim()
}

Write-Host "Checking Railway auth..."
try {
    $whoami = Invoke-Railway -RailwayArgs @("whoami")
    Write-Host "Logged in as: $whoami"
} catch {
    Write-Host "Not logged in. Open PowerShell and run: railway login"
    exit 1
}

try {
    $status = Invoke-Railway -RailwayArgs @("status")
    Write-Host $status
} catch {
    Write-Host "No linked project - creating echotrader..."
    try {
        Invoke-Railway -RailwayArgs @("init", "-n", "echotrader") | Out-Host
    } catch {
        if ($_.Exception.Message -match "trial has expired") {
            Write-Host ""
            Write-Host "Railway trial expired. Upgrade at: https://railway.com/account/plans"
            Write-Host "Then run: railway init -n echotrader"
            Write-Host "Or link an existing project: railway link -p <project-id>"
            exit 1
        }
        throw
    }
}

$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "Missing .env at $envFile"
    exit 1
}

$requiredKeys = @(
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_MODEL",
    "CMC_API_KEY",
    "DRY_RUN",
    "CORS_ORIGINS"
)
$twakKeys = @(
    "TWAK_ENABLED",
    "TWAK_ACCESS_ID",
    "TWAK_HMAC_SECRET",
    "TWAK_WALLET_PASSWORD",
    "TWAK_CHAIN",
    "TWAK_QUOTE_AMOUNT"
)

$vars = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if (-not $line -or $line.StartsWith("#")) { return }
    $idx = $line.IndexOf("=")
    if ($idx -lt 1) { return }
    $key = $line.Substring(0, $idx).Trim()
    $val = $line.Substring($idx + 1).Trim()
    if ($val) { $vars[$key] = $val }
}

$missing = $requiredKeys | Where-Object { -not $vars.ContainsKey($_) }
if ($missing.Count -gt 0) {
    if ($missing -contains "CORS_ORIGINS") {
        $vars["CORS_ORIGINS"] = "https://echotrader.vercel.app"
        $missing = $missing | Where-Object { $_ -ne "CORS_ORIGINS" }
    }
    if ($missing.Count -gt 0) {
        Write-Host "Missing required keys in .env: $($missing -join ', ')"
        exit 1
    }
}

$statusText = Invoke-Railway -RailwayArgs @("status")
if ($statusText -match "Service: None") {
    Write-Host "No service yet - running initial deploy to create one..."
    Invoke-Railway -RailwayArgs @("up", "--detach") | Out-Host
    Start-Sleep -Seconds 5
}

Write-Host "Setting Railway variables..."
foreach ($key in ($requiredKeys + $twakKeys)) {
    if (-not $vars.ContainsKey($key)) { continue }
    $val = $vars[$key]
    $val | & $Railway variable set --stdin $key 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to set $key"
    }
    Write-Host "  set $key"
}

Write-Host "Deploying..."
Invoke-Railway -RailwayArgs @("up", "--detach") | Out-Host

Write-Host "Generating public domain (if needed)..."
try {
    Invoke-Railway -RailwayArgs @("domain") | Out-Host
} catch {
    Write-Host "Domain may already exist or require dashboard setup."
}

Write-Host ""
Write-Host "Done. Check status:"
Invoke-Railway -RailwayArgs @("status") | Out-Host
Write-Host "Test health endpoint after deploy completes."