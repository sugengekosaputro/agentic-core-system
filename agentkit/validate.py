#!/usr/bin/env python3
"""Validate canonical agent context and generated adapters for a target project."""

from __future__ import annotations

import json
import re
from pathlib import Path

from . import generate_adapters
from . import presets as presets_mod

CHECK_PATHS = [
    "AGENTS.md",
    ".agents",
    ".codex/config.example.toml",
    ".codex/rules",
    "CLAUDE.md",
    ".claude",
    "opencode.json",
    ".kiro",
    ".mcp.json",
    ".antigravity",
]
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
    re.compile(r"\b(?:postgres|postgresql)://[^\s\"']+:[^\s\"']+@"),
    re.compile(r"\bjdbc:postgresql://[^\s\"']+password=", re.IGNORECASE),
]
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
AGENTS_MD_MAX_BYTES = 7000  # AGENTS.md loads every turn; keep it lean
MEMORY_MAX_BYTES = 16000  # .agents/memory/journal.md is on-demand; keep it bounded
SKILL_GROUPS = ("workflow", "stack")


def load_json(root: Path, relative_path: str) -> dict:
    with (root / relative_path).open(encoding="utf-8") as handle:
        return json.load(handle)


def run_generator_check(root: Path, errors: list[str]) -> None:
    mismatches = generate_adapters.sync(root, check=True)
    if mismatches:
        errors.append("generated adapters are out of sync:\n  " + "\n  ".join(mismatches))


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for relative in CHECK_PATHS:
        path = root / relative
        if not path.exists():
            continue
        if path.is_file() and not path.is_symlink():
            files.append(path)
        elif path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and not child.is_symlink():
                    files.append(child)
    return files


def check_secret_literals(root: Path, errors: list[str]) -> None:
    for path in iter_text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible secret literal in {path.relative_to(root)}")
                break


def check_mcp_aliases(root: Path, errors: list[str]) -> None:
    mcp = load_json(root, ".agents/mcp/servers.json")
    seen: set[str] = set()
    for server in mcp.get("servers", []):
        name = server.get("name", "")
        if "_" in name:
            errors.append(f"MCP alias uses underscore: {name}")
        if name in seen:
            errors.append(f"duplicate MCP alias: {name}")
        seen.add(name)


def parse_skill_name(skill_file: Path) -> str | None:
    lines = skill_file.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        return None
    for line in lines[1:]:
        if line == "---":
            return None
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip()
    return None


def check_duplicate_skill_names(root: Path, errors: list[str]) -> None:
    skills_root = root / ".agents/skills"
    names: dict[str, Path] = {}
    if not skills_root.exists():
        errors.append(".agents/skills is missing")
        return
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        name = parse_skill_name(skill_file)
        if not name:
            errors.append(f"missing skill name in {skill_file.relative_to(root)}")
            continue
        if name in names:
            errors.append(
                f"duplicate skill name {name}: {names[name].relative_to(root)} and "
                f"{skill_file.relative_to(root)}"
            )
        names[name] = skill_file


def check_provider_overrides(root: Path, errors: list[str]) -> None:
    overrides = load_json(root, ".agents/provider-overrides.json")
    for index, override in enumerate(overrides.get("overrides", []), start=1):
        provider = override.get("provider")
        path = override.get("path")
        reason = override.get("reason")
        if not provider or not path or not reason or not str(reason).strip():
            errors.append(f"provider override #{index} must include provider, path, and reason")


def check_no_codex_skill_source(root: Path, errors: list[str]) -> None:
    if (root / ".codex/skills").exists():
        errors.append(".codex/skills exists; canonical skills must live only in .agents/skills")


def check_canonical_schema(root: Path, errors: list[str]) -> None:
    try:
        mcp = load_json(root, ".agents/mcp/servers.json")
        servers = mcp.get("servers")
        if not isinstance(servers, list):
            errors.append(".agents/mcp/servers.json: 'servers' must be a list")
        else:
            for s in servers:
                for key in ("name", "transport"):
                    if key not in s:
                        errors.append(f"MCP server missing '{key}': {s.get('name', '?')}")
                if s.get("transport") == "http" and "url" not in s:
                    errors.append(f"MCP http server '{s.get('name', '?')}' missing 'url'")
                if s.get("transport") == "stdio" and "command" not in s:
                    errors.append(f"MCP stdio server '{s.get('name', '?')}' missing 'command'")
    except (OSError, ValueError) as exc:
        errors.append(f".agents/mcp/servers.json invalid: {exc}")

    try:
        rules = load_json(root, ".agents/permissions.json").get("rules", {})
        for decision in ("allow", "prompt", "deny"):
            if not isinstance(rules.get(decision, []), list):
                errors.append(f".agents/permissions.json: rules.{decision} must be a list")
    except (OSError, ValueError) as exc:
        errors.append(f".agents/permissions.json invalid: {exc}")

    if (root / ".agents/project.json").exists():
        try:
            proj = load_json(root, ".agents/project.json")
            for key in ("name", "skills"):
                if key not in proj:
                    errors.append(f".agents/project.json missing '{key}'")
            skills = proj.get("skills")
            if isinstance(skills, dict):
                for group in SKILL_GROUPS:
                    if not isinstance(skills.get(group), list):
                        errors.append(f".agents/project.json: skills.{group} must be a list")
                for group in skills:
                    if group not in SKILL_GROUPS:
                        errors.append(
                            f".agents/project.json: unsupported skills group '{group}'; "
                            "expected only workflow and stack"
                        )
                for group in SKILL_GROUPS:
                    for name in skills.get(group, []):
                        try:
                            expected = presets_mod.skill_group(name)
                        except ValueError as exc:
                            errors.append(f".agents/project.json: {exc}")
                            continue
                        if expected != group:
                            errors.append(
                                f".agents/project.json: skill '{name}' belongs in skills.{expected}, "
                                f"not skills.{group}"
                            )
            elif "skills" in proj:
                errors.append(".agents/project.json: skills must be an object")
        except (OSError, ValueError) as exc:
            errors.append(f".agents/project.json invalid: {exc}")


def check_mcp_env_documented(root: Path, errors: list[str]) -> None:
    try:
        mcp = load_json(root, ".agents/mcp/servers.json")
    except (OSError, ValueError):
        return
    example = root / ".env.mcp.example"
    text = example.read_text(encoding="utf-8") if example.exists() else ""
    documented = {
        line.split("=", 1)[0].strip()
        for line in text.splitlines()
        if "=" in line and not line.strip().startswith("#")
    }
    for server in mcp.get("servers", []):
        for var in server.get("envVars", []):
            if var not in documented:
                errors.append(
                    f"MCP server '{server.get('name', '?')}' env var {var} is not documented "
                    "in .env.mcp.example"
                )


def check_skill_name_format(root: Path, errors: list[str]) -> None:
    skills_root = root / ".agents/skills"
    for skill_file in sorted(skills_root.glob("*/SKILL.md")):
        dir_name = skill_file.parent.name
        name = parse_skill_name(skill_file)
        if name is None:
            continue
        if not SKILL_NAME_RE.match(name):
            errors.append(f"skill name not lowercase-hyphen: {name}")
        if name != dir_name:
            errors.append(f"skill name '{name}' does not match directory '{dir_name}'")
        try:
            presets_mod.skill_group(name)
        except ValueError as exc:
            errors.append(f"{skill_file.relative_to(root)}: {exc}")


def check_context_budget(root: Path, errors: list[str]) -> None:
    agents = root / "AGENTS.md"
    if agents.exists():
        size = len(agents.read_bytes())
        if size > AGENTS_MD_MAX_BYTES:
            errors.append(
                f"AGENTS.md is {size} bytes (> {AGENTS_MD_MAX_BYTES}); it loads every turn — "
                "trim it or move detail into skill references or docs/."
            )


def check_memory_budget(root: Path, errors: list[str]) -> None:
    journal = root / ".agents/memory/journal.md"
    if journal.exists():
        size = len(journal.read_bytes())
        if size > MEMORY_MAX_BYTES:
            errors.append(
                f".agents/memory/journal.md is {size} bytes (> {MEMORY_MAX_BYTES}); "
                "summarize or rotate it — keep memory terse and pointer-based."
            )


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    run_generator_check(root, errors)
    check_secret_literals(root, errors)
    check_mcp_aliases(root, errors)
    check_canonical_schema(root, errors)
    check_mcp_env_documented(root, errors)
    check_duplicate_skill_names(root, errors)
    check_skill_name_format(root, errors)
    check_provider_overrides(root, errors)
    check_no_codex_skill_source(root, errors)
    check_context_budget(root, errors)
    check_memory_budget(root, errors)
    return errors
