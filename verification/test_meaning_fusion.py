"""Data-free self-test for hdlab/meaning_fusion.py (2026-08-25) -- the GENERAL word-meaning read-out
(complementary equal-weight z-fusion of a reading spoke + a grounded spoke; NOT distillation).

The full WordSim-353 reproduction (organ read-out reproduces the diag cell's FUSION_EQUAL 0.4455 on
n_eval=228, beats both spokes, shuffled-grounding twin loses CI-separated) was validated by the
strategy session against the diag cell's cached FROZEN reading spoke -- 5/5 -- because rebuilding the
reading store via a live 10k read is prohibitively slow on the USB (deferred to post-drive-move; the
store->phi path is separately proven by the distributional_meaning_channel witness: ConceptSpace
roundtrip exact + ppmi_svd reproduces phi to 3.4e-4). THIS file is the fast formula/policy check that
runs in the routine gate.
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.meaning_fusion import self_test


def test_meaning_fusion_self_test():
    ev = self_test()
    t = ev["toy_fusion_beats_spokes"]
    assert t["fusion"] > t["raw"] and t["fusion"] > t["grnd"], "fusion must beat both spokes"
    assert t["shuffle"] <= max(t["raw"], t["grnd"]) + 1e-9, "info-free twin must not beat a real spoke"
    assert ev["oov_policy_ok"], "OOV policy"
    assert ev["determinism_ok"], "determinism"
    assert ev["batch_matches_zfusion_formula"], "batch read-out must equal 0.5*z(read)+0.5*z(grounded)"
    print("PASS meaning_fusion self_test %r" % ev)


if __name__ == "__main__":
    test_meaning_fusion_self_test()
    print("1/1 WITNESS PASSED")
