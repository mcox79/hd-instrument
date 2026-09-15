"""Scaffold-free witness for the BRAIN-FIDELITY drill of
notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule.

Reproduces the fidelity headline of exp_reader_cue_retrieval_interference_v1 without touching any
landed directory: on the Gordon (2001) object-relative design (SIMILAR vs DISSIMILAR intervening
noun), a brain-faithful CUE-BASED RETRIEVAL mechanism reproduces the human similarity-based
interference signature (worse under similarity), while the structural point-to-antecedent
(FILLERGAP_ORACLE) is FLAT (over-accurate) -- the tell that structural pointing is a convenient
substitute, not a copy of the brain's computation.

Run:  .venv/Scripts/python.exe verification/test_reader_cue_retrieval_interference.py
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

import exp_reader_cue_retrieval_interference_v1 as EX  # noqa: E402

EX.N_BOOT = 3000


def main() -> int:
    EX.self_test()
    from experiments.exp_stated_entity_fate_reading_extractor_v1 import _load_or_build_frontend
    gen = _load_or_build_frontend()
    items = EX.build_items(seed=7, per_cond=400)
    res, n = EX.score(items, gen, temp=0.5, n_boot=EX.N_BOOT)
    cue = res["CUE_RETRIEVAL"]
    orc = res["FILLERGAP_ORACLE"]
    print(f"n={n}  CUE_RETRIEVAL sim={cue['similar']['point']:.3f} dis={cue['dissimilar']['point']:.3f} "
          f"effect(dis-sim)={cue['similarity_effect']['point']:+.3f} "
          f"CI[{cue['similarity_effect']['ci95'][0]:+.3f},{cue['similarity_effect']['ci95'][1]:+.3f}] "
          f"{cue['band_similarity_effect']}", flush=True)
    print(f"          FILLERGAP_ORACLE sim={orc['similar']['point']:.3f} dis={orc['dissimilar']['point']:.3f} "
          f"effect={orc['similarity_effect']['point']:+.3f} {orc['band_similarity_effect']}", flush=True)

    ok = True
    # 1. cue-based retrieval reproduces the human interference: worse under similarity (effect ABOVE 0).
    if cue["band_similarity_effect"] != "ABOVE":
        print("FAIL: cue-based retrieval does not show the human similarity-interference drop")
        ok = False
    # 2. the structural point-to-antecedent is FLAT (over-accurate): no similarity effect.
    if orc["band_similarity_effect"] != "NOT_SEPARATED":
        print("FAIL: structural filler-gap unexpectedly shows a similarity effect")
        ok = False
    # 3. sanity: the structural arm is near-perfect (the over-accuracy that is the fidelity gap).
    if not (orc["similar"]["point"] > 0.95 and orc["dissimilar"]["point"] > 0.95):
        print("FAIL: structural filler-gap is not near-perfect")
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
