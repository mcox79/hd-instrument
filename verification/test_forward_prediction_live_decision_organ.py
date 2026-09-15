"""Scaffold-free witness for `the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision`.

Recomputes every headline FROM SOURCE through the LIVE SituationReader.read() (never trusting the
landed metrics.json): fits hdlab.predictive_reader on QA-SRL TRAIN, runs the role-capable reader on
held-out QA-SRL dev+test sentences, computes per-argument surprisal on the reader's OWN who-did-what
bindings, and re-derives the two gates + the enumerated negative + the generalization slice.

  W1  ISLAND CONFIRMED: hdlab.predictive_reader is imported by NEITHER situation_reader NOR substrate
      (grep on disk) -- the forward-prediction signal is never computed on a live path without this wire.
  W2  the LIVE signal drives end-to-end: the reader emits events, roles are bound, surprisal is computed
      on the reader's OWN picks (n_scored > 0).
  W3  INFORMATIVE gate: live per-argument surprisal predicts the reader's OWN who-did-what errors, AUC
      lower bound > 0.5 (CI-separated over chance).
  W4  the SHUFFLED-surprisal twin LOSES: real AUC > the info-free null p95.
  W5  ACTIONABLE (abstain / confidence): withholding the highest-surprisal answers raises committed
      accuracy over the un-gated reader, and over a random-abstention twin (delta at 0.8 coverage > 0).
  W6  the ENUMERATED NEGATIVE is real (not hidden): using surprisal to RE-SELECT the patient does NOT
      beat the un-gated reader CI-separated -- the grounded-space (prototype) re-selection wall.
  W7  precision-diagnosticity GRADED signature: the surprisal->error AUC is >= for SHARP (high-precision)
      verbs than diffuse ones (Friston/Federmeier precision-weighting), measured at the decision layer.
  W8  GENERALIZATION: on 19c LitBank narrative the INFORMATIVE signal holds (AUC lower bound > 0.5, twin
      loses) -- the meaning-level prediction transfers across register (not a modern-vocabulary artifact).
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

FAILS = []


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("  -- " + detail if detail else ""))
    if not cond:
        FAILS.append(name)


def _grep_imports(path, needle):
    if not os.path.exists(path):
        return False
    with open(path, "r", encoding="utf-8") as f:
        txt = f.read()
    return re.search(r"(^|\n)\s*(from|import)\s+[\w\.]*predictive_reader", txt) is not None or needle in txt


def main():
    import experiments.exp_forward_prediction_live_decision_v1 as E

    # W1 -- island: neither situation_reader nor substrate import predictive_reader
    sr = os.path.join(REPO, "hdlab/situation_reader.py")
    sub = os.path.join(REPO, "hdlab/substrate.py")
    sr_imports = _grep_imports(sr, "predictive_reader")
    sub_imports = _grep_imports(sub, "predictive_reader") if os.path.exists(sub) else False
    check("W1 ISLAND: predictive_reader NOT imported by situation_reader/substrate (the wire is needed)",
          (not sr_imports) and (not sub_imports),
          f"situation_reader_imports={sr_imports} substrate_imports={sub_imports}")

    # recompute FROM SOURCE through live read() (moderate size for a witness; fresh build, no reuse)
    res = E.run(smoke=False, n_boot=1500, role_route="wired",
                dev_limit_full=800, test_limit_full=800, do_litbank=True, reuse_items=False)
    out = res[0]

    pop = out["population"]
    check("W2 the LIVE signal drives end-to-end (reader emits events, roles bound, surprisal computed)",
          pop["n_scored_all"] > 100,
          f"n_scored_all={pop['n_scored_all']} reader_error_rate={pop['reader_error_rate']:.3f}")

    ig = out["informative_gate"]
    auc_pt, auc_lo, auc_hi = ig["auc_surprisal_predicts_error"]
    check("W3 INFORMATIVE: surprisal predicts the reader's OWN who-did-what errors, AUC lo > 0.5",
          auc_lo > 0.5,
          f"AUC {auc_pt:.3f} [{auc_lo:.3f},{auc_hi:.3f}]")
    check("W4 the SHUFFLED-surprisal twin LOSES: real AUC > null p95",
          auc_pt > ig["shuffle_twin_auc"]["p95"],
          f"AUC {auc_pt:.3f} > twin p95 {ig['shuffle_twin_auc']['p95']:.3f} (twin mean {ig['shuffle_twin_auc']['mean']:.3f})")

    ab = out["actionable_abstain"]
    m = ab["margin_at_0.8"]
    check("W5 ACTIONABLE (abstain): committed accuracy rises over the random-abstain twin (delta@0.8 > 0)",
          m["delta"] > 0 and m["real"] > m["twin"],
          f"committed@0.8 real {m['real']:.3f} vs twin {m['twin']:.3f} delta {m['delta']:+.3f} CI{m['ci95']}")

    rn = out["actionable_reanalysis"]
    rd = rn["delta_test"]
    check("W6 ENUMERATED NEGATIVE is real: surprisal-driven RE-SELECTION does NOT beat the reader CI-sep "
          "(grounded-space prototype re-selection wall)",
          not (rd["ci95"][0] > 0),
          f"reanalysis delta {rd['point']:+.4f} CI{rd['ci95']} (NOT CI-separated above 0)")

    ps = out.get("precision_signature", {})
    if ps:
        check("W7 precision-diagnosticity GRADED signature: AUC steeper for SHARP than diffuse verbs",
              ps.get("auc_sharp", 0) >= ps.get("auc_diffuse", 1) or ps.get("auc_top_tercile", 0) >= ps.get("auc_bot_tercile", 1),
              f"sharp {ps.get('auc_sharp'):.3f} vs diffuse {ps.get('auc_diffuse'):.3f}; "
              f"top-tercile {ps.get('auc_top_tercile')} vs bot {ps.get('auc_bot_tercile')}")
    else:
        check("W7 precision-diagnosticity signature present", False, "no precision items")

    lb = out.get("generalization_litbank", {})
    if lb and "auc" in lb:
        la_pt, la_lo, la_hi = lb["auc"]
        check("W8 GENERALIZATION (19c LitBank narrative): INFORMATIVE holds, AUC lo > 0.5 and twin loses",
              la_lo > 0.5 and la_pt > lb["shuffle_twin"]["p95"],
              f"LitBank AUC {la_pt:.3f} [{la_lo:.3f},{la_hi:.3f}] n={lb['n_items']}; twin p95 {lb['shuffle_twin']['p95']:.3f}")
    else:
        check("W8 GENERALIZATION LitBank slice ran", False, str(lb)[:120])

    print()
    if FAILS:
        print("WITNESS FAILED: " + ", ".join(FAILS))
        sys.exit(1)
    print("ALL WITNESS CHECKS PASS")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
