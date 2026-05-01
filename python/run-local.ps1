<#
.SYNOPSIS
  Mirror GitHub Actions steps locally: pip install, materialize credentials, run scripts.

.DESCRIPTION
  Matches .github/workflows/remote-switch-*.yml behavior.

  -EnvFile must be the script produced by secrets/build_env.py (default: secrets\env.ps1).
  Dot-sourcing runs $env:KEY = '...' assignments. Missing or wrong secrets show up as Python errors.

.PARAMETER Task
  MakeCalls | SendEmail | SyncWithToku | Both

.PARAMETER SkipPip
  Skip pip install (faster reruns)

.PARAMETER EnvFile
  Path to secrets/env.ps1 from build_env.py (required).

.EXAMPLE
  .\run-local.ps1 -Task MakeCalls -EnvFile secrets\env.ps1

.EXAMPLE
  .\run-local.ps1 -Task SendEmail -EnvFile C:\Work\remote_switch\python\secrets\env.ps1 -SkipPip

.EXAMPLE
  .\run-local.ps1 -Task SyncWithToku -EnvFile secrets\env.ps1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("MakeCalls", "SendEmail", "SyncWithToku", "Both")]
    [string] $Task,

    [switch] $SkipPip,

    [Parameter(Mandatory = $true)]
    [string] $EnvFile
)

$ErrorActionPreference = "Stop"
$PythonDir = $PSScriptRoot
Set-Location $PythonDir

if (-not (Test-Path -LiteralPath $EnvFile)) {
    throw "Secrets script not found: $EnvFile (run: python secrets/build_env.py)"
}
Write-Host "Dot-sourcing: $EnvFile"
. (Resolve-Path -LiteralPath $EnvFile)

if (-not $SkipPip) {
    Write-Host "pip install -r requirements.txt"
    python -m pip install -r requirements.txt
}

$runMakeCalls = $Task -eq "MakeCalls" -or $Task -eq "Both"
$runSendEmail = $Task -eq "SendEmail" -or $Task -eq "Both"
$runSyncWithToku = $Task -eq "SyncWithToku" -or $Task -eq "Both"

if ($runMakeCalls) {
    Write-Host "python make_calls.py"
    python make_calls.py
}

if ($runSendEmail) {
    Write-Host "python send_weekly_report.py"
    python send_weekly_report.py
}

if ($runSyncWithToku) {
    Write-Host "python sync_with_toku.py"
    python sync_with_toku.py
}

Write-Host "Done."
