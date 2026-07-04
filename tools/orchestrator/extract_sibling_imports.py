#!/usr/bin/env python3
"""Parse a wrapper script's imports and print local `experiments/*.py` sibling
module basenames it depends on (Pattern 6 fix for queue_add.sh auto-SCP gap;
2026-07-04).

Patterns 1-5 in queue_add.sh detect siblings by NAME CONVENTION (strip
_seed_<N>/_s<N> suffix, look for {base}.py / _{base}_core.py / _{base}_base.py,
or match a hardcoded shared-framework allow-list). That misses the
increasingly-common convention where a wrapper `exp_<name>_seed_<N>.py`
imports a sibling CORE named `exp_<name>_core.py` (no leading underscore --
the _seed_N-stripped basename does not equal the core's actual filename), and
it misses any other one-off local import that isn't in the allow-list.
Concrete misses this session: exp_encoder_v3e_decline_vs_plateau_v1_seed_7.py
-> exp_encoder_v3e_decline_vs_plateau_v1_core.py, and
exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_13.py ->
exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
(a core name that does NOT derive from the wrapper name by any suffix rule --
only the actual `from experiments import ... as core` statement reveals it).

This script reads the wrapper's ACTUAL `from experiments import <mod>` /
`from experiments.<mod> import ...` / `import experiments.<mod>` statements
via `ast` (not regex/string transforms), so it generalizes past any single
naming convention and closes the class of bug, not just this one instance.

Usage:
  python extract_sibling_imports.py <script_path>

Prints one sibling module basename (no .py, no path) per line to stdout for
every `experiments.<X>` (or bare `experiments` package) import found in the
script AND for which <script_dir>/<X>.py exists on disk. Best-effort: on any
read/parse error, prints nothing and exits 0 -- this is a safety-net layer on
top of Patterns 1-5, not a replacement, and must never block a ship.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path


def find_sibling_modules(script_path: Path) -> list[str]:
    """Return sibling `experiments/*.py` basenames imported by script_path."""
    try:
        src = script_path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(script_path))
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return []

    script_dir = script_path.parent
    self_base = script_path.stem
    found: list[str] = []
    seen: set[str] = set()

    def maybe_add(base: str) -> None:
        if not base or base == self_base or base in seen:
            return
        if (script_dir / f"{base}.py").is_file():
            seen.add(base)
            found.append(base)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level:
                # relative import (from . import X) -- not this repo's
                # convention (wrappers add repo root to sys.path and import
                # the absolute `experiments` package); skip to stay precise.
                continue
            if node.module == "experiments":
                for alias in node.names:
                    maybe_add(alias.name.split(".")[0])
            elif node.module and node.module.startswith("experiments."):
                rest = node.module[len("experiments."):]
                maybe_add(rest.split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("experiments."):
                    rest = alias.name[len("experiments."):]
                    maybe_add(rest.split(".")[0])

    return found


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract_sibling_imports.py <script_path>", file=sys.stderr)
        return 2
    script_path = Path(sys.argv[1]).resolve()
    for base in find_sibling_modules(script_path):
        print(base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
