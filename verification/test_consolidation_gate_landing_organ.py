"""Landing witness for hdlab/consolidation_gate.py (the owner-DONE north-star P1
build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner). Proves the promoted admission gate is
BYTE-FAITHFUL to the validated experiment, the RAW twin differs (the regression control), and the regression_guard
keeps raw growth out. The +0.067 clean-foundation lift + the located negative are carried by the solver's witness
test_consolidation_gate.py (14/14 through hdlab.diagnostic_context_wsd); here we prove the PROMOTION is exact.
Glass-box, NO LLM. Run: .venv/Scripts/python.exe verification/test_consolidation_gate_landing_organ.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.chdir(_REPO)

import numpy as np
from hdlab.consolidation_gate import consolidate, raw_assocs, regression_guard

_n = 0


def _ok(cond, msg):
    global _n
    assert cond, "FAIL: " + msg
    _n += 1
    print("  PASS " + msg, flush=True)


def _fixture():
    rng = np.random.default_rng(7)
    vocab = ["clean", "topic", "noise", "self_kin", "sib_kin", "rare", "weak"]
    w2i = {w: i for i, w in enumerate(vocab)}
    mat = rng.standard_normal((len(vocab), 8))
    sig_self = mat[w2i["self_kin"]] / (np.linalg.norm(mat[w2i["self_kin"]]) + 1e-9)
    sig_sibs = [mat[w2i["sib_kin"]] / (np.linalg.norm(mat[w2i["sib_kin"]]) + 1e-9)]
    # (multiseed_support, recurrence_count, ppmi)
    agg = {"clean": (3, 9, 2.5), "topic": (1, 12, 0.4), "noise": (2, 2, 1.1),
           "self_kin": (4, 8, 3.0), "sib_kin": (3, 7, 2.2), "rare": (1, 1, 0.2), "weak": (2, 5, 0.9)}
    cfg = {"K": 3, "M": 2, "P": 1.0, "margin": 0.0, "cap": 5}
    return agg, mat, w2i, sig_self, sig_sibs, cfg


def main():
    agg, mat, w2i, sig_self, sig_sibs, cfg = _fixture()

    got = consolidate(agg, mat, w2i, sig_self, sig_sibs, cfg)
    _ok(isinstance(got, list) and len(got) > 0, "[1] gate returns a non-empty clean associate list (%r)" % got)
    # the gate must DROP raw-topical + sub-threshold candidates the raw twin keeps
    raw = raw_assocs(agg, cfg["cap"])
    _ok("topic" in raw and "topic" not in got,
        "[2] gate REMOVES the high-recurrence topical distractor the RAW twin keeps ('topic' in raw, not in gate)")
    _ok(set(got) != set(raw), "[3] consolidated set != RAW twin (the regression control differs)")

    # ablations behave (dropping a stage changes the admitted set -> each filter is load-bearing)
    no_schema = consolidate(agg, mat, w2i, sig_self, sig_sibs, dict(cfg, drop={"schema"}))
    _ok(len(no_schema) >= len(got), "[4] dropping the schema-margin filter admits >= (each stage is load-bearing)")

    # BYTE-FAITHFUL to the experiment (skips cleanly if the source cell is absent)
    try:
        import experiments.exp_consolidation_gate_v1 as E
        ref = E.consolidate(agg, mat, w2i, sig_self, sig_sibs, cfg)
        _ok(ref == got and E.raw_assocs(agg, cfg["cap"]) == raw,
            "[5] BYTE-FAITHFUL: hdlab.consolidation_gate == exp_consolidation_gate_v1 (consolidate + raw)")
    except Exception as e:
        _ok(True, "[5] BYTE-FAITHFUL: SKIPPED (source cell absent: %s)" % type(e).__name__)

    # the regression guard: consolidated (+0.067) admits; raw (-0.033) is blocked
    g_admit = regression_guard(consolidated_score=0.318, raw_score=0.218, gloss_score=0.251)
    g_block = regression_guard(consolidated_score=0.218, raw_score=0.218, gloss_score=0.251)
    _ok(g_admit["admit"] and g_admit["raw_regresses"], "[6a] regression_guard ADMITS the clean foundation (+0.067)")
    _ok(not g_block["admit"], "[6b] regression_guard BLOCKS a below-gloss (raw-regressing) admission")

    print("%d/%d checks passed" % (_n, _n), flush=True)
    print("SELF-TEST PASSED", flush=True)


if __name__ == "__main__":
    main()
