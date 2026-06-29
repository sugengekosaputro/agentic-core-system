#!/usr/bin/env python3
"""Apply presets onto a project's canonical .agents context.

A preset is an overlay shipped under ``agentkit/presets/<name>/`` (bundled) or a
local directory. Applying a preset is additive and idempotent:

- ``skills/<name>/``        -> copied into ``.agents/skills/`` (skipped if present)
- ``mcp.overlay.json``      -> servers merged into ``.agents/mcp/servers.json`` (by name)
- ``env.mcp.additions``     -> variable names appended to ``.env.mcp.example``
- ``commands.json``         -> merged into ``.agents/project.json`` ``commands``
- ``agents.project.md``     -> inserted into the AGENTS.md project region
- ``preset.json``           -> recorded in ``project.json`` (presets + skill groups)

Metadata uses JSON (not YAML) so the engine stays standard-library only.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

PRESETS_DIR = Path(__file__).parent / "presets"

_PROJECT_START = "<!-- agentkit:project:start"
_PROJECT_END = "<!-- agentkit:project:end"
_PLACEHOLDER = "_Add project-specific guidance here"


def available_presets() -> list[str]:
    if not PRESETS_DIR.exists():
        return []
    return sorted(p.name for p in PRESETS_DIR.iterdir() if (p / "preset.json").is_file())


def preset_info(preset_dir: Path) -> dict[str, Any]:
    """Return normalized metadata for a preset directory."""
    meta = _read_json(preset_dir / "preset.json")
    return {
        "name": meta.get("name") or preset_dir.name,
        "version": meta.get("version", ""),
        "coreVersion": meta.get("coreVersion", ""),
        "kind": meta.get("kind", ""),
        "language": meta.get("language", ""),
        "framework": meta.get("framework", ""),
        "description": meta.get("description", ""),
    }


def available_preset_infos() -> list[dict[str, Any]]:
    infos: list[dict[str, Any]] = []
    for name in available_presets():
        preset_dir = resolve_preset(name)
        if preset_dir is not None:
            infos.append(preset_info(preset_dir))
    return infos


def resolve_preset(name_or_path: str) -> Path | None:
    """Resolve a preset by bundled name or by local directory path."""
    bundled = PRESETS_DIR / name_or_path
    if (bundled / "preset.json").exists():
        return bundled
    candidate = Path(name_or_path)
    if (candidate / "preset.json").exists():
        return candidate
    return None


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def skill_group(name: str) -> str:
    """Return the project.json skill group for a skill name, or raise clearly."""
    if name.startswith("workflow-"):
        return "workflow"
    if name.startswith("stack-"):
        return "stack"
    if name.startswith("core-"):
        raise ValueError(
            f"core-* project skills are no longer supported: {name}. "
            "Move durable guidance into AGENTS.md/docs or rename reusable task "
            "workflows to workflow-*."
        )
    if name.startswith("virtual-assistant-"):
        raise ValueError(
            f"virtual-assistant-* skills are no longer supported: {name}. "
            "Rename reusable task workflows to workflow-* or stack conventions to stack-*."
        )
    raise ValueError(f"unsupported skill prefix for {name}: expected workflow-* or stack-*")


def _merge_mcp(root: Path, overlay: Path, applied: list[str]) -> None:
    servers_path = root / ".agents/mcp/servers.json"
    doc = _read_json(servers_path)
    existing = {s.get("name") for s in doc.get("servers", [])}
    for server in _read_json(overlay).get("servers", []):
        if server.get("name") not in existing:
            doc.setdefault("servers", []).append(server)
            applied.append(f"mcp:{server.get('name')}")
    _write_json(servers_path, doc)


def _merge_env(root: Path, additions: Path, applied: list[str]) -> None:
    example = root / ".env.mcp.example"
    current = example.read_text(encoding="utf-8") if example.exists() else ""
    add_text = additions.read_text(encoding="utf-8")
    documented = {
        line.split("=", 1)[0].strip()
        for line in current.splitlines()
        if "=" in line and not line.strip().startswith("#")
    }
    new_lines = []
    for line in add_text.splitlines():
        if "=" in line and not line.strip().startswith("#"):
            var = line.split("=", 1)[0].strip()
            if var not in documented:
                new_lines.append(line)
                applied.append(f"env:{var}")
    if new_lines:
        sep = "" if current.endswith("\n") or not current else "\n"
        example.write_text(current + sep + "\n".join(new_lines) + "\n", encoding="utf-8")


def _insert_project_region(agents_path: Path, text: str) -> None:
    content = agents_path.read_text(encoding="utf-8")
    start = content.find(_PROJECT_START)
    end = content.find(_PROJECT_END)
    if start == -1 or end == -1:
        return
    inner_start = content.find("\n", start) + 1
    inner = content[inner_start:end]
    if text.strip() and text.strip() in inner:
        return  # idempotent
    if _PLACEHOLDER in inner:
        new_inner = "\n" + text.rstrip() + "\n\n"
    else:
        new_inner = inner.rstrip() + "\n\n" + text.rstrip() + "\n\n"
    agents_path.write_text(content[:inner_start] + new_inner + content[end:], encoding="utf-8")


def apply_preset(root: Path, preset_dir: Path, overwrite: bool = False) -> list[str]:
    """Apply one preset onto `root`'s canonical context. Returns what was applied.

    With ``overwrite=True`` (used by ``agentkit upgrade --refresh-presets``), existing
    preset-provided skills are replaced with the bundled versions.
    """
    root = Path(root).resolve()
    preset_dir = Path(preset_dir)
    meta = _read_json(preset_dir / "preset.json")
    applied: list[str] = []

    proj_path = root / ".agents/project.json"
    proj = _read_json(proj_path)
    proj.setdefault("skills", {})
    proj["skills"].setdefault("workflow", [])
    proj["skills"].setdefault("stack", [])
    proj.setdefault("commands", {})
    proj.setdefault("kit", {}).setdefault("presets", [])
    proj.setdefault("kitManaged", [])

    # 1. skills (additive; replaced when overwrite=True)
    skills_src = preset_dir / "skills"
    if skills_src.is_dir():
        skill_dirs = [skill for skill in sorted(skills_src.iterdir()) if skill.is_dir()]
        skill_groups = {skill.name: skill_group(skill.name) for skill in skill_dirs}
        for skill in skill_dirs:
            if not skill.is_dir():
                continue
            dst = root / ".agents/skills" / skill.name
            if dst.exists() and overwrite:
                shutil.rmtree(dst)
            if not dst.exists():
                shutil.copytree(skill, dst)
                applied.append(f"skill:{skill.name}")
            group = skill_groups[skill.name]
            if skill.name not in proj["skills"].setdefault(group, []):
                proj["skills"][group].append(skill.name)

    # 2. MCP overlay
    overlay = preset_dir / "mcp.overlay.json"
    if overlay.exists():
        _merge_mcp(root, overlay, applied)

    # 3. env additions
    env_add = preset_dir / "env.mcp.additions"
    if env_add.exists():
        _merge_env(root, env_add, applied)

    # 4. commands -> project.json
    for key, value in _read_json(preset_dir / "commands.json").items():
        proj["commands"][key] = value
        applied.append(f"command:{key}")

    # 5. record preset
    entry = {"name": meta.get("name", preset_dir.name), "version": meta.get("version", "")}
    if entry not in proj["kit"]["presets"]:
        proj["kit"]["presets"].append(entry)
    _write_json(proj_path, proj)

    # 6. AGENTS.md project region
    ap = preset_dir / "agents.project.md"
    if ap.exists():
        _insert_project_region(root / "AGENTS.md", ap.read_text(encoding="utf-8"))

    return applied
