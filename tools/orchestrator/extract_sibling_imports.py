#!/usr/bin/env python3
"""Parse a wrapper script's imports and print the local sibling module(s) it
depends on, so queue_add.sh can auto-SCP them to the (stale) remote runner
before the remote --self-test gate imports them.

TWO MODES:

  (default, basename mode -- Pattern 6, 2026-07-04) prints the DIRECT
  `experiments/*.py` sibling BASENAMES the script imports (no path, no .py),
  for which <script_dir>/<X>.py exists. Kept for backward-compat with the
  Pattern 6 loop in queue_add.sh.

  (--closure-paths mode -- Pattern 7, 2026-09-02) prints the FULL TRANSITIVE
  import closure across experiments/ + tools/ + hdlab/ as REPO-RELATIVE PATHS
  (e.g. `experiments/foo.py`, `tools/bar.py`, `hdlab/baz.py`), EXCLUDING the
  entry script itself. This closes the ACTUAL recurring dispatch bug (2026-09-02,
  MISDIAGNOSED for weeks as "the remote enqueue write is broken"): the remote is
  a STALE checkout, and the basename mode shipped ONLY the cell's DIRECT
  experiments siblings -- so a TRANSITIVE sibling (a sibling importing another
  sibling) or any tools/ / hdlab/ module the cell needs was missing on the
  remote, the remote --self-test died with ModuleNotFoundError, and queue_add.sh
  exited 1 (read as "watcher not dispatching"). The transitive cross-package
  closure is exactly the set of first-party files the remote must have.

Reads ACTUAL `import experiments.X` / `from experiments import X` /
`from experiments.X import ...` (and the same for tools/ + hdlab/) via `ast`
(not regex), transitively. Best-effort: any read/parse error on a file yields no
edges from that file and never raises -- this is a safety net on top of Patterns
1-5, it must NEVER block a ship.

Usage:
  python extract_sibling_imports.py <script_path>                 # basenames (direct experiments siblings)
  python extract_sibling_imports.py <script_path> --closure-paths # repo-relative paths (transitive closure)
"""
from __future__ import annotations

import ast
import sys
from collections import deque
from pathlib import Path

ROOTS = ("experiments", "tools", "hdlab")


def _first_party_imports(path: Path) -> list[str]:
    """Return the fully-qualified first-party module names (experiments/tools/hdlab.*)
    imported by `path`, via ast. Never raises."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return []
    mods: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level or not node.module:
                continue
            if node.module.split(".")[0] in ROOTS:
                # `from experiments import X` -> the submodule is X; `from experiments.X import y` -> X
                if node.module in ROOTS:
                    for alias in node.names:
                        mods.append(node.module + "." + alias.name.split(".")[0])
                else:
                    mods.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in ROOTS:
                    mods.append(alias.name)
    return mods


def _mod_to_path(repo_root: Path, mod: str) -> Path | None:
    """Map a first-party module name to its repo-relative .py file, if it exists."""
    parts = mod.split(".")
    if not parts or parts[0] not in ROOTS:
        return None
    p = repo_root.joinpath(*parts).with_suffix(".py")
    return p if p.is_file() else None


def find_sibling_modules(script_path: Path) -> list[str]:
    """(basename mode, unchanged) DIRECT experiments/*.py sibling basenames."""
    try:
        tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=str(script_path))
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
                continue
            if node.module == "experiments":
                for alias in node.names:
                    maybe_add(alias.name.split(".")[0])
            elif node.module and node.module.startswith("experiments."):
                maybe_add(node.module[len("experiments."):].split(".")[0])
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("experiments."):
                    maybe_add(alias.name[len("experiments."):].split(".")[0])
    return found


def closure_paths(script_path: Path) -> list[str]:
    """(closure mode) The transitive experiments/tools/hdlab import closure of
    script_path as sorted repo-relative POSIX paths, EXCLUDING script_path itself."""
    # repo root = the parent of the first ROOT dir on the script's path, else the
    # script's grandparent (script is <repo>/experiments/x.py). Robust: walk up
    # until a dir containing an `experiments` subdir is found.
    repo_root = script_path.parent
    for anc in [script_path.parent, *script_path.parents]:
        if (anc / "experiments").is_dir():
            repo_root = anc
            break
    start = script_path.resolve()
    seen: set[Path] = {start}
    q: deque[Path] = deque([start])
    out: set[str] = set()
    while q:
        f = q.popleft()
        for mod in _first_party_imports(f):
            p = _mod_to_path(repo_root, mod)
            if p is None:
                continue
            rp = p.resolve()
            if rp in seen:
                continue
            seen.add(rp)
            q.append(rp)
            out.add(p.relative_to(repo_root).as_posix())
    return sorted(out)


def _nltk_corpora_in_file(path: Path) -> set[str]:
    """NLTK corpus names a file depends on at RUNTIME: `from nltk.corpus import X`,
    `import nltk.corpus.X`, `nltk.download("X")`, `nltk.data.find(".../X")`. These are
    NOT file-path KB_REFERENTs (PROT-022 misses them) and often are NOT hit by the
    --self-test (so the gate passes and the FULL run dies 7 min in with LookupError:
    Resource 'X' not found -- exactly the sg_lite/semcor failure 2026-09-02)."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
        return set()
    out: set[str] = set()
    for node in ast.walk(tree):
        # `from nltk.corpus import semcor, wordnet as wn` -- nltk.corpus.<X> IS a corpus by
        # definition, so this is unambiguous (no false positives, unlike parsing find()/download()
        # string args which caught arbitrary paths).
        if isinstance(node, ast.ImportFrom) and node.module == "nltk.corpus" and not node.level:
            for a in node.names:
                if a.name != "*":
                    out.add(a.name)
        elif isinstance(node, ast.Import):
            for a in node.names:
                if a.name.startswith("nltk.corpus."):
                    out.add(a.name.split(".")[2])
    return out


def nltk_corpora(script_path: Path) -> list[str]:
    """The union of NLTK corpus deps across the cell's full transitive closure."""
    files = [script_path.relative_to(_repo_root_of(script_path)).as_posix()] + closure_paths(script_path)
    root = _repo_root_of(script_path)
    found: set[str] = set()
    for rel in files:
        found |= _nltk_corpora_in_file(root / rel)
    # drop obvious non-corpus tokens (download of a tokenizer model etc. is still a real dep, keep it)
    return sorted(found)


def _repo_root_of(script_path: Path) -> Path:
    for anc in [script_path.parent, *script_path.parents]:
        if (anc / "experiments").is_dir():
            return anc
    return script_path.parent


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != 1:
        print("usage: extract_sibling_imports.py <script_path> [--closure-paths|--nltk-corpora]", file=sys.stderr)
        return 2
    script_path = Path(args[0]).resolve()
    if "--closure-paths" in flags:
        for rel in closure_paths(script_path):
            print(rel)
    elif "--nltk-corpora" in flags:
        for c in nltk_corpora(script_path):
            print(c)
    else:
        for base in find_sibling_modules(script_path):
            print(base)
    return 0


if __name__ == "__main__":
    sys.exit(main())
