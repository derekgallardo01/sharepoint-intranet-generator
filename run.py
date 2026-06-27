#!/usr/bin/env python3
"""Generate a static HTML preview of the intranet from ``site-definition.json``.

Run it from anywhere:

    python assets/accelerators/08-sharepoint-intranet/run.py

It writes the preview to ``out/`` next to this file and prints a summary. Open
``out/index.html`` in a browser to click through the proposed intranet. Stdlib only.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Make the local package importable regardless of the working directory.
sys.path.insert(0, str(HERE))

from intranet_gen import generate  # noqa: E402


def main() -> int:
    definition = HERE / "site-definition.json"
    out_dir = HERE / "out"

    written = generate(definition, out_dir)

    print(f"Generated {len(written)} page(s) from {definition.name}:")
    for path in written:
        print(f"  - {path.relative_to(HERE)}")
    print(f"\nOpen {(out_dir / 'index.html')} in a browser to preview the intranet.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
