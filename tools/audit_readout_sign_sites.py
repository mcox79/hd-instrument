"""RUNTIME ENUMERATION of every np.sign() call reached on the LIVE C3 open-vocabulary read-out
path. Not a grep: numpy.sign is monkeypatched with a wrapper that records (file, lineno, function)
of the calling frame, then the real C3 harness is driven at smoke scale under BOTH settings of
HD_GRADED_COMPARATOR. Read-only; writes one JSON into scratch/.

Usage: .venv/Scripts/python.exe scratch/probe_readout_sign_sites.py <0|1>
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

_G = sys.argv[1] if len(sys.argv) > 1 else "1"
os.environ["HD_GRADED_COMPARATOR"] = _G

import collections
import inspect
import json

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np

_REAL_SIGN = np.sign
_HITS: collections.Counter = collections.Counter()
_ACTIVE = {"on": False}


def _tracing_sign(x, *a, **k):
    if _ACTIVE["on"]:
        f = inspect.currentframe().f_back
        _HITS["%s:%d:%s" % (os.path.relpath(f.f_code.co_filename, _REPO).replace("\\", "/"),
                            f.f_lineno, f.f_code.co_name)] += 1
    return _REAL_SIGN(x, *a, **k)


np.sign = _tracing_sign

import hdlab.reading_grounding_loop as RGL  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402

OUT = os.path.join(_REPO, "scratch", "readout_sign_sites_G%s.json" % _G)


def main() -> int:
    print("GRADED_COMPARATOR at import =", RGL.GRADED_COMPARATOR, flush=True)
    sents = C3.build_corpus("smoke")
    buckets, counts = C3.build_buckets(sents)
    out_dir = os.path.join(_REPO, "scratch", "_probe_sign_sites")
    os.makedirs(out_dir, exist_ok=True)

    phases = {}

    # --- PHASE 1: ENCODE (one encounter -> a context vector)
    _HITS.clear()
    _ACTIVE["on"] = True
    lem = sorted(buckets)[0]
    _ = RGL.context_vector_masked(sents[buckets[lem][0]], lem)
    _ACTIVE["on"] = False
    phases["1_ENCODE_one_encounter"] = dict(_HITS)

    # --- PHASE 2: ACCUMULATE (build the whole space)
    _HITS.clear()
    _ACTIVE["on"] = True
    space = C3.build_space(sents, buckets, out_dir)
    _ACTIVE["on"] = False
    phases["2_ACCUMULATE_build_space"] = dict(_HITS)

    anchors, _mat = space.anchor_matrix()
    items, diag = C3.build_items(space, buckets, counts, 40)
    print("n_anchors=%d n_items=%d" % (len(anchors), len(items)), flush=True)

    # --- PHASE 3: FIELD (anchor_matrix, the store side of the read-out)
    space._mat_cache = None
    _HITS.clear()
    _ACTIVE["on"] = True
    _an, _m = space.anchor_matrix()
    _ACTIVE["on"] = False
    phases["3_FIELD_anchor_matrix"] = dict(_HITS)

    # --- PHASE 4: QUERY (bundle(L) -- what B5_OPEN_REAL queries with)
    _HITS.clear()
    _ACTIVE["on"] = True
    q = space.bundle(items[0]["L"])
    _ACTIVE["on"] = False
    phases["4_QUERY_bundle"] = dict(_HITS)

    # --- PHASE 5: COMPARE (canonicalize_fast, the argmax the read-out performs)
    pos = {a: i for i, a in enumerate(anchors)}
    mask = np.ones(len(anchors), dtype=bool)
    mask[pos[items[0]["L"]]] = False
    _HITS.clear()
    _ACTIVE["on"] = True
    pick, cos = RGL.canonicalize_fast("__slot__", q, space, thresh=-1.0, eligible_mask=mask)
    _ACTIVE["on"] = False
    phases["5_COMPARE_canonicalize_fast"] = dict(_HITS)

    # --- PHASE 6: the SLOW canonicalize (is it the same site? is it switch-aware?)
    _HITS.clear()
    _ACTIVE["on"] = True
    pick2, cos2 = RGL.canonicalize("__slot__", q, space, thresh=-1.0)
    _ACTIVE["on"] = False
    phases["6_COMPARE_canonicalize_slow_reference"] = dict(_HITS)

    # --- PHASE 7: HELD-OUT SENTENCE QUERY (the B4 partial-cue query)
    it = next((x for x in items if x["sent_idx"] is not None), None)
    if it is not None:
        _HITS.clear()
        _ACTIVE["on"] = True
        qs = RGL.context_vector_masked(sents[it["sent_idx"]], it["L"])
        _p, _c = RGL.canonicalize_fast("__slot__", qs, space, thresh=-1.0, eligible_mask=mask)
        _ACTIVE["on"] = False
        phases["7_HELDOUT_SENTENCE_QUERY_then_compare"] = dict(_HITS)

    rep = {
        "HD_GRADED_COMPARATOR": _G,
        "GRADED_COMPARATOR_at_import": bool(RGL.GRADED_COMPARATOR),
        "graded_query_default": bool(RGL.ReadoutConfig().graded_query),
        "method": "numpy.sign monkeypatched with a caller-frame recorder; the REAL C3 harness "
                  "functions were then called. Static grep was NOT used to decide reachability.",
        "phases": phases,
        "field_is_bipolar": bool(set(np.abs(_m[0]).tolist()) <= {0.0, 1.0}),
        "query_is_bipolar": bool(set(np.abs(q).tolist()) <= {0.0, 1.0}),
        "readout_pick": str(pick), "readout_cos": float(cos),
        "slow_pick": str(pick2), "slow_cos": float(cos2),
        "fast_equals_slow": bool(pick == pick2),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep, indent=1), flush=True)
    print("WROTE", OUT, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
