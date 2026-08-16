"""Does the SWITCH-BLIND sign() at reading_grounding_loop.py:757 cost GOLD ACCURACY on the live
grounding decision, or does it merely change the answer?

canonicalize() (:757, signed query, live at :1273/:1492) vs canonicalize_fast() (graded query, the
C3 measurement path) on the IDENTICAL space, items, eligibility and WordNet gold. Smoke corpus, so
this is a DIRECTIONAL diagnostic, not a headline; the headline curve is
experiments/exp_readout_sign_cue_overlap_curve_v1.py.

Read-only. Writes one JSON into scratch/.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("HD_GRADED_COMPARATOR", "1")

import json
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

import hdlab.reading_grounding_loop as RGL  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402


def main() -> int:
    assert RGL.GRADED_COMPARATOR is True
    sents = C3.build_corpus("smoke")
    buckets, counts = C3.build_buckets(sents)
    out = os.path.join(_REPO, "scratch", "_probe_sign_sites")
    os.makedirs(out, exist_ok=True)
    space = C3.build_space(sents, buckets, out)
    anchors, _m = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    items, _d = C3.build_items(space, buckets, counts, 1000)

    n = agree = 0
    hit_fast = hit_slow = 0
    both = neither = only_fast = only_slow = 0
    for it in items:
        L = it["L"]
        q = space.bundle(L)
        if q is None or float(np.linalg.norm(q)) < 1e-9:
            continue
        mask = np.ones(len(anchors), dtype=bool)
        mask[pos[L]] = False
        pf, _ = RGL.canonicalize_fast(L, q, space, thresh=-1.0, eligible_mask=mask)
        ps, _ = RGL.canonicalize(L, q, space, thresh=-1.0)
        gold = C3.gold_meaning_set(L)
        f_ok, s_ok = (pf in gold), (ps in gold)
        n += 1
        agree += int(pf == ps)
        hit_fast += int(f_ok)
        hit_slow += int(s_ok)
        both += int(f_ok and s_ok)
        neither += int((not f_ok) and (not s_ok))
        only_fast += int(f_ok and not s_ok)
        only_slow += int(s_ok and not f_ok)

    b = only_fast + only_slow
    mcnemar_note = ("discordant pairs %d (graded-only %d, signed-only %d)" % (b, only_fast,
                                                                             only_slow))
    rep = {
        "scope": "SMOKE corpus (2000 sentences), directional diagnostic only -- NOT a headline",
        "n_items": n, "n_anchors": len(anchors),
        "agreement_rate": round(agree / max(1, n), 6),
        "disagreement_rate": round(1 - agree / max(1, n), 6),
        "gold_hit_canonicalize_fast_GRADED_query": round(hit_fast / max(1, n), 6),
        "gold_hit_canonicalize_SIGNED_query_the_757_site": round(hit_slow / max(1, n), 6),
        "paired_table": {"both": both, "neither": neither, "graded_only": only_fast,
                         "signed_only": only_slow},
        "mcnemar": mcnemar_note,
        "reading": "canonicalize (:757) is what the LIVE grounding gate and the banking path call. "
                   "Its query is signed regardless of HD_GRADED_COMPARATOR.",
    }
    p = os.path.join(_REPO, "scratch", "probe_757_costs_gold.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
