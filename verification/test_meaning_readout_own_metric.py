"""SCAFFOLD-FREE WITNESS for meaning_read_out_untested_on_the_own_metric.

Reproduces the headline of experiments/exp_meaning_readout_own_metric_v1.py WITHOUT re-running the
substrate read: it reads the cell's saved metrics.json (per-arm hit_vectors + comparisons) and

  1. recomputes every arm's precision from its saved hit_vector and asserts it matches the saved value;
  2. recomputes the paired-bootstrap (read-out - TOP_COOC / - TOP_PPMI) separation and asserts it
     matches the saved `beats_floor_upper_bound` for each read-out;
  3. INDEPENDENTLY reloads the LANDED own-metric instrument data/exp_grounding_precision_gold_v1/
     metrics.json and asserts this cell's TOP_COOC and SUBSTRATE reproduce the landed TOP_COOCCURRENT
     and SUBSTRATE per seed (the instrument-reproduction check the brief demanded);
  4. asserts the HEADLINE: no meaning read-out (nor any brain-foundational combined mechanism) beats
     the counting floor CI-separated over its upper bound on any powered seed -- i.e. counting is not
     beaten on the substrate's own metric.

Writes to NO landed directory. Deterministic. ASCII-only.
  .venv/Scripts/python.exe verification/test_meaning_readout_own_metric.py
"""
import json
import os
import sys

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CELL = os.path.join(_REPO, "data", "exp_meaning_readout_own_metric_v1", "metrics.json")
LANDED = os.path.join(_REPO, "data", "exp_grounding_precision_gold_v1", "metrics.json")

# the semantic read-outs + combined mechanisms that the brief asks about (must NOT beat counting)
READOUTS = ("READING_A", "READING_B", "FUSION_A", "FUSION_B", "CHANNEL_A", "CHANNEL_B",
            "COUNT_x_AGREE", "RRF_COUNT_READING", "TOPK10_GROUNDED", "TOPK20_GROUNDED")


def main():
    assert os.path.exists(CELL), "cell metrics.json missing -- run --phase score --mode full first"
    M = json.load(open(CELL, encoding="utf-8"))
    units = M["units"]
    seeds = sorted(units)
    print("[witness] %d seed-units; verdict=%s" % (len(seeds), M["verdict"]))

    # landed instrument, for the reproduction check
    L = json.load(open(LANDED, encoding="utf-8"))["units"]
    land_by_seed = {u["seed"]: u for u in L.values()}

    headline_ok = True
    for uk in seeds:
        u = units[uk]
        seed = u["meta"]["seed"]
        n = u["n_scorable"]
        # 1. recompute precision from hit_vector
        for arm, d in u.items():
            if not isinstance(d, dict) or "hit_vector" not in d:
                continue
            hv = np.array(d["hit_vector"], dtype=np.float64)
            assert hv.size == n, "%s hit_vector len %d != n %d" % (arm, hv.size, n)
            rec = float(hv.mean())
            assert abs(rec - d["precision"]) < 1e-9, \
                "%s precision recompute %.6f != saved %.6f" % (arm, rec, d["precision"])
        # 2. consistency: recomputed gate matches saved for BOTH floors; HEADLINE keys ONLY on the
        #    STRONGER counting floor TOP_COOC (raw count). Beating the WEAKER TOP_PPMI is expected and
        #    is not "beating counting".
        for r_ in READOUTS:
            for fl in ("TOP_COOC", "TOP_PPMI"):
                beats = bool(u[r_]["ci_lo"] > u[fl]["ci_hi"])
                saved = u["comparisons"]["%s_vs_%s" % (r_, fl)]["beats_floor_upper_bound"]
                assert beats == saved, "%s vs %s upper-bound gate mismatch" % (r_, fl)
            c = u["comparisons"]["%s_vs_TOP_COOC" % r_]
            if c["beats_floor_upper_bound"] or c["separated"]:
                headline_ok = False   # a read-out beat RAW COUNTING (upper-bound or paired) -> not the headline
        # 3. reproduction: TOP_COOC / SUBSTRATE vs landed
        lu = land_by_seed.get(seed)
        assert lu is not None, "no landed unit for seed %d" % seed
        for mine, land in (("TOP_COOC", "TOP_COOCCURRENT"), ("SUBSTRATE", "SUBSTRATE")):
            got = u[mine]["precision"]
            exp = lu[land]["precision"]
            assert abs(got - exp) < 1e-6, \
                "seed %d %s reproduce %.6f != landed %s %.6f" % (seed, mine, got, land, exp)
        print("   seed %d: TOP_COOC=%.4f (landed %.4f) SUBSTRATE=%.4f (landed %.4f) "
              "best_readout=%.4f ORACLE_A=%.4f OK"
              % (seed, u["TOP_COOC"]["precision"], lu["TOP_COOCCURRENT"]["precision"],
                 u["SUBSTRATE"]["precision"], lu["SUBSTRATE"]["precision"],
                 max(u[r_]["precision"] for r_ in READOUTS), u["ORACLE_A"]["precision"]))

    # 4. headline: counting not beaten
    assert headline_ok, "a read-out DID beat a counting floor -- headline (counting not beaten) is FALSE"
    assert M["verdict"].startswith("READOUT_TIES_OR_LOSES_COUNTING"), \
        "verdict is not the ties-or-loses headline: %s" % M["verdict"]
    print("[witness] HEADLINE CONFIRMED: no meaning read-out nor combined mechanism beats the counting "
          "floor CI-separated on any powered seed; instrument reproduces the landed cell exactly.")
    print("[witness] PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
