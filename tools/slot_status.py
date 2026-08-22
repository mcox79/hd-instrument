"""THE SIXTH PRIOR-WORK READ: is the organ you are about to improve actually CONNECTED?

WHY THIS EXISTS, and it is one specific failure on 2026-08-22. I spent four autoloop continuations
building the case for repairing the sensorimotor norms lookup -- measuring its coverage gain
(`0.6035 -> 0.7350`), proving its verb signal clears, quantifying which word classes it recovers --
and only then checked whether anything CALLS it. Nothing does: `read()` registers zero calls and
never even loads the table.

**That fact was already written down, in `hdlab/substrate.py`'s own slot table**, slot `B5`:

    "The organ EXISTS, self-tests, and is invoked by exp_sensorimotor_spoke_grounding_v1, but
     `read()` does not consult it, so it is NEEDS_ADAPTER and not FILLED."

CLAUDE.md lists FIVE prior-work reads -- the registry, `experiment_index.py`, `organ_map_cite.py`,
`symbol_corrections.py`, `cite_check.py`. **NOT ONE of them searches the slot table**, and measured
here: **no file in `tools/` or `verification/` reads it at all.** So the one document that says
whether an organ is WIRED was unreachable by every habit built to prevent exactly this.

The table holds **28 slots: 9 `FILLED`, 8 `NEEDS_ADAPTER`, 8 `EMPTY`, 3 `EXCLUDED`.** A
`NEEDS_ADAPTER` organ can be improved all day without a single downstream number moving.

*(Two of my own counts were wrong before this line settled: a regex over `Slot(` found 16 of the 28 --
hence the AST parse -- and this tool's first summary line printed "not FILLED" as `NEEDS_ADAPTER`,
reading 19 where the truth is 8. **BUILT-BUT-UNWIRED, NOTHING-BUILT-YET and DELIBERATELY-OUT need
different work and must never share a number.**)

Usage:
    python tools/slot_status.py                 # all 16 slots, status first
    python tools/slot_status.py sensorimotor    # every slot whose id/organ/need matches
    python tools/slot_status.py --self-test
"""

from __future__ import annotations

import ast
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# A DOC PARSED BY CODE IS COUPLED TO IT: this reads the `Slot(...)` calls in the file below. If that
# constructor is renamed or moved, this tool must change in the same commit.
SUBSTRATE = os.path.join(REPO_ROOT, "hdlab", "substrate.py")


def _const(node):
    """Fold a literal or an implicitly-concatenated string; return None for anything else."""
    try:
        return ast.literal_eval(node)
    except Exception:                                  # noqa: BLE001
        return None


def slots(path: str = SUBSTRATE):
    """[(slot_id, need, organ, status, rationale)] parsed from the real source, not a copy."""
    src = open(path, encoding="utf-8", errors="replace").read()
    out = []
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.Call) and getattr(node.func, "id", "") == "Slot"):
            continue
        args = node.args
        if len(args) < 4:
            continue
        sid, need, organ = _const(args[0]), _const(args[1]), _const(args[2])
        status = getattr(args[3], "id", None) or _const(args[3])
        rationale = _const(args[4]) if len(args) > 4 else ""
        if sid is None:
            continue
        out.append((sid, need or "", organ or "", str(status), rationale or ""))
    return out


def find(query: str, rows=None):
    rows = rows if rows is not None else slots()
    q = query.lower()
    return [r for r in rows if q in r[0].lower() or q in r[1].lower()
            or q in r[2].lower() or q in r[4].lower()]


def _print(rows, verbose):
    for sid, need, organ, status, rationale in rows:
        flag = "  " if status == "FILLED" else ">>"
        print("%s %-4s %-14s %-34s %s" % (flag, sid, status, organ[:34], need[:44]))
        if verbose and rationale:
            for i in range(0, min(len(rationale), 460), 100):
                print("        %s" % rationale[i:i + 100])


def run(argv):
    import collections
    rows = slots()
    terms = [a for a in argv if not a.startswith("--")]
    # COUNTS BEFORE RESULTS -- silence must never read as absence.
    # AND REPORT THE STATUSES SEPARATELY. The first draft of this line printed "not FILLED" as
    # NEEDS_ADAPTER and read 19 where the truth is 8 -- conflating BUILT-BUT-UNWIRED with
    # NOTHING-BUILT-YET and DELIBERATELY-OUT. Those need different work and must not share a number.
    c = collections.Counter(r[3] for r in rows)
    print("[slot-status] %d slots in hdlab/substrate.py: %s"
          % (len(rows), ", ".join("%s %d" % (k, c[k]) for k in sorted(c))))
    print("  FILLED = wired and live | NEEDS_ADAPTER = BUILT but not on the live path |"
          " EMPTY = nothing built | EXCLUDED = deliberately out of scope")
    if not terms:
        _print(sorted(rows, key=lambda r: (r[3] == "FILLED", r[0])), verbose=False)
        print("\n  >> = NOT wired into the live path. Improving one moves no downstream number.")
        print("  pass a term (e.g. `sensorimotor`) for the full rationale.")
        return 0
    for t in terms:
        hits = find(t, rows)
        print("\n  query %r -> %d slot(s)" % (t, len(hits)))
        if not hits:
            print("    no slot matches. That is NOT evidence the organ is wired -- it may simply")
            print("    not be in the slot table. Check the capability registry too.")
        _print(hits, verbose=True)
    return 0


def self_test():
    ok = True

    def check(c, label):
        nonlocal ok
        print("[self-test] %s %s" % ("PASS" if c else "FAIL", label),
              file=sys.stdout if c else sys.stderr)
        ok = ok and bool(c)

    rows = slots()
    check(len(rows) >= 10, "parses the real slot table (%d slots)" % len(rows))
    statuses = {r[3] for r in rows}
    check("FILLED" in statuses and "NEEDS_ADAPTER" in statuses,
          "both statuses present: %s" % sorted(statuses))

    # POSITIVE CONTROL -- the exact miss that motivated this tool must be findable.
    b5 = [r for r in rows if r[0] == "B5"]
    check(len(b5) == 1, "slot B5 exists")
    if b5:
        check(b5[0][3] == "NEEDS_ADAPTER", "B5 is NEEDS_ADAPTER, not FILLED")
        check("does not consult" in b5[0][4],
              "B5's rationale carries the sentence I read past")
    check(any(r[0] == "B5" for r in find("sensorimotor")),
          "searching 'sensorimotor' returns B5 -- the query I would actually have typed")

    # NEGATIVE CONTROL -- a nonsense term must return nothing, so a hit means something.
    check(find("zzqqxx_not_a_real_organ") == [],
          "NEGATIVE CONTROL: a nonsense term returns no slots")
    # and a known-FILLED organ must not be flagged, or the tool cries wolf
    filled = [r for r in rows if r[3] == "FILLED"]
    check(len(filled) >= 3, "at least 3 FILLED slots exist (%d)" % len(filled))

    print("[self-test] RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv else run(sys.argv[1:]))
