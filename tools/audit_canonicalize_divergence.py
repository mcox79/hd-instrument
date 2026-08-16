"""Is the SWITCH-BLIND np.sign at reading_grounding_loop.py:757 (`canonicalize`, the reference
implementation) a real divergence from `canonicalize_fast` under the live graded default, with
MATCHED eligibility? And is `canonicalize` reached from the live entry point?

Read-only. Writes one JSON into scratch/.
Usage: .venv/Scripts/python.exe scratch/probe_canonicalize_divergence.py
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
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
    out_dir = os.path.join(_REPO, "scratch", "_probe_sign_sites")
    os.makedirs(out_dir, exist_ok=True)
    space = C3.build_space(sents, buckets, out_dir)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    items, _diag = C3.build_items(space, buckets, counts, 200)

    agree = 0
    n = 0
    ex = []
    for it in items[:200]:
        L = it["L"]
        q = space.bundle(L)
        if q is None or float(np.linalg.norm(q)) < 1e-9:
            continue
        mask = np.ones(len(anchors), dtype=bool)
        mask[pos[L]] = False
        pf, cf = RGL.canonicalize_fast(L, q, space, thresh=-1.0, eligible_mask=mask)
        ps, cs = RGL.canonicalize(L, q, space, thresh=-1.0)
        n += 1
        if pf == ps:
            agree += 1
        elif len(ex) < 12:
            ex.append({"L": L, "fast_graded_query": pf, "slow_signed_query": ps,
                       "cos_fast": round(float(cf), 4), "cos_slow": round(float(cs), 4)})

    # is canonicalize (the slow, switch-blind one) reached from the live entry point?
    import inspect
    src_state = inspect.getsource(RGL)
    live_callers = []
    for ln, line in enumerate(src_state.splitlines(), start=1):
        s = line.strip()
        if "canonicalize(" in s and not s.startswith("#") and "def canonicalize(" not in s \
                and "canonicalize_fast(" not in s:
            live_callers.append({"lineno": ln, "line": s})

    rep = {
        "GRADED_COMPARATOR": bool(RGL.GRADED_COMPARATOR),
        "n_compared": n,
        "agree": agree,
        "agreement_rate": round(agree / max(1, n), 6),
        "disagreement_rate": round(1.0 - agree / max(1, n), 6),
        "examples_of_disagreement": ex,
        "canonicalize_call_sites_inside_reading_grounding_loop": live_callers,
        "note": "canonicalize (:757) hardcodes np.sign(new_raw_sum) and does NOT follow "
                "GRADED_COMPARATOR; canonicalize_fast (:802-806) does. Its docstring claims "
                "SAME contract / SAME return values.",
    }
    p = os.path.join(_REPO, "scratch", "canonicalize_divergence.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=1)
    print(json.dumps(rep, indent=1), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
