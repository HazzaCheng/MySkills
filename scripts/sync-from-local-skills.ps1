param(
  [string]$SkillsRoot = "$env:USERPROFILE\.codex\skills",
  [switch]$Commit,
  [switch]$Push,
  [string]$Message = "Sync Codex skills"
)

$ErrorActionPreference = 'Stop'
$RepoRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Snapshot = Join-Path $RepoRoot 'skills'

if (-not (Test-Path -LiteralPath $SkillsRoot)) {
  throw "Cannot find Codex skills root: $SkillsRoot"
}

New-Item -ItemType Directory -Force -Path $Snapshot | Out-Null

Get-ChildItem -LiteralPath $Snapshot -Directory | Remove-Item -Recurse -Force
$SkillDirs = Get-ChildItem -LiteralPath $SkillsRoot -Directory | Where-Object { $_.Name -ne '.system' } | Sort-Object Name

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
  note = 'This repository snapshots non-system Codex skills from ~/.codex/skills. System and plugin-provided skills are intentionally not copied.'
  skillCount = $Items.Count
  skills = $Items
}

$Manifest | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $RepoRoot 'skills-manifest.json') -Encoding UTF8

$Rows = ($Items | ForEach-Object { "| $($_.folder) | $($_.name) | $($_.description.Replace('|','/')) |" }) -join "`r`n"
$Readme = @"
# MySkills

Personal Codex skills installed on this Windows machine.

This repo is a migration record and backup for the non-system skills currently under:

```text
$SkillsRoot
```

## What is included

- `skills/`: a snapshot of each user-installed skill folder.
- `skills-manifest.json`: machine-readable inventory generated from local `SKILL.md` files.
- `scripts/install-local-skills.ps1`: helper script for restoring these skills on a new Windows machine.
- `scripts/sync-from-local-skills.ps1`: helper script for refreshing this repo after installing new skills.

System skills under `.system` and plugin-provided skills are not copied here, because Codex/plugins should provide those again on a new machine.

## Restore on a new Windows machine

From this repo root, run PowerShell:

```powershell
.\scripts\install-local-skills.ps1
```

The script copies every folder in `skills/` into:

```text
%USERPROFILE%\.codex\skills
```

## Update this repo after installing new skills

From this repo root, run:

```powershell
.\scripts\sync-from-local-skills.ps1 -Commit -Push
```

## Skill Inventory

Count: $($Items.Count)

| Folder | Skill name | Description |
|---|---|---|
$Rows
"@
Set-Content -LiteralPath (Join-Path $RepoRoot 'README.md') -Value $Readme -Encoding UTF8

Write-Host "Synced $($Items.Count) skills from $SkillsRoot"

if ($Commit) {
  git -C $RepoRoot add README.md skills-manifest.json scripts skills
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
