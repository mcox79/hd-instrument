"""Scaffold-free witness: the BRAIN-FOUNDATIONAL causal reasoner on MODERN non-circular gold (WIQA)
REFUTES the prior WIQA HARD_FAILs and shows the multi-hop traversal is LOAD-BEARING -- while honestly
bounding WIQA as a weak (procedural, monotone-linear) instrument for multi-hop causal reasoning.

  W1 the reasoner (gold-anchored, reasoning-isolated) BEATS the prior polarity-echo baseline the loop
     barely beat, AND beats majority -- CI-separated (refutes 'inference approach flawed even with
     gold anchors': the prior loop LOST to majority; this reasoner wins).
  W2 on the MULTI-HOP subset (|j-i|>=2) the traversal is load-bearing: reason beats the 1-hop
     ADJACENCY floor (which scores ~0 -- it cannot propagate through the chain) AND the shuffled-edge
     TWIN, both CI-separated.
  W3 `no_effect` modeled as REACHABILITY/necessity beats the prior chance-level LEXICAL trick
     (polarity-echo's no_effect balanced-acc ~0.49 = the reproduced prior 0.4997); AND the honest
     bound: grounding-presence is an even better no_effect detector -> WIQA's no_effect is a GROUNDING
     phenomenon, its multi-hop SIGN an edge-extraction wall, not a reasoning flaw.

Re-derives live from experiments.exp_causal_reasoner_wiqa_v1 (does NOT overwrite the landed metrics).
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_wiqa.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_reasoner_wiqa_v1 import (
    load_items, score, acc, balanced_acc_no_effect, paired_boot)

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    items = load_items()
    chk("W0 loaded WIQA dev_with_expl (>1000 items)", len(items) > 1000, "n=%d" % len(items))
    rows = score(items)
    ov = {a: acc(rows, a) for a in ("reason_oracle", "reason_glass", "adjacency", "polarity_echo", "majority")}

    d_pe = paired_boot(rows, "reason_oracle", "polarity_echo")
    chk("W1 reasoner beats polarity-echo CI-sep AND beats majority (refutes prior HARD_FAIL)",
        d_pe["ci_sep"] and ov["reason_oracle"] > ov["majority"],
        "reason_oracle %.4f | polarity_echo %.4f (+%.4f CI%s) | majority %.4f" % (
            ov["reason_oracle"], ov["polarity_echo"], d_pe["delta"], d_pe["ci"], ov["majority"]))

    d_adj = paired_boot(rows, "reason_oracle", "adjacency", key="oracle_multihop")
    d_tw = paired_boot(rows, "reason_oracle", "twin", key="oracle_multihop")
    adj_mh = acc([r for r in rows if r["oracle_multihop"]], "adjacency")
    chk("W2 multi-hop traversal LOAD-BEARING: beats 1-hop adjacency (~0) + twin, both CI-sep",
        d_adj["ci_sep"] and d_tw["ci_sep"] and adj_mh <= 0.05,
        "multihop n=%d | adjacency %.4f | reason-adj +%.4f CI%s | reason-twin +%.4f CI%s" % (
            d_adj["n"], adj_mh, d_adj["delta"], d_adj["ci"], d_tw["delta"], d_tw["ci"]))

    ne_reason = balanced_acc_no_effect(rows, "reason_glass")
    ne_pe = balanced_acc_no_effect(rows, "polarity_echo")
    ne_gr = balanced_acc_no_effect(rows, "grounding")
    chk("W3 reachability no_effect beats the prior lexical trick (~0.49); grounding is the honest bound",
        ne_reason > ne_pe + 0.02 and ne_pe < 0.55 and ne_gr >= ne_reason,
        "reason_glass %.4f > polarity_echo %.4f (prior lexical ~0.4997) ; grounding %.4f" % (
            ne_reason, ne_pe, ne_gr))

    print("\n%d/%d checks passed" % (PASS, PASS + FAIL), flush=True)
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
