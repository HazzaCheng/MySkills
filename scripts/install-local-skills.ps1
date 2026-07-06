param(
  [string]$Destination = "$env:USERPROFILE\.codex\skills",
  [switch]$RunInstallers
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Source = Join-Path $RepoRoot 'skills'
$InstallersConfig = Join-Path $RepoRoot 'skills-installers.json'

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

if (Test-Path -LiteralPath $InstallersConfig) {
  $InstallerConfigJson = Get-Content -LiteralPath $InstallersConfig -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($InstallerConfigJson.skills) {
    Write-Host ''
    Write-Host 'Package-managed skills:'
    foreach ($installer in ($InstallerConfigJson.skills.PSObject.Properties | Sort-Object Name)) {
      $managedCsv = ''
      if ($installer.Value.managedSkillNames) {
        $managedCsv = (@($installer.Value.managedSkillNames | ForEach-Object { [string]$_ }) -join ',')
      }
      $command = ([string]$installer.Value.installCommand).Replace('{managedSkillNamesCsv}', $managedCsv)
      if ($RunInstallers) {
        Write-Host "Running installer for $($installer.Name): $command"
        Invoke-Expression $command
      } else {
        $displayCommand = $command
        if ($installer.Value.displayInstallCommand) {
          $displayCommand = [string]$installer.Value.displayInstallCommand
        }
        Write-Host "  $($installer.Name): $displayCommand"
      }
    }
    if (-not $RunInstallers) {
      Write-Host 'Run again with -RunInstallers to execute these commands.'
    }
  }
}

Write-Host "Done. Restart Codex so it reloads installed skills."
