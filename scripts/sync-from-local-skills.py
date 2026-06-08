#!/usr/bin/env python3
"""Refresh this repository from the local Codex skills folder.

The script intentionally writes UTF-8 without BOM so the snapshot is friendly to
macOS/Linux tools and modern Windows terminals.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path.home() / ".codex" / "skills"
SKILL_BLOCK_RE = re.compile(
    r"(?ms)^description:\s*(.+?)(?:\r?\n---|\r?\n[a-zA-Z_-]+:)"
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8", newline="\n")


def copy_snapshot(source_root: Path, snapshot_root: Path) -> list[Path]:
    if source_root.resolve() == snapshot_root.resolve():
        raise SystemExit("Source skills root cannot be the repository skills snapshot.")

    snapshot_root.mkdir(parents=True, exist_ok=True)
    for existing in snapshot_root.iterdir():
        if existing.is_dir():
            shutil.rmtree(existing)

    skill_dirs = sorted(
        path for path in source_root.iterdir() if path.is_dir() and path.name != ".system"
    )
    for skill_dir in skill_dirs:
        shutil.copytree(skill_dir, snapshot_root / skill_dir.name)

    return skill_dirs


def parse_skill(skill_dir: Path, snapshot_dir: Path) -> dict[str, object]:
    skill_md = skill_dir / "SKILL.md"
    name = skill_dir.name
    description = ""

    if skill_md.is_file():
        raw = read_text(skill_md)
        name_match = re.search(r"(?m)^name:\s*(.+?)\s*$", raw)
        if name_match:
            name = name_match.group(1).strip().strip('"')

        desc_match = SKILL_BLOCK_RE.search(raw)
        if desc_match:
            description = re.sub(r"\s+", " ", desc_match.group(1).strip()).strip('"')

    size = sum(path.stat().st_size for path in skill_dir.rglob("*") if path.is_file())
    return {
        "folder": skill_dir.name,
        "name": name,
        "description": description,
        "snapshotPath": f"skills/{skill_dir.name}",
        "hasSkillMd": skill_md.is_file(),
        "sizeBytes": size,
    }


def build_readme(manifest: dict[str, object]) -> str:
    rows = []
    for item in manifest["skills"]:
        description = str(item["description"]).replace("|", "/")
        rows.append(f"| {item['folder']} | {item['name']} | {description} |")

    return f"""# MySkills

Personal Codex skills shared across Windows and macOS machines.

This repo is a migration record and backup for non-system skills normally stored under:

```text
~/.codex/skills
```

On Windows this usually resolves to `%USERPROFILE%\\.codex\\skills`. On macOS it resolves to `$HOME/.codex/skills`.

## What is included

- `skills/`: a snapshot of each user-installed skill folder.
- `skills-manifest.json`: machine-readable inventory generated from local `SKILL.md` files.
- `scripts/install-local-skills.py`: cross-platform restore script for Windows and macOS.
- `scripts/sync-from-local-skills.py`: cross-platform sync script for Windows and macOS.
- `scripts/*.ps1`: legacy Windows PowerShell helpers kept for convenience.

System skills under `.system` and plugin-provided skills are not copied here, because Codex/plugins should provide those again on each machine.

## Restore on a machine

From this repo root, run one of:

```bash
python3 scripts/install-local-skills.py
```

```powershell
py -3 scripts\\install-local-skills.py
```

The script copies every folder in `skills/` into `~/.codex/skills`.

## Update this repo after installing new skills

From this repo root, run one of:

```bash
python3 scripts/sync-from-local-skills.py --commit --push
```

```powershell
py -3 scripts\\sync-from-local-skills.py --commit --push
```

All generated text files are written as UTF-8 without BOM so both macOS/Linux tools and Windows terminals can read them cleanly.

## Skill Inventory

Count: {manifest["skillCount"]}

| Folder | Skill name | Description |
|---|---|---|
{chr(10).join(rows)}
"""


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(REPO_ROOT), *args],
        check=True,
        text=True,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync non-system Codex skills into this repository."
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Source skills directory. Defaults to ~/.codex/skills.",
    )
    parser.add_argument("--commit", action="store_true", help="Commit changes after sync.")
    parser.add_argument("--push", action="store_true", help="Push HEAD after sync.")
    parser.add_argument("--message", default="Sync Codex skills", help="Commit message.")
    args = parser.parse_args()

    if not args.source.is_dir():
        raise SystemExit(f"Cannot find Codex skills root: {args.source}")

    snapshot = REPO_ROOT / "skills"
    source_dirs = copy_snapshot(args.source, snapshot)
    items = [
        parse_skill(source_dir, snapshot / source_dir.name) for source_dir in source_dirs
    ]

    manifest = {
        "generatedAt": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "sourceComputer": os.environ.get("COMPUTERNAME") or socket.gethostname(),
        "sourceRoot": str(args.source),
        "note": "This repository snapshots non-system Codex skills from ~/.codex/skills. System and plugin-provided skills are intentionally not copied.",
        "skillCount": len(items),
        "skills": items,
    }

    write_text(REPO_ROOT / "skills-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write_text(REPO_ROOT / "README.md", build_readme(manifest))

    print(f"Synced {len(items)} skills from {args.source}")

    if args.commit:
        run_git(["add", "README.md", "skills-manifest.json", "scripts", "skills"])
        status = run_git(["status", "--short"]).stdout.strip()
        if status:
            run_git(["commit", "-m", args.message])
        else:
            print("No git changes to commit.")

    if args.push:
        run_git(["push", "origin", "HEAD"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
