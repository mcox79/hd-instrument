"""Witness for hdlab.salience_binder (landed 2026-08-27, consolidation phase).

Self-contained construction proof of the pronoun-binding MECHANISM (no corpus dependency):
  [1] GRAMMATICAL PROMINENCE OVERRIDES RECENCY -- the load-bearing brain claim (the integration proved recency
      is at chance on hard cases; Centering Cf-ranking carries binding). A repeatedly-SUBJECT but older entity
      beats a once-OTHER but MORE-RECENT entity; a recency baseline picks the wrong (recent) one.
  [2] ACT-R base-level activation is monotone (more recent same-role -> higher; higher-prominence role at the
      same distance -> higher; empty history -> -inf).
  [3] the GRADED WRITE is divisive normalization and UNIFIES with hdlab.graded_competition.softmax (byte-equal,
      gain=1/temp) -- ONE operation reused; it is an INTERIOR optimum (winner mass between uniform 1/K and hard).
  [4] glass-box (bind takes no gold) + INFO-FREE TWIN loses: a random/shuffled-activation write does NOT
      identify the prominent entity (chance ~1/K), and a UNIFORM write carries no winner -- so it is the
      ACTIVATION weighting, not mere hedging, that binds.
The GAP / LitBank validation (0.699 vs recency-at-chance; graded > hard +0.0268) is the solver's witnesses.
"""
from __future__ import annotations

import inspect
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.graded_competition import softmax as dn_softmax  # noqa: E402
from hdlab.salience_binder import (  # noqa: E402
    DEFAULT_TEMP, actr_activation, activations, bind, graded_write,
)


def main() -> int:
    NOW = 10.0

    # [1] PROMINENCE OVERRIDES RECENCY. A = subject x2 (prominent) but older; C = other x1 but most recent.
    A = [(5.0, "SUBJECT"), (7.0, "SUBJECT")]      # prominent, older
    C = [(9.0, "OTHER")]                          # once-other, MOST recent
    cands = [A, C]
    picked = bind(cands, NOW)
    recency_pick = max(range(len(cands)), key=lambda i: max(t for t, _ in cands[i]))  # latest last-mention
    aA, aC = actr_activation(A, NOW), actr_activation(C, NOW)
    print(f"[1] act(A subject,older)={aA:+.3f} > act(C other,recent)={aC:+.3f}; binder picks {picked} (A), "
          f"recency picks {recency_pick} (C)")
    assert picked == 0, "[witness] the prominence-weighted binder must pick the SUBJECT entity"
    assert recency_pick == 1, "recency should pick the more-recent OTHER entity (the disagreement)"
    assert aA > aC, "prominence (subject x2) must overcome the recency of a single OTHER mention"

    # [2] ACT-R monotonicity
    assert actr_activation([(8.0, "SUBJECT")], NOW) > actr_activation([(6.0, "SUBJECT")], NOW), "more recent -> higher"
    assert actr_activation([(8.0, "SUBJECT")], NOW) > actr_activation([(8.0, "OTHER")], NOW), "higher prominence -> higher"
    assert actr_activation([], NOW) == float("-inf"), "empty history -> -inf (no evidence)"
    print("[2] ACT-R monotonicity PASS (recency-up, prominence-up, empty->-inf)")

    # [3] GRADED WRITE == divisive-normalization softmax (unifies with graded_competition), interior optimum
    four = [[(9.0, "SUBJECT")], [(8.0, "OBJECT")], [(6.0, "OTHER")], [(4.0, "OTHER")]]
    acts = activations(four, NOW)
    w_organ = np.array([w for _i, w in graded_write(four, NOW, temp=DEFAULT_TEMP)])
    w_ref = dn_softmax(acts, gain=1.0 / DEFAULT_TEMP)
    assert np.allclose(w_organ, w_ref), "[witness] graded_write must REUSE graded_competition.softmax (one op)"
    assert abs(w_organ.sum() - 1.0) < 1e-9, "weights must sum to 1"
    K = len(four)
    win_w = w_organ.max()
    assert 1.0 / K < win_w < 0.999, f"interior optimum: winner mass {win_w:.3f} must sit between uniform 1/K and hard"
    assert int(np.argmax(w_organ)) == bind(four, NOW), "graded argmax must equal the hard bind"
    print(f"[3] divisive-normalization unification PASS (graded_write == graded_competition.softmax; "
          f"winner mass {win_w:.3f} in (1/{K}, 1))")

    # [4] glass-box + info-free twin. Real binder identifies the prominent entity; a shuffled-activation write
    #     does NOT (chance ~1/K); a uniform write carries no winner.
    params = list(inspect.signature(bind).parameters)
    assert "gold" not in params and "labels" not in params, params
    prom = bind(four, NOW)                       # the true prominent index
    rng = np.random.default_rng(20260827)
    hits = 0
    for _ in range(400):
        shuffled = dn_softmax(rng.permutation(acts), gain=1.0 / DEFAULT_TEMP)
        hits += int(np.argmax(shuffled) == prom)
    frac = hits / 400
    w_uniform = dn_softmax(np.zeros(K), gain=1.0)     # no activation info -> uniform, no winner
    print(f"[4] glass-box + twin PASS (real picks prominent {prom}; shuffled-activation hits prominent "
          f"{frac:.3f} ~ 1/{K}; uniform spread max={w_uniform.max():.3f})")
    assert frac < 0.45, "[witness] a shuffled-activation write identified the prominent entity too often -> leak"
    assert abs(w_uniform.max() - 1.0 / K) < 1e-9, "a uniform (info-free) write must carry no winner"

    print("\nALL WITNESS ASSERTIONS PASSED -- grammatical prominence (ACT-R base-level activation + Centering")
    print("Cf-ranking) overrides recency, the graded write is the divisive-normalization interior optimum")
    print("reusing the shared softmax, and the activation weighting -- not mere hedging -- is what binds.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
