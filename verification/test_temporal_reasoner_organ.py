"""Witness for the temporal REASONER over the extracted timeline (before/after + overlap + duration).

problem: reason_over_event_time_order_and_duration_on_a_modern_gold.

Scaffold-free checks of the load-bearing claims (fast; smoke scale where a cell is heavy, cached prior
for duration). Each check asserts a DIRECTIONAL, CI-anchored claim, not a brittle exact number.

Run: .venv/Scripts/python.exe verification/test_temporal_reasoner_organ.py
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments import _aspect_interval as AI
from experiments import exp_temporal_reason_before_after_v1 as BA
from experiments import exp_temporal_reason_overlap_v1 as OV
from experiments import exp_temporal_reason_duration_v1 as DU

PASS = "PASS"


def check(name, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {name}: {detail}")
    return bool(cond)


def main():
    oks = []

    # W0: upstream aspect->interval module self-test (additivity + progressive recovery + overlap).
    try:
        AI._selftest()
        oks.append(check("W0 upstream aspect_interval self-test", True, "additive + progressive + Allen overlap"))
    except AssertionError as e:
        oks.append(check("W0 upstream aspect_interval self-test", False, str(e)))

    # ---- BEFORE/AFTER (TB-Dense modern newswire) ----
    items, items_base, ndoc = BA.tbdense_before_after(smoke=False)
    full = BA._block(items, "full")
    rev = BA._block([it for it in items if it["reverse"]], "reverse")
    cue = BA._block([it for it in items if it["cue"]], "cue")
    oks.append(check("W1 before/after reg beats iconicity CI-separated (full pop)",
                     full["sep"] and full["reg_acc"] > full["icon_acc"],
                     f"reg={full['reg_acc']} icon={full['icon_acc']} d={full['delta_vs_icon']} CI{full['ci']}"))
    oks.append(check("W2 before/after reverse-order positive control (iconicity=0)",
                     rev["sep"] and rev["icon_acc"] < 0.02 and rev["reg_acc"] > rev["icon_acc"],
                     f"reg={rev['reg_acc']} icon={rev['icon_acc']} CI{rev['ci']}"))
    oks.append(check("W3 before/after cue-bearing subset strongly beats iconicity",
                     cue["sep"] and cue["reg_acc"] > 0.8,
                     f"reg={cue['reg_acc']} icon={cue['icon_acc']} d={cue['delta_vs_icon']}"))
    # no-regression: same-pair base vs aspect extractor
    bk = {it["key"]: it for it in items_base}
    ak = {it["key"]: it for it in items}
    shared = set(bk) & set(ak)
    import numpy as np
    base_acc = float(np.mean([1.0 if bk[k]["reg_correct"] else 0.0 for k in shared]))
    asp_acc = float(np.mean([1.0 if ak[k]["reg_correct"] else 0.0 for k in shared]))
    oks.append(check("W4 no downstream regression (aspect vs base extractor, same pairs)",
                     asp_acc >= base_acc - 0.02,
                     f"base={base_acc:.4f} aspect={asp_acc:.4f} +{len(set(ak)-set(bk))} extra pairs"))

    # ---- OVERLAP ----
    con = OV.constructed_block(smoke=False)
    oks.append(check("W5 constructed Allen overlap ~1.0 vs point-order control 0.5, CI-separated",
                     con["sep"] and con["allen_acc"] > 0.95 and con["point_acc"] < 0.55,
                     f"allen={con['allen_acc']} point={con['point_acc']} d={con['delta_vs_point']} twin_p95={con['twin_p95']}"))
    oks.append(check("W6 constructed overlap info-free twin LOSES (twin p95 < allen)",
                     con["twin_p95"] < con["allen_acc"] - 0.2,
                     f"twin_acc={con['twin_acc']} p95={con['twin_p95']} allen={con['allen_acc']}"))
    tb = OV.tbdense_overlap(smoke=False, lexical=True)
    oks.append(check("W7 TB-Dense overlap-gold subset: interval reasoner recovers overlaps the point-order control gets 0%",
                     tb["overlap_subset_sep"] and tb["allen_recall_on_overlap"] > 0.15,
                     f"recall={tb['allen_recall_on_overlap']} vs point=0 d={tb['overlap_subset_delta_vs_point']} CI{tb['overlap_subset_ci']}"))
    av = OV.aspect_validation(smoke=False)
    oks.append(check("W8 upstream fidelity: progressive recall vs gold TimeML aspect = 1.0 (all gold progressives recovered)",
                     av["progressive_recall"] >= 0.99,
                     f"recall={av['progressive_recall']} precision={av['progressive_precision']} (tp={av['progressive_tp']} fn={av['fn']})"))
    # located negative (real-prose overlap): full mixed pop does NOT beat the trivial floor
    oks.append(check("W9 LOCATED NEGATIVE: real-prose full-pop overlap does not beat the 'never-overlap' floor",
                     not tb["sep"],
                     f"allen={tb['allen_acc']} point={tb['point_acc']} fire_prec={tb['fire_precision']} (fires 2x base {tb['overlap_base_rate']})"))

    # ---- DURATION ----
    rel = DU.relative_block(smoke=False)
    oks.append(check("W10 relative duration magnitude line ~1.0 on un-stated transitive pairs; twin ~chance",
                     rel["line_acc"] > 0.95 and rel["twin_acc"] < 0.6,
                     f"line={rel['line_acc']} twin={rel['twin_acc']} blind={rel['blind_acc']} (n={rel['n_unstated_pairs']})"))
    prior = DU.mine_prior(smoke=False, use_cache=True)   # cached self-mined prior
    typ = DU.mctaco_typical(prior, smoke=False)
    oks.append(check("W11 LOCATED NEGATIVE: text-mined typical-duration prior does NOT beat MCTACO majority floor",
                     not typ["sep_covered"] or typ["delta_covered"] < 0,
                     f"covered prior={typ['prior_acc_covered']} floor={typ['majority_floor_covered']} d={typ['delta_covered']} cov={typ['coverage']}"))

    # ---- UPGRADES (brain-foundational) ----
    # W12: INTEGRATED reasoner (cue + TIMEX event-local anchoring + transitive closure) beats iconicity
    from experiments import exp_temporal_reason_integrated_v1 as IN
    ig = IN.run(smoke=False)
    oks.append(check("W12 UPGRADE integrated reasoner (cue+TIMEX+closure) beats iconicity CI-separated; date channel reliable",
                     ig["integrated_vs_iconicity"]["sep"] and ig["signal_class_provenance"]["date"]["acc"] > 0.7,
                     f"integrated={ig['accuracy']['integrated']} vs icon d={ig['integrated_vs_iconicity']['delta']} "
                     f"CI{ig['integrated_vs_iconicity']['ci']} | date-channel acc={ig['signal_class_provenance']['date']['acc']}"))
    # W13: UDS-Time duration organ dissolves the located negative (coverage up, ties floor, recovers plausible)
    uds_path = os.path.join(_REPO, "data", "exp_temporal_reason_duration_udstime_v1", "uds_prior.json")
    if os.path.exists(uds_path):
        import json as _json
        uds = _json.load(open(uds_path, encoding="ascii"))
        ut = DU.mctaco_typical(uds, smoke=False, tol=0.7)
        oks.append(check("W13 UPGRADE UDS-Time duration organ: ~2x coverage + ties floor (dissolves the mined-prior located negative)",
                         ut["coverage"] > 0.6 and ut["delta_covered"] > typ["delta_covered"],
                         f"UDS cov={ut['coverage']} covered={ut['prior_acc_covered']} floor={ut['majority_floor_covered']} "
                         f"d={ut['delta_covered']} (mined d was {typ['delta_covered']})"))

    # W14: SCRIPT/SCHEMA organ (ROCStories narrative event chains) beats baselines on TRACIE implicit-event
    from experiments import exp_temporal_reason_tracie_script_v1 as SC
    ch_path = os.path.join(_REPO, "data", "exp_temporal_reason_tracie_script_v1", "chains.json")
    if os.path.exists(ch_path):
        chains = _json.load(open(ch_path, encoding="ascii"))
        tr = SC.tracie_eval(chains, smoke=False)
        oks.append(check("W14 UPGRADE script/schema organ beats chance+story-internal on TRACIE implicit-event (covered)",
                         tr["script_acc_covered"] > 0.55 and tr["script_acc_covered"] > tr["story_internal_baseline"],
                         f"covered acc={tr['script_acc_covered']} vs majority {tr['majority_baseline']} / story-internal {tr['story_internal_baseline']} (cov {tr['coverage']})"))
    # W15: TORQUE in-context overlap -- the Allen reasoner beats the point-order control (which has no overlap category)
    tq_path = os.path.join(_REPO, "data", "corpora", "torque", "dev.json")
    if os.path.exists(tq_path):
        from experiments import exp_temporal_reason_torque_overlap_v1 as TQ
        tq = TQ.run(refetch=False)
        oks.append(check("W15 UPGRADE TORQUE in-context overlap: Allen reasoner beats point-order control (no overlap category)",
                         tq["reasoner_overlap_F1"] > tq["point_order_control_F1"],
                         f"reasoner F1={tq['reasoner_overlap_F1']} vs point-order {tq['point_order_control_F1']}"))

    # W16: DURATION FAIRNESS -- the organ's knowledge is real on the threshold-free native ranking (drilled wall)
    from experiments import exp_temporal_reason_duration_fairness_v1 as FR
    fr = FR.run()
    nr = fr["native_relative_ranking"]
    oks.append(check("W16 DRILLED WALL: duration organ has REAL knowledge -- native relative-duration ranking CI-sep over chance",
                     nr["sep_above_chance"] and nr["concordance"] > 0.55,
                     f"concordance={nr['concordance']} CI{nr['ci']} vs chance 0.5 | (raw candidate precision={fr['raw_candidate_precision']} recall={fr['raw_candidate_recall']})"))

    # W17: TOKEN-INDEXED overlap -- same-verb simultaneity the type-keyed reasoner drops (episodic event tokens)
    from experiments import exp_temporal_reason_more_upgrades_v1 as MU
    from experiments import _tbdense as TB
    import glob as _glob
    _files = sorted(_glob.glob(os.path.join(TB.TBDENSE_DIR, "**", "*.tml"), recursive=True))
    sv = MU.same_verb_overlap(_files)
    oks.append(check("W17 UPGRADE token-indexed overlap recovers same-verb simultaneity the type-keyed reasoner drops (0)",
                     sv["token_indexed_overlap_acc"] > 0.7 and sv["n_same_verb_pairs_recovered"] > 20,
                     f"token-indexed acc={sv['token_indexed_overlap_acc']} on {sv['n_same_verb_pairs_recovered']} pairs vs type-keyed 0.0 {sv['by_relation']}"))

    n = sum(oks)
    print("=" * 80)
    print(f"{'ALL CHECKS PASS' if n == len(oks) else 'SOME CHECKS FAILED'} ({n}/{len(oks)})")
    print("=" * 80)
    return 0 if n == len(oks) else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
