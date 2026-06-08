#!/usr/bin/env python3
"""Install the repository skill snapshot into the local Codex skills folder."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DESTINATION = Path.home() / ".codex" / "skills"


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
    args = parser.parse_args()

    source = REPO_ROOT / "skills"
    if not source.is_dir():
        raise SystemExit(f"Cannot find skills snapshot: {source}")

    args.destination.mkdir(parents=True, exist_ok=True)
    for skill_dir in sorted(path for path in source.iterdir() if path.is_dir()):
        copy_skill(skill_dir, args.destination)
        print(f"Installed skill: {skill_dir.name}")

    print("Done. Restart Codex so it reloads installed skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
