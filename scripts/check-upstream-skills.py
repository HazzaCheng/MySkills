#!/usr/bin/env python3
"""Check whether mirrored skills differ from their upstream repositories."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = REPO_ROOT / "skills"
DEFAULT_CONFIG = REPO_ROOT / "skills-upstreams.json"
DEFAULT_REPORT = REPO_ROOT / "upstream-skill-report.json"
IGNORE_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "node_modules",
}
IGNORE_FILES = {
    ".DS_Store",
    "Thumbs.db",
}
DEFAULT_PATH_CANDIDATES = (
    "skills/{skill}",
    ".agents/skills/{skill}",
    "{skill}",
)


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    origin: str | None
    frontmatter_repo: str | None


@dataclass(frozen=True)
class Mapping:
    skill: str
    repo: str | None
    ref: str | None
    path: str | None
    path_candidates: tuple[str, ...]
    source: str
    enabled: bool = True


@dataclass(frozen=True)
class RepoCheckout:
    repo: str
    ref: str | None
    path: Path | None
    commit: str | None
    error: str | None


@dataclass(frozen=True)
class Fingerprint:
    digest: str
    file_count: int
    byte_count: int


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise SystemExit(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def parse_frontmatter_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}:\s*(.+?)\s*$", text)
    if not match:
        return None
    value = match.group(1).strip().strip('"').strip("'")
    return value or None


def load_skills(skills_root: Path) -> list[Skill]:
    skills: list[Skill] = []
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        origin = None
        frontmatter_repo = None
        if skill_md.is_file():
            raw = read_text(skill_md)
            origin = parse_frontmatter_value(raw, "origin")
            frontmatter_repo = parse_frontmatter_value(raw, "repo")
        skills.append(
            Skill(
                name=skill_dir.name,
                path=skill_dir,
                origin=origin,
                frontmatter_repo=frontmatter_repo,
            )
        )
    return skills


def mapping_from_entry(skill: str, entry: dict[str, Any], source: str) -> Mapping:
    path_candidates = entry.get("pathCandidates") or entry.get("path_candidates") or []
    return Mapping(
        skill=skill,
        repo=entry.get("repo"),
        ref=entry.get("ref"),
        path=entry.get("path"),
        path_candidates=tuple(str(item) for item in path_candidates),
        source=str(entry.get("source") or source),
        enabled=bool(entry.get("enabled", True)),
    )


def mapping_for_skill(skill: Skill, config: dict[str, Any]) -> Mapping:
    explicit = config.get("skills", {}).get(skill.name)
    if explicit is not None:
        return mapping_from_entry(skill.name, explicit, "explicit")

    if skill.origin:
        default = config.get("originDefaults", {}).get(skill.origin)
        if default is not None:
            return mapping_from_entry(skill.name, default, f"origin:{skill.origin}")

    if skill.frontmatter_repo:
        return Mapping(
            skill=skill.name,
            repo=skill.frontmatter_repo,
            ref=None,
            path=None,
            path_candidates=DEFAULT_PATH_CANDIDATES + (".",),
            source="frontmatter repo",
            enabled=True,
        )

    return Mapping(
        skill=skill.name,
        repo=None,
        ref=None,
        path=None,
        path_candidates=(),
        source="unknown",
        enabled=True,
    )


def run_command(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def cache_key(repo: str, ref: str | None) -> str:
    value = f"{repo}@{ref or 'default'}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def clone_checkout(
    repo: str,
    ref: str | None,
    cache_root: Path,
    refresh_cache: bool,
) -> RepoCheckout:
    target = cache_root / cache_key(repo, ref)
    if refresh_cache and target.exists():
        shutil.rmtree(target)

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        command = ["git", "clone", "--depth", "1", repo, str(target)]
        result = run_command(command)
        if result.returncode != 0:
            return RepoCheckout(
                repo=repo,
                ref=ref,
                path=None,
                commit=None,
                error=(result.stderr or result.stdout).strip()[:1000],
            )

    if ref:
        fetch_result = run_command(
            ["git", "-C", str(target), "fetch", "--depth", "1", "origin", ref]
        )
        if fetch_result.returncode != 0:
            return RepoCheckout(
                repo=repo,
                ref=ref,
                path=target,
                commit=None,
                error=(fetch_result.stderr or fetch_result.stdout).strip()[:1000],
            )
        checkout_result = run_command(
            ["git", "-C", str(target), "checkout", "--detach", "FETCH_HEAD"]
        )
        if checkout_result.returncode != 0:
            return RepoCheckout(
                repo=repo,
                ref=ref,
                path=target,
                commit=None,
                error=(checkout_result.stderr or checkout_result.stdout).strip()[:1000],
            )

    commit_result = run_command(["git", "-C", str(target), "rev-parse", "HEAD"])
    if commit_result.returncode != 0:
        return RepoCheckout(
            repo=repo,
            ref=ref,
            path=target,
            commit=None,
            error=(commit_result.stderr or commit_result.stdout).strip()[:1000],
        )

    return RepoCheckout(
        repo=repo,
        ref=ref,
        path=target,
        commit=commit_result.stdout.strip(),
        error=None,
    )


def should_ignore(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if path.name in IGNORE_FILES:
        return True
    return any(part in IGNORE_DIRS for part in relative.parts)


def fingerprint_dir(path: Path) -> Fingerprint:
    digest = hashlib.sha256()
    file_count = 0
    byte_count = 0

    files = sorted(item for item in path.rglob("*") if item.is_file())
    for file_path in files:
        if should_ignore(file_path, path):
            continue
        relative = file_path.relative_to(path).as_posix()
        content = file_path.read_bytes()
        file_hash = hashlib.sha256(content).hexdigest()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\0")
        file_count += 1
        byte_count += len(content)

    return Fingerprint(
        digest=digest.hexdigest(),
        file_count=file_count,
        byte_count=byte_count,
    )


def safe_child(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def resolve_upstream_path(checkout: Path, mapping: Mapping) -> tuple[Path | None, str | None]:
    candidates: list[str] = []
    if mapping.path:
        candidates.append(mapping.path)
    candidates.extend(mapping.path_candidates)
    if not candidates:
        candidates.extend(DEFAULT_PATH_CANDIDATES)

    tried: list[str] = []
    for raw_candidate in candidates:
        relative = raw_candidate.format(skill=mapping.skill)
        tried.append(relative)
        candidate = safe_child(checkout, relative)
        if candidate and candidate.is_dir():
            return candidate, relative

    return None, ", ".join(tried)


def result_for_skill(
    skill: Skill,
    mapping: Mapping,
    checkouts: dict[tuple[str, str | None], RepoCheckout],
) -> dict[str, Any]:
    base = {
        "skill": skill.name,
        "origin": skill.origin,
        "mappingSource": mapping.source,
        "upstreamRepo": mapping.repo,
        "upstreamRef": mapping.ref,
        "upstreamCommit": None,
        "upstreamPath": None,
        "status": None,
        "detail": None,
    }

    if not mapping.enabled:
        return {**base, "status": "disabled", "detail": "Mapping disabled in config"}

    if not mapping.repo:
        return {**base, "status": "unknown-upstream", "detail": "No upstream repo mapping"}

    checkout = checkouts[(mapping.repo, mapping.ref)]
    base["upstreamCommit"] = checkout.commit

    if checkout.error or checkout.path is None:
        return {**base, "status": "upstream-unavailable", "detail": checkout.error}

    upstream_path, tried = resolve_upstream_path(checkout.path, mapping)
    if upstream_path is None:
        return {
            **base,
            "status": "upstream-path-missing",
            "detail": f"No candidate path found. Tried: {tried}",
        }

    base["upstreamPath"] = (
        upstream_path.resolve().relative_to(checkout.path.resolve()).as_posix()
    )
    upstream_fingerprint = fingerprint_dir(upstream_path)
    local_fingerprint = fingerprint_dir(skill.path)

    if upstream_fingerprint.digest == local_fingerprint.digest:
        return {
            **base,
            "status": "up-to-date",
            "detail": (
                f"{local_fingerprint.file_count} files, "
                f"{local_fingerprint.byte_count} bytes"
            ),
        }

    return {
        **base,
        "status": "upstream-changed",
        "detail": (
            f"local {local_fingerprint.file_count} files/"
            f"{local_fingerprint.byte_count} bytes; upstream "
            f"{upstream_fingerprint.file_count} files/"
            f"{upstream_fingerprint.byte_count} bytes"
        ),
    }


def print_table(results: list[dict[str, Any]]) -> None:
    columns = ("skill", "status", "mappingSource", "upstreamPath", "upstreamCommit")
    widths = {
        "skill": 32,
        "status": 24,
        "mappingSource": 24,
        "upstreamPath": 32,
        "upstreamCommit": 12,
    }
    header = "  ".join(name.ljust(widths[name]) for name in columns)
    print(header)
    print("  ".join("-" * widths[name] for name in columns))
    for item in results:
        values = {
            "skill": str(item.get("skill") or "")[: widths["skill"]],
            "status": str(item.get("status") or "")[: widths["status"]],
            "mappingSource": str(item.get("mappingSource") or "")[: widths["mappingSource"]],
            "upstreamPath": str(item.get("upstreamPath") or "")[: widths["upstreamPath"]],
            "upstreamCommit": str(item.get("upstreamCommit") or "")[: widths["upstreamCommit"]],
        }
        print("  ".join(values[name].ljust(widths[name]) for name in columns))


def print_summary(results: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for item in results:
        status = str(item["status"])
        counts[status] = counts.get(status, 0) + 1

    print()
    print("Summary:")
    for status in sorted(counts):
        print(f"  {status}: {counts[status]}")


def print_coverage(skills: list[Skill], config: dict[str, Any]) -> None:
    counts: dict[str, int] = {}
    origins: dict[str, int] = {}
    unknown: list[str] = []

    for skill in skills:
        mapping = mapping_for_skill(skill, config)
        source = mapping.source
        counts[source] = counts.get(source, 0) + 1
        origin = skill.origin or "<missing>"
        origins[origin] = origins.get(origin, 0) + 1
        if not mapping.repo:
            unknown.append(skill.name)

    print(f"Skills: {len(skills)}")
    print("Mapping coverage:")
    for source, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {source}: {count}")
    print("Origins:")
    for origin, count in sorted(origins.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {origin}: {count}")
    print(f"Unknown upstream: {len(unknown)}")
    if unknown:
        print("Unknown skills:")
        for name in unknown:
            print(f"  {name}")


def selected_skills(skills: list[Skill], names: list[str]) -> list[Skill]:
    if not names:
        return skills
    wanted = set(names)
    found = [skill for skill in skills if skill.name in wanted]
    missing = sorted(wanted - {skill.name for skill in found})
    if missing:
        raise SystemExit(f"Unknown skill(s): {', '.join(missing)}")
    return found


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check mirrored skills against their upstream repositories."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--skill", action="append", default=[], help="Check one skill")
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Show mapping coverage without cloning upstream repositories.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Cache upstream clones in this directory. Defaults to a temp dir.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Delete cached checkouts before cloning.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print full JSON results instead of a table.",
    )
    parser.add_argument(
        "--write-report",
        type=Path,
        default=None,
        nargs="?",
        const=DEFAULT_REPORT,
        help="Write JSON report. Defaults to upstream-skill-report.json.",
    )
    parser.add_argument(
        "--fail-on-changed",
        action="store_true",
        help="Exit 2 when any tracked skill differs from upstream.",
    )
    args = parser.parse_args()

    if not SKILLS_ROOT.is_dir():
        raise SystemExit(f"Cannot find skills directory: {SKILLS_ROOT}")

    config = read_json(args.config)
    skills = selected_skills(load_skills(SKILLS_ROOT), args.skill)

    if args.coverage:
        print_coverage(skills, config)
        return 0

    mappings = {skill.name: mapping_for_skill(skill, config) for skill in skills}
    repo_keys = sorted(
        {
            (mapping.repo, mapping.ref)
            for mapping in mappings.values()
            if mapping.enabled and mapping.repo
        },
        key=lambda item: (item[0] or "", item[1] or ""),
    )

    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if args.cache_dir is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="skill-upstreams-")
        cache_root = Path(temp_dir.name)
    else:
        cache_root = args.cache_dir

    try:
        checkouts: dict[tuple[str, str | None], RepoCheckout] = {}
        for repo, ref in repo_keys:
            assert repo is not None
            print(f"Fetching {repo} ({ref or 'default'})...", file=sys.stderr)
            checkouts[(repo, ref)] = clone_checkout(
                repo=repo,
                ref=ref,
                cache_root=cache_root,
                refresh_cache=args.refresh_cache,
            )

        results = [
            result_for_skill(skill, mappings[skill.name], checkouts)
            for skill in skills
        ]
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()

    if args.write_report is not None:
        args.write_report.parent.mkdir(parents=True, exist_ok=True)
        args.write_report.write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + os.linesep,
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_table(results)
        print_summary(results)

    if args.fail_on_changed and any(
        item["status"] == "upstream-changed" for item in results
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
