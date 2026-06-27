#!/usr/bin/env python3
"""Apply presets onto a project's canonical .agents context.

A preset is an overlay shipped under ``agentkit/presets/<name>/`` (bundled) or a
local directory. Applying a preset is additive and idempotent:

- ``skills/<name>/``        -> copied into ``.agents/skills/`` (skipped if present)
- ``mcp.overlay.json``      -> servers merged into ``.agents/mcp/servers.json`` (by name)
- ``env.mcp.additions``     -> variable names appended to ``.env.mcp.example``
- ``commands.json``         -> merged into ``.agents/project.json`` ``commands``
- ``agents.project.md``     -> inserted into the AGENTS.md project region
- ``preset.json``           -> recorded in ``project.json`` (presets + skill layers)

Metadata uses JSON (not YAML) so the engine stays standard-library only.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

PRESETS_DIR = Path(__file__).parent / "presets"

_PROJECT_START = "<!-- agentkit:project:start"
_PROJECT_END = "<!-- agentkit:project:end"
_PLACEHOLDER = "_Add project-specific guidance here"


def available_presets() -> list[str]:
    if not PRESETS_DIR.exists():
        return []
    return sorted(p.name for p in PRESETS_DIR.iterdir() if p.is_dir())


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


def _skill_layer(name: str) -> str:
    if name.startswith("virtual-assistant-"):
        return "virtual-assistant"
    if name.startswith("stack-"):
        return "stack"
    if name.startswith("core-"):
        return "core"
    return "stack"


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
    proj.setdefault("skills", {"core": [], "virtual-assistant": [], "stack": []})
    proj.setdefault("commands", {})
    proj.setdefault("kit", {}).setdefault("presets", [])
    proj.setdefault("kitManaged", [])

    # 1. skills (additive; replaced when overwrite=True)
    skills_src = preset_dir / "skills"
    if skills_src.is_dir():
        for skill in sorted(skills_src.iterdir()):
            if not skill.is_dir():
                continue
            dst = root / ".agents/skills" / skill.name
            if dst.exists() and overwrite:
                shutil.rmtree(dst)
            if not dst.exists():
                shutil.copytree(skill, dst)
                applied.append(f"skill:{skill.name}")
            layer = _skill_layer(skill.name)
            if skill.name not in proj["skills"].setdefault(layer, []):
                proj["skills"][layer].append(skill.name)

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
