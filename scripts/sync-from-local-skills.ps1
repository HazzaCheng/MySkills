param(
  [string]$SkillsRoot = "$env:USERPROFILE\.codex\skills",
  [switch]$Commit,
  [switch]$Push,
  [string]$Message = "Sync Codex skills"
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Snapshot = Join-Path $RepoRoot 'skills'
$InstallersConfig = Join-Path $RepoRoot 'skills-installers.json'

function Set-Utf8NoBomContent {
  param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Value
  )

  $Utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Value, $Utf8NoBom)
}

if (-not (Test-Path -LiteralPath $SkillsRoot)) {
  throw "Cannot find Codex skills root: $SkillsRoot"
}

New-Item -ItemType Directory -Force -Path $Snapshot | Out-Null

$PackageManagedSkillNames = @()
if (Test-Path -LiteralPath $InstallersConfig) {
  $InstallerConfigJson = Get-Content -LiteralPath $InstallersConfig -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($InstallerConfigJson.skills) {
    $PackageManagedSkillNames = @($InstallerConfigJson.skills.PSObject.Properties.Name)
  }
}

Get-ChildItem -LiteralPath $Snapshot -Directory | Remove-Item -Recurse -Force
$SkillDirs = Get-ChildItem -LiteralPath $SkillsRoot -Directory | Where-Object {
  $_.Name -ne '.system' -and $PackageManagedSkillNames -notcontains $_.Name
} | Sort-Object Name

foreach ($dir in $SkillDirs) {
  $dest = Join-Path $Snapshot $dir.Name
  New-Item -ItemType Directory -Force -Path $dest | Out-Null
  Get-ChildItem -LiteralPath $dir.FullName -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $dest -Recurse -Force
  }
}

$Items = @()
foreach ($dir in $SkillDirs) {
  $skillMd = Join-Path $dir.FullName 'SKILL.md'
  $name = $dir.Name
  $description = ''

  if (Test-Path -LiteralPath $skillMd) {
    $raw = Get-Content -LiteralPath $skillMd -Raw -Encoding UTF8
    $nameMatch = [regex]::Match($raw, '(?m)^name:\s*(.+?)\s*$')
    if ($nameMatch.Success) { $name = $nameMatch.Groups[1].Value.Trim().Trim('"') }

    $descMatch = [regex]::Match($raw, '(?ms)^description:\s*(.+?)(?:\r?\n---|\r?\n[a-zA-Z_-]+:)')
    if ($descMatch.Success) { $description = ($descMatch.Groups[1].Value.Trim() -replace '\s+', ' ').Trim('"') }
  }

  $size = (Get-ChildItem -LiteralPath $dir.FullName -Recurse -Force | Measure-Object -Property Length -Sum).Sum
  $Items += [pscustomobject]@{
    folder = $dir.Name
    name = $name
    description = $description
    snapshotPath = "skills/$($dir.Name)"
    hasSkillMd = (Test-Path -LiteralPath $skillMd)
    sizeBytes = [int64]$size
  }
}

$Manifest = [pscustomobject]@{
  generatedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')
  sourceComputer = $env:COMPUTERNAME
  sourceRoot = $SkillsRoot
  note = 'This repository snapshots non-system user skills, usually from ~/.codex/skills. Package-managed skills listed in skills-installers.json are intentionally not copied. System and plugin-provided skills are intentionally not copied.'
  skillCount = $Items.Count
  skills = $Items
}

$ManifestJson = $Manifest | ConvertTo-Json -Depth 6
Set-Utf8NoBomContent -Path (Join-Path $RepoRoot 'skills-manifest.json') -Value $ManifestJson

$InstallerRows = ''
if ($InstallerConfigJson -and $InstallerConfigJson.skills) {
  $InstallerRows = ($InstallerConfigJson.skills.PSObject.Properties | Sort-Object Name | ForEach-Object {
    $command = [string]$_.Value.installCommand
    $note = [string]$_.Value.notes
    if ($_.Value.auth -and $_.Value.auth.env) {
      $note = "Set ``$($_.Value.auth.env)`` locally after install."
    }
    "| $($_.Name) | ``$command`` | $note |"
  }) -join "`r`n"
}

$Rows = ($Items | ForEach-Object { "| $($_.folder) | $($_.name) | $($_.description.Replace('|','/')) |" }) -join "`r`n"
$ReadmeTemplate = @'
# MySkills

Personal Codex skills shared across Windows and macOS machines.

This repo is a migration record and backup for non-system skills normally stored under:

~~~text
~/.codex/skills
~~~

On Windows this usually resolves to `%USERPROFILE%\.codex\skills`. On macOS it resolves to `$HOME/.codex/skills`.

## What is included

- `skills/`: a snapshot of each user-installed skill folder.
- `skills-manifest.json`: machine-readable inventory generated from local `SKILL.md` files.
- `skills-installers.json`: install recipes for package-managed skills that should not be copied from old machines.
- `scripts/install-local-skills.py`: cross-platform restore script for Windows and macOS.
- `scripts/sync-from-local-skills.py`: cross-platform sync script for Windows and macOS.
- `scripts/*.ps1`: legacy Windows PowerShell helpers kept for convenience.

System skills under `.system` and plugin-provided skills are not copied here, because Codex/plugins should provide those again on each machine.

## Restore on a machine

From this repo root, run one of:

~~~bash
python3 scripts/install-local-skills.py
~~~

~~~powershell
py -3 scripts\install-local-skills.py
~~~

The script copies every folder in `skills/` into `~/.codex/skills`.

Package-managed skills listed in `skills-installers.json` are installed from their package command instead of copied from this repo. Current installer-backed skills:

| Skill | Install command | Notes |
|---|---|---|
__INSTALLER_ROWS__

## Update this repo after installing new skills

From this repo root, run one of:

~~~bash
python3 scripts/sync-from-local-skills.py --commit --push
~~~

~~~powershell
py -3 scripts\sync-from-local-skills.py --commit --push
~~~

For skills installed through package runners, for example:

~~~bash
npx skills add Tencent/WeChatReading -g
~~~

add them to `skills-installers.json` instead of committing the installed `SKILL.md` files. The command is the restore path for new machines. Do not commit credentials or API keys; keep them in local environment variables.

All generated text files are written as UTF-8 without BOM so both macOS/Linux tools and Windows terminals can read them cleanly.

## Skill Inventory

Count: __SKILL_COUNT__

| Folder | Skill name | Description |
|---|---|---|
__SKILL_ROWS__
'@
$Readme = $ReadmeTemplate.Replace('__SKILL_COUNT__', [string]$Items.Count).Replace('__SKILL_ROWS__', $Rows).Replace('__INSTALLER_ROWS__', $InstallerRows)
Set-Utf8NoBomContent -Path (Join-Path $RepoRoot 'README.md') -Value $Readme

Write-Host "Synced $($Items.Count) skills from $SkillsRoot"

if ($Commit) {
  git -C $RepoRoot add README.md skills-manifest.json skills-installers.json skills-upstreams.json scripts skills
  $changes = git -C $RepoRoot status --short
  if ($changes) {
    git -C $RepoRoot commit -m $Message
  } else {
    Write-Host 'No git changes to commit.'
  }
}

if ($Push) {
  git -C $RepoRoot push origin HEAD
}
