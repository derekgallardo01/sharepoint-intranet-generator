"""Orchestrate parsing the blueprint and writing the static preview to disk.

Stdlib only. :func:`generate` is the single entry point used by ``run.py`` and the
tests; it takes explicit paths so tests can target a temporary output directory.
"""

from __future__ import annotations

import json
from pathlib import Path

from .model import Intranet
from .render import render_all


def load_intranet(definition_path: str | Path) -> Intranet:
    """Read ``site-definition.json`` and parse it into an :class:`Intranet`."""
    path = Path(definition_path)
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return Intranet.from_dict(data)


def generate(definition_path: str | Path, out_dir: str | Path) -> list[Path]:
    """Generate the static intranet preview.

    Parses ``definition_path``, renders every page, writes them into ``out_dir``
    (created if needed), and returns the list of written file paths in the order
    they were rendered.
    """
    net = load_intranet(definition_path)
    pages = render_all(net)

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for filename, html in pages.items():
        target = out / filename
        target.write_text(html, encoding="utf-8")
        written.append(target)
    return written
