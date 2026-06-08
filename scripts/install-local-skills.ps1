param(
  [string]$Destination = "$env:USERPROFILE\.codex\skills"
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Source = Join-Path $RepoRoot 'skills'

if (-not (Test-Path -LiteralPath $Source)) {
  throw "Cannot find skills snapshot: $Source"
}

New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Get-ChildItem -LiteralPath $Source -Directory | Sort-Object Name | ForEach-Object {
  $dest = Join-Path $Destination $_.Name
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Get-ChildItem -LiteralPath $_.FullName -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $dest -Recurse -Force
  }
  Write-Host "Installed skill: $($_.Name)"
}

Write-Host "Done. Restart Codex so it reloads installed skills."
