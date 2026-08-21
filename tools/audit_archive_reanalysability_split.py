"""Split "saved no output list" into RECOVERABLE and GENUINELY LOST -- because they are not the same.

**THE DISTINCTION THE FIRST SCAN COULD NOT MAKE, AND WITHOUT WHICH ITS 96.5% IS MISLEADING:**

  * A cell that scores a **FIXED, NAMED item set** (a gold file, a vocabulary rank range, a
    deterministic seed + corpus) has **lost nothing** -- the population is reconstructible from the
    named source, so a re-score is cheap even with no list persisted.
  * A cell that scores a population **THE RUN ITSELF PRODUCED** -- terms it happened to bank,
    concepts it happened to form -- has **lost it permanently.** That is the foraging case: which
    604 words were banked is a fact about that execution and exists nowhere else.

**Only the second class is the defect.** Reporting the first class as a defect would be exactly the
overclaim this session has already made twice, so the split is computed rather than assumed.

HEURISTIC, and stated as such: a cell is called RECOVERABLE if its metrics name a gold/dataset/
probe-range/fixed-seed source. That over-credits (a named gold set does not prove the SCORED
population came from it), so **GENUINELY-LOST is a LOWER bound** -- the opposite direction of bias
from the first scan, which is the point of running both.
"""
from __future__ import annotations

import json
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(_REPO, "data")
SCORE_HINTS = ("coverage", "hits", "accuracy", "precision", "recall", "agreement", "f1")
FIXED_HINTS = ("gold", "dataset", "probe_range", "heldout_probe_range", "item_file",
               "eval_set", "benchmark", "testset", "test_set", "gold_path")
GENERATED_HINTS = ("banked", "n_grounded", "grounded", "concepts_formed", "anchors",
                   "n_distinct_sources_banked", "consolidated", "emergent")
MIN_LIST = 20


def str_lists(o, depth=0):
    if depth > 6:
        return
    if isinstance(o, dict):
        for v in o.values():
            yield from str_lists(v, depth + 1)
    elif isinstance(o, list):
        if o and all(isinstance(x, str) for x in o):
            yield len(o)
        else:
            for v in o[:50]:
                yield from str_lists(v, depth + 1)


def main():
    both = fixed_only = gen_only = neither = 0
    lost_hp = []
    for name in sorted(os.listdir(DATA)):
        d = os.path.join(DATA, name)
        mp = os.path.join(d, "metrics.json")
        if not os.path.isdir(d) or not os.path.exists(mp):
            continue
        try:
            with open(mp, encoding="utf-8") as fh:
                m = json.load(fh)
        except Exception:
            continue
        blob = json.dumps(m).lower()
        if not any(h in blob for h in SCORE_HINTS):
            continue
        if max(list(str_lists(m)) or [0]) >= MIN_LIST:
            continue                                    # persisted something; not at risk
        has_fixed = any(h in blob for h in FIXED_HINTS)
        has_gen = any(h in blob for h in GENERATED_HINTS)
        if has_fixed and has_gen:
            both += 1
        elif has_fixed:
            fixed_only += 1
        elif has_gen:
            gen_only += 1
            if "HARD_PASS" in str(m.get("verdict", "")):
                lost_hp.append(name)
        else:
            neither += 1

    tot = both + fixed_only + gen_only + neither
    print("cells scoring a population with NO persisted output list: %d\n" % tot)
    print("  %5d  (%4.1f%%)  scored a FIXED named set only -> RECOVERABLE, not a defect"
          % (fixed_only, 100.0 * fixed_only / max(1, tot)))
    print("  %5d  (%4.1f%%)  scored a RUN-GENERATED population only -> GENUINELY LOST"
          % (gen_only, 100.0 * gen_only / max(1, tot)))
    print("  %5d  (%4.1f%%)  mentions BOTH -> ambiguous, needs reading" % (both, 100.0 * both / max(1, tot)))
    print("  %5d  (%4.1f%%)  neither hint -> unclassified" % (neither, 100.0 * neither / max(1, tot)))
    print("\nGENUINELY-LOST is a LOWER bound (a named gold set is credited as recoverable even when")
    print("the scored population may not have come from it). The first scan's 96.5% was an UPPER")
    print("bound. The truth is between them, and BOTH are reported rather than either alone.")
    print("\n%d of the genuinely-lost are HARD_PASS. First 20:" % len(lost_hp))
    for n in lost_hp[:20]:
        print("   %s" % n[:70])
    return 0


if __name__ == "__main__":
    sys.exit(main())
