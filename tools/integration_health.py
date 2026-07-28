#!/usr/bin/env python3
"""Integration-health tripwire: catch proven-but-unwired capabilities before they pile up.

The substrate's failure mode (2026-07-25 audit): capabilities get proven in exp_ cells,
VET'd, atomized -- and left as ISLANDS. The atom store records the CLAIM, never the CODE.
This script makes detection AUTOMATIC + CHEAP so the debt can't silently accumulate again.

Reports:
  1. PROMOTE candidates: exp_ modules imported by >= K OTHER cells (de-facto shared code
     trapped in experiments/ that should live in hdlab/).
  2. Frontier bypass: how many cells import `from experiments import ...` (the exp-as-module
     smell); and whether a designated composed entry exists.
  3. Dead hdlab modules: core-library modules with ~0 consumers (quarantine candidates).

Run standalone (prints report) or on a cadence (cron / meta_audit). ASCII-only, stdlib-only.
"""
from __future__ import annotations
import os
import re
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(ROOT, "experiments")
HDLAB_DIR = os.path.join(ROOT, "hdlab")
PROMOTE_MIN_CONSUMERS = 3          # exp module imported by >=3 others = promotion candidate
COMPOSED_ENTRY_CANDIDATES = ("reasoner.py", "substrate.py", "pipeline.py")

# import patterns
RE_FROM_EXP = re.compile(r"^\s*from\s+experiments\s+import\s+(.+)", re.M)
RE_FROM_EXP_SUB = re.compile(r"^\s*from\s+experiments\.([A-Za-z0-9_]+)\s+import", re.M)
RE_IMPORT_EXP_SUB = re.compile(r"^\s*import\s+experiments\.([A-Za-z0-9_]+)", re.M)
RE_FROM_HDLAB = re.compile(r"^\s*from\s+hdlab\.([A-Za-z0-9_]+)\s+import", re.M)
RE_FROM_HDLAB_BARE = re.compile(r"^\s*from\s+hdlab\s+import\s+(.+)", re.M)
RE_HDLAB_ATTR = re.compile(r"\bhdlab\.([A-Za-z0-9_]+)")
RE_REL = re.compile(r"^\s*from\s+\.([A-Za-z0-9_]+)\s+import", re.M)   # relative, inside hdlab
RE_REL_BARE = re.compile(r"^\s*from\s+\.\s+import\s+(.+)", re.M)      # `from . import a, b` (e.g. __init__ re-export)


def _pyfiles(d):
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".py")]


def _read(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return ""


def _names(chunk):
    # parse an import list like "a as x, b, c" -> ['a','b','c']
    out = []
    for part in chunk.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(part.split(" as ")[0].split("#")[0].strip().strip("()"))
    return [n for n in out if n and n.isidentifier()]


def compute_import_graph(exp_dir=EXP_DIR, hdlab_dir=HDLAB_DIR):
    """Reusable core: build the exp/hdlab import graph.

    Returns (exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files,
    hdlab_mods) so callers (this script's main(), capability_registry_audit.py) share ONE
    computation instead of re-deriving the regex logic. Pure function, no I/O side effects
    besides reading source files.
    """
    exp_files = _pyfiles(exp_dir)
    hdlab_files = _pyfiles(hdlab_dir)
    hdlab_mods = {os.path.basename(f)[:-3] for f in hdlab_files} - {"__init__"}

    exp_module_consumers = defaultdict(set)   # exp_module -> set of files importing it as a module
    hdlab_consumers = defaultdict(set)        # hdlab_module -> set of consumer files
    bypass_cells = set()                      # cells doing `from experiments import ...`

    all_files = exp_files + hdlab_files
    for p in all_files:
        base = os.path.basename(p)[:-3]
        src = _read(p)
        # exp-as-module imports
        got_exp = False
        for m in RE_FROM_EXP.finditer(src):
            for n in _names(m.group(1)):
                if n != base:
                    exp_module_consumers[n].add(p)
                    got_exp = True
        for rex in (RE_FROM_EXP_SUB, RE_IMPORT_EXP_SUB):
            for m in rex.finditer(src):
                n = m.group(1)
                if n != base:
                    exp_module_consumers[n].add(p)
                    got_exp = True
        if got_exp:
            bypass_cells.add(p)
        # hdlab consumers (absolute)
        for rex in (RE_FROM_HDLAB, RE_HDLAB_ATTR):
            for m in rex.finditer(src):
                mod = m.group(1)
                if mod in hdlab_mods and mod != base:
                    hdlab_consumers[mod].add(p)
        for m in RE_FROM_HDLAB_BARE.finditer(src):
            for n in _names(m.group(1)):
                if n in hdlab_mods and n != base:
                    hdlab_consumers[n].add(p)
        # relative imports (only meaningful inside hdlab/)
        if p in hdlab_files:
            for m in RE_REL.finditer(src):
                mod = m.group(1)
                if mod in hdlab_mods and mod != base:
                    hdlab_consumers[mod].add(p)
            for m in RE_REL_BARE.finditer(src):
                for n in _names(m.group(1)):
                    if n in hdlab_mods and n != base:
                        hdlab_consumers[n].add(p)

    return exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files, hdlab_mods


def main():
    exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files, hdlab_mods = (
        compute_import_graph()
    )

    # ---- report ----
    print("=" * 72)
    print("INTEGRATION HEALTH  (%d exp cells, %d hdlab modules)" % (len(exp_files), len(hdlab_mods)))
    print("=" * 72)

    # 1. promotion candidates
    promote = sorted(
        ((len(c), n) for n, c in exp_module_consumers.items() if len(c) >= PROMOTE_MIN_CONSUMERS),
        reverse=True,
    )
    print("\n[1] PROMOTE CANDIDATES -- exp_ modules imported as shared code by >= %d cells" % PROMOTE_MIN_CONSUMERS)
    print("    (de-facto library trapped in experiments/ -> should be promoted to hdlab/)")
    if not promote:
        print("    (none -- clean)")
    for n_consumers, name in promote[:30]:
        print("    %3d  %s" % (n_consumers, name))
    if len(promote) > 30:
        print("    ... +%d more" % (len(promote) - 30))

    # 2. bypass + composed entry
    print("\n[2] FRONTIER BYPASS")
    print("    cells importing `from experiments import ...` (exp-as-module): %d / %d"
          % (len(bypass_cells), len(exp_files)))
    entry = [c for c in COMPOSED_ENTRY_CANDIDATES if os.path.exists(os.path.join(HDLAB_DIR, c))]
    print("    composed substrate entry (%s): %s"
          % ("/".join(COMPOSED_ENTRY_CANDIDATES), (", ".join(entry) if entry else "ABSENT -- no wired 'run the substrate' entry")))

    # 3. dead hdlab modules
    dead = sorted(m for m in hdlab_mods if len(hdlab_consumers.get(m, ())) == 0)
    print("\n[3] DEAD hdlab MODULES -- 0 detected consumers (quarantine/doc candidates): %d" % len(dead))
    for m in dead:
        print("    %s" % m)

    # grade heuristic
    print("\n" + "-" * 72)
    n_promote = len(promote)
    print("SUMMARY: %d promotion candidates, %d bypass cells, %d dead hdlab modules, entry=%s"
          % (n_promote, len(bypass_cells), len(dead), "yes" if entry else "NO"))
    print("Action: promote the top candidates into hdlab; create the composed entry if ABSENT.")
    print("-" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
