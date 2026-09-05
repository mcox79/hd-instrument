"""Landing witness for hdlab/meaning_foundation.py (owner-DONE
build_and_freeze_the_clean_curated_knowledge_foundation..., Q111 landing 2026-09-05). The +0.0755 meaning
lift through diagnostic_context_wsd is reverified by verification/test_knowledge_factory_meaning_store.py
(6/6); this asserts the PROMOTED hdlab loader is byte-identical to a direct load of the frozen asset. ASCII.

  W1 dim() + covers() correct against the on-disk store.
  W2 sense_signature(s) is BYTE-IDENTICAL to the direct npz row (float64 upcast); None on absent/zero-norm.
  W3 sense_signatures(list) matrix == the direct-load matrix, with a ZERO row per absent sense.

Run: .venv/Scripts/python.exe verification/test_meaning_foundation_landing.py
"""
from __future__ import annotations
import os, sys
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np
from hdlab import meaning_foundation as MF

ASSET = os.path.join(_REPO, "data", "frontend_assets", "meaning_sense_signatures_v1.npz")


def _norm(v):
    return float(np.linalg.norm(v))


def main():
    z = np.load(ASSET, allow_pickle=True)
    names = [str(n) for n in z["names"]]
    vecs = z["vecs"]
    row = {n: i for i, n in enumerate(names)}

    # W1
    assert MF.dim() == vecs.shape[1], "dim mismatch"
    assert MF.covers(names[0]) and not MF.covers("no_such_synset.n.99"), "covers() wrong"
    print("W1 dim()=%d, covers() correct (%d synsets): PASS" % (MF.dim(), len(names)), flush=True)

    # W2 byte-identity on a deterministic sample (every step-th synset)
    step = max(1, len(names) // 800)
    n_checked = n_none = 0
    for s in names[::step]:
        ref = np.asarray(vecs[row[s]], dtype=np.float64)
        got = MF.sense_signature(s)
        if _norm(ref) > 1e-6:
            assert got is not None and np.array_equal(got, ref), "sense_signature diverges on %s" % s
            n_checked += 1
        else:
            assert got is None, "zero-norm row should be None (%s)" % s
            n_none += 1
    assert MF.sense_signature("no_such_synset.n.99") is None, "absent should be None"
    print("W2 sense_signature byte-identical on %d sampled synsets (%d zero-norm->None): PASS" % (n_checked, n_none), flush=True)

    # W3 matrix, including a ZERO row for an absent sense
    syns = [names[0], names[1], "no_such_synset.n.99", names[len(names) // 2]]
    G = MF.sense_signatures(syns)
    ref_G = np.zeros((len(syns), vecs.shape[1]), dtype=np.float64)
    for k, s in enumerate(syns):
        if s in row:
            v = np.asarray(vecs[row[s]], dtype=np.float64)
            if _norm(v) > 1e-6:
                ref_G[k] = v
    assert G.shape == ref_G.shape and np.array_equal(G, ref_G), "sense_signatures matrix diverges"
    assert _norm(G[2]) == 0.0, "absent sense must be a ZERO row"
    print("W3 sense_signatures matrix byte-identical (absent -> zero row): PASS", flush=True)
    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
