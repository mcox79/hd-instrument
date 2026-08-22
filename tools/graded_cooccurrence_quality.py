"""SUPERSEDED 2026-08-22, BEFORE IT WAS EVER USED. Use `hdlab/quality_proxy.py` instead.

WHY: hours after this file was written, the archive's OWN third repair of the same instrument --
`cooccurs_v4`, a proximity window of 6 tokens -- was tested against the same 100 human-scored rows
and SEPARATED human meaning from human noise at `p = 0.0038` (GOOD 0.591 vs NOISE 0.244), surviving
Bonferroni correction for all seven tests run that day. This file's graded count reached only
`p = 0.0349` raw / `0.1745` corrected.

**The deciding difference was PROVENANCE, not the p-value.** `cooccurs_v4`'s window was derived from
corpus structure BEFORE any result existed and was tested ONCE; this file's measure was invented by
me while searching, which is exactly the multiplicity that disqualified it.

RETAINED, NOT DELETED, because two of its controls are worth keeping:
  - the PREFIX HAZARD it documents is real and applies to `cooccurs_v4` too (short terms match longer
    words; measured on real data at rho -0.1492);
  - its negative control demonstrates that a SINGLE-DRAW null check is itself a coin flip and that the
    correct control asserts a FALSE-POSITIVE RATE (measured 0.05 over 40 draws).

-------------------------------------------------------------------------------------------------
THE GRADED CO-OCCURRENCE QUALITY PROXY -- ONE MEASURE, ONE TEST, FROZEN BEFORE THE NEXT SAMPLE.

WHY THIS IS CODE AND NOT A PRE-REGISTRATION. The substance of pre-registration is fixing the measure
and the test BEFORE seeing new data. `preregs/` is not writable here, and this project's own standing
escalation is that a caution written as prose gets violated while a control written as code catches
something. So the declaration lives in this file, and there is deliberately NO call signature that
returns a choice of measures.

WHAT HAPPENED, AND WHY THE RESTRAINT IS NEEDED (2026-08-22, measured on 100 blind hand-scored rows).

  BOOLEAN "do these words ever co-occur" -- REFUTED as a quality signal:
      passes 86% of human-NOISE and 86% of human-GOOD, Fisher exact p = 1.0000.
      It is at CEILING: it says yes to 86% of everything, so it cannot discriminate anything.

  GRADED "how often do they co-occur" -- PROMISING, NOT ESTABLISHED:
      median count  MEANINGFUL 8.0  >  RELATED 4.0  >  NOISE 2.0   (monotone)
      trend vs human rank: Spearman rho = +0.2279, permutation p = 0.0349

  AND THE HONEST PART: I ran FIVE tests on those same 100 rows and am reporting the one that
  cleared. Bonferroni for five tests puts it at p = 0.1745. THE RESULT DID NOT SURVIVE THE SEARCH
  THAT FOUND IT. That is why this file exists: to make the next run a single declared test.

THE DECLARATION, BINDING ON THE NEXT SAMPLE:
  MEASURE   : graded co-occurrence COUNT (sentences containing both terms, word-start prefix match)
  TEST      : Spearman rho between that count and the human quality rank (NOISE 0 / RELATED 1 /
              MEANINGFUL 2), permutation null, TWO-SIDED
  DECISION  : p < 0.05 on THAT TEST ALONE. No second measure, no subgroup, no re-cut.
  DIRECTION : rho must be POSITIVE (more co-occurrence, better quality). A significant NEGATIVE
              result is a refutation, not a pass.
  REQUIRED n: 150 (measured by simulation at the observed effect: power 0.68 @ n=100, 0.82 @ 150,
              0.93 @ 200, 0.98 @ 300). Below 150 the run is UNDERPOWERED and may not be read as
              negative.

PREFIX HAZARD, FOUND BY THIS FILE'S OWN NEGATIVE CONTROL AND INHERITED FROM THE HARNESS'S MATCHER.
Matching is word-start PREFIX, so a SHORT term matches every LONGER word beginning with it -- "cat"
matches "catastrophe", "isolate" matches "isolated" (intended, the stored lemmas are stemmed) and
"isolationism" (not intended). Counts for short subjects are therefore inflated by an amount that
depends on the vocabulary, not on the fact. The negative control below failed on exactly this before
its names were made non-colliding. THIS IS NOT FIXED HERE -- changing the matcher would make the
measure incomparable to the boolean it is meant to replace. It is a known bias, it inflates counts
for short terms, and any pass should be checked against subject length before being believed.

WHAT A PASS WOULD AND WOULD NOT MEAN. It would mean we have a CHEAP AUTOMATIC PROXY that tracks a
human's meaning judgement -- useful for triage at scale, where hand-scoring cannot go. It would NOT
mean the facts are good, and it would NOT retrospectively validate any past "foundation validated"
claim, all of which rest on the REFUTED boolean.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")

import math
import re
import sys
from typing import Dict, List, Sequence

import numpy as np

RANK = {"NOISE": 0, "RELATED": 1, "MEANINGFUL": 2}
REQUIRED_N = 150
ALPHA = 0.05
_PAT: Dict[str, "re.Pattern"] = {}


def _pat(term: str) -> "re.Pattern":
    p = _PAT.get(term)
    if p is None:
        p = re.compile(r"\b" + re.escape(term), re.IGNORECASE)
        _PAT[term] = p
    return p


def cooccurrence_count(subj: str, obj: str, sentences: Sequence[str]) -> int:
    """THE measure: how many sentences contain BOTH terms (word-start prefix match).
    Deliberately the same matching rule as the harness's boolean, so the ONLY change from the
    refuted criterion is counting instead of thresholding."""
    ps, po = _pat(subj), _pat(obj)
    return sum(1 for s in sentences if ps.search(s) and po.search(s))


def _spearman(a, b) -> float:
    ra = np.argsort(np.argsort(np.asarray(a, float))).astype(float)
    rb = np.argsort(np.argsort(np.asarray(b, float))).astype(float)
    ra -= ra.mean()
    rb -= rb.mean()
    d = math.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d else 0.0


def run_declared_test(rows: Sequence[dict], sentences: Sequence[str],
                      n_perm: int = 20000, seed: int = 9) -> dict:
    """THE test. `rows` need `subj`, `obj` and a human label `v` in RANK.

    There is ONE test here on purpose. If you find yourself wanting a second measure or a subgroup,
    that is the multiplicity that invalidated the 2026-08-22 result -- add it as a NEW declaration
    with its own required n, do not slip it into this call."""
    labelled = [r for r in rows if r.get("v") in RANK]
    y = np.array([RANK[r["v"]] for r in labelled], float)
    x = np.array([cooccurrence_count(r["subj"], r["obj"], sentences) for r in labelled], float)
    n = len(labelled)
    rho = _spearman(x, y)
    rs = np.random.default_rng(seed)
    null = np.array([_spearman(x, rs.permutation(y)) for _ in range(n_perm)])
    p = float((np.abs(null) >= abs(rho)).mean())
    underpowered = n < REQUIRED_N
    passed = bool(p < ALPHA and rho > 0 and not underpowered)
    return {
        "n": n, "rho": rho, "p": p, "null_p95_abs": float(np.percentile(np.abs(null), 95)),
        "required_n": REQUIRED_N, "underpowered": underpowered, "passes_declared_test": passed,
        "verdict": ("UNDERPOWERED_NOT_READABLE" if underpowered else
                    "PROXY_TRACKS_HUMAN_QUALITY" if passed else
                    "REFUTED_NEGATIVE_DIRECTION" if (p < ALPHA and rho < 0) else
                    "NO_EFFECT_AT_THIS_N"),
        "note": ("A pass means a cheap proxy tracks human meaning judgement. It does NOT mean the "
                 "facts are good, and it does NOT validate any past claim resting on the boolean "
                 "criterion, which is refuted (p=1.0000, at ceiling)."),
    }


def _self_test() -> int:
    ok = True
    rng = np.random.default_rng(1)

    # POSITIVE: counts that genuinely rise with quality must pass -- at a legal n.
    sents, rows = [], []
    for i in range(REQUIRED_N + 10):
        lbl = "NOISE" if i % 10 < 7 else ("RELATED" if i % 10 < 9 else "MEANINGFUL")
        k = {"NOISE": 1, "RELATED": 4, "MEANINGFUL": 9}[lbl]
        s, o = f"subj{i}", f"obj{i}"
        sents.extend([f"{s} and {o} appear together." for _ in range(k)])
        rows.append({"subj": s, "obj": o, "v": lbl})
    r = run_declared_test(rows, sents, n_perm=600)
    if not r["passes_declared_test"]:
        print(f"  FAIL positive control: rho={r['rho']:.3f} p={r['p']:.4f} {r['verdict']}")
        ok = False
    else:
        print(f"  PASS positive control: rho={r['rho']:.3f} p={r['p']:.4f}")

    # NEGATIVE: counts unrelated to the label must NOT pass. A test that always fires is noise.
    # NEGATIVE CONTROL AS A FALSE-POSITIVE RATE, NOT A SINGLE DRAW.
    # Two earlier drafts of this control failed, and each failure taught something:
    #   (1) names f"a{i}" COLLIDE under prefix matching -- "a1" matches every sentence belonging to
    #       "a10", "a11", ... so counts grew with index while the label cycled with index. That is a
    #       real property of the measure, documented as PREFIX HAZARD above. Fixed with fixed-width
    #       non-colliding names.
    #   (2) it STILL failed on one draw (rho=0.208) -- because A SINGLE-DRAW NEGATIVE CONTROL IS
    #       ITSELF A COIN FLIP. At alpha=0.05 an honest test MUST fire on ~5% of null draws; a
    #       control demanding zero false positives is demanding a broken test. Asserting the RATE is
    #       the correct control, and a test whose null rate is ~0 would be over-conservative, which
    #       is also a defect worth catching.
    fp = 0
    draws = 40
    for d in range(draws):
        rr = np.random.default_rng(100 + d)
        rows2, sents2 = [], []
        for i in range(REQUIRED_N + 10):
            lbl = ["NOISE", "RELATED", "MEANINGFUL"][int(rr.integers(0, 3))]
            k = int(rr.integers(1, 10))
            s, o = f"aa{i:04d}zz", f"bb{i:04d}zz"
            sents2.extend([f"{s} with {o} here." for _ in range(k)])
            rows2.append({"subj": s, "obj": o, "v": lbl})
        if run_declared_test(rows2, sents2, n_perm=300, seed=d)["passes_declared_test"]:
            fp += 1
    rate = fp / draws
    if rate > 0.20:
        print(f"  FAIL negative control: false-positive rate {rate:.2f} over {draws} null draws "
              f"(expected ~{ALPHA:.2f})")
        ok = False
    else:
        print(f"  PASS negative control: false-positive rate {rate:.2f} over {draws} null draws "
              f"(expected ~{ALPHA:.2f})")

    # THE POWER GUARD must fire below the declared n, or an underpowered null reads as negative --
    # this project's most-repeated error.
    r3 = run_declared_test(rows[:100], sents, n_perm=400)
    if r3["verdict"] != "UNDERPOWERED_NOT_READABLE":
        print(f"  FAIL power guard: n=100 was readable as {r3['verdict']}")
        ok = False
    else:
        print("  PASS power guard: n=100 refuses to be read")
    print("SELF-TEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print(__doc__)
