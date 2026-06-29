#!/usr/bin/env python3
"""agentkit command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import (
    __version__,
    agents as agents_mod,
    generate_adapters,
    init as init_mod,
    presets,
    validate as validate_mod,
)


def _table(headers: list[str], rows: list[list[str]]) -> str:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, cell in enumerate(row):
            widths[index] = max(widths[index], len(cell))
    lines = [
        "  ".join(cell.ljust(widths[index]) for index, cell in enumerate(headers)),
        "  ".join("-" * width for width in widths),
    ]
    lines.extend("  ".join(cell.ljust(widths[index]) for index, cell in enumerate(row)) for row in rows)
    return "\n".join(lines)


def _load_project(root: Path) -> dict:
    path = root / ".agents/project.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _print_init_next_steps(root: Path) -> None:
    proj = _load_project(root)
    skills = proj.get("skills", {}) if isinstance(proj.get("skills"), dict) else {}
    preset_names = [
        entry.get("name", str(entry)) if isinstance(entry, dict) else str(entry)
        for entry in (proj.get("kit", {}) or {}).get("presets", [])
    ]
    installed = [*skills.get("workflow", []), *skills.get("stack", [])]

    print(f"agentkit: initialized agent context in {root}")
    print("")
    print("Next steps:")
    print("  Canonical context: AGENTS.md and .agents/")
    print("  Installed presets: " + (", ".join(preset_names) if preset_names else "none"))
    print("  Installed skills: " + (", ".join(installed) if installed else "none"))
    print("  Invoke skills in Codex/Claude by naming them, for example: use stack-angular")
    print("  Next command: agentkit validate")


def _preset_stack(info: dict) -> str:
    language = info.get("language", "")
    framework = info.get("framework", "")
    if language and framework:
        return f"{language}/{framework}"
    return language or framework or "-"


def _cmd_presets_list() -> int:
    infos = presets.available_preset_infos()
    if not infos:
        print("No bundled presets found")
        return 0
    rows = [
        [
            str(info["name"]),
            str(info.get("kind") or "-"),
            _preset_stack(info),
            str(info.get("description") or ""),
        ]
        for info in infos
    ]
    print(_table(["Name", "Kind", "Language/Framework", "Description"], rows))
    return 0


def _cmd_presets_add(root: Path, name: str) -> int:
    if not (root / ".agents/project.json").exists():
        print("ERROR: .agents/project.json not found; run agentkit init first", file=sys.stderr)
        return 1
    preset_dir = presets.resolve_preset(name)
    if preset_dir is None:
        print(f"ERROR: preset not found: {name}", file=sys.stderr)
        return 1
    try:
        applied = presets.apply_preset(root, preset_dir)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    generate_adapters.sync(root, check=False)
    print(f"agentkit: applied preset {name}")
    if applied:
        print("  " + "\n  ".join(applied))
    print("agentkit: generated agent adapters")
    return 0


def _cmd_skills_list(root: Path) -> int:
    skills_root = root / ".agents/skills"
    groups = {"workflow": [], "stack": []}
    other: list[str] = []
    if skills_root.exists():
        for skill_file in sorted(skills_root.glob("*/SKILL.md")):
            name = validate_mod.parse_skill_name(skill_file) or skill_file.parent.name
            try:
                group = presets.skill_group(name)
            except ValueError:
                other.append(name)
                continue
            groups[group].append(name)

    for group in ("workflow", "stack"):
        print(f"{group}:")
        names = groups[group]
        if names:
            for name in names:
                print(f"  {name}")
        else:
            print("  (none)")
    if other:
        print("other:")
        for name in other:
            print(f"  {name}")
    return 0


def _manifest_text(root: Path, preset_names: list[str]) -> str:
    infos: list[dict] = []
    commands: dict[str, str] = {"verify": ""}
    for name in preset_names:
        preset_dir = presets.resolve_preset(name)
        if preset_dir is None:
            raise ValueError(f"preset not found: {name}")
        infos.append(presets.preset_info(preset_dir))
        commands_path = preset_dir / "commands.json"
        if commands_path.exists():
            commands.update(json.loads(commands_path.read_text(encoding="utf-8")))

    language = next((str(info.get("language", "")) for info in infos if info.get("language")), "")
    framework = next((str(info.get("framework", "")) for info in infos if info.get("framework")), "")

    lines = [
        "# agentkit manifest - human-authored intent consumed by `agentkit init`.",
        "core:",
        f"  version: {json.dumps(__version__)}",
        "",
    ]
    if infos:
        lines.append("presets:")
        for info in infos:
            lines.append(f"  - name: {json.dumps(str(info['name']))}")
            lines.append(f"    version: {json.dumps(str(info.get('version', '')))}")
    else:
        lines.append("presets: []")
    lines.extend(
        [
            "",
            "project:",
            f"  name: {json.dumps(root.name)}",
            f"  language: {json.dumps(language)}",
            f"  framework: {json.dumps(framework)}",
            "  commands:",
        ]
    )
    for key, value in sorted(commands.items()):
        lines.append(f"    {key}: {json.dumps(value)}")
    lines.extend(["", "memory:", "  scope: both", ""])
    return "\n".join(lines)


def _cmd_manifest_new(root: Path, preset_names: list[str], force: bool) -> int:
    path = root / "agentkit.yaml"
    if path.exists() and not force:
        print("ERROR: agentkit.yaml already exists; pass --force to overwrite", file=sys.stderr)
        return 1
    try:
        content = _manifest_text(root, preset_names)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    path.write_text(content, encoding="utf-8")
    print(f"agentkit: wrote {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentkit",
        description="Provider-agnostic agent context kit: canonical .agents -> generated adapters.",
    )
    parser.add_argument("--version", action="version", version=f"agentkit {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)
    init_p = sub.add_parser("init", help="bootstrap or adapt agent context in the current project")
    init_p.add_argument(
        "--preset",
        action="append",
        default=[],
        help="apply a bundled preset during init; repeat for multiple presets",
    )
    sync_p = sub.add_parser("sync", help="regenerate provider adapters from .agents")
    sync_p.add_argument("--check", action="store_true", help="check only; do not write")
    sub.add_parser("validate", help="validate canonical context + adapter sync")
    upgrade_p = sub.add_parser("upgrade", help="refresh kit-managed files to the installed version")
    upgrade_p.add_argument(
        "--refresh-presets",
        action="store_true",
        help="also re-apply recorded presets (overwrites preset-provided skills)",
    )
    presets_p = sub.add_parser("presets", help="inspect or apply bundled presets")
    presets_sub = presets_p.add_subparsers(dest="presets_cmd", required=True)
    presets_sub.add_parser("list", help="show bundled presets")
    presets_add = presets_sub.add_parser("add", help="apply a preset to an initialized project")
    presets_add.add_argument("name", help="preset name or local preset directory")

    skills_p = sub.add_parser("skills", help="inspect installed project skills")
    skills_sub = skills_p.add_subparsers(dest="skills_cmd", required=True)
    skills_sub.add_parser("list", help="show installed skills grouped by kind")

    manifest_p = sub.add_parser("manifest", help="create or inspect agentkit manifests")
    manifest_sub = manifest_p.add_subparsers(dest="manifest_cmd", required=True)
    manifest_new = manifest_sub.add_parser("new", help="write a starter agentkit.yaml")
    manifest_new.add_argument(
        "--preset",
        action="append",
        default=[],
        help="include a preset in the starter manifest; repeat for multiple presets",
    )
    manifest_new.add_argument("--force", action="store_true", help="overwrite an existing agentkit.yaml")

    agents_p = sub.add_parser("agents", help="generate provider-specific custom agents")
    agents_sub = agents_p.add_subparsers(dest="agents_cmd", required=True)
    agents_generate = agents_sub.add_parser("generate", help="generate custom agents for a provider")
    agents_generate.add_argument("--provider", required=True, help="provider to generate agents for (currently codex)")
    agents_generate.add_argument("--check", action="store_true", help="check only; do not write")

    args = parser.parse_args(argv)
    root = Path.cwd()

    if args.cmd == "init":
        init_mod.run(root, preset_names=args.preset)
        _print_init_next_steps(root)
        return 0

    if args.cmd == "sync":
        mismatches = generate_adapters.sync(root, check=args.check)
        if args.check:
            if mismatches:
                print("out of sync:\n  " + "\n  ".join(mismatches), file=sys.stderr)
                return 1
            print("agent adapters are in sync")
            return 0
        print("generated agent adapters")
        return 0

    if args.cmd == "validate":
        errors = validate_mod.validate(root)
        if errors:
            for err in errors:
                print(f"ERROR: {err}", file=sys.stderr)
            return 1
        print("agent context is valid")
        return 0

    if args.cmd == "upgrade":
        updated = init_mod.upgrade(root, refresh_presets=args.refresh_presets)
        if updated:
            print("agentkit: refreshed kit-managed files:\n  " + "\n  ".join(updated))
        else:
            print("agentkit: nothing to upgrade")
        return 0

    if args.cmd == "presets":
        if args.presets_cmd == "list":
            return _cmd_presets_list()
        if args.presets_cmd == "add":
            return _cmd_presets_add(root, args.name)

    if args.cmd == "skills":
        if args.skills_cmd == "list":
            return _cmd_skills_list(root)

    if args.cmd == "manifest":
        if args.manifest_cmd == "new":
            return _cmd_manifest_new(root, args.preset, args.force)

    if args.cmd == "agents":
        if args.agents_cmd == "generate":
            try:
                paths = agents_mod.generate(root, args.provider, check=args.check)
            except agents_mod.AgentGenerationError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                return 1
            provider = args.provider.lower()
            if args.check:
                if paths:
                    print(f"{provider} agents out of sync:\n  " + "\n  ".join(paths), file=sys.stderr)
                    return 1
                print(f"{provider} agents are in sync")
                return 0
            if paths:
                print(f"agentkit: generated {provider} agents:\n  " + "\n  ".join(paths))
            else:
                print(f"agentkit: {provider} agents are up to date")
            return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
