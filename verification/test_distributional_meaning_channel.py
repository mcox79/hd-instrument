"""Data-free self-test for hdlab/distributional_meaning_channel (2026-08-24).

The HEAVY live-path acceptance witness -- which drives the Route B separable store and reproduces
substitutability AUC ~0.84 over the 484 licensed pairs, clearing the info-free twin CI-separated --
is verification/witness_distributional_meaning_channel.py (run manually / in cert; not auto-collected
by pytest because it reads checkpoints and does minutes of SVD). THIS file is the fast formula check
that runs in the routine gate: it exercises the organ's ported math with no data on disk.
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.distributional_meaning_channel import self_test


def test_distributional_meaning_channel_self_test():
    ev = self_test()
    assert ev["l2n_ok"], "l2n"
    assert ev["ppmi_svd_ok"], "ppmi_svd"
    assert ev["hub_sim_ok"], "hub_sim"
    assert ev["distill_recovers_planted"] > 0.99, "distillation must recover a planted target"
    assert ev["orientation_flips_inverted"], "batch orientation must flip an inverted reference"
    print("PASS distributional_meaning_channel self_test %r" % ev)


if __name__ == "__main__":
    test_distributional_meaning_channel_self_test()
    print("1/1 WITNESS PASSED")
