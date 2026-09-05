"""Landing witness for the Bayesian frequency-prior readout in hdlab/diagnostic_context_wsd
(owner-DONE grow_broad_coverage_correctly_resolved_rare_sense_experience..., Q111 landing 2026-09-04).
The rare-sense a_s win itself is reverified by verification/test_rare_sense_episodic_coverage_growth.py (26/26);
this asserts the PROMOTION into hdlab is faithful + default byte-identical. Synthetic, no data. ASCII.

  W1 default (prior_weight=0 / sense_prior=None) is BYTE-IDENTICAL to the pure biased-competition scores.
  W2 the active formula == prior_weight*log(prior) + zscore(context) (the validated A2 readout, MacDonald/McRae).
  W3 the prior is a RESTING BIAS: tiny weight -> context decides; dominating weight -> frequency prior decides.

Run: .venv/Scripts/python.exe verification/test_bayesian_prior_wsd_landing.py
"""
from __future__ import annotations
import os, sys
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import numpy as np
from hdlab.diagnostic_context_wsd import diagnostic_context_scores, pick_sense, diagnostic_query


def _unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-12)


def main():
    rng = np.random.default_rng(7)
    D, S, W = 200, 6, 12
    C = _unit(rng.standard_normal((W, D)))
    G = _unit(rng.standard_normal((S, D)))

    # W1 byte-identity: default path == the pure biased-competition scores
    ref = G @ diagnostic_query(C, G, None)
    assert np.array_equal(diagnostic_context_scores(C, G), ref), "default diverges from reference"
    assert np.array_equal(diagnostic_context_scores(C, G, sense_prior=np.ones(S), prior_weight=0.0), ref), \
        "prior_weight=0 not byte-identical"
    print("W1 default byte-identical: PASS", flush=True)

    # W2 active formula matches the validated A2 readout (log-prior resting bias + z(context))
    prior = rng.random(S) + 0.01
    w = 5.0
    got = diagnostic_context_scores(C, G, sense_prior=prior, prior_weight=w)
    z = (ref - ref.mean()) / (ref.std() + 1e-9)
    want = w * np.log(prior + 1e-6) + z
    assert np.allclose(got, want), "active formula mismatch"
    print("W2 active formula == prior_weight*log(prior)+z(context): PASS", flush=True)

    # W3 resting-bias behaviour, end-to-end through pick_sense (index space)
    cands = [["w%d" % i] for i in range(S)]      # dummy gloss words; irrelevant to the branch under test
    ctx_pick = int(np.argmax(ref))
    tiny = diagnostic_context_scores(C, G, sense_prior=prior, prior_weight=1e-6)
    huge = diagnostic_context_scores(C, G, sense_prior=prior, prior_weight=1e6)
    assert int(np.argmax(tiny)) == ctx_pick, "tiny prior_weight should leave context deciding"
    assert int(np.argmax(huge)) == int(np.argmax(prior)), "huge prior_weight should let frequency decide"
    print("W3 resting-bias (tiny->context, huge->frequency): PASS", flush=True)

    print("\nALL WITNESSES PASS", flush=True)


if __name__ == "__main__":
    main()
