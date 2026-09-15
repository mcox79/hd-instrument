"""Witness for exp_crosstype_gum_conll_fullread_v1 -- the crosstype bridge measured through the WHOLE
SituationReader.read() on MODERN GUM (the last "equivalent-path" caveat, closed).

  W1  CONVERTER round-trip: the GUM->reader-CoNLL converter's output, parsed by the reader's own parse_litbank_conll,
      reproduces the GOLD mention spans+clusters exactly (a few docs).
  W2  the gold-coref LEAK reproduces end-to-end: baseline (gold-inherit) C3 >> de-leaked honest C3 through read().
  W3  the WIRE FIRES and LIFTS end-to-end: on a doc subset, the bridge applies merges (n_applied>0) and the honest
      floor C3 is lifted by the bridge (directional; the full-100-doc CI-separated +0.0430 [+0.0198,+0.0738] with the
      info-free twin losing lives in data/exp_crosstype_gum_conll_fullread_v1/metrics_stage2.json).

Run: .venv/Scripts/python.exe verification/test_crosstype_fullread_endtoend.py
"""
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import tempfile
import experiments.gum_coref as G
from experiments.exp_name_entity_clustering_v1 import load_given_gazetteer
import experiments.exp_crosstype_gum_conll_fullread_v1 as FR


def main():
    ok = 0
    gaz = load_given_gazetteer()

    # W1 -- converter round-trip
    docs = G.load_docs(gum_only=True, limit=12, name_gazetteer=gaz)
    with tempfile.TemporaryDirectory() as td:
        allok = True
        for i, d in enumerate(docs):
            p = os.path.join(td, "d%d.conll" % i)
            FR.gum_to_conll(d, p)
            rok, ng, gg = FR.verify_roundtrip(d, p, gaz)
            allok = allok and rok
    assert allok, "W1: GUM->CoNLL converter must round-trip gold mention spans"
    print("W1 PASS: GUM->reader-CoNLL converter round-trips gold mention spans (12 docs)")
    ok += 1

    # W2 -- the leak reproduces end-to-end (run() on a subset)
    r = FR.run(docs_limit=40, verbose=False)
    assert r["baseline_gold_inherit_C3"] > r["honest_deleaked_C3"] + 0.1, \
        "W2: baseline gold-inherit must exceed the de-leaked honest floor end-to-end: %.4f vs %.4f" % (
            r["baseline_gold_inherit_C3"], r["honest_deleaked_C3"])
    print("W2 PASS: gold-coref LEAK reproduces through the WHOLE read() -- baseline %.4f >> honest %.4f (n=%d)"
          % (r["baseline_gold_inherit_C3"], r["honest_deleaked_C3"], r["honest_n"]))
    ok += 1

    # W3 -- the wire fires and lifts end-to-end (directional; CI-sep is the full-100 number in metrics)
    FR.DeLeakedBridgeReader.n_applied = 0
    s = FR.stage2(docs_limit=60, verbose=False)
    assert s["bridge_merges_applied"] > 0, "W3: the bridge wire must FIRE end-to-end (merges applied): %s" % s
    assert s["bridge_C3"] > s["floor_C3"] and s["bridge_C3"] >= s["twin_C3"], \
        "W3: bridge must lift the honest floor and beat the twin end-to-end: floor %.4f bridge %.4f twin %.4f" % (
            s["floor_C3"], s["bridge_C3"], s["twin_C3"])
    print("W3 PASS: bridge fires end-to-end (%d merges) -- honest floor %.4f -> bridge %.4f (twin %.4f) through the WHOLE read()"
          % (s["bridge_merges_applied"], s["floor_C3"], s["bridge_C3"], s["twin_C3"]))
    ok += 1

    print("\nALL WITNESSES PASS (%d/%d)" % (ok, ok))
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
