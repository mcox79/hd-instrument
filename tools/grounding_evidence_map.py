"""WHICH GROUNDING RESULTS CARRY THE EVIDENCE THEIR VERDICT CLAIMS -- built ON the census, not beside it.

WHY THIS EXISTS AS A TOOL. Owner 2026-08-22: "we did a fuckton of work on grounding. make sure you
understand all of it." There are 237 such cells. Reading verdict strings does not answer it: only
0.5% of archive-wide HARD_PASS carry both a CI and a null, so the label is not the finding.

WHY IT IMPORTS `assess` INSTEAD OF MATCHING PATTERNS ITSELF. Measured the same day, on me: I counted
the evidenced subset twice and was wrong twice -- 198 with my own regexes, then 58 using the census
tool's OWN patterns in my own loop, against a true 14. Two causes, both invisible without the
comparison:

  1. I matched the string "HARD_PASS" ANYWHERE in the file. `assess()` reads the VERDICT FIELD, and
     prefers `final_verdict` over `verdict`. Cells merely MENTIONING the label in a gate-name field
     were counted as passes -- `exp_grounding_quality_readout_v1` is really STRUCTURAL_PASS_PENDING_B3
     with no null at all.
  2. The census population is directories starting with `exp_` only. I scanned every directory.

So this module calls `assess()` and does no detection of its own. THE SELF-TEST PINS THAT: it
recomputes the archive-wide "both a CI and a null" count and FAILS unless it matches what
`verdict_evidence_gate --census` reports. If a future edit reintroduces private matching, the number
drifts and the test fails.

WHAT A PASS HERE MEANS, AND MOSTLY WHAT IT DOES NOT. Carrying a CI and a null is the CHEAPEST hurdle.
The gate's own docstring: it cannot see a written-in answer, gold defined by the rule under test, a
skipped stronger floor, or a gate tuned after the fact. A cell can pass this and still be worthless.
This narrows 237 cells to a readable few; it does not certify them.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from verdict_evidence_gate import DATA, assess          # noqa: E402  THE instrument, not a copy

GROUND = re.compile(r"ground", re.I)

# The count `verdict_evidence_gate.py --census` reports for "carries BOTH a CI and a NULL".
# The self-test fails if this module's own walk stops reproducing it.
CENSUS_BOTH_CI_AND_NULL = 14


def walk(only_grounding: bool = True):
    """Yield (name, assessment) over the SAME population the census uses: data/exp_*/metrics.json."""
    for dd in sorted(os.listdir(DATA)):
        if not dd.startswith("exp_"):
            continue
        mp = Path(DATA) / dd / "metrics.json"
        if not mp.exists():
            continue
        a = assess(mp)
        if not a:
            continue
        if only_grounding:
            try:
                if not (GROUND.search(dd) or GROUND.search(mp.read_text(
                        encoding="utf-8", errors="replace")[:200000])):
                    continue
            except Exception:
                continue
        yield dd, a


def main() -> int:
    rows = list(walk(only_grounding=True))
    hp = [(n, a) for n, a in rows if a["hard_pass"]]
    both = [(n, a) for n, a in hp if a["has_ci"] and a["has_null"]]
    print(f"grounding cells with a metrics.json (census population): {len(rows):,}")
    print(f"  verdict is HARD_PASS                                 : {len(hp):,}")
    print(f"  ...AND carries BOTH a CI and a null                  : {len(both):,}")
    print(f"  ...AND a floor as well                               : "
          f"{sum(1 for _n, a in both if a['has_floor']):,}")
    print()
    print("THE READABLE SET -- grounding HARD_PASS carrying CI + null (floor marked):")
    for n, a in both:
        print(f"    {'[+floor]' if a['has_floor'] else '[no flr]'} {n}")
    print()
    ident = [n for n, a in rows if a["seeds_bit_identical"]]
    if ident:
        print(f"WARNING -- grounding cells whose per-seed numbers are BIT-IDENTICAL ({len(ident)}):")
        for n in ident:
            print(f"    {n}   <- n seeds that are one measurement")
    print()
    print("Carrying a CI and a null is the CHEAPEST hurdle. It does not certify any cell:")
    print("the gate cannot see a written-in answer, circular gold, a skipped floor or a tuned gate.")
    return 0


def _self_test() -> int:
    """POSITIVE CONTROL AGAINST THE AUTHORITY. This module must reproduce the census's own count."""
    ok = True
    n_both = sum(1 for _n, a in walk(only_grounding=False)
                 if a["hard_pass"] and a["has_ci"] and a["has_null"])
    if n_both != CENSUS_BOTH_CI_AND_NULL:
        print(f"  FAIL: archive-wide both-CI-and-null = {n_both}, census says "
              f"{CENSUS_BOTH_CI_AND_NULL}. This module has drifted from the instrument.")
        ok = False
    else:
        print(f"  PASS: reproduces the census exactly ({n_both} archive-wide)")

    # NEGATIVE CONTROL: the cell that fooled the author must NOT be classed HARD_PASS.
    mp = Path(DATA) / "exp_grounding_quality_readout_v1" / "metrics.json"
    if mp.exists():
        a = assess(mp)
        if a and a["hard_pass"]:
            print("  FAIL: exp_grounding_quality_readout_v1 read as HARD_PASS "
                  "(its verdict is STRUCTURAL_PASS_PENDING_B3) -- string matching has crept back in")
            ok = False
        else:
            print("  PASS: the known false positive is correctly NOT a HARD_PASS")

    # The grounding filter must actually exclude something, or it is not a filter.
    n_all = sum(1 for _ in walk(only_grounding=False))
    n_gr = sum(1 for _ in walk(only_grounding=True))
    if not (0 < n_gr < n_all):
        print(f"  FAIL: grounding filter excluded nothing ({n_gr} of {n_all})")
        ok = False
    else:
        print(f"  PASS: grounding filter selects {n_gr:,} of {n_all:,}")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(_self_test() if "--self-test" in sys.argv else main())
