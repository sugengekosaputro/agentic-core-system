#!/usr/bin/env python3
"""agentkit command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, generate_adapters, init as init_mod, validate as validate_mod


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="agentkit",
        description="Provider-agnostic agent context kit: canonical .agents -> generated adapters.",
    )
    parser.add_argument("--version", action="version", version=f"agentkit {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="bootstrap or adapt agent context in the current project")
    sync_p = sub.add_parser("sync", help="regenerate provider adapters from .agents")
    sync_p.add_argument("--check", action="store_true", help="check only; do not write")
    sub.add_parser("validate", help="validate canonical context + adapter sync")
    sub.add_parser("upgrade", help="refresh kit-managed files to the installed version")

    args = parser.parse_args(argv)
    root = Path.cwd()

    if args.cmd == "init":
        init_mod.run(root)
        print(f"agentkit: initialized agent context in {root}")
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
        updated = init_mod.upgrade(root)
        if updated:
            print("agentkit: refreshed kit-managed files:\n  " + "\n  ".join(updated))
        else:
            print("agentkit: nothing to upgrade")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
