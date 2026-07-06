#!/usr/bin/env python3
"""Install the repository skill snapshot into the local Codex skills folder."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = Path.home() / ".codex" / "skills"
INSTALLERS_CONFIG = REPO_ROOT / "skills-installers.json"


def load_installers() -> dict[str, object]:
    if not INSTALLERS_CONFIG.is_file():
        return {"skills": {}}
    return json.loads(INSTALLERS_CONFIG.read_text(encoding="utf-8-sig"))


def resolved_install_command(entry: dict[str, object]) -> str:
    command = str(entry.get("installCommand", ""))
    managed_names = entry.get("managedSkillNames", [])
    if isinstance(managed_names, list):
        csv = ",".join(str(name) for name in managed_names)
        command = command.replace("{managedSkillNamesCsv}", csv)
    return command


def copy_skill(source_dir: Path, destination_root: Path) -> None:
    destination = destination_root / source_dir.name
    destination.mkdir(parents=True, exist_ok=True)

    for item in source_dir.iterdir():
        target = destination / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install skills from this repository into ~/.codex/skills."
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help="Destination skills directory. Defaults to ~/.codex/skills.",
    )
    parser.add_argument(
        "--run-installers",
        action="store_true",
        help="Run package-manager install commands from skills-installers.json.",
    )
    args = parser.parse_args()

    source = REPO_ROOT / "skills"
    if not source.is_dir():
        raise SystemExit(f"Cannot find skills snapshot: {source}")

    args.destination.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(path for path in source.iterdir() if path.is_dir()):
        copy_skill(skill_dir, args.destination)
        print(f"Installed skill: {skill_dir.name}")

    installers = load_installers()
    skills = installers.get("skills", {})
    installer_commands = []
    if isinstance(skills, dict):
        for name, entry in sorted(skills.items()):
            if not isinstance(entry, dict):
                continue
            command = resolved_install_command(entry)
            if command:
                display_command = str(entry.get("displayInstallCommand") or command)
                installer_commands.append((str(name), command, display_command))

    if installer_commands:
        print("\nPackage-managed skills:")
        for name, command, display_command in installer_commands:
            if args.run_installers:
                print(f"Running installer for {name}: {command}")
                subprocess.run(command, shell=True, check=True)
            else:
                print(f"  {name}: {display_command}")
        if not args.run_installers:
            print("Run again with --run-installers to execute these commands.")

    print("Done. Restart Codex so it reloads installed skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
