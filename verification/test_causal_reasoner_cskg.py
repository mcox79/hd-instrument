"""Scaffold-free witness: the c-LEVER tested with a real directed causal KB (CSKG). The phase diagram
says correctness c is the sole binding axis; this measures whether the on-disk directed causal-knowledge
prior (CSKG, 86k causal edges) can raise c on real narrative -- and locates the wall at a NUMBER.

  K1 CSKG loads a large directed causal graph (>10k cause->effect lemma pairs) and answers directed
     causal queries (ring->sound).
  K2 IDENTIFIABILITY WALL, MEASURED: CSKG covers only ~18% of the TRUE narrative cause-pairs -- generic
     causal knowledge does not contain the CONTEXTUAL/specific causal links narratives use.
  K3 consequently the CSKG-gated densification does NOT raise the non-adjacent cause-ID (c) over the
     topical baseline (cskg_backoff is not CI-separated above dense) -- coverage-bounded + redundant
     where it fires. A rigorous located negative: the c-lever is the right axis, but the available
     glass-box knowledge is too generic; contextual causal inference (barred: external LLM) is required.

Re-derives live from experiments.exp_causal_reasoner_cskg_v1. Requires data/cskg_foundation_v1 + tellmewhy.
Run: .venv/Scripts/python.exe verification/test_causal_reasoner_cskg.py
"""
import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments.exp_causal_reasoner_cskg_v1 import run, build_cskg_causal, cskg_causal, CSKG_DIR

PASS = FAIL = 0


def chk(name, cond, detail=""):
    global PASS, FAIL
    ok = bool(cond)
    print(("  PASS " if ok else "  FAIL ") + name + ("" if not detail else "  [%s]" % detail), flush=True)
    PASS += int(ok); FAIL += int(not ok)
    return ok


def main():
    if not os.path.isdir(CSKG_DIR):
        print("  SKIP: CSKG foundation not on disk", flush=True)
        return 0
    c = build_cskg_causal()
    n_edges = sum(len(v) for v in c.values())
    chk("K1 CSKG directed causal KB loads + answers directed queries (ring->sound)",
        n_edges > 10000 and cskg_causal("ring", "sound"), "%d cause->effect lemma pairs" % n_edges)

    out = run(n=1500)
    cov = out["cskg_coverage_of_true_cause_pairs"]
    chk("K2 IDENTIFIABILITY WALL measured: CSKG covers <30%% of true narrative cause-pairs",
        cov < 0.30, "coverage of true cause-pairs = %.3f (generic KB misses contextual causation)" % cov)

    cm = out["contrasts_multihop"]
    am = out["acc_multihop"]
    chk("K3 CSKG does NOT raise c over topical (coverage-bounded + redundant where it fires)",
        not cm["cskg_backoff_vs_dense"]["ci_sep"],
        "cskg %.4f / cskg_backoff %.4f / dense(topical) %.4f ; backoff-dense %+.4f CI%s" % (
            am["cskg"], am["cskg_backoff"], am["dense"],
            cm["cskg_backoff_vs_dense"]["delta"], cm["cskg_backoff_vs_dense"]["ci"]))
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
