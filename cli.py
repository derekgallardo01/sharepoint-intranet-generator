"""CLI for the intranet generator.

    python cli.py validate site-definition.json
    python cli.py generate site-definition.json --out out/
    python cli.py generate site-definition.json --out out/ --skip-validation
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from intranet_gen import generate  # noqa: E402
from intranet_gen.validate import validate  # noqa: E402


def _cmd_validate(args) -> int:
    errors = validate(args.definition)
    blocking = [e for e in errors if e.severity == "error"]
    warnings = [e for e in errors if e.severity != "error"]
    if not errors:
        print(f"OK: {args.definition} is structurally valid.")
        return 0
    for e in errors:
        print(str(e))
    print()
    print(f"{len(blocking)} error(s), {len(warnings)} warning(s).")
    return 0 if not blocking else 1


def _cmd_generate(args) -> int:
    if not args.skip_validation:
        errors = [e for e in validate(args.definition) if e.severity == "error"]
        if errors:
            print("Refusing to generate: definition has blocking errors:")
            for e in errors:
                print(f"  {e}")
            print("Re-run with --skip-validation to bypass.")
            return 1
    written = generate(args.definition, args.out)
    print(f"Generated {len(written)} page(s) into {args.out}:")
    for p in written:
        print(f"  - {p.name}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Validate or generate the intranet from a definition file.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    pv = sub.add_parser("validate",
                        help="Check the definition against the schema rules.")
    pv.add_argument("definition", help="Path to site-definition.json.")
    pv.set_defaults(func=_cmd_validate)

    pg = sub.add_parser("generate",
                        help="Generate static HTML pages from the definition.")
    pg.add_argument("definition", help="Path to site-definition.json.")
    pg.add_argument("--out", default=os.path.join(HERE, "out"),
                    help="Output directory (default: ./out).")
    pg.add_argument("--skip-validation", action="store_true",
                    help="Generate even if validation would block.")
    pg.set_defaults(func=_cmd_generate)

    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
