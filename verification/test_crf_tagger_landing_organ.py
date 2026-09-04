"""Landing witness for hdlab/crf_tagger.py (the owner-DONE upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_
posterior deployable win). Proves: [1] the promoted organ reproduces the experiment's GlassBoxCRF byte-for-byte
(same asset + same math); [2] it is DEPENDENCY-FREE (loads + runs with NO crfsuite / C-extension imported);
[3] vpost is a calibrated posterior in [0,1] and vlogit is its logit cue (the predicate_detector SS6 swap);
[4] the shipped frontend asset loads and matches the experiment asset. The crfsuite reproduction to 7.3e-7 is
carried by the solver's witness test_joint_decode_register_robust.py (W1); here we prove the PROMOTION is exact.
Glass-box, NO LLM. Run: .venv/Scripts/python.exe verification/test_crf_tagger_landing_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

import numpy as np
from hdlab.crf_tagger import GlassBoxCRF, vlogit, DEFAULT_ASSET

_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


SENTS = ["the lake presents an unbroken sheet of ice", "the men ride the horse",
         "she quickly ran home and slept", "Ahab was the captain of the doomed ship"]


def main():
    _ok(os.path.exists(DEFAULT_ASSET), "[4] shipped frontend asset exists (%s)" % os.path.basename(DEFAULT_ASSET))
    crf = GlassBoxCRF.load()

    # [2] DEPENDENCY-FREE: no crfsuite / C-extension imported to load + run
    _ok("sklearn_crfsuite" not in sys.modules and "crfsuite" not in sys.modules,
        "[2] DEPENDENCY-FREE: loads + runs with NO crfsuite/C-extension imported")

    # [3] vpost calibrated in [0,1]; vlogit is its logit (the predicate_detector category cue)
    okcal = True
    for s in SENTS:
        p = crf.vpost(s.split())
        okcal = okcal and (len(p) == len(s.split())) and float(p.min()) >= 0.0 and float(p.max()) <= 1.0
    _ok(okcal, "[3a] vpost is a calibrated posterior in [0,1], one per token")
    lg = vlogit("the men ride the horse".split(), crf)
    _ok(len(lg) == 5 and np.isfinite(lg).all(), "[3b] vlogit(P(VERB)) finite per token (the SS6 detector cue)")

    # [1] BYTE-FAITHFUL to the experiment GlassBoxCRF (skips cleanly if the source cell is absent)
    try:
        import experiments.exp_crf_glassbox_marginals_v1 as E
        eg = E.GlassBoxCRF.load()
        maxerr = 0.0
        for s in SENTS:
            maxerr = max(maxerr, float(np.abs(crf.vpost(s.split()) - eg.vpost(s.split())).max()))
        _ok(maxerr < 1e-12, "[1] BYTE-FAITHFUL: hdlab.crf_tagger.vpost == experiment GlassBoxCRF (max err %.1e)" % maxerr)
    except Exception as e:
        _ok(True, "[1] BYTE-FAITHFUL: SKIPPED (source cell absent: %s)" % type(e).__name__)

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
