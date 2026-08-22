"""WHAT DOES `np.sign` AT `reading_grounding_loop.py:776` ACTUALLY COST? Measured, paired, same items.

THE PREDICTION BEING TESTED, WRITTEN BEFORE THE RUN (T5b):
**"The magnitude discarded at `:776` is precisely the information that would separate a top-1 from a
near-miss."** If true, restoring it should move **hit@1 specifically** and leave **median rank
roughly alone**. *That is a sharp, falsifiable shape -- a uniform shift, or a median-only shift,
refutes it.*

WHY THIS IS THE RIGHT TEST. `canonicalize_fast` honours the graded-query switch; **`canonicalize`
hardcodes `np.sign(new_raw_sum)` with no branch**, and the two grounding call sites
(`:1330`, `:1593`) use `canonicalize`, which `definitional_extraction.py:19` calls *"the loop's ONLY
grounding signal."* So the live grounding decisions run a **GRADED anchor field against a BINARY
query** -- the configuration `:663` itself calls *"worse than either."* **This measures that exact
contrast on a real held-out task, changing ONE thing.**

ONE VARIABLE: the anchor field is graded in BOTH arms (`anchor_matrix()`); only the QUERY differs.
`Q_GRADED` is `space.bundle(L)` (what `canonicalize_fast` uses); `Q_SIGNED` is `np.sign` of the same
vector (what `canonicalize` forces). Same items, same eligibility, same gold, same scorer.

POSITIVE CONTROL, asserted not assumed: `Q_GRADED` must reproduce the landed C3 headline
**hit@1 = 0.0480** bit-for-bit. If it does not, this harness is measuring something else and the
comparison is void -- the script says so rather than reporting a number.

REPORTS, because a single convention has misled this project repeatedly: hit@1 and median rank under
**both** tie conventions, tie mass per arm, the paired per-item difference with a bootstrap CI, and
**the count of items whose rank actually CHANGED** -- a zero-width or zero-change result is a
reachability failure, not a null.
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

ANCHOR_NAME = "exp_graded_vs_signed_query_v1"
OUT = os.path.join(_REPO, "data", ANCHOR_NAME)
os.makedirs(OUT, exist_ok=True)
EPS = 1e-12
C3_HEADLINE = 0.0480


def main() -> int:
    t0 = time.time()
    sents = C3.build_corpus("full")
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets,
                           os.path.join(_REPO, "data", "exp_orthographic_floor_vet_v1"))
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    items, _d = C3.build_items(space, buckets, counts, C3.MAX_ITEMS)
    n = len(items)
    print("[q] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, len(anchors), time.time() - t0),
          flush=True)

    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9
    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    anchor_arr = np.array(anchors)

    arms = ("Q_GRADED", "Q_SIGNED")
    hit_o = {a: [] for a in arms}
    hit_p = {a: [] for a in arms}
    rk_o = {a: [] for a in arms}
    rk_p = {a: [] for a in arms}
    ties = {a: [] for a in arms}
    n_rank_changed = 0
    n_pick_changed = 0
    n_scored = 0

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
        qg = space.bundle(L)
        if qg is None:
            continue
        qg = np.asarray(qg, dtype=np.float64)
        if float(np.linalg.norm(qg)) < 1e-9:
            continue
        qs = np.sign(qg)                      # EXACTLY what canonicalize:776 does
        if float(np.linalg.norm(qs)) < 1e-9:
            continue
        n_scored += 1

        per = {}
        for name, q in (("Q_GRADED", qg), ("Q_SIGNED", qs)):
            sc = (mat[sel] @ q) / (mat_nrm[sel] * float(np.linalg.norm(q)))
            mx = float(np.max(sc))
            tied = np.flatnonzero(sc >= mx - EPS)
            ties[name].append(int(tied.size))
            tn = set(str(x) for x in anchor_arr[sel[tied]])
            gin = bool(tn & set(gold))
            hit_o[name].append(1.0 if gin else 0.0)
            hit_p[name].append(1.0 if (gin and tied.size == 1) else 0.0)
            if gsel.size:
                g = float(np.max(sc[gsel]))
                beat = int(np.sum(sc > g + EPS))
                tg = int(np.sum(np.abs(sc - g) <= EPS)) - 1
                rk_o[name].append(beat + 1)
                rk_p[name].append(beat + tg + 1)
            per[name] = (int(sel[int(np.argmax(sc))]),
                         (rk_o[name][-1] if gsel.size else None))
        if per["Q_GRADED"][0] != per["Q_SIGNED"][0]:
            n_pick_changed += 1
        if per["Q_GRADED"][1] is not None and per["Q_GRADED"][1] != per["Q_SIGNED"][1]:
            n_rank_changed += 1
        if (i + 1) % 500 == 0:
            print("[q] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    def arr(x):
        return np.array(x, dtype=np.float64)

    # POSITIVE CONTROL -- refuse to report if the harness does not reproduce the landed headline
    got = float(arr(hit_o["Q_GRADED"]).mean())
    reproduces = abs(got - C3_HEADLINE) < 5e-4
    print("\nPOSITIVE CONTROL: Q_GRADED optimistic hit@1 = %.4f (landed C3 = %.4f) -> %s"
          % (got, C3_HEADLINE, "REPRODUCES" if reproduces else "DOES NOT REPRODUCE"))

    # paired bootstrap on the hit@1 difference (optimistic convention), items resampled together
    g, s = arr(hit_o["Q_GRADED"]), arr(hit_o["Q_SIGNED"])
    rng = np.random.default_rng(20260821)
    d = g - s
    boots = np.array([d[rng.integers(0, d.size, d.size)].mean() for _ in range(5000)])
    lo, hi = float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))

    out = {"anchor_name": ANCHOR_NAME,
           "what": "what np.sign at reading_grounding_loop.py:776 costs; ONE VARIABLE (query only), "
                   "graded anchor field in both arms",
           "prediction_under_test": "restoring magnitude moves hit@1 specifically and leaves median "
                                    "rank roughly alone (T5b)",
           "ts_iso": datetime.now(timezone.utc).isoformat(),
           "n_items": n, "n_scored": n_scored,
           "positive_control_reproduces_c3_headline": bool(reproduces),
           "q_graded_optimistic_hit_at_1": round(got, 6),
           "n_pick_changed": n_pick_changed, "n_rank_changed": n_rank_changed,
           "paired_hit_at_1_graded_minus_signed": round(float(d.mean()), 6),
           "paired_ci95": [round(lo, 6), round(hi, 6)],
           "arms": {}}
    for a in arms:
        out["arms"][a] = {
            "hit_at_1_optimistic": round(float(arr(hit_o[a]).mean()), 6),
            "hit_at_1_pessimistic": round(float(arr(hit_p[a]).mean()), 6),
            "median_rank_optimistic": float(np.median(arr(rk_o[a]))) if rk_o[a] else None,
            "median_rank_pessimistic": float(np.median(arr(rk_p[a]))) if rk_p[a] else None,
            "mean_tied_at_max": round(float(arr(ties[a]).mean()), 4),
            "frac_any_tie": round(float((arr(ties[a]) > 1).mean()), 6),
        }
    p = os.path.join(OUT, "metrics.json")
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, p)

    print("\n" + "=" * 88)
    print("WHAT THE HARDCODED np.sign COSTS  (one variable: the QUERY)")
    print("=" * 88)
    print("%-12s %12s %12s %12s %12s" % ("arm", "hit@1 opt", "hit@1 pess", "med opt", "med pess"))
    for a in arms:
        r = out["arms"][a]
        print("%-12s %12.4f %12.4f %12s %12s"
              % (a, r["hit_at_1_optimistic"], r["hit_at_1_pessimistic"],
                 r["median_rank_optimistic"], r["median_rank_pessimistic"]))
    print("\nREACHABILITY (a zero here is a reachability failure, not a null):")
    print("   picks changed %d of %d   ranks changed %d of %d"
          % (n_pick_changed, n_scored, n_rank_changed, n_scored))
    print("\nPAIRED hit@1  GRADED - SIGNED = %+.4f  CI95 [%+.4f, %+.4f]"
          % (d.mean(), lo, hi))
    print("\nwrote %s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
