"""verification/test_typed_selectional_preference_organ.py -- the promoted knowledge organ hdlab/typed_selectional_preference
equals the owner-DONE solver's computation and ships as a persisted asset.
  O1 the asset exists and profiles > 1000 verbs (Resnik association over WordNet noun supersenses).
  O2 the organ's A(v,c) equals the solver's cell (experiments/exp_typed_selectional_preference_v1) on every profiled verb
     (same fillers, same formula) -- abs diff <= 1e-9.
  O3 the read is typed: A(eat, bread [noun.food]) > A(eat, idea [noun.cognition]); an unknown verb -> None.
  O4 graceful: loading from a missing path gives an empty organ that abstains (None) everywhere.
Run: .venv/Scripts/python.exe verification/test_typed_selectional_preference_organ.py
"""
from __future__ import annotations
import os
import sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.typed_selectional_preference as TSP


def main():
    if not os.path.isfile(TSP.ASSET):
        TSP.build_asset()
    m = TSP.get()
    assert len(m._A) > 1000, len(m._A)
    print("[PASS] O1 asset present; %d verbs profiled" % len(m._A))
    import experiments.exp_typed_selectional_preference_v1 as T
    ref = T.TypedSelectionalPreference().fit()
    assert set(ref._A) == set(m._A), (len(ref._A), len(m._A), list(set(ref._A) ^ set(m._A))[:5])
    worst = 0.0
    for v, row in ref._A.items():
        for c, a in row.items():
            worst = max(worst, abs(a - m._A[v].get(c, 0.0)))
    assert worst <= 1e-9, worst
    print("[PASS] O2 organ == solver's cell on %d verbs (max |dA| = %.1e)" % (len(ref._A), worst))
    b, i = m.score("eat", "bread"), m.score("eat", "idea")
    assert b is not None and i is not None and b > i, (b, i)
    assert m.score("zzqv_unknown_verb", "bread") is None
    print("[PASS] O3 typed read: A(eat,bread)=%.3f > A(eat,idea)=%.3f; unknown verb -> None" % (b, i))
    empty = TSP.TypedSelectionalPreference.load(os.path.join(_REPO, "data", "nonexistent_asset.json"))
    assert empty.score("eat", "bread") is None and not empty.covers("eat")
    print("[PASS] O4 missing asset -> abstains everywhere")
    print("4/4 witnesses passed. Typed selectional preference organ promoted (LATENT knowledge organ; consumer = pri-1).")


if __name__ == "__main__":
    main()
