"""DOES THIS RESULT CARRY THE EVIDENCE ITS VERDICT CLAIMS? A gate, and an archive-wide census.

WHY (2026-08-18, four vetting passes, 24 claimed HARD_PASS cells, ZERO UPHELD AS CLAIMED).

The passes kept finding the same shape rather than the same bug, and the fourth pass named the
cause: **not one of six cells computed a single confidence interval, null distribution or p-value.**
Every HARD_PASS in that batch was a point estimate compared to another point estimate, several at
gate margins of exactly 0.0 (`HP_CONTROL_SEP = 0.0`, `CONTRAST_EPS = 0.0`). That is not a scoring
accident. It is the method the archive was built with, and it is why the results do not survive
being read.

Representative failures, all from cells whose verdict string said HARD_PASS:
  - a causal-link organ that re-ran to a BIT-IDENTICAL 0.9722 when its gold links were replaced by
    RANDOM PAIRS -- the answer was written in and read straight back;
  - a baseline SWEPT until it failed ("the smallest min_dist that keeps mr_control >= the can-fail
    floor while driving mr_integration to 0.0000");
  - a self-learning loop whose own SCRAMBLE control scored HIGHER than the treatment;
  - a "held-out" set of 16 words sharing ONE hand-written tag vector with the seeds;
  - a 12-line `Counter` with no substrate reproducing a headline 8/8 exactly.

Four of those five are invisible to any automated check. **The one thing that IS mechanically
checkable is whether the file contains the evidence a verdict of that strength requires** -- and
that check is cheap, unambiguous, and would have flagged most of this batch before anyone read it.

WHAT IT CHECKS, per metrics.json:
  CI       any interval / half-width / Wilson / bootstrap bound
  NULL     any permutation, scramble, shuffle or explicitly-named null distribution
  FLOOR    any named floor, baseline or control the result is scored against
  SEEDS    whether per-seed numbers are BIT-IDENTICAL (n seeds that are one measurement)

A HARD_PASS missing CI or NULL is reported `EVIDENCE_INSUFFICIENT`. That is a statement about the
FILE, not about the science: the result may well be true. It means the file does not contain what
would be needed to know.

WHAT IT CANNOT DO, stated so nobody mistakes a pass for a verdict. It cannot see whether the answer
was written in, whether the gold is defined by the rule under test, whether a stronger floor was
computable and skipped, or whether a gate was tuned after the fact. **A cell can pass this gate and
still be worthless.** `tools/refloor_sweep.py` is the cautionary tale: an earlier attempt to catch
those semantically FAILED ITS OWN SPOT-CHECK and is marked unreliable. Reading the cell remains the
only method that works; this gate only makes the cheapest failure visible without reading.

USAGE
  python tools/verdict_evidence_gate.py --census        # archive-wide: how bad is it, in numbers
  python tools/verdict_evidence_gate.py --cell NAME     # one cell, with the evidence it does carry
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

# `confidence` ALONE WAS A BUG AND IT INFLATED THE HEADLINE NUMBER. It matched
# `lookup_confidence` and `high_confidence_idxs` -- fields that are model confidences, not
# intervals -- so two cells with NO interval of any kind entered the "best evidenced" shortlist and
# the Director quoted 26 cells / 1.0% to the owner. Caught by the vetting agent reading those two
# cells. Only interval-shaped names count.
CI_PAT = re.compile(r"ci95|ci_9|ci_low|ci_high|conf_int|confidence_interval|half_width|\bhw\b|"
                    r"wilson|bootstrap|credible|lower_bound|upper_bound", re.I)
NULL_PAT = re.compile(r"permut|scramble|shuffl|null_|_null|p95|pval|p_value|binomtest|"
                      r"exact_test|mcnemar|z_score|montecarlo", re.I)
PARTS_PAT = re.compile(r"per_unit|per_arm|per_set|per_seed|per_process|per_triple|per_encoder|"
                       r"per_row|per_item|per_cell|per_dimension|curve_by|_per_arm|_per_set|"
                       r"arm_accuracy|per_spoke|per_draw|_per_encoder", re.I)
LIMIT_PAT = re.compile(r"honest_scope|honest_claim|hp_scope|scope_limit|limitations?|caveats?|"
                       r"not_claimed|does_not_claim|out_of_scope|known_limit|narrowing", re.I)
FLOOR_PAT = re.compile(r"floor|baseline|control|chance|prototype|orthographic|frequency_only|"
                       r"random_", re.I)


def _keys(obj, prefix="", out=None, depth=0):
    if out is None:
        out = []
    if depth > 12:
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.append(str(k))
            _keys(v, prefix, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj[:25]:
            _keys(v, prefix, out, depth + 1)
    return out


def _seed_blocks(obj, out=None, depth=0):
    """Collect per-seed result blocks so bit-identical 'n seeds' can be detected."""
    if out is None:
        out = []
    if depth > 10:
        return out
    if isinstance(obj, dict):
        seedish = [k for k in obj if re.fullmatch(r"seed[_-]?\w+", str(k), re.I)]
        if len(seedish) >= 2:
            out.append([json.dumps(obj[k], sort_keys=True) for k in seedish])
        for v in obj.values():
            _seed_blocks(v, out, depth + 1)
    elif isinstance(obj, list):
        for v in obj[:25]:
            _seed_blocks(v, out, depth + 1)
    return out


def assess(mp: Path):
    try:
        d = json.loads(mp.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None
    blob = " ".join(_keys(d))
    verdict = ""
    # `final_verdict` FIRST, added 2026-08-21. This tool read `verdict` and ignored `final_verdict`
    # -- the identical defect found and fixed in tools/experiment_index.py the same day, where it
    # showed the wrong state for 9 cells and nothing for 2. MEASURED BLAST RADIUS HERE, so nobody
    # inflates it: of 7,812 cells with a metrics.json, 9 carry a differing `final_verdict` and
    # exactly ONE flips the HARD_PASS classification --
    # exp_stated_entity_fate_reading_extractor_v2_highprecision, whose `verdict` is
    # STRICT_READY_PENDING_HANDCHECK while its `final_verdict` is HARD_PASS. That cell was
    # therefore never audited by this gate at all. One cell does not move the census percentages;
    # it does mean the census population was mis-derived, which is worth fixing for its own sake.
    for k in ("final_verdict", "verdict", "VERDICT", "verdict_msg"):
        if isinstance(d.get(k), str) and d[k].strip():
            verdict = d[k]
            break
    seeds_identical = any(len(set(b)) == 1 for b in _seed_blocks(d) if len(b) >= 2)
    return {
        "verdict": verdict,
        "hard_pass": "HARD_PASS" in verdict.upper().replace("-", "_"),
        "has_ci": bool(CI_PAT.search(blob)),
        "has_null": bool(NULL_PAT.search(blob)),
        "has_floor": bool(FLOOR_PAT.search(blob)),
        "seeds_bit_identical": seeds_identical,
        # TWO CHECKS ADDED 2026-08-21, from a constraint-check run over eight standing claims that
        # went 3 PASS / 5 KILL. The split was not random: all three passes were result notes
        # carrying (a) the constituent values behind the headline, (b) a control, (c) a stated
        # limit. All five kills were summary headlines or same-day inferences with none of those.
        # `has_ci`/`has_null` above already cover (b). These cover (a) and (c).
        #
        # (a) HAS_PARTS -- can the headline be RE-DERIVED? Every kill was caught by re-deriving an
        # aggregate from its parts and finding they disagreed (a subset out-recalling its whole; a
        # paired figure matching its per-set mean exactly). A cell that reports only aggregates
        # cannot be checked that way at all. Presence of a >=2-entry per-arm/per-set structure, NOT
        # an inference about values -- deliberately, because tonight a value-inferring detector of
        # mine fired 3,990 false positives on dates.
        # ⚠️ FALSE means NOT FOUND UNDER THE ARCHIVE'S NAMING CONVENTION -- it does NOT mean absent.
        # Verified counter-example: exp_stated_entity_fate_reading_extractor_v2_highprecision reads
        # parts=False and limit=False, yet its claim was independently checked and HOLDS. Its parts
        # live in a SIBLING file (_survivors_handcheck_adjudicated.json, 100 per-row verdicts) and
        # under `error_category_counts`; its limit is free text in `hand_check.note` ("fresh random
        # sample drawn AFTER the hardening... independent of the v1 sample the filters were designed
        # from"). This gate reads metrics.json only. Treat a False as "go and look", never as a
        # finding -- an absence claim requires an enumeration, not a failed pattern match.
        "has_parts": bool(PARTS_PAT.search(blob)),
        # (c) HAS_LIMIT -- does it say what it does NOT cover? Matched on STRUCTURED FIELD NAMES the
        # archive already uses (`honest_scope`, `HP_SCOPE`, `honest_claim`, `caveat`...), never on
        # free text, because a free-text keyword detector here is the cry-wolf failure this project
        # has already paid for twice (49/49 false positives once, 3,990 tonight).
        "has_limit": bool(LIMIT_PAT.search(blob)),
    }


def census() -> int:
    n, hp = 0, 0
    c = collections.Counter()
    worst = []
    for dd in sorted(os.listdir(DATA)):
        if not dd.startswith("exp_"):
            continue
        mp = DATA / dd / "metrics.json"
        if not mp.exists():
            continue
        a = assess(mp)
        if not a:
            continue
        n += 1
        if a["seeds_bit_identical"]:
            c["ANY__seeds_bit_identical"] += 1
        if not a["hard_pass"]:
            continue
        hp += 1
        if a["has_ci"]:
            c["HP__has_ci"] += 1
        if a["has_null"]:
            c["HP__has_null"] += 1
        if a["has_floor"]:
            c["HP__has_floor"] += 1
        if a["has_ci"] and a["has_null"]:
            c["HP__has_BOTH_ci_and_null"] += 1
        else:
            c["HP__EVIDENCE_INSUFFICIENT"] += 1
            worst.append(dd)
        if a["seeds_bit_identical"]:
            c["HP__seeds_bit_identical"] += 1
    # Counts FIRST and ALWAYS, so an empty result is never mistaken for a clean archive.
    print(f"[census] scanned {n:,} landed metrics.json; {hp:,} claim HARD_PASS\n")
    if not hp:
        return 1
    def pct(k):
        return f"{c[k]:>6,}  ({100.0*c[k]/hp:5.1f}% of HARD_PASS)"
    print(f"  carries a CI / interval          {pct('HP__has_ci')}")
    print(f"  carries a NULL / permutation     {pct('HP__has_null')}")
    print(f"  carries a FLOOR / baseline       {pct('HP__has_floor')}")
    print(f"  carries BOTH a CI and a NULL     {pct('HP__has_BOTH_ci_and_null')}")
    print(f"  EVIDENCE_INSUFFICIENT            {pct('HP__EVIDENCE_INSUFFICIENT')}")
    print(f"  per-seed numbers BIT-IDENTICAL   {pct('HP__seeds_bit_identical')}")
    print(f"\n  (across ALL landed cells, bit-identical seeds: {c['ANY__seeds_bit_identical']:,})")
    print("\n  EVIDENCE_INSUFFICIENT means the FILE lacks what a verdict of that strength needs.")
    print("  It is NOT a claim that the science is wrong -- and passing is NOT a claim that it is")
    print("  right: this gate cannot see a written-in answer, a tuned gate, or a skipped floor.")
    print(f"\n  first 12 EVIDENCE_INSUFFICIENT HARD_PASS cells:")
    for w in worst[:12]:
        print(f"    {w}")
    return 0


def one(cell: str) -> int:
    mp = DATA / cell / "metrics.json"
    if not mp.exists():
        print(f"no metrics.json for {cell}", file=sys.stderr)
        return 1
    a = assess(mp)
    print(f"=== {cell}")
    print(f"  verdict           {a['verdict'][:150]}")
    print(f"  HARD_PASS         {a['hard_pass']}")
    print(f"  has CI            {a['has_ci']}")
    print(f"  has NULL          {a['has_null']}")
    print(f"  has FLOOR         {a['has_floor']}")
    print(f"  seeds identical   {a['seeds_bit_identical']}")
    if a["hard_pass"] and not (a["has_ci"] and a["has_null"]):
        print("  -> EVIDENCE_INSUFFICIENT: claims HARD_PASS without both a CI and a null.")
    return 0


def main() -> int:
    if "--cell" in sys.argv:
        return one(sys.argv[sys.argv.index("--cell") + 1])
    if "--census" in sys.argv:
        return census()
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
