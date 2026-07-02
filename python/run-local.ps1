<#
.SYNOPSIS
  Mirror GitHub Actions steps locally: pip install, materialize credentials, run scripts.

.DESCRIPTION
  Matches .github/workflows/remote-switch-*.yml behavior.

  -EnvFile must be the script produced by secrets/build_env.py (default: secrets\env.ps1).
  Dot-sourcing runs $env:KEY = '...' assignments. Missing or wrong secrets show up as Python errors.

.PARAMETER Task
  MakeCalls | SendEmail | SyncWithToku | ExplainCustomer | ExplainLastTwilioDigit | Both

.PARAMETER CustomerNumber
  Required for ExplainCustomer: Toku / Firebase client number (# Cliente).

.PARAMETER PhoneNumber
  Required for ExplainLastTwilioDigit: switch phone number.

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

.EXAMPLE
  .\run-local.ps1 -Task ExplainCustomer -CustomerNumber 12345 -EnvFile secrets\env.ps1

.EXAMPLE
  .\run-local.ps1 -Task ExplainLastTwilioDigit -PhoneNumber +528711234567 -EnvFile secrets\env.ps1
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("MakeCalls", "SendEmail", "SyncWithToku", "ExplainCustomer", "ExplainLastTwilioDigit", "Both")]
    [string] $Task,

    [switch] $SkipPip,

    [Parameter(Mandatory = $true)]
    [string] $EnvFile,

    [string] $CustomerNumber = "",

    [string] $PhoneNumber = ""
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

if ($Task -eq "ExplainCustomer") {
    if (-not $CustomerNumber.Trim()) {
        throw "ExplainCustomer requires -CustomerNumber (Toku / Firebase # Cliente)."
    }
    Write-Host "python explain_customer_invoices.py $CustomerNumber"
    python explain_customer_invoices.py $CustomerNumber
}

if ($Task -eq "ExplainLastTwilioDigit") {
    if (-not $PhoneNumber.Trim()) {
        throw "ExplainLastTwilioDigit requires -PhoneNumber."
    }
    Write-Host "python explain_last_twilio_digit.py $PhoneNumber"
    python explain_last_twilio_digit.py $PhoneNumber
}

Write-Host "Done."
