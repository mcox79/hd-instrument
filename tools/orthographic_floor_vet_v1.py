"""AUDITOR RECOMPUTE, promoted from scratch/ (not a pre-registered experiment cell; wires nothing;
changes no hdlab default). PROMOTED 2026-08-14 from `scratch/ortho_floor_vet_trigram_only.py` per
CLAUDE.md "Scratch files" corollary: a durable citation into a gitignored, periodically-wiped
directory is a dangling citation, and this script is now the sole provenance of a load-bearing
number (the spelling-alone C3 floor). See notes/orthographic_floor_vet_and_rebaseline_2026-08-14.md
(commit 9ca1cffa2) for the audit that drafted it and the reasoning below.

QUESTION: exp_meaning_supply_separation_v1's A5_STRINGCTRL is z(base) + w*z(trigram) -- the
substrate read-out PLUS an orthographic channel, NOT orthography alone. So 0.1027 cannot be read
as "a spell-checker scores 0.1027". This script measures the arm that WOULD support that reading:
A6_TRIGRAM_ONLY, character-trigram cosine alone, zero substrate signal, on the IDENTICAL items,
IDENTICAL eligible pool, IDENTICAL gold set and IDENTICAL scorer (argmax hit@1) as
exp_grounding_readout_known_answer_v1 (204eba1a0, hit@1 0.0480, n=4000, 5491 anchors).

Also computes A7_PREFIX_ONLY (longest-common-prefix / shared-stem heuristic) as a second, simpler
orthographic floor, A8_MAXORTHO (max-attack blend of both, since a FLOOR should be the strongest
available zero-meaning attack), and re-derives A1_BASE to prove the harness reproduces 0.0480
bit-for-bit -- that reproduction is what licenses reading A6/A7/A8 as pool-identical to the C3
headline rather than a different measurement dressed up as a comparison.

POOL IDENTITY, verified by reading (not assumed): this file imports build_corpus / build_buckets /
build_space / build_items / gold_meaning_set / MASTER_SEED / MAX_ITEMS directly from
exp_grounding_readout_known_answer_v1 (never reimplemented), and reuses the exact per-item
eligibility construction (self-lemma + normalized spelling variants excluded, mat_ok-filtered) that
exp_meaning_supply_separation_v1 already used to reproduce C3's B5_OPEN_REAL arm bit-identically
(same hit@1, same bootstrap sd to 9 decimal places -- see the 2026-08-14 audit note). This script
is that same construction with the base score subtracted out and pure trigram / prefix similarity
substituted in.

Run:  .venv/Scripts/python.exe tools/orthographic_floor_vet_v1.py
Output: data/exp_orthographic_floor_vet_v1/metrics.json (atomic os.replace, ts_iso stamped).
Expected runtime ~10 minutes (rebuilds the same ConceptSpace as the 543s C3 run).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402

ANCHOR_NAME = "exp_orthographic_floor_vet_v1"
OUT = os.path.join(_REPO, "data", ANCHOR_NAME)
os.makedirs(OUT, exist_ok=True)


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
    space = C3.build_space(sents, buckets, OUT)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    items, diag = C3.build_items(space, buckets, counts, C3.MAX_ITEMS)
    n = len(items)
    print("[recompute] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0),
          flush=True)

    t_mat, t_cov = MS.trigram_matrix(anchors)
    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])

    arms = ("A1_BASE", "A6_TRIGRAM_ONLY", "A7_PREFIX_ONLY", "A8_MAXORTHO")
    hits = {a: np.zeros(n, dtype=bool) for a in arms}
    ranks = {a: np.zeros(n, dtype=np.int64) for a in arms}
    picks = {a: [] for a in arms}

    anchor_arr = np.array(anchors)
    alen = np.array([len(a) for a in anchors], dtype=np.float64)

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(n_anchors, dtype=bool)
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

        # shared-stem / longest-common-prefix, length-normalized (a "spell-checker" with no vectors)
        pre = np.array([_lcp(L, anchors[a]) for a in sel], dtype=np.float64)
        pre = pre / np.maximum(np.maximum(alen[sel], len(L)), 1.0)

        scores = {"A1_BASE": base, "A6_TRIGRAM_ONLY": trig, "A7_PREFIX_ONLY": pre,
                  "A8_MAXORTHO": MS._z(trig) + MS._z(pre)}
        for a in arms:
            sc = scores[a]
            b = int(np.argmax(sc))
            p = anchor_arr[sel[b]]
            picks[a].append(str(p))
            hits[a][i] = str(p) in gold
            if gsel.size:
                ranks[a][i] = int(np.sum(sc > float(np.max(sc[gsel])))) + 1
            else:
                ranks[a][i] = sel.size
        if (i + 1) % 500 == 0:
            print("[score] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    armv = {a: hits[a].astype(float) for a in arms}
    dl = [("d_A6_TRIGRAM_ONLY_minus_BASE", "A6_TRIGRAM_ONLY", "A1_BASE"),
          ("d_A7_PREFIX_ONLY_minus_BASE", "A7_PREFIX_ONLY", "A1_BASE"),
          ("d_A8_MAXORTHO_minus_BASE", "A8_MAXORTHO", "A1_BASE")]
    bs = MS.paired_bootstrap(armv, dl, 5000, C3.MASTER_SEED + 5)

    a1_matches_c3_headline = abs(bs["arm_acc_ci"]["A1_BASE"]["acc"] - 0.048) < 1e-9

    rep = {
        "anchor_name": ANCHOR_NAME,
        "what": "AUDITOR RECOMPUTE: orthography-ONLY arms on the identical C3 harness",
        "provenance_note": "promoted from scratch/ortho_floor_vet_trigram_only.py 2026-08-14; see "
                            "notes/orthographic_floor_vet_and_rebaseline_2026-08-14.md (9ca1cffa2)",
        "compares_against": {"cell": "exp_grounding_readout_known_answer_v1", "metrics": "204eba1a0",
                             "arm": "B5_OPEN_REAL", "hit_at_1": 0.048},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_items": n, "n_anchors": n_anchors, "item_construction": diag,
        "a1_base_reproduces_c3_headline_exactly": a1_matches_c3_headline,
        "bootstrap": bs,
        "per_arm": {a: {"hit_at_1": float(hits[a].mean()),
                        "median_rank": float(np.median(ranks[a])),
                        "example_picks": picks[a][:12]} for a in arms},
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(OUT, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print(json.dumps(rep["per_arm"], indent=1))
    print(json.dumps(bs["deltas"], indent=1))
    print("A1_BASE reproduces C3 headline 0.0480 exactly:", a1_matches_c3_headline)
    print("WROTE", p)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        _crash = os.path.join(OUT, "_crash_diagnostic.json")
        with open(_crash + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME,
                       "error": "%s: %s" % (type(exc).__name__, exc),
                       "traceback": traceback.format_exc(),
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        os.replace(_crash + ".tmp", _crash)
        raise
