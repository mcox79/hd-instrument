"""THE MISSING TIE DIAGNOSTIC for the orthographic floor. Neither cell computed it.

WHY THIS EXISTS. `exp_orthographic_floor_vet_v1` reports that PURE SPELLING (`A6_TRIGRAM_ONLY`,
character-trigram cosine, zero substrate signal) beats the substrate's meaning read-out
(`A1_BASE`) at hit@1 by **0.087 vs 0.048, CIs non-overlapping**. That is a serious claim about the
architecture -- and the ONE check that could overturn it was never run.

**THE ENTIRE ADVANTAGE LIVES AT RANK 1. MEDIAN RANK IS IDENTICAL: 37.0 vs 37.0.** Over the full
ranking the two arms are indistinguishable; only the top slot separates them. Searching both
`metrics.json` files for `tie` / `n_tied` / `pessimist` returns **absent from both**, while
`CLAUDE.md` mandates the count in two separate sections -- both added after tie degeneracy produced
three false results in a single day.

*** THE TWO TIE-EXPOSED LINES, READ FROM THE VET TOOL'S SOURCE ***
1. `b = int(np.argmax(sc))`  -- **`argmax` breaks ties by ARRAY POSITION**, so when k candidates
   share the maximum, the "winner" is decided by anchor insertion order, not by score.
2. `ranks[...] = int(np.sum(sc > max(sc[gsel]))) + 1` -- **the STRICT inequality**, which counts
   every tie as BEATEN. That is the optimistic convention and it is the only one reported.

**A PREDICTION IS RECORDED HERE BEFORE THE RUN, so the result cannot be rationalised afterwards:**
for `A6_TRIGRAM_ONLY`, anchors sharing NO trigram with the query score EXACTLY 0.0, so ties should
be MASSIVE. If the max itself is 0.0, `argmax` returns an arbitrary anchor -- which should DEPRESS
A6's hit@1, not inflate it. **So the expected finding is that ties HURT the spelling arm, which
would STRENGTHEN the headline rather than overturn it.** *If the opposite comes back, the headline
is the artifact and this file is the reason we know.*

**AND THE DEGENERATE CASE, WHICH IS THE ONE THAT MATTERS:** where `t_cov` is False the arm scores
`np.zeros(...)` -- every candidate 0.0 -- and the strict-inequality rank then evaluates to
`sum(0 > 0) + 1 = 1`. **A PERFECT RANK FROM AN ARM CARRYING NO INFORMATION AT ALL.** This script
counts those items separately; they are the `empty representation scores perfectly` failure in its
exact documented form.

REUSES the VET tool's construction by IMPORT, never reimplemented: same corpus, buckets, space,
items, gold, eligibility and trigram matrix. Read-only; writes one metrics file of its own and
touches no landed artifact.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from collections import defaultdict  # noqa: E402
from datetime import datetime, timezone  # noqa: E402
from typing import Dict, List  # noqa: E402

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402

ANCHOR_NAME = "exp_orthographic_floor_tie_mass_v1"
OUT = os.path.join(_REPO, "data", ANCHOR_NAME)
os.makedirs(OUT, exist_ok=True)
EPS = 1e-12


def _lcp(a: str, b: str) -> int:
    k = 0
    for x, y in zip(a, b):
        if x != y:
            break
        k += 1
    return k


def main() -> int:
    t0 = time.time()
    sents = C3.build_corpus("full")
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, os.path.join(_REPO, "data",
                                                        "exp_orthographic_floor_vet_v1"))
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    items, _diag = C3.build_items(space, buckets, counts, C3.MAX_ITEMS)
    n = len(items)
    print("[tie] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, len(anchors), time.time() - t0),
          flush=True)

    t_mat, t_cov = MS.trigram_matrix(anchors)
    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9
    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    anchor_arr = np.array(anchors)

    arms = ("A1_BASE", "A6_TRIGRAM_ONLY")
    acc = {a: {"n_scored": 0, "tied_at_max": [], "any_tie": 0, "all_zero_scores": 0,
               "hit_optimistic": 0, "hit_pessimistic": 0,
               "rank_optimistic": [], "rank_pessimistic": []} for a in arms}

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(len(anchors), dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        elig &= mat_ok
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        gold = C3.gold_meaning_set(L)
        gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)

        q = space.bundle(L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        base = (mat[sel] @ q) / (mat_nrm[sel] * qn)
        tq = t_mat[pos[L]] if t_cov[pos[L]] else None
        trig = t_mat[sel] @ tq if tq is not None else np.zeros(sel.size)

        for a, sc in (("A1_BASE", base), ("A6_TRIGRAM_ONLY", trig)):
            A = acc[a]
            A["n_scored"] += 1
            mx = float(np.max(sc))
            tied = np.flatnonzero(sc >= mx - EPS)
            A["tied_at_max"].append(int(tied.size))
            if tied.size > 1:
                A["any_tie"] += 1
            if float(np.max(sc)) <= EPS and float(np.min(sc)) >= -EPS:
                A["all_zero_scores"] += 1

            # HIT, BOTH CONVENTIONS. optimistic = gold anywhere in the tied-at-max set (what a
            # lucky argmax would give); pessimistic = gold is the UNIQUE maximum.
            tied_names = set(str(x) for x in anchor_arr[sel[tied]])
            gold_in_tie = bool(tied_names & set(gold))
            A["hit_optimistic"] += 1 if gold_in_tie else 0
            A["hit_pessimistic"] += 1 if (gold_in_tie and tied.size == 1) else 0

            if gsel.size:
                g = float(np.max(sc[gsel]))
                beat = int(np.sum(sc > g + EPS))
                tie_g = int(np.sum(np.abs(sc - g) <= EPS)) - 1   # excl. gold itself
                A["rank_optimistic"].append(beat + 1)            # ties counted as BEATEN
                A["rank_pessimistic"].append(beat + tie_g + 1)   # ties counted as BEATING
        if (i + 1) % 500 == 0:
            print("[tie] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    out = {"anchor_name": ANCHOR_NAME,
           "what": "THE MISSING TIE DIAGNOSTIC for A1_BASE vs A6_TRIGRAM_ONLY; neither landed cell "
                   "computed tie mass or the pessimistic convention",
           "reuses": "exp_orthographic_floor_vet_v1 construction by import",
           "ts_iso": datetime.now(timezone.utc).isoformat(), "n_items": n, "arms": {}}
    for a in arms:
        A = acc[a]
        t = np.array(A["tied_at_max"], dtype=np.float64)
        ro = np.array(A["rank_optimistic"], dtype=np.float64)
        rp = np.array(A["rank_pessimistic"], dtype=np.float64)
        ns = max(1, A["n_scored"])
        out["arms"][a] = {
            "n_scored": A["n_scored"],
            "mean_tied_at_max": round(float(t.mean()), 4) if t.size else None,
            "median_tied_at_max": float(np.median(t)) if t.size else None,
            "max_tied_at_max": int(t.max()) if t.size else None,
            "frac_items_with_ANY_tie_at_max": round(A["any_tie"] / ns, 6),
            "frac_items_ALL_SCORES_ZERO": round(A["all_zero_scores"] / ns, 6),
            "hit_at_1_optimistic": round(A["hit_optimistic"] / ns, 6),
            "hit_at_1_pessimistic": round(A["hit_pessimistic"] / ns, 6),
            "median_rank_optimistic": float(np.median(ro)) if ro.size else None,
            "median_rank_pessimistic": float(np.median(rp)) if rp.size else None,
            "n_rank_scored": int(ro.size),
        }
    path = os.path.join(OUT, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, path)

    print("\n" + "=" * 90)
    print("TIE DIAGNOSTIC -- the check neither landed cell ran")
    print("=" * 90)
    for a in arms:
        r = out["arms"][a]
        print("\n%s  (n=%d)" % (a, r["n_scored"]))
        print("   tied at max: mean %.3f  median %s  max %s"
              % (r["mean_tied_at_max"], r["median_tied_at_max"], r["max_tied_at_max"]))
        print("   items with ANY tie at max : %.1f%%" % (100 * r["frac_items_with_ANY_tie_at_max"]))
        print("   items with ALL scores 0.0 : %.1f%%   <- zero information, argmax arbitrary"
              % (100 * r["frac_items_ALL_SCORES_ZERO"]))
        print("   hit@1   optimistic %.4f   pessimistic %.4f"
              % (r["hit_at_1_optimistic"], r["hit_at_1_pessimistic"]))
        print("   median rank  optimistic %s   pessimistic %s"
              % (r["median_rank_optimistic"], r["median_rank_pessimistic"]))
    print("\nwrote %s" % path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
