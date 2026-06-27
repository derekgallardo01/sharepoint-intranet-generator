"""Run the validator against the golden eval set.

    python evals/run.py

Each case is a small definition (inline JSON) with an expected validity. Exit
code 0 if every case behaves as expected, 1 otherwise.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from intranet_gen.validate import validate  # noqa: E402


def _check(case: dict) -> tuple[bool, list[str]]:
    errors = validate(case["definition"])
    blocking = [e for e in errors if e.severity == "error"]
    warnings = [e for e in errors if e.severity != "error"]
    expect = case["expect"]
    details: list[str] = []

    if expect.get("valid") and blocking:
        details.append(f"expected valid; got {len(blocking)} blocking error(s)")
        for e in blocking[:3]:
            details.append(f"  {e}")
        return False, details

    if not expect.get("valid", True):
        if not blocking:
            details.append("expected invalid; got no blocking errors")

    for needle in expect.get("errors_contain", []):
        if not any(needle in e.message for e in blocking):
            details.append(f"missing expected error substring {needle!r}")

    for needle in expect.get("warnings_contain", []):
        if not any(needle in w.message for w in warnings):
            details.append(f"missing expected warning substring {needle!r}")

    return (len(details) == 0, details)


def main() -> int:
    with open(os.path.join(HERE, "golden.json"), encoding="utf-8") as fh:
        cases = json.load(fh)

    passed, failed = [], []
    for case in cases:
        ok, details = _check(case)
        rec = {"id": case["id"], "details": details}
        (passed if ok else failed).append(rec)

    total = len(cases)
    rate = (len(passed) / total * 100) if total else 0.0
    print(f"Eval: {len(passed)}/{total} passed ({rate:.0f}%)")
    if failed:
        print(f"\n{len(failed)} failed:")
        for f in failed:
            print(f"  [{f['id']}]")
            for d in f["details"]:
                print(f"       {d}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
