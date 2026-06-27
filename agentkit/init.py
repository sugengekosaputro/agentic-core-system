#!/usr/bin/env python3
"""`agentkit init` / `agentkit upgrade`: scaffold and refresh agent context.

init vendors base templates + core skills into a target project (without
overwriting existing files), seeds .agents/project.json from a manifest, generates
adapters, and enables the git hooks. upgrade refreshes only kit-managed files.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from . import generate_adapters, presets

TEMPLATES = Path(__file__).parent / "templates"
CORE_SKILLS = TEMPLATES / "skills" / "core"


def _copy_if_missing(src: Path, dst: Path) -> bool:
    if dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)
    return True


def _load_manifest(root: Path) -> dict:
    path = root / "agentkit.yaml"
    if not path.exists():
        return {}
    try:
        import yaml  # PyYAML
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "agentkit.yaml found but PyYAML is not installed. Install agentkit-core "
            "(which depends on PyYAML) or remove the manifest."
        ) from exc
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _seed_project_json(root: Path, manifest: dict) -> None:
    dst = root / ".agents/project.json"
    if dst.exists():
        return
    proj = manifest.get("project", {}) or {}
    data = {
        "schemaVersion": 1,
        "name": proj.get("name") or root.name,
        "description": proj.get("description", ""),
        "language": proj.get("language", ""),
        "framework": proj.get("framework", ""),
        "buildTool": proj.get("buildTool", ""),
        "commands": proj.get("commands", {"verify": ""}),
        "kit": {
            "core": (manifest.get("core") or {}).get("version", ""),
            "presets": [],
        },
        "skills": {
            "core": ["core-init", "core-consultant", "core-orchestrator"],
            "virtual-assistant": [],
            "stack": [],
        },
        "memory": manifest.get("memory", {"scope": "both"}),
        "kitManaged": [
            ".agents/README.md",
            ".agents/skills/core-init",
            ".agents/skills/core-consultant",
            ".agents/skills/core-orchestrator",
            ".githooks",
        ],
    }
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _enable_hooks(root: Path) -> None:
    for hook in ("pre-commit", "pre-push"):
        hp = root / ".githooks" / hook
        if hp.exists():
            hp.chmod(0o755)
    if (root / ".git").exists():
        subprocess.run(
            ["git", "-C", str(root), "config", "core.hooksPath", ".githooks"],
            check=False,
        )


def _marked_block(text: str, start_prefix: str, end_prefix: str) -> str | None:
    """Return the full lines from the start-marker line through the end-marker line."""
    start = text.find(start_prefix)
    end = text.find(end_prefix)
    if start == -1 or end == -1:
        return None
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", end)
    line_end = len(text) if line_end == -1 else line_end + 1
    return text[line_start:line_end]


def _refresh_agents_core_region(root: Path, updated: list[str]) -> None:
    """Replace the AGENTS.md core region with the template's, preserving the rest."""
    target = root / "AGENTS.md"
    if not target.exists():
        return
    template = (TEMPLATES / "AGENTS.base.md").read_text(encoding="utf-8")
    new_core = _marked_block(template, "<!-- agentkit:core:start", "<!-- agentkit:core:end")
    content = target.read_text(encoding="utf-8")
    old_core = _marked_block(content, "<!-- agentkit:core:start", "<!-- agentkit:core:end")
    if not new_core or not old_core or old_core == new_core:
        return
    target.write_text(content.replace(old_core, new_core, 1), encoding="utf-8")
    updated.append("AGENTS.md (core region)")


def run(root: Path) -> Path:
    """Bootstrap or adapt agent context in `root` (idempotent; never overwrites)."""
    root = Path(root).resolve()
    manifest = _load_manifest(root)

    _copy_if_missing(TEMPLATES / "agents-README.md", root / ".agents/README.md")
    _copy_if_missing(TEMPLATES / "permissions.json", root / ".agents/permissions.json")
    _copy_if_missing(TEMPLATES / "provider-overrides.json", root / ".agents/provider-overrides.json")
    _copy_if_missing(TEMPLATES / "mcp.base.json", root / ".agents/mcp/servers.json")
    _copy_if_missing(TEMPLATES / "AGENTS.base.md", root / "AGENTS.md")
    _copy_if_missing(TEMPLATES / "env.mcp.example", root / ".env.mcp.example")
    _copy_if_missing(TEMPLATES / "docs", root / "docs")
    _copy_if_missing(TEMPLATES / "githooks", root / ".githooks")

    for skill_dir in sorted(CORE_SKILLS.iterdir()):
        if skill_dir.is_dir():
            _copy_if_missing(skill_dir, root / ".agents/skills" / skill_dir.name)

    _seed_project_json(root, manifest)

    # apply presets declared in the manifest (bundled by name or a local path)
    for entry in manifest.get("presets", []) or []:
        name = entry.get("name") if isinstance(entry, dict) else entry
        if not name:
            continue
        preset_dir = presets.resolve_preset(name)
        if preset_dir is not None:
            presets.apply_preset(root, preset_dir)
        else:
            print(f"agentkit: warning — preset not found, skipped: {name}")

    generate_adapters.sync(root, check=False)
    _enable_hooks(root)
    return root


def upgrade(root: Path) -> list[str]:
    """Refresh kit-managed files (core skills, .agents/README.md, hooks) and re-sync.

    Project-owned files (permissions.json, provider-overrides.json, mcp servers,
    AGENTS.md, docs/, project.json) are left untouched.
    """
    root = Path(root).resolve()
    updated: list[str] = []

    def _overwrite(src: Path, dst: Path) -> None:
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        updated.append(str(dst.relative_to(root)))

    _overwrite(TEMPLATES / "agents-README.md", root / ".agents/README.md")
    for skill_dir in sorted(CORE_SKILLS.iterdir()):
        if skill_dir.is_dir():
            _overwrite(skill_dir, root / ".agents/skills" / skill_dir.name)
    _overwrite(TEMPLATES / "githooks", root / ".githooks")

    _refresh_agents_core_region(root, updated)
    _enable_hooks(root)
    generate_adapters.sync(root, check=False)
    return updated
