"""GUARD: `hdlab/` imports 13 experiment CELLS. If one is deleted or renamed, this fails LOUDLY.

WHY. `experiments/` is where DISPOSABLE cells live -- that is the stated convention, and
`tools/clear_scratch.py` exists because throwaway work is expected to be thrown away. But measured
2026-08-22, **6 modules under `hdlab/` import 13 named experiment cells**, which makes those thirteen
load-bearing library dependencies. **Nothing anywhere marks them as such.** Someone tidying old
experiments would break the live path with no warning, and the break would surface as an ImportError
deep inside a read.

This witness is the warning. It does NOT fix the layering inversion (see
notes/IMPORTING_THE_LIVE_MODULE_MUTATES_GLOBAL_STDOUT_...md for the specified, deliberately unapplied
fix) -- it makes the dependency VISIBLE and its removal LOUD.

WHY A SINGLE GUARD RATHER THAN 13 COMMENTS. A comment at the top of each cell would go stale silently
the moment the import list changes. This re-derives the list FROM THE SOURCE on every run, so it
cannot drift: add a new `from experiments import exp_*` to `hdlab/` and this test starts protecting it
automatically.
"""
from __future__ import annotations

import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

# All three import spellings. Kept in one place because a missed spelling silently shrinks the
# protected set -- the failure mode of any enumeration-based guard.
PATTERNS = [
    re.compile(r"from\s+experiments\s+import\s+([A-Za-z_][A-Za-z0-9_]*)"),
    re.compile(r"from\s+experiments\.([A-Za-z_][A-Za-z0-9_]*)\s+import"),
    re.compile(r"import\s+experiments\.([A-Za-z_][A-Za-z0-9_]*)"),
]


def discover():
    """(cell_name -> set of hdlab files importing it), re-derived from source every run."""
    deps: dict[str, set[str]] = {}
    for root, _dirs, files in os.walk(os.path.join(REPO, "hdlab")):
        for f in files:
            if not f.endswith(".py"):
                continue
            p = os.path.join(root, f)
            try:
                text = open(p, encoding="utf-8", errors="ignore").read()
            except OSError:
                continue
            for pat in PATTERNS:
                for name in pat.findall(text):
                    rel = os.path.relpath(p, REPO).replace("\\", "/")
                    deps.setdefault(name, set()).add(rel)
    return deps


def test_every_experiment_hdlab_depends_on_still_exists():
    """THE guard: each imported module must still be on disk."""
    deps = discover()
    missing = []
    for name, importers in sorted(deps.items()):
        path = os.path.join(REPO, "experiments", name + ".py")
        if not os.path.exists(path):
            missing.append(f"{name} (imported by {', '.join(sorted(importers))})")
    assert not missing, (
        "hdlab imports experiment modules that NO LONGER EXIST -- the live path is broken:\n  "
        + "\n  ".join(missing))


def test_the_dependency_set_is_not_empty():
    """POSITIVE CONTROL. If the patterns stop matching, the guard above passes vacuously and
    protects nothing -- which is how an enumeration-based check dies quietly."""
    deps = discover()
    assert len(deps) >= 10, (
        f"only {len(deps)} experiment dependencies discovered; expected >=10 (13 cells + 9 helpers "
        f"measured 2026-08-22). The patterns have probably stopped matching, so this guard is no "
        f"longer protecting anything.")


def test_cells_are_reported_separately_from_helpers():
    """The two groups differ in severity: an `exp_*` CELL is a real layering inversion, an
    `_helper` is shared infrastructure in the wrong folder. Reported so the distinction survives."""
    deps = discover()
    cells = sorted(n for n in deps if n.startswith("exp_"))
    helpers = sorted(n for n in deps if not n.startswith("exp_"))
    print(f"    hdlab depends on {len(cells)} experiment CELLS and {len(helpers)} shared helpers")
    for c in cells:
        print(f"      CELL   {c}   <- {', '.join(sorted(deps[c]))}")
    assert cells, "no exp_* cells found -- pattern drift, see the positive control above"


def _run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
