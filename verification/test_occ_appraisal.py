"""Scaffold-free witness for the OCC APPRAISAL inference (infer_unstated_emotion_via_occ_appraisal_over_event_
goal_congruence). Recomputes the headline + floors + twin + upstream superset FROM SOURCE (drives the LIVE
SituationReader over the constructed OCC gold; re-runs NO landed cell). 9 checks.

  W1  pure OCC rule table exact (desirability x prospect -> the 8 OCC types).
  W2  end-to-end TYPE accuracy on the gold (LIVE reader + upstream generalizations) >= 0.85.
  W3  APPRAISAL beats the STRONGEST type floor CI-separated (paired bootstrap over items).
  W4  the info-free goal<->event-shuffle TWIN LOSES CI-separated.
  W5  NOFIX (the CURRENT live substrate: baseline track_status + no prospect) COLLAPSES -> the upstream fix is
      the lever (APPRAISAL beats NOFIX CI-sep).
  W6  the LOAD-BEARING prospect subset (relief+fears_confirmed): APPRAISAL beats the valence-only + last-word
      floors, both PROVABLY wrong (0.0) there -- valence alone cannot name the OCC type.
  W7  APPRAISAL_ORACLE (gold structural variables) = 1.0 -> the composition rule is EXACT.
  W8  the upstream goal-failure generalization is a STRICT SUPERSET of hdlab.goal_register.track_status on the
      gold (0 satisfied/failed flips) AND adds real active->failed thwart detections.
  W9  VALENCE task: APPRAISAL beats the majority-valence floor CI-sep AND the twin loses.

Run: .venv/Scripts/python.exe verification/test_occ_appraisal.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
import copy
import numpy as np

from experiments import _occ_appraisal as OCC
from experiments._occ_upstream_goal_status import track_status_thwart
from experiments._occ_probe import load_gold
from experiments import exp_occ_appraisal_emotion_v1 as M


def main():
    print("witness: OCC appraisal inference (event x goal -> unstated emotion) -- recompute from source")

    # ---- W1 pure rule ----
    table = [(+1, "actual", "satisfaction"), (-1, "actual", "disappointment"), (+1, "prospective", "hope"),
             (-1, "prospective", "fear"), (-1, "confirmed", "fears_confirmed"), (-1, "disconfirmed", "relief"),
             (+1, "confirmed", "satisfaction"), (+1, "disconfirmed", "disappointment")]
    assert all(OCC.appraise(d, p) == t for d, p, t in table), "W1 FAIL: OCC rule table wrong"
    print("  W1 PASS: pure OCC rule table exact (8/8 desirability x prospect -> type)")

    # ---- drive the LIVE reader over the gold (recompute) ----
    gold = load_gold()
    rows = M.extract_all(gold)
    n = len(rows)
    rng = np.random.RandomState(20260906)
    twin_perm = M._derange(n, rng)
    mft = M._mft(rows); majtype = M._majority_type_of_valence(rows)
    mfv = 1 if sum(r["gold_val"] for r in rows) >= 0 else -1
    idx_ps = np.array([r["is_prospect_subset"] for r in rows], bool)

    T = {a: M.arm_type_correct(rows, a, mft=mft, majtype=majtype, twin_perm=twin_perm)
         for a in ["APPRAISAL", "APPRAISAL_ORACLE", "NOFIX", "FLOOR_MFT", "FLOOR_LASTWORD", "FLOOR_VAL_TYPE", "TWIN"]}
    V = {a: M.arm_val_correct(rows, a, mfv=mfv, twin_perm=twin_perm)
         for a in ["APPRAISAL", "NOFIX", "FLOOR_MFV", "FLOOR_LASTWORD", "TWIN"]}

    def ci(a, b):
        d, lo, hi, hw, p95 = M._paired_ci(a, b, rng)
        return d, lo, hi

    # ---- W2 end-to-end type accuracy ----
    acc = float(T["APPRAISAL"].mean())
    print("  W2: end-to-end TYPE acc = %.3f (n=%d)" % (acc, n))
    assert acc >= 0.85, "W2 FAIL: end-to-end type accuracy below 0.85"
    print("  W2 PASS: OCC appraisal names the unstated OCC emotion type >= 0.85 end-to-end")

    # ---- W3 vs strongest floor ----
    type_floor = max(("FLOOR_MFT", "FLOOR_LASTWORD", "FLOOR_VAL_TYPE"), key=lambda a: T[a].mean())
    d, lo, hi = ci(T["APPRAISAL"], T[type_floor])
    print("  W3: APPRAISAL vs strongest floor %s (%.3f): %+.3f CI[%+.3f,%+.3f]" % (type_floor, T[type_floor].mean(), d, lo, hi))
    assert lo > 0, "W3 FAIL: not CI-separated over the strongest type floor"
    print("  W3 PASS: beats the strongest type floor CI-separated")

    # ---- W4 twin loses ----
    d, lo, hi = ci(T["APPRAISAL"], T["TWIN"])
    print("  W4: APPRAISAL vs TWIN (%.3f): %+.3f CI[%+.3f,%+.3f]" % (T["TWIN"].mean(), d, lo, hi))
    assert lo > 0, "W4 FAIL: the goal<->event-shuffle twin did not lose CI-sep"
    print("  W4 PASS: the info-free goal<->event-shuffle twin LOSES CI-separated")

    # ---- W5 NOFIX collapses ----
    d, lo, hi = ci(T["APPRAISAL"], T["NOFIX"])
    print("  W5: APPRAISAL vs NOFIX/current-substrate (%.3f): %+.3f CI[%+.3f,%+.3f]" % (T["NOFIX"].mean(), d, lo, hi))
    assert lo > 0 and T["NOFIX"].mean() < 0.3, "W5 FAIL: NOFIX did not collapse / upstream fix not the lever"
    print("  W5 PASS: the current substrate collapses; the upstream generalization is the lever")

    # ---- W6 prospect subset ----
    valtype_ps = float(T["FLOOR_VAL_TYPE"][idx_ps].mean()); lw_ps = float(T["FLOOR_LASTWORD"][idx_ps].mean())
    app_ps = float(T["APPRAISAL"][idx_ps].mean())
    print("  W6: prospect-subset APPRAISAL %.3f | valence-only floor %.3f | last-word floor %.3f" % (app_ps, valtype_ps, lw_ps))
    assert app_ps >= 0.9 and valtype_ps == 0.0 and lw_ps == 0.0, "W6 FAIL: prospect subset not provably beating valence/last-word"
    print("  W6 PASS: on relief+fears_confirmed, valence alone is provably wrong (0.0); appraisal names the type")

    # ---- W7 oracle exact ----
    assert float(T["APPRAISAL_ORACLE"].mean()) == 1.0, "W7 FAIL: oracle rule not exact"
    print("  W7 PASS: APPRAISAL_ORACLE = 1.000 (the composition rule is exact given the structural variables)")

    # ---- W8 upstream strict superset ----
    from hdlab.goal_register import track_status as baseline_status
    from experiments._occ_probe import write_conll, _protagonist_canon
    from experiments._tom_chain import split_sents, tokenize
    from hdlab.situation_reader import SituationReader
    import tempfile
    reader = SituationReader(track_goals=True, track_affect=True)
    tmp = tempfile.mkdtemp(prefix="occ_wit_")
    violations = 0; a2f = 0; checked = 0
    for it in gold:
        cp = write_conll(it["text"], it["char"], tmp, it["id"]); sm = reader.read(cp)
        reg = getattr(sm, "goal_register", None)
        if not reg or not reg.goals:
            continue
        sents = [tokenize(s) for s in split_sents(it["text"])]
        canon = _protagonist_canon(sm, it["char"]); events = list(getattr(sm, "events", []) or [])
        gb = copy.deepcopy(reg.goals); baseline_status(gb, events)
        gt = copy.deepcopy(reg.goals); track_status_thwart(gt, events, sents=sents, canon=canon)
        for b, t in zip(gb, gt):
            checked += 1
            if b.status in ("satisfied", "failed") and t.status != b.status:
                violations += 1
            if b.status == "active" and t.status == "failed":
                a2f += 1
    print("  W8: upstream superset over %d goals: %d violations, %d active->failed additions" % (checked, violations, a2f))
    assert violations == 0 and a2f > 0, "W8 FAIL: not a strict superset / no thwart additions"
    print("  W8 PASS: the upstream goal-failure generalization is a strict superset + adds real thwart detections")

    # ---- W9 valence task ----
    d, lo, hi = ci(V["APPRAISAL"], V["FLOOR_MFV"])
    dt, lot, hit = ci(V["APPRAISAL"], V["TWIN"])
    print("  W9: VALENCE APPRAISAL %.3f vs majority-floor %.3f: %+.3f CI[%+.3f,%+.3f] | vs twin %+.3f CI[%+.3f,%+.3f]"
          % (V["APPRAISAL"].mean(), V["FLOOR_MFV"].mean(), d, lo, hi, dt, lot, hit))
    assert lo > 0 and lot > 0, "W9 FAIL: valence not CI-sep over floor / twin"
    print("  W9 PASS: valence beats the majority floor AND the twin CI-separated")

    print("ALL CHECKS PASS (9/9) -- the glass-box OCC appraisal infers the UNSTATED emotion (valence + OCC type) "
          "from event-vs-goal congruence x prospect, CI-separated over the strongest floors with the goal<->event "
          "twin LOSING; the upstream goal-failure generalization is a strict superset; NO trained encoder, NO LLM")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
