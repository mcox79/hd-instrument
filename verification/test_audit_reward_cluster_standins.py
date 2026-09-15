#!/usr/bin/env python3
"""PURE-DISK WITNESS for the reward / action-selection / vigor control-cluster brain-fidelity audit.

Reproduces EVERY liveness / stand-in / fidelity claim in
notes/problems/audit_the_reward_action_selection_vigor_control_cluster_for_non_brain_faithful_stand_ins/CATALOG.md
on the CURRENT bytes, plus the powered #1 localization headline, plus a POSITIVE CONTROL that the
guard actually fires. Side-effect-safe: hdlab modules are AST-parsed / byte-scanned, never imported;
the two audit cells are imported from experiments/ and their own self-tests / run() are executed.

Run:  .venv/Scripts/python.exe verification/test_audit_reward_cluster_standins.py
      (exit 0 = all PASS, 1 = any FAIL)
"""
from __future__ import annotations

import ast
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HDLAB = os.path.join(ROOT, "hdlab")


def _bytes(mod: str) -> str:
    with open(os.path.join(HDLAB, mod + ".py"), "r", encoding="utf-8") as fh:
        return fh.read()


def _load_cell(name: str):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "experiments", name + ".py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _defs(mod: str):
    """Top-level + nested function/class names defined in an hdlab module."""
    tree = ast.parse(_bytes(mod))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


RESULTS = []


def check(name: str, cond: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(cond), detail))
    print(f"  {'ok' if cond else 'XX'}  {name}{('  -- ' + detail) if detail else ''}")


# =============================================================================================
def main() -> int:
    denom = _load_cell("exp_audit_reward_cluster_denominator_v1")
    res = denom.run()
    cls = res["classification"]
    pc = denom._positive_controls(res)

    print("REWARD/ACTION-SELECTION/VIGOR CLUSTER -- PURE-DISK WITNESS\n")

    # --- W1: the enumerated DENOMINATOR reproduces + its positive controls fire ----------------
    check("W1 denominator: 7 seeds -> import closure enumerated + all positive controls fire",
          all(pc.values()) and res["n_seed_import_closure"] >= 30,
          f"closure={res['n_seed_import_closure']} organs; PCs all pass")

    # --- W2: the three pinned DECISION organs are DORMANT-ISLANDED (0 hdlab importers) ---------
    check("W2 action_selection / successor_representation / self_manager = DORMANT-ISLANDED (0 importers)",
          all(cls[o]["status"] == "DORMANT-ISLANDED" and cls[o]["n_importers"] == 0
              for o in ("action_selection", "successor_representation", "self_manager")),
          "no hdlab organ imports any of the three; off every live loop")

    # --- W3: goal_achievement DORMANT (only importer = outcome_event_extraction, itself dormant) -
    check("W3 goal_achievement = DORMANT-ISLANDED (sole importer outcome_event_extraction, non-live)",
          cls["goal_achievement"]["status"] == "DORMANT-ISLANDED"
          and cls["goal_achievement"]["importers"] == ["outcome_event_extraction"],
          f"importers={cls['goal_achievement']['importers']}")

    # --- W4: consequence_learning_loop + goal_typing LIVE-IMPORTED via the grounding subsystem --
    check("W4 consequence_learning_loop LIVE-IMPORTED via grounding_acquisition_loop",
          cls["consequence_learning_loop"]["status"] == "LIVE-IMPORTED"
          and "grounding_acquisition_loop" in cls["consequence_learning_loop"]["importers"])
    check("W4b goal_typing LIVE-IMPORTED (module runs via consequence_learning_loop <- grounding)",
          cls["goal_typing"]["status"] == "LIVE-IMPORTED"
          and "consequence_learning_loop" in cls["goal_typing"]["live_importers"])

    # --- W5: state_of_mind LIVE via the coref path (already dispositioned as coref) -------------
    check("W5 state_of_mind LIVE-IMPORTED via the coref cluster (event_centrality_coref)",
          cls["state_of_mind"]["status"] == "LIVE-IMPORTED"
          and "event_centrality_coref" in cls["state_of_mind"]["importers"])

    # --- W6: VIGOR IS MISSING -- the #1 finding ------------------------------------------------
    # the ONLY occurrence of the token 'vigor' in all of hdlab is self_manager's docstring MENTION;
    # NO organ implements a vigor computation (optimal_latency / response-rate / VigorDial).
    vigor_files = []
    vigor_impl_hits = []
    for f in os.listdir(HDLAB):
        if not f.endswith(".py") or f.startswith("__"):
            continue
        src = _bytes(f[:-3])
        if re.search(r"\bvigor\b", src, re.IGNORECASE):
            vigor_files.append(f[:-3])
        # an actual vigor IMPLEMENTATION would define one of these
        if re.search(r"def optimal_latency|class VigorDial|response_vigor|response_rate\s*=",
                     src):
            vigor_impl_hits.append(f[:-3])
    check("W6 'vigor' appears in hdlab ONLY in self_manager (a docstring mention, not an implementation)",
          vigor_files == ["self_manager"],
          f"files mentioning vigor = {vigor_files}")
    check("W6b NO hdlab organ IMPLEMENTS a vigor computation (optimal_latency/VigorDial/response_rate)",
          vigor_impl_hits == [],
          f"vigor-impl hits = {vigor_impl_hits}")

    # --- W7: self_manager advertises a 6-channel bank but builds ONLY DIAL #1 (ACC/EVC halting) --
    sm = _bytes("self_manager")
    sm_defs = _defs("self_manager")
    advertises_six = "6 separable neuromodulatory channels" in sm and "tonic-DA vigor" in sm
    only_halting = ({"accuracy_per_compute", "tune_halt_threshold", "run_halting",
                     "AdaptiveHaltController"} <= sm_defs)
    no_vigor_fn = not any("vigor" in d.lower() or "latency" in d.lower() for d in sm_defs)
    check("W7 self_manager: docstring advertises 6 neuromodulatory channels incl 'tonic-DA vigor'",
          advertises_six)
    check("W7b self_manager: implements ONLY DIAL #1 (ACC/EVC halting); no vigor/latency function",
          only_halting and no_vigor_fn,
          "halting API present; zero vigor functions")

    # --- W8: action_selection is FAITHFUL (positive control -- the audit does NOT over-fire) ----
    asel = _bytes("action_selection")
    td_target = "Enxt + gamma * (Enxt @ M)" in asel        # TD(0) bootstrap target
    rpe_comment = "TD-error == RPE" in asel or "TD-error" in asel
    gonogo = "class GoNoGoActionGate" in asel and "argmax" in asel
    check("W8 action_selection FAITHFUL: TD(0) RPE target + SR-transport M + Go/NoGo argmax actor",
          td_target and gonogo,
          "TD target + GoNoGo WTA present at file bytes")

    # --- W9: successor_representation is FAITHFUL (M=(I-gamma P)^-1 closed form) -----------------
    sr = _bytes("successor_representation")
    closed_form = "np.eye(n) - gamma * P" in sr and "np.linalg.solve(A, np.eye(n))" in sr
    has_identity_selftest = "_selftest_closed_form_identity" in sr
    check("W9 successor_representation FAITHFUL: M=(I-gamma P)^-1 closed form + closed-form identity selftest",
          closed_form and has_identity_selftest)

    # --- W10: consequence_learning_loop teacher = MET/UNMET lexicon vote 'standing in for the ---
    #          felt affective core' (honestly labelled), and it is INERT in the grounding loop -----
    cll = _bytes("consequence_learning_loop")
    standin_labelled = "standing in for the felt affective core" in cll
    teacher_symbolic = ("congruence_decision" in cll and "lexicon_predict" in cll)
    # INERT: grounding_acquisition_loop calls teacher_verdict/credit_window ONLY inside its self-test
    gal = _bytes("grounding_acquisition_loop")
    gal_tree = ast.parse(gal)
    # find line numbers of calls to teacher_verdict / credit_window, and whether each sits inside a
    # function whose name contains 'selftest'/'self_test'/'test'
    call_lines = [n.lineno for n in ast.walk(gal_tree)
                  if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                  and n.func.id in ("teacher_verdict", "credit_window", "_credit_targets")]
    selftest_ranges = [(n.lineno, getattr(n, "end_lineno", n.lineno))
                       for n in ast.walk(gal_tree)
                       if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                       and re.search(r"self.?test|selftest|_test", n.name)]
    all_in_selftest = all(any(lo <= ln <= hi for (lo, hi) in selftest_ranges) for ln in call_lines) \
        and len(call_lines) > 0
    check("W10 consequence_learning_loop teacher = symbolic MET/UNMET lexicon vote, self-labelled a stand-in",
          standin_labelled and teacher_symbolic,
          "'standing in for the felt affective core' + congruence_decision/lexicon_predict")
    check("W10b the teacher/credit calls in grounding_acquisition_loop are ALL inside its self-test (INERT)",
          all_in_selftest,
          f"{len(call_lines)} calls, all within a *self-test* function")

    # --- W11: state_of_mind is a coref tracker, labelled NOT-ToM (already dispositioned) --------
    som = _bytes("state_of_mind")
    check("W11 state_of_mind labelled NOT-ToM (a coreference overlay), already dispositioned as coref",
          "NOT THEORY-OF-MIND" in som and "COREFERENCE" in som.upper())

    # --- W12: the powered #1 localization reproduces (Niv 2007 vigor dial) ----------------------
    vig = _load_cell("exp_reward_cluster_vigor_dial_v1")
    vr = vig.run(n_sessions=120, n_boot=500)
    nf, nt = vr["niv_vs_fixed"], vr["niv_vs_twin"]
    check("W12 vigor dial: NIV net reward BEATS the strongest FIXED floor CI-separated (missing dial COSTS reward)",
          nf["ci_separated"] and nf["diff"] > 0,
          f"NIV-FIXED={nf['diff']:.1f} CI[{nf['ci_lo']:.1f},{nf['ci_hi']:.1f}]")
    check("W12b vigor dial: NIV BEATS the info-free TWIN CI-separated (reward-rate signal is load-bearing)",
          nt["ci_separated"] and nt["diff"] > 0,
          f"NIV-TWIN={nt['diff']:.1f} CI[{nt['ci_lo']:.1f},{nt['ci_hi']:.1f}]")
    check("W12c vigor dial: closed form tau*=sqrt(C_v/rho) matches grid argmax + vigor~sqrt(rho) monotone",
          vr["identity_max_rel_err"] < 0.20 and vr["monotone_vigor_sqrt_rho"],
          f"identity rel-err={vr['identity_max_rel_err']:.3f}")
    check("W12d vigor dial: ORACLE is the ceiling (>= NIV) and SCRAMBLE collapses toward FIXED",
          vr["rates"]["oracle"] >= vr["rates"]["niv"]
          and vr["rates"]["scramble"] <= vr["rates"]["niv"],
          f"oracle={vr['rates']['oracle']:.0f} niv={vr['rates']['niv']:.0f} scr={vr['rates']['scramble']:.0f}")

    # --- W14: the vigor dial COMPOSES with the SHIPPED halting dial (joint EVC / separable bank) --
    jevc = _load_cell("exp_reward_cluster_joint_evc_v1")
    jr = jevc.run(n_sessions=60, n_boot=300)
    bh, bv = jr["both_vs_halting"], jr["both_vs_vigor"]
    check("W14 joint EVC: adding the vigor dial ON TOP of the shipped AdaptiveHaltController helps CI-sep",
          bh["ci_separated"] and bh["diff"] > 0,
          f"BOTH-HALTING={bh['diff']:.1f} CI[{bh['ci_lo']:.1f},{bh['ci_hi']:.1f}]")
    check("W14b joint EVC: the two dials are COMPLEMENTARY (BOTH also beats VIGOR-only CI-sep)",
          bv["ci_separated"] and bv["diff"] > 0,
          f"BOTH-VIGOR={bv['diff']:.1f} CI[{bv['ci_lo']:.1f},{bv['ci_hi']:.1f}]")
    check("W14c separability: halting hop-decisions are BYTE-IDENTICAL under a vigor toggle "
          "(the halting rule never reads rho; the vigor rule never reads confidence)",
          jr["separability_halting_identical_under_vigor_toggle"])

    # --- W15-W18: the FOLLOW-ON PROTOTYPES (owner-directed), each brain-foundational + can-fail ---
    bank = _load_cell("exp_self_manager_neuromodulatory_bank_v1")
    br = bank.run()
    check("W15 the 4 missing neuromodulatory dials (NE/ACh/5HT/homeostasis) each beat their tuned "
          "fixed floor + info-free twin CI-sep",
          br["all_pass"] and len(br["dials"]) == 4,
          "each dial copies a PINNED neuromodulatory computation")

    r4 = _load_cell("exp_action_selection_linear_sr_value_v1")
    r4r = r4.run(n_envs=40)
    check("W16 R4: linear SR value V=M@R beats action_selection's cosine-to-one-goal + info-free twin CI-sep",
          r4r["linear_vs_cosine"]["ci_separated"] and r4r["linear_vs_twin"]["ci_separated"]
          and r4r["identity_max_rel_err"] < 1e-3,
          f"Spearman linear={r4r['spearman']['linear']:.2f} cosine={r4r['spearman']['cosine']:.2f}")

    tom = _load_cell("exp_theory_of_mind_belief_partition_v1")
    tomr = tom.run(n_scenarios=80)
    check("W17 ToM: per-agent observation-gated belief partition beats reality-only floor + twin CI-sep "
          "on false-belief items; true-belief control agrees with reality",
          tomr["tom_vs_reality_fb"]["ci_separated"] and tomr["tom_vs_twin_fb"]["ci_separated"]
          and abs(tomr["true_belief_acc"]["tom"] - tomr["true_belief_acc"]["reality"]) < 0.05,
          f"false-belief TOM={tomr['false_belief_acc']['tom']:.2f} reality={tomr['false_belief_acc']['reality']:.2f}")

    r2 = _load_cell("exp_consequence_graded_value_teacher_v1")
    r2r = r2.run(n_runs=80)
    check("W18 R2: graded OFC-value teacher beats the binary MET/UNMET category (value fidelity + "
          "same-sign discrimination) + info-free twin CI-sep",
          r2r["graded_vs_binary_pearson"]["ci_separated"] and r2r["graded_vs_binary_pair"]["ci_separated"]
          and r2r["graded_vs_twin_pearson"]["ci_separated"],
          f"same-sign acc graded={r2r['same_sign_pair_acc']['graded']:.2f} binary={r2r['same_sign_pair_acc']['binary']:.2f}")

    # --- W19: the state-representation fix -- SUCCESSOR FEATURES generalize where the tabular organ collapses
    sf = _load_cell("exp_successor_features_state_abstraction_v1")
    sfr = sf.run(n_envs=40)
    check("W19 successor FEATURES (shared basis) beat the tabular successor_representation organ on "
          "HELD-OUT states + info-free twin CI-sep; TD==closed-form; grid-cell rank-k basis generalizes",
          sfr["sf_vs_tabular_heldout"]["ci_separated"] and sfr["sf_vs_twin_heldout"]["ci_separated"]
          and sfr["identity_mean_rel_err"] < 0.25
          and sfr["held_out"]["sf_rank_k_eigen"] > sfr["held_out"]["tabular"],
          f"held-out SF={sfr['held_out']['sf']:.2f} tabular={sfr['held_out']['tabular']:.2f} "
          f"rank-k={sfr['held_out']['sf_rank_k_eigen']:.2f}")

    # --- W20: model-free -> SR -> model-based control HIERARCHY under revaluation (Daw/Momennejad) --
    mb = _load_cell("exp_model_based_control_revaluation_v1")
    mbr = mb.run(n_envs=80)
    check("W20 model-based control: reward-reval SR+MB beat frozen model-free CI-sep; transition-reval "
          "MB beats the (stale) SR CI-sep (the strict MF<SR<MB hierarchy); info-free twins lose",
          mbr["rr_sr_vs_mf"]["ci_separated"] and mbr["rr_mb_vs_mf"]["ci_separated"]
          and mbr["tr_mb_vs_sr"]["ci_separated"] and mbr["rr_sr_vs_twin"]["ci_separated"]
          and mbr["tr_mb_vs_twin"]["ci_separated"],
          f"reward MF={mbr['reward_reval']['mf']:.2f} SR={mbr['reward_reval']['sr']:.2f}; "
          f"transition SR={mbr['transition_reval']['sr']:.2f} MB={mbr['transition_reval']['mb']:.2f}")

    # --- W21: RECURSIVE 2nd-order ToM -- nested belief partitions (ice-cream-van false belief) -----
    tom2 = _load_cell("exp_theory_of_mind_recursive_v1")
    t2r = tom2.run(n_scenarios=120)
    check("W21 recursive 2nd-order ToM beats the 1st-order ceiling + reality + info-free twin CI-sep on "
          "2nd-order false-belief items; consistency control agrees",
          t2r["order2_vs_order1"]["ci_separated"] and t2r["order2_vs_reality"]["ci_separated"]
          and t2r["order2_vs_twin"]["ci_separated"] and t2r["agree_control_acc"]["order2"] > 0.9,
          f"divergent ORDER2={t2r['divergent_acc']['order2']:.2f} ORDER1={t2r['divergent_acc']['order1']:.2f}")

    # --- W22: INTEGRATION -- the composed agent (SF value + model-based planning) beats the flat gate
    integ = _load_cell("exp_integrated_reward_cluster_agent_v1")
    ir = integ.run(n_sessions=100)
    check("W22 integrated loop: the composed agent (successor-feature value + model-based planning) "
          "beats the flat model-free gate + no-replan ablation in acting reward CI-sep",
          ir["reward_full_vs_flat"]["ci_separated"] and ir["reward_full_vs_noMB"]["ci_separated"],
          f"reward FULL={ir['reward']['full']:.1f} FLAT_MF={ir['reward']['flat_mf']:.1f}")

    # --- W13: POSITIVE CONTROL -- the byte-search guard FIRES on a KNOWN-present token -----------
    # If the search mechanism were broken (matching nothing), W6/W6b would pass vacuously. Prove it
    # can find a token that IS present: 'AdaptiveHaltController' exists in self_manager.
    guard_fires = bool(re.search(r"class AdaptiveHaltController", sm))
    guard_negative = not bool(re.search(r"def optimal_latency", sm))   # and correctly ABSENT there
    check("W13 positive control: the byte-search guard FIRES on a present token (AdaptiveHaltController) "
          "and correctly reports vigor ABSENT",
          guard_fires and guard_negative)

    # -----------------------------------------------------------------------------------------
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    ntot = len(RESULTS)
    print(f"\n{npass}/{ntot} PASS")
    return 0 if npass == ntot else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
