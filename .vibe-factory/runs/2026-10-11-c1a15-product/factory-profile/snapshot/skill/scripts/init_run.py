#!/usr/bin/env python3
"""Create an isolated vibe-coding-factory run directory."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_version() -> str:
    match = re.search(r"^Skill version: `([0-9]+\.[0-9]+\.[0-9]+)`$", (SKILL_ROOT / "SKILL.md").read_text(), re.MULTILINE)
    if not match:
        raise SystemExit("Could not determine the Vibe Coding Factory skill version")
    return match.group(1)


def write_factory_profile(run_dir: Path) -> tuple[str, str]:
    """Snapshot the exact local Factory runtime used to begin this run."""
    profile_root = run_dir / "factory-profile"
    snapshot_root = profile_root / "snapshot"
    sources: list[tuple[str, Path, Path]] = [("skill_entry", SKILL_ROOT / "SKILL.md", Path("skill/SKILL.md"))]
    for directory in ("references", "templates", "schemas", "scripts"):
        for source in sorted((SKILL_ROOT / directory).glob("*")):
            if source.is_file() and source.suffix in {".md", ".json", ".py"}:
                if source == SKILL_ROOT / "references" / "03-critic-protocols.md":
                    continue
                role = "validator" if source.name == "validate_artifacts.py" else "factory_runtime"
                sources.append((role, source, Path("skill") / directory / source.name))
    sources.append((
        "critic_protocol",
        SKILL_ROOT / "references" / "03-critic-protocols.md",
        Path("critic/03-critic-protocols.md"),
    ))
    critic_adapter = SKILL_ROOT.parent.parent / "agents" / "vibe-factory-critic.md"
    if critic_adapter.is_file():
        sources.append(("critic_adapter", critic_adapter, Path("critic/vibe-factory-critic.md")))

    entries = []
    for role, source, relative_snapshot in sources:
        destination = snapshot_root / relative_snapshot
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        entries.append({
            "role": role,
            "source_path": str(source),
            "snapshot_path": str(Path("factory-profile/snapshot") / relative_snapshot),
            "sha256": sha256(destination),
        })
    profile = {
        "format_version": 2,
        "skill_name": "vibe-coding-factory",
        "skill_version": skill_version(),
        "runtime": {
            "skill_entry": "factory-profile/snapshot/skill/SKILL.md",
            "validator": "factory-profile/snapshot/skill/scripts/validate_artifacts.py",
            "critic_protocol": "factory-profile/snapshot/critic/03-critic-protocols.md",
        },
        "files": entries,
        "resume_rule": "Use this run-local snapshot for Factory instructions, critic protocol, and validation.",
    }
    profile_path = profile_root / "profile.json"
    profile_path.write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    return str(profile_path.relative_to(run_dir)), sha256(profile_path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--project-id")
    parser.add_argument("--wiki-root")
    parser.add_argument("--risk-level", choices=("standard", "high"), default="standard")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    run_dir = root / ".vibe-factory" / "runs" / args.run_id
    if run_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing run: {run_dir}")

    profile_path, profile_hash = write_factory_profile(run_dir)

    state = {
        "run_id": args.run_id,
        "project_id": args.project_id or root.name,
        "skill_version": skill_version(),
        "factory_profile": {
            "path": profile_path,
            "sha256": profile_hash,
            "skill_version": skill_version(),
        },
        "work_type": "new_flow",
        "risk_level": args.risk_level,
        "phase": "prebuild",
        "current_gate": "G0",
        "status": "draft",
        "artifacts": {},
        "next_action": "compile_context_packet",
    }
    snapshot = {"project_root": str(root), "git_repository": False, "git_head": None, "baseline_dirty": None}
    try:
        repository = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True, text=True
        ).stdout.strip() == "true"
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"], check=False, capture_output=True, text=True
        ).stdout.strip() or None
        dirty = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--", ".", ":!.vibe-factory"], check=True, capture_output=True, text=True
        ).stdout
        snapshot.update({"git_repository": repository, "git_head": head, "baseline_dirty": bool(dirty.strip()), "note": "no commits" if head is None else None})
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    if args.wiki_root:
        wiki_root = Path(args.wiki_root).resolve()
        wiki_snapshot = {"root": str(wiki_root), "git_repository": False, "git_head": None, "dirty": None}
        try:
            wiki_snapshot["git_repository"] = subprocess.run(
                ["git", "-C", str(wiki_root), "rev-parse", "--is-inside-work-tree"], check=True, capture_output=True, text=True
            ).stdout.strip() == "true"
            wiki_snapshot["git_head"] = subprocess.run(
                ["git", "-C", str(wiki_root), "rev-parse", "--verify", "HEAD"], check=False, capture_output=True, text=True
            ).stdout.strip() or None
            wiki_snapshot["dirty"] = bool(subprocess.run(
                ["git", "-C", str(wiki_root), "status", "--porcelain"], check=True, capture_output=True, text=True
            ).stdout.strip())
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
        snapshot["wiki"] = wiki_snapshot
    for relative in ("wireframes/flows", "wireframes/samples", "wireframes/structure", "wireframes/design", "prototype", "use-case", "verification", "critics", "decisions", "manifests", "sources/intent", "approved-inputs", "discovery", "coding-plan/v1/diagrams", "coding-plan/v1/decisions", "coding-plan/amendments", "implementation", "execution"):
        (run_dir / relative).mkdir(parents=True, exist_ok=True)
    (run_dir / "run-state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    manifest = {"run_id": args.run_id, "sources": [], "excluded_sources": []}
    (run_dir / "source-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    (run_dir / "repository-snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n")
    print(run_dir)
    print(f"Validate with: {run_dir / 'factory-profile/snapshot/skill/scripts/validate_artifacts.py'} {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
