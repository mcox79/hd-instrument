"""Witness for hdlab.graded_role_assigner (landed 2026-08-27).

Self-contained construction proof of the Competition-Model non-canonical patient route (no corpus/cache):
  [1] REDUCED OBJECT-RELATIVES ("the oxygen plants release" -> patient = oxygen, the fronted antecedent): the hybrid
      recovers them where the front-end `resolve_patient` picks the wrong (post-/nearest) nominal.
  [2] CANONICAL PRESERVED: on canonical clauses the hybrid is BYTE-IDENTICAL to `resolve_patient` (routing, not
      replacement -- the fidelity lever).
  [3] INFO-FREE TWIN (shuffled cue validities) LOSES: it recovers fewer reduced-relatives than the learned validities.
  [4] glass-box: `hybrid_role_patient` takes no gold; the `-ed` garden-path `passive_weak` validity is NEGATIVE.
The held-out CI-separated win on the role-balanced gold (0.60 vs 0.576 non-canonical, net-positive) is the solver's
test_noncanonical_role_assigner.py.
"""
from __future__ import annotations

import inspect
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.graded_role_assigner import DEFAULT_VALIDITIES, hybrid_role_patient  # noqa: E402
from hdlab.relcl_resolver import resolve_patient, _cands  # noqa: E402

# reduced (relativizer-LESS) object-relatives: "the X <plural-noun> <verb>" -> patient = X (the fronted antecedent, idx 2)
REDUCED_REL = [
    (["the", "oxygen", "plants", "release"], ["DET", "NOUN", "NOUN", "VERB"], 4, 2),
    (["the", "food", "animals", "eat"], ["DET", "NOUN", "NOUN", "VERB"], 4, 2),
    (["the", "water", "rocks", "absorb"], ["DET", "NOUN", "NOUN", "VERB"], 4, 2),
    (["the", "heat", "metals", "conduct"], ["DET", "NOUN", "NOUN", "VERB"], 4, 2),
]
# canonical SVO: patient = the post-verbal object
CANONICAL = [
    (["the", "lawyer", "chased", "the", "doctor"], ["DET", "NOUN", "VERB", "DET", "NOUN"], 3),
    (["the", "cat", "ate", "the", "food"], ["DET", "NOUN", "VERB", "DET", "NOUN"], 3),
    (["the", "dog", "found", "the", "bone"], ["DET", "NOUN", "VERB", "DET", "NOUN"], 3),
]


def main() -> int:
    # [1] reduced object-relatives: hybrid recovers the antecedent where resolve_patient fails
    hy_ok = res_ok = 0
    for toks, pos, v, gold in REDUCED_REL:
        c = _cands(pos)
        hy_ok += int(hybrid_role_patient(toks, pos, v, c) == gold)
        res_ok += int(resolve_patient(toks, pos, v, c) == gold)
    n = len(REDUCED_REL)
    print(f"[1] reduced object-relatives (n={n}): hybrid {hy_ok}/{n}  vs  resolve_patient {res_ok}/{n}")
    assert hy_ok >= n - 0, f"hybrid must recover the reduced-relative antecedent ({hy_ok}/{n})"
    assert hy_ok > res_ok, f"hybrid must beat resolve_patient on the non-canonical slice ({hy_ok} vs {res_ok})"

    # [2] canonical PRESERVED: hybrid byte-identical to resolve_patient
    same = all(hybrid_role_patient(toks, pos, v, _cands(pos)) == resolve_patient(toks, pos, v, _cands(pos))
               for toks, pos, v in CANONICAL)
    print(f"[2] canonical preserved (hybrid == resolve_patient on all canonical): {same}")
    assert same, "[witness] hybrid changed a canonical answer -- it must ROUTE, not replace"

    # [3] info-free TWIN (shuffled validities) recovers fewer reduced-relatives
    keys = list(DEFAULT_VALIDITIES); vals = [DEFAULT_VALIDITIES[k] for k in keys]
    perm = np.random.default_rng(20260827).permutation(len(vals))
    twin = {keys[i]: vals[perm[i]] for i in range(len(keys))}
    twin_ok = sum(int(hybrid_role_patient(toks, pos, v, _cands(pos), weights=twin) == gold)
                  for toks, pos, v, gold in REDUCED_REL)
    print(f"[3] shuffled-validity twin: {twin_ok}/{n} (must lose to learned {hy_ok}/{n})")
    assert twin_ok < hy_ok, "[witness] the shuffled-validity twin did not lose -> the learned validities carry it"

    # [4] glass-box + the -ed garden-path is distrusted
    params = list(inspect.signature(hybrid_role_patient).parameters)
    assert "gold" not in params and "labels" not in params, params
    assert DEFAULT_VALIDITIES["passive_weak"] < 0, "the bare-participle (-ed ambiguity) validity must be NEGATIVE"
    print(f"[4] glass-box PASS (no gold in signature; passive_weak validity {DEFAULT_VALIDITIES['passive_weak']:.2f} < 0)")

    print("\nALL WITNESS ASSERTIONS PASSED -- the graded role assigner recovers non-canonical (reduced-relative)")
    print("patients where the front-end fails, keeps canonical byte-identical (routing not replacement), the")
    print("shuffled-validity twin loses, and the -ed garden-path cue is correctly distrusted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
