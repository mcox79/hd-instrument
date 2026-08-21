"""Rank the 81 islanded modules by EVIDENCE, so wiring is not 81 guesses.

**THE PROBLEM THIS SOLVES.** 150 modules on disk, all registered, **36 loaded by a live read, 81
`gate=WIRE` and never called by reading.** That 81 is the real backlog. *But wiring them on
assumption would be 81 fresh chances to repeat today's pattern -- proposing before measuring, which
cost four withdrawn claims in one session.*

**SO EACH IS SCORED ON WHAT THE RESULTS ARCHIVE ACTUALLY SAYS ABOUT IT**, in three tiers:

| tier | meaning |
|---|---|
| **PROVEN + ISLANDED** | landed cells with a passing verdict, and the reading path never calls it. **The strongest case for wiring: someone already showed it works.** |
| **TRIED, NOT PASSING** | landed cells, none passing. **Wiring this is a build, not a connection** -- and the archive already says what went wrong |
| **NEVER EVALUATED** | no landed cells name it. **A wiring target with no evidence at all** -- the most dangerous kind, because it looks free |

⚠️ **TIER 3 MEANS "NO LANDED CELL", NOT "NO EVIDENCE", AND THAT IS THIS TOOL'S OWN BLIND SPOT.**
*Measured on its first run: `sensorimotor_spoke` lands in tier 3, yet its complementarity result --
the one route measured NOT subsumed by counting -- exists in a `scratch/` script cited from a note.
`experiment_index.py` correctly returns nothing, because it was never a cell.* **This is the SAME
blind spot found in `prior_work_check.py` one turn earlier and fixed there by adding a notes read.
It is recorded here rather than silently repeated: a tier-3 placing means the RESULTS ARCHIVE is
silent, and this project keeps significant findings in notes.**

⚠️ **AND EVIDENCE CAN BE FILED UNDER A SIBLING'S NAME.** *`prelim_tier` lands in tier 3 while
`three_tier_loop` sits in tier 1 with 12 cells -- they are the same proven subsystem. A per-module
name match splits a subsystem's evidence across tiers.*

⚠️ **A HIGH SCORE HERE IS NOT PERMISSION TO WIRE.** It says evidence exists, not that the evidence is
about reading. *A cell can HARD_PASS on its own bench and still contribute nothing to the loop -- the
day's own lesson was that a rubric win inverted on the task.* This ranks where to look, nothing more.
"""
from __future__ import annotations

import json
import os
import re
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for _p in (_REPO, os.path.join(_REPO, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

INDEX = os.path.join(_REPO, "data", "experiment_index.jsonl")
PASSY = re.compile(r"HARD_PASS|^PASS|REPLICATED|_REAL\b|VALIDATED|PROVEN|SURVIVED", re.I)
FAILY = re.compile(r"HARD_FAIL|^FAIL|REFUTED|VOID|INCONCLUSIVE|NOT_|NO_|UNDERPOWERED|COLLAPSE", re.I)


def main():
    import hdlab.substrate as S

    # ---- which modules does a live read actually touch?
    sub = S.Substrate()
    sub.read(n_sentences=60)
    live = {m.split(".")[-1] for m in sys.modules if m.startswith("hdlab.")}
    on_disk = sorted(f[:-3] for f in os.listdir(os.path.join(_REPO, "hdlab"))
                     if f.endswith(".py") and not f.startswith("_"))
    islanded = [m for m in on_disk if m not in live]
    print("%d modules on disk, %d live, %d islanded" % (len(on_disk), len(live & set(on_disk)),
                                                        len(islanded)))

    if not os.path.exists(INDEX):
        print("experiment index missing at %s -- run `experiment_index.py build`" % INDEX)
        return 1
    rows = []
    for line in open(INDEX, encoding="utf-8"):
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    print("scanned %d indexed cells" % len(rows))

    blobs = []
    for r in rows:
        blobs.append(((json.dumps(r).lower()), str(r.get("verdict") or ""),
                      str(r.get("name") or r.get("cell") or "")))

    proven, tried, never = [], [], []
    for m in islanded:
        key = m.lower()
        hits = [(v, n) for b, v, n in blobs if key in b]
        if not hits:
            never.append(m)
            continue
        good = [(v, n) for v, n in hits if PASSY.search(v) and not FAILY.search(v)]
        (proven if good else tried).append((m, len(hits), good[:2]))

    proven.sort(key=lambda t: -t[1])
    print("\n" + "=" * 90)
    print("TIER 1 -- PROVEN AND ISLANDED (%d). Someone already showed it works; reading never calls it."
          % len(proven))
    print("=" * 90)
    for m, n, good in proven[:24]:
        print("  %-34s %2d cells | %s" % (m, n, (good[0][0][:60] if good else "")))
    if len(proven) > 24:
        print("  ... and %d more" % (len(proven) - 24))

    print("\n" + "=" * 90)
    print("TIER 2 -- TRIED, NOT PASSING (%d). Wiring these is a BUILD; the archive says why." % len(tried))
    print("=" * 90)
    for m, n, _ in sorted(tried, key=lambda t: -t[1])[:12]:
        print("  %-34s %2d cells" % (m, n))
    if len(tried) > 12:
        print("  ... and %d more" % (len(tried) - 12))

    print("\n" + "=" * 90)
    print("TIER 3 -- NEVER EVALUATED (%d). No landed cell names them. **The most dangerous tier,"
          % len(never))
    print("because a wiring target with no evidence looks free.**")
    print("=" * 90)
    for i in range(0, min(len(never), 45), 3):
        print("  " + "  ".join("%-28s" % x for x in never[i:i + 3]))
    if len(never) > 45:
        print("  ... and %d more" % (len(never) - 45))

    print("\n" + "=" * 90)
    print("A TIER-1 PLACING IS NOT PERMISSION TO WIRE. It says evidence EXISTS, not that the evidence")
    print("is about READING. A cell can HARD_PASS on its own bench and add nothing to the loop -- today")
    print("a rubric win inverted completely when measured on a task. This ranks where to LOOK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
