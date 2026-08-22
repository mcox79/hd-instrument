"""WHERE DID A SMOKE RUN PASS AND ITS FULL RUN NOT? -- the failure class the evidence gate cannot see.

FOUND BY ACCIDENT 2026-08-22, WHICH IS WHY THIS IS A SWEEP AND NOT A NOTE. While mapping the
grounding archive, `exp_context_conditioned_near_neighbour_v1_SMOKE_n600` appeared in the readable
set as a HARD_PASS. Its FULL run, same cell, reads `MIDDLE_BAND_FLOOR_HUGGING`.

    SMOKE_n600 : HARD_PASS
    full       : MIDDLE_BAND_FLOOR_HUGGING

**The smoke passed and the full run hugged the floor.** Both carry a CI, a null AND a floor, so
`verdict_evidence_gate` passes both -- it audits ONE FILE AT A TIME and this defect only exists
BETWEEN two files. Anyone counting HARD_PASS rows, or citing the cell by name, gets the smoke's
answer. I nearly filtered smoke rows out as noise before printing them.

WHY IT MATTERS BEYOND ONE CELL. A smoke run is smaller by design -- fewer items, fewer seeds, an
easier population. CLAUDE.md already records that "a smoke with smaller numbers does not test the
full run's arithmetic". This is the evaluative twin: a smoke with smaller numbers does not test the
full run's CONCLUSION either, and when the two disagree the smoke is the one that gets quoted,
because it is the one that says PASS.

WHAT THIS IS NOT. A disagreement is not automatically a defect -- a smoke SHOULD sometimes differ,
and a cell whose full run passes where the smoke failed is a cell that got BETTER with scale, which
is fine and is reported separately. The reportable direction is SMOKE PASSES, FULL DOES NOT.

Uses `verdict_evidence_gate.assess` for verdict reading -- the same instrument, never a copy, because
imitating it produced two wrong counts the day before this was written.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verdict_evidence_gate import DATA, assess          # noqa: E402

# Suffixes that mark a reduced-scale companion run. Matched case-insensitively at the END of a name,
# optionally followed by a size tag (_n150, _n600, _p120, ...).
SMOKE_SUF = re.compile(r"_(smoke|smoketest|selftest|self_test)([_-]?[a-z]*\d+)?$", re.I)


def base_name(name: str):
    """The full-run cell a smoke name belongs to, or None if this is not a smoke name."""
    m = SMOKE_SUF.search(name)
    return name[:m.start()] if m else None


def pairs():
    """Yield (smoke_name, full_name, smoke_assessment, full_assessment) for every matched pair."""
    seen = {}
    for dd in sorted(os.listdir(DATA)):
        if not dd.startswith("exp_"):
            continue
        mp = Path(DATA) / dd / "metrics.json"
        if mp.exists():
            seen[dd] = mp
    for name, mp in seen.items():
        base = base_name(name)
        if not base or base not in seen:
            continue
        a_s, a_f = assess(mp), assess(seen[base])
        if a_s and a_f:
            yield name, base, a_s, a_f


def main() -> int:
    smoke_pass_full_not, full_pass_smoke_not, agree = [], [], 0
    for sn, fn, a_s, a_f in pairs():
        if a_s["hard_pass"] and not a_f["hard_pass"]:
            smoke_pass_full_not.append((sn, fn, a_s["verdict"], a_f["verdict"]))
        elif a_f["hard_pass"] and not a_s["hard_pass"]:
            full_pass_smoke_not.append((sn, fn, a_s["verdict"], a_f["verdict"]))
        else:
            agree += 1
    total = len(smoke_pass_full_not) + len(full_pass_smoke_not) + agree
    print(f"matched smoke/full pairs: {total:,}")
    print(f"  agree                                    : {agree:,}")
    print(f"  FULL passes, smoke does not (got BETTER) : {len(full_pass_smoke_not):,}")
    print(f"  SMOKE PASSES, FULL DOES NOT              : {len(smoke_pass_full_not):,}   <-- reportable")
    print()
    if smoke_pass_full_not:
        print("EVERY CASE WHERE THE SMALL RUN PASSED AND THE REAL RUN DID NOT:")
        for sn, fn, vs, vf in sorted(smoke_pass_full_not):
            print(f"    {sn}")
            print(f"        smoke: {str(vs)[:90]}")
            print(f"        FULL : {str(vf)[:90]}")
    else:
        print("No smoke-passes-full-fails pairs found.")
    print()
    print("A single-file evidence gate cannot see this class: the defect exists BETWEEN two files.")
    return 0


def _self_test() -> int:
    """Controls, including the real case that motivated the sweep."""
    ok = True

    # POSITIVE: the known instance must be detected.
    found = [t for t in pairs() if t[0].startswith("exp_context_conditioned_near_neighbour_v1_SMOKE")]
    if not found:
        print("  FAIL: the motivating pair (context_conditioned_near_neighbour) was not matched")
        ok = False
    else:
        hits = [(s, f) for s, f, a_s, a_f in found if a_s["hard_pass"] and not a_f["hard_pass"]]
        if not hits:
            print("  FAIL: motivating pair matched but not flagged smoke-pass/full-fail")
            ok = False
        else:
            print(f"  PASS: motivating pair detected ({hits[0][0]})")

    # NEGATIVE: base_name must not fire on ordinary cell names, or every cell becomes a 'smoke'.
    for n in ("exp_reading_grounding_loop_cycle2_v1", "exp_graded_divisive_comparator_v1"):
        if base_name(n) is not None:
            print(f"  FAIL: {n} misread as a smoke name")
            ok = False
    else:
        print("  PASS: ordinary cell names are not misread as smoke names")

    # And it must actually match SOMETHING, or an empty result reads as 'no problems'.
    n_pairs = sum(1 for _ in pairs())
    if n_pairs < 10:
        print(f"  FAIL: only {n_pairs} pairs matched -- the matcher is probably broken, and an empty "
              f"sweep would read as a clean archive")
        ok = False
    else:
        print(f"  PASS: matcher finds {n_pairs:,} smoke/full pairs to compare")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_self_test() if "--self-test" in sys.argv else main())
