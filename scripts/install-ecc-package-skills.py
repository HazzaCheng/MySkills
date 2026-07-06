#!/usr/bin/env python3
"""Install selected ECC skills from the ecc-universal npm package."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path


DEFAULT_DESTINATION = Path.home() / ".codex" / "skills"


def parse_skills(value: str) -> list[str]:
    return sorted({item.strip() for item in value.split(",") if item.strip()})


def npm_pack(package: str, destination: Path) -> Path:
    result = subprocess.run(
        ["npm", "pack", package, "--json", "--pack-destination", str(destination)],
        check=True,
        text=True,
        capture_output=True,
    )
    packages = json.loads(result.stdout)
    if not packages:
        raise SystemExit(f"npm pack returned no package metadata for {package}")
    filename = packages[0].get("filename")
    if not filename:
        raise SystemExit(f"npm pack returned no filename for {package}")
    return destination / str(filename)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install selected SKILL.md folders from the ecc-universal npm package."
    )
    parser.add_argument(
        "--package",
        default="ecc-universal",
        help="npm package spec to install from. Defaults to ecc-universal.",
    )
    parser.add_argument(
        "--skills",
        required=True,
        help="Comma-separated ECC skill directory names to install.",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help="Destination skills directory. Defaults to ~/.codex/skills.",
    )
    args = parser.parse_args()

    skills = parse_skills(args.skills)
    if not skills:
        raise SystemExit("No skills were provided.")

    args.destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ecc-package-skills.") as tmp:
        tmp_path = Path(tmp)
        tarball = npm_pack(args.package, tmp_path)
        with tarfile.open(tarball) as archive:
            archive.extractall(tmp_path)

        package_root = tmp_path / "package"
        missing = []
        for skill in skills:
            source = package_root / "skills" / skill
            if not source.is_dir():
                missing.append(skill)
                continue
            target = args.destination / skill
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(source, target)
            print(f"Installed ECC package skill: {skill}")

    if missing:
        raise SystemExit(
            "These skills were not found in the npm package: " + ", ".join(missing)
        )

    print("Done. Restart Codex so it reloads installed skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
