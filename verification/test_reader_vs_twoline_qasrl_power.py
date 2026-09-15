"""Scaffold-free witness for notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule.

Reproduces the HEADLINE without touching any landed directory: on QA-SRL v2 gold PATIENT selection,
the elaborate perceptron cue-integration reader does NOT beat the clean two-line word-order+voice
rule (it ties or loses, CI-separated), while the information-free random-nominal TWIN loses to the
two-line rule, and the model's learned cue-weighting is WORD-ORDER-dominant not animacy-dominant
(order_only >> animacy_only), the brain-faithful pattern for English.

It imports the experiment module as a library and calls run_full() with reduced caps/n_boot -- it
computes, it does not re-run the landed cell, so no landed metrics.json is rewritten. The DIRECTION
(two-line >= elaborate; twin loses; order >> animacy) is robust to the reduced size.

Run:  .venv/Scripts/python.exe verification/test_reader_vs_twoline_qasrl_power.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_reader_vs_twoline_qasrl_power_v1 as EX  # noqa: E402

# Reduced but REAL: cap training entries and bootstrap for speed. The direction reproduces at
# a fraction of the landed run's size (CI width is governed by n, and n here is still thousands).
EX.MAX_TRAIN_ENTRIES = 6000
EX.N_BOOT = 3000


def main() -> int:
    EX.self_test()
    from experiments.exp_stated_entity_fate_reading_extractor_v1 import _load_or_build_frontend
    gen = _load_or_build_frontend()
    # Use the smoke path's caps for eval size but keep it real (dev+test capped inside run_full smoke).
    m = EX.run_full(gen, smoke=True)
    allc = m["strata"]["ALL"]
    elab = allc["acc"]["ELABORATE"]
    twoline = allc["acc"]["TWO_LINE"]
    twin = allc["acc"]["TWIN"]
    anim = allc["acc"]["ELAB_ANIMACY_ONLY"]
    order = allc["acc"]["ELAB_ORDER_ONLY"]
    band_et = allc["band_elaborate_vs_twoline"]
    band_tt = allc["band_twoline_vs_twin"]
    n = allc["n"]
    print(f"n={n}  ELABORATE={elab:.4f}  TWO_LINE={twoline:.4f}  TWIN={twin:.4f}  "
          f"animacy_only={anim:.4f}  order_only={order:.4f}", flush=True)
    print(f"elab_vs_twoline={band_et}  twoline_vs_twin={band_tt}  verdict={m['verdict']}", flush=True)

    ok = True
    # 1. The elaborate reader does NOT beat the two-line rule (it ties or loses) -> REPLACE.
    if band_et == "ABOVE":
        print("FAIL: elaborate reader beats the two-line rule CI-separated (headline would flip)")
        ok = False
    # 2. The info-free twin loses to the two-line rule (mandated control).
    if band_tt != "ABOVE":
        print("FAIL: info-free twin does NOT lose to the two-line rule")
        ok = False
    # 3. Brain-faithful English cue-weighting: word order dominates, animacy is near-useless.
    if not (order > anim + 0.15):
        print("FAIL: model is not word-order-dominant (order_only should far exceed animacy_only)")
        ok = False
    # 4. sanity: two-line rule is a real reader, well above the info-free floor.
    if not (twoline > twin + 0.20):
        print("FAIL: two-line rule not clearly above the info-free floor")
        ok = False
    print("WITNESS PASS" if ok else "WITNESS FAIL", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
