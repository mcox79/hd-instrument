"""Scaffold-free witness for the BRAIN-FOUNDATIONAL DEEPENING of
notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule.

Reproduces the headline of exp_reader_fillergap_reversible_objrel_v1 without touching any landed
directory: on a controlled reversible set, the positional two-line rule CATASTROPHICALLY FAILS on
object-relatives / object-clefts (the constructions the brain's dorsal parser exists for), the
brain's filler-gap/movement operation with a correct parse resolves them PERFECTLY, and even the
real (weak) arc parser beats the two-line rule there CI-separated -- so the two-line rule is NOT the
ceiling; the bottleneck is parser quality. The two-line rule remains perfect on canonical/passive.

Run:  .venv/Scripts/python.exe verification/test_reader_fillergap_reversible_objrel.py
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

import exp_reader_fillergap_reversible_objrel_v1 as EX  # noqa: E402

EX.N_BOOT = 3000


def main() -> int:
    EX.self_test()
    from experiments.exp_stated_entity_fate_reading_extractor_v1 import _load_or_build_frontend
    gen = _load_or_build_frontend()
    items = EX.build_items(seed=7, per_type=300)
    res = EX.score(items, gen, EX.N_BOOT)
    S = res["strata"]
    orl, ocl, ca, rp = S["object_relative"], S["object_cleft"], S["canonical_active"], S["reversible_passive"]

    def acc(s, arm):
        return s["acc"][arm]
    print(f"object_relative n={orl['n']}: 2LINE={acc(orl,'TWO_LINE'):.3f} ORACLE={acc(orl,'FILLERGAP_ORACLE'):.3f} "
          f"REAL={acc(orl,'FILLERGAP_REAL'):.3f} TWIN={acc(orl,'TWIN'):.3f} "
          f"[oracle-2line {orl['band_oracle_vs_twoline']}; real-2line {orl['band_real_vs_twoline']}]", flush=True)
    print(f"object_cleft   n={ocl['n']}: 2LINE={acc(ocl,'TWO_LINE'):.3f} ORACLE={acc(ocl,'FILLERGAP_ORACLE'):.3f} "
          f"REAL={acc(ocl,'FILLERGAP_REAL'):.3f} [oracle-2line {ocl['band_oracle_vs_twoline']}; "
          f"real-2line {ocl['band_real_vs_twoline']}]", flush=True)
    print(f"canonical n={ca['n']}: 2LINE={acc(ca,'TWO_LINE'):.3f}  passive n={rp['n']}: 2LINE={acc(rp,'TWO_LINE'):.3f}", flush=True)

    ok = True
    # 1. two-line CATASTROPHICALLY fails on the fronted regime (the brain's dorsal-parser regime).
    if not (acc(orl, "TWO_LINE") < 0.10 and acc(ocl, "TWO_LINE") < 0.10):
        print("FAIL: two-line rule did not fail on object-relatives/clefts")
        ok = False
    # 2. the brain's mechanism with a correct parse resolves them (oracle beats two-line, CI-separated).
    if not (orl["band_oracle_vs_twoline"] == "ABOVE" and ocl["band_oracle_vs_twoline"] == "ABOVE"):
        print("FAIL: filler-gap ORACLE does not beat two-line on the fronted regime")
        ok = False
    # 3. even the REAL (weak) parser beats two-line there CI-separated -> two-line is not the ceiling.
    if not (orl["band_real_vs_twoline"] == "ABOVE" and ocl["band_real_vs_twoline"] == "ABOVE"):
        print("FAIL: filler-gap REAL parser does not beat two-line on the fronted regime")
        ok = False
    # 4. two-line stays perfect on canonical + passive (the mechanism is additive, regime-specific).
    if not (acc(ca, "TWO_LINE") > 0.95 and acc(rp, "TWO_LINE") > 0.95):
        print("FAIL: two-line rule not near-perfect on canonical/passive")
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
