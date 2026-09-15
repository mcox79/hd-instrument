"""SCAFFOLD-FREE WITNESS for the predict-and-revise parse-RECALL organ
(problem: the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise).

Recomputes the headline FROM SOURCE through the LIVE reader on a fresh QA-SRL sample (no pre-baked
metrics.json): builds the population by running the POSITIONAL and WIRED readers, fits the plausibility
prior on held-out QA-SRL train, and checks the predict-and-revise pass RECOVERS who-did-what:
  [1] revise-on-WIRED beats the WIRED parse-router (the STRONGEST real floor) CI-separated;
  [2] revise-on-POSITIONAL beats the positional parse-as-truth floor CI-separated;
  [3] the info-free RANDOM-LOCI twin LOSES CI-separated (the violation gate localises the fix);
  [4] the info-free UNIFORM-prior twin does not beat the real pass (prior content is not free);
  [5] revise-everywhere does NOT beat the surprisal-gated pass (the gate is not doing negative work);
  [6] the recovery is concentrated in the PRE-VERBAL-gap construction (floor ~0 -> recovered);
  [7] the LOCATED finding reproduces: a NO-PRIOR structural re-parse ties the prior pass (the lever is
      the gated STRUCTURAL recall of the dropped argument, not the verb-specific selectional prior).

Glass-box, NO external LLM, NO spaCy. Deterministic. ASCII only. ~2-3 min (small fresh read)."""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from experiments._forward_prediction_live import get_tagger, fit_predictor
from experiments.exp_reader_vs_twoline_qasrl_power_v1 import load_patient_items
import experiments.exp_predict_revise_recall_v1 as M

# the frozen config (OUR-INVENTION-UNDER-TEST, swept in the cell; the witness pins the selected point --
# tau=2.0 beta=0.35 prec_floor=0.3, the full-run n=2737 selection)
TAU, BETA, PREC_FLOOR = 2.0, 0.35, 0.3
LIMIT = 350          # dev + test items each (fresh read; small but powered for the direction)
FIT_LIMIT = 40000    # predictor fit on QA-SRL TRAIN (held out from dev/test)


def main():
    tagger = get_tagger()
    predictor = fit_predictor(limit=FIT_LIMIT)
    dev = load_patient_items("dev.jsonl.gz", limit=LIMIT)
    for d in dev:
        d["split"] = "dev"
    test = load_patient_items("test.jsonl.gz", limit=LIMIT)
    for d in test:
        d["split"] = "test"
    pop, counts = M.build_population(dev + test, predictor, tagger, corpus="qasrl")
    n = len(pop)
    final = M.evaluate(pop, TAU, BETA, PREC_FLOOR, n_boot=2000)
    arms, _ = M.make_arms(pop, TAU, BETA, PREC_FLOOR)
    pc = M.per_construction(pop, arms)
    r = final["recall"]

    checks = []

    def chk(name, cond, detail):
        checks.append((name, bool(cond), detail))

    d1 = final["wired_gated_vs_wired"]
    chk("[1] revise-on-WIRED beats the STRONGEST floor (wired) CI-sep",
        d1["ci_lo"] > 0.0,
        f"delta {d1['delta']:+.4f} CI[{d1['ci_lo']:+.4f},{d1['ci_hi']:+.4f}] "
        f"(wired {r['wired']:.4f} -> revise {r['revise_wired_gated']:.4f})")

    d2 = final["pos_gated_vs_floor"]
    chk("[2] revise-on-POSITIONAL beats the positional floor CI-sep",
        d2["ci_lo"] > 0.0,
        f"delta {d2['delta']:+.4f} CI[{d2['ci_lo']:+.4f},{d2['ci_hi']:+.4f}] "
        f"(floor {r['floor_positional']:.4f} -> revise {r['revise_pos_gated']:.4f})")

    d3 = final["wired_gated_vs_random"]
    chk("[3] info-free RANDOM-LOCI twin LOSES CI-sep",
        d3["ci_lo"] > 0.0,
        f"delta {d3['delta']:+.4f} CI[{d3['ci_lo']:+.4f},{d3['ci_hi']:+.4f}]")

    d4 = final["wired_gated_vs_uniform"]
    chk("[4] info-free UNIFORM-prior twin does not beat the real pass",
        d4["delta"] >= -0.005,
        f"delta {d4['delta']:+.4f} CI[{d4['ci_lo']:+.4f},{d4['ci_hi']:+.4f}]")

    d5 = final["wired_gated_vs_everywhere"]
    chk("[5] revise-EVERYWHERE does not beat the gated pass (gate not contraindicated)",
        d5["delta"] >= -0.01,
        f"delta {d5['delta']:+.4f} CI[{d5['ci_lo']:+.4f},{d5['ci_hi']:+.4f}]")

    pv = pc.get("preverbal_gap", {})
    chk("[6] PRE-VERBAL-gap construction recovered (revise_wired > floor)",
        pv.get("revise_wired_gated", 0.0) > pv.get("floor", 1.0),
        f"n={pv.get('n')} floor {pv.get('floor'):.4f} -> revise_wired {pv.get('revise_wired_gated'):.4f} "
        f"(wired {pv.get('wired'):.4f})")

    d7 = final["wired_gated_vs_struct"]
    chk("[7] LOCATED: a NO-PRIOR structural re-parse ~ties the prior pass (lever is STRUCTURE, gated)",
        abs(d7["delta"]) < 0.05,
        f"delta {d7['delta']:+.4f} CI[{d7['ci_lo']:+.4f},{d7['ci_hi']:+.4f}] (|delta|<0.05 => prior content not the lever)")

    d8a = final["dropped_only_vs_wired"]
    d8b = final["wired_gated_vs_dropped_only"]
    chk("[8] LOCATED: the gain is DROP-FILLING (dropped-only beats wired CI-sep; surprisal gate adds ~0)",
        d8a["ci_lo"] > 0.0 and abs(d8b["delta"]) < 0.03,
        f"dropped_only-vs-wired {d8a['delta']:+.4f} CI[{d8a['ci_lo']:+.4f},{d8a['ci_hi']:+.4f}]; "
        f"gated-vs-dropped_only {d8b['delta']:+.4f} CI[{d8b['ci_lo']:+.4f},{d8b['ci_hi']:+.4f}] "
        f"(=> the surprisal gate on COMMITTED picks is not load-bearing; a structural drop trigger suffices)")

    print(f"\n=== witness: predict-and-revise parse-RECALL (n={n}, tau={TAU} beta={BETA} prec_floor={PREC_FLOOR}) ===")
    npass = 0
    for name, ok, detail in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}\n           {detail}")
        npass += int(ok)
    print(f"\nRESULT: {npass}/{len(checks)} checks pass")
    if npass != len(checks):
        sys.exit(1)


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
