#!/usr/bin/env python3
"""Witness for the grounded-successor-features LANDING investigation -- reproduces the LOCATED NEGATIVE
on the current bytes + real assets: SF over grounded WORD dynamics does NOT generalise (fast mixing
washes out the successor structure), though grounded features DO carry information.

Run:  .venv/Scripts/python.exe verification/test_grounded_successor_features_landing.py
"""
from __future__ import annotations

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "experiments", name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    cell = _load("exp_grounded_successor_features_landing_v1")
    # the organ is promotion-ready + self-contained (no experiments.* import in its own body)
    src = open(os.path.join(ROOT, "experiments", "exp_grounded_successor_features_landing_v1.py"),
               encoding="utf-8").read()
    r = cell.run(vocab_cap=500, n_boot=800)
    tw = r["sf_vs_twin_heldout"]; st = r["sf_vs_tabular_heldout"]; mps = r["meaning_predicts_succession"]
    results = []

    def chk(name, cond, detail=""):
        results.append(cond)
        print(f"  {'ok' if cond else 'XX'}  {name}{('  -- ' + detail) if detail else ''}")

    print("GROUNDED SUCCESSOR FEATURES LANDING -- located-negative witness (real GUM + real ATL norms)\n")
    chk("G1 the organ is self-contained (promotion-ready: no experiments.* import in its body)",
        "from experiments" not in src and "import experiments" not in src)
    chk("G2 loaders read the REAL grounded basis (>=30k grounded words) + modern GUM sequences",
        r["config"]["n_grounded_words"] >= 30000 and r["config"]["n_sequences"] > 1000,
        f"grounded={r['config']['n_grounded_words']} gum_seqs={r['config']['n_sequences']}")
    chk("G3 POSITIVE CONTROL: grounded features carry information (SF beats the info-free twin CI-sep)",
        tw["ci_separated"] and tw["diff"] > 0, f"SF-TWIN={tw['diff']:.3f}")
    chk("G4 LOCATED NEGATIVE: grounded SF does NOT beat the tabular successor_representation constant "
        "on held-out words (fast mixing washes out the successor structure)",
        not (st["ci_separated"] and st["diff"] > 0),
        f"SF-TABULAR={st['diff']:.3f} (SF={r['held_out']['grounded_sf']:.2f} vs tab={r['held_out']['tabular']:.2f})")
    chk("G5 MECHANISM: a word's grounded MEANING does not predict its co-occurrence successors' "
        "features better than the global average (the SR cannot generalise on this dynamics)",
        not mps["grounded_beats_baseline"],
        f"grounded={mps['grounded']:.2f} vs baseline={mps['baseline']:.2f} diff={mps['diff']:.2f}")

    npass = sum(1 for c in results if c)
    print(f"\n{npass}/{len(results)} PASS")
    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
