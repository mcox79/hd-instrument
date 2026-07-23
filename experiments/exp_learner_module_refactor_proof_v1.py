#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_learner_module_refactor_proof_v1

REFACTOR-VERIFICATION cell (NOT a new capability claim; NOT queued; NOT banked -- skunkworks VETs
the refactor, not this cell). Proves the centralized Learner module (hdlab/learner/) is
BEHAVIOR-PRESERVING against the two banked cells it wraps, and that its MDL-based model-selection
AUTOMATICALLY picks the correct hypothesis-class plugin per task (per
preregs/2026-07-23_learner_module_refactor.md; bands pre-registered BEFORE this cell ran).

PART A -- condenser reproduction (wraps experiments/exp_online_knowledge_condenser_selectional_v1.py,
  banked 29476, HARD_PASS_CONDENSATION_GENERALIZES): rebuild the SAME seed table + reading stream +
  held-out unseen/seen probe items via the condenser's OWN functions (unchanged import, no
  reimplementation), then re-derive the exposure-curve 2AFC accuracy THROUGH
  hdlab.learner.plugins.estimation_plugin's 'condenser_reproduce' mode (a thin wrapper around
  CONDENSER.build_condensed_counts / CONDENSER.make_score_fn) and compare to the banked curve.
  MEASURED@d:/AI/hd-instrument/data/exp_online_knowledge_condenser_selectional_v1/metrics.json:
  curve_full_unseen={"0.00":0.5,"0.25":0.5729,"0.50":0.6667,"0.75":0.7083,"1.00":0.75},
  curve_verbatim_unseen["1.00"]=0.5.

PART B -- rule-inducer reproduction (wraps experiments/exp_parser_ruleinduction_cls_ppattach_v1.py,
  banked 29485, verdict=MIDDLE_BAND / control_verdict=HARD_PASS_CONTROL): rebuild the SAME control
  instances (XOR+topic-distractor) and the SAME real PP-attachment harvest (parser train + DEV+TEST
  corpus + verb-disjoint split) via the rule-inducer's OWN functions, run BOTH the DIRECT (unwrapped)
  call and the MODULE-wrapped call on the identical seen/held split per seed, and compare.
  MEASURED@d:/AI/hd-instrument/data/exp_parser_ruleinduction_cls_ppattach_v1/metrics.json:
  CONTROL_ruleind_acc_mean=1.0, CONTROL_simvote_acc_mean=0.4389, beat_simvote_margin_mean=0.0537
  (REAL task), PRIMARY_real_ruleind_net_gain_mean=0.0657.

PART C -- model-selection auto-choice: hdlab.learner.registry.learn() (fits BOTH plugins, MDL-
  selects) on two probe tasks: TASK_XOR_CONTROL (rule-inducer's own synthetic XOR+topic-distractor
  control; estimation plugin keyed on a single feature 'a:<val>' alone -- CITED Minsky & Papert 1969,
  no single feature carries XOR label information) and TASK_PPATTACH_REAL (the real PP-attachment
  seen_fail cases; estimation plugin keyed on the single preposition feature 'p:<form>' alone --
  CITED Ratnaparkhi 1994 lexical-frequency PP-attachment cue). Expect ruleind selected on the
  former (beyond-linear witness), estimation selected on the latter (cheap plugin suffices per the
  real task's own MIDDLE_BAND / marginal-lift banked result, Occam prefers it on comparable
  compression) -- see prereg for exact bands.

COMPUTE ARCHITECTURE: class (b) sequential-CPU, reuses both source cells' own pipelines unchanged
  (condenser reading-stream mining ~6s per its own banked elapsed_s; rule-inducer parser-train+
  PP-harvest ~85s per its own banked elapsed_s). No matmul/GPU-batchable primitive. LOCAL-ONLY,
  foreground-to-completion; NO queue, NO push, NO remote-persist, NO bank.

CELL-TEMPLATE MANDATORY subset (proof/measurement cell, not a queued anchor):
  - final_metrics_atomicity: tmp_replace (os.replace)
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: reproduction-delta + auto-select discrimination measurement
  - deterministic_seeding: true (reuses both source cells' own fixed int seeds unchanged)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import time
import traceback
from datetime import datetime, timezone

ANCHOR_NAME = "learner_module_refactor_proof_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_online_knowledge_condenser_selectional_v1 as CONDENSER  # noqa: E402
from experiments import exp_parser_ruleinduction_cls_ppattach_v1 as RULEIND  # noqa: E402
from hdlab.learner import registry  # noqa: E402
from hdlab.learner.plugins import estimation_plugin, ruleind_plugin  # noqa: E402

REPRO_HARD_PASS_MAX_DELTA = 0.02
REPRO_HARD_FAIL_MIN_DELTA = 0.05


def _out_dir():
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:400]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
    try:
        write_metrics(output_dir, diag)
    except Exception:
        pass


# ================================================================================================
# PART A: condenser reproduction.
# ================================================================================================
def run_part_a(out_dir):
    banked = json.load(open(os.path.join(REPO_ROOT, "data",
                       "exp_online_knowledge_condenser_selectional_v1", "metrics.json"), encoding="utf-8"))

    seed_table, seed_records, n_vetted_pool, n_seed_kept = CONDENSER.build_seed_table()
    stream, n_mine = CONDENSER.build_reading_stream("full", out_dir)
    attested, verb_any_full, class_pool_full = CONDENSER.attested_maps(stream)
    heldout = CONDENSER.select_heldout(attested, CONDENSER.HOLDOUT_RNG_SEED)
    training_stream = CONDENSER.remove_heldout_from_stream(stream, heldout)
    unseen_items = CONDENSER.build_unseen_items(heldout, verb_any_full, class_pool_full)
    seen_items = CONDENSER.build_seen_items(training_stream, verb_any_full, class_pool_full)
    n_train = len(training_stream)

    curve_full_unseen_module = {}
    curve_verbatim_unseen_module = {}
    curve_full_seen_module = {}
    for frac in CONDENSER.EXPOSURE_POINTS:
        idx = int(round(frac * n_train))
        sl = training_stream[:idx]
        res_class = estimation_plugin.learn(sl, None, {"mode": "condenser_reproduce", "granularity": "class"},
                                             {"seed_table": seed_table})
        res_pair = estimation_plugin.learn(sl, None, {"mode": "condenser_reproduce", "granularity": "pair"},
                                            {"seed_table": seed_table})

        def score_class(v, n, ss, _h=res_class.hypothesis):
            return estimation_plugin.score_condenser_reproduce(_h, seed_table, v, n, ss)

        def score_pair(v, n, ss, _h=res_pair.hypothesis):
            return estimation_plugin.score_condenser_reproduce(_h, seed_table, v, n, ss)

        acc_fu, _ = CONDENSER._2afc(unseen_items, score_class)
        acc_vu, _ = CONDENSER._2afc(unseen_items, score_pair)
        acc_fs, _ = CONDENSER._2afc(seen_items, score_class)
        key = f"{frac:.2f}"
        curve_full_unseen_module[key] = acc_fu
        curve_verbatim_unseen_module[key] = acc_vu
        curve_full_seen_module[key] = acc_fs

    banked_curve_full_unseen = banked["curve_full_unseen"]
    banked_curve_verbatim_unseen = banked["curve_verbatim_unseen"]
    deltas = {k: round(abs(curve_full_unseen_module[k] - banked_curve_full_unseen[k]), 4)
              for k in curve_full_unseen_module}
    deltas_verbatim = {k: round(abs(curve_verbatim_unseen_module[k] - banked_curve_verbatim_unseen[k]), 4)
                        for k in curve_verbatim_unseen_module}
    max_delta_full = max(deltas.values())
    max_delta_verbatim = max(deltas_verbatim.values())
    max_delta = max(max_delta_full, max_delta_verbatim)

    print(f"[{ANCHOR_NAME}] PART A condenser: module curve_full_unseen={curve_full_unseen_module} "
          f"banked={banked_curve_full_unseen} deltas={deltas}", flush=True)
    print(f"[{ANCHOR_NAME}] PART A condenser: module curve_verbatim_unseen={curve_verbatim_unseen_module} "
          f"banked={banked_curve_verbatim_unseen} deltas={deltas_verbatim}", flush=True)

    return {
        "n_mine": n_mine, "n_train_evidence": n_train, "n_unseen_items": len(unseen_items),
        "n_seen_items": len(seen_items),
        "module_curve_full_unseen": curve_full_unseen_module,
        "module_curve_verbatim_unseen": curve_verbatim_unseen_module,
        "module_curve_full_seen": curve_full_seen_module,
        "banked_curve_full_unseen": banked_curve_full_unseen,
        "banked_curve_verbatim_unseen": banked_curve_verbatim_unseen,
        "deltas_full_unseen": deltas, "deltas_verbatim_unseen": deltas_verbatim,
        "max_delta": max_delta,
        "reproduction_verdict": ("HARD_PASS_BEHAVIOR_PRESERVED" if max_delta <= REPRO_HARD_PASS_MAX_DELTA
                                  else ("HARD_FAIL_BEHAVIOR_CHANGED" if max_delta > REPRO_HARD_FAIL_MIN_DELTA
                                        else "MIDDLE_BAND")),
        # raw data handed to PART C for the TASK_XOR_CONTROL / TASK_PPATTACH_REAL auto-select probes
        "_seed_table": seed_table,
    }


# ================================================================================================
# PART B: rule-inducer reproduction.
# ================================================================================================
def run_part_b(out_dir):
    banked = json.load(open(os.path.join(REPO_ROOT, "data",
                       "exp_parser_ruleinduction_cls_ppattach_v1", "metrics.json"), encoding="utf-8"))

    # ---- CONTROL ----
    ctrl_seeds = RULEIND.CTRL_SEEDS
    ctrl_n_per_quad = 50   # cfg_full()
    ctrl_rows = []
    for seed in ctrl_seeds:
        instances = RULEIND.make_control_instances(ctrl_n_per_quad, seed)
        for a in instances:
            a["sig"] = RULEIND.control_signature(a)
        seen, held = RULEIND.control_split(instances, seed, frac_seen=0.7)

        # direct (unwrapped) recompute, same split -- this is the ground truth this run should
        # reproduce (deterministic; must equal the banked ctrl_per_seed row for this seed).
        direct_rules, direct_residual = RULEIND.induce_rules(seen, RULEIND.control_feat_fn)
        direct_lookup = RULEIND.build_residual_lookup(seen, direct_residual, RULEIND.control_key_fn)
        direct_fn = RULEIND.ruleind_predict_factory(direct_rules, direct_lookup, RULEIND.control_feat_fn,
                                                     RULEIND.control_key_fn, "XOR0")
        direct_acc = RULEIND._accuracy(direct_fn, held)

        role_codebook = RULEIND.BASE.build_role_codebook(("XOR1", "XOR0"), seed=91 + seed)
        sigs = [a["sig"] for a in seen]
        labels = [a["gold_class"] for a in seen]
        W_lin = RULEIND.BASE.consolidate_store(sigs, labels, role_codebook, n_cycles=6, replay_frac=0.5, seed=seed)
        lin_fn = lambda a: RULEIND.BASE.store_predict(W_lin, role_codebook, ["XOR1", "XOR0"], a["sig"])  # noqa: E731
        linear_acc = RULEIND._accuracy(lin_fn, held)
        simvote_fn = lambda a: RULEIND.BASE.knn_predict(sigs, labels, a["sig"], k=RULEIND.BASE.K_KNN)  # noqa: E731
        simvote_acc = RULEIND._accuracy(simvote_fn, held)

        # module-wrapped
        module_result = ruleind_plugin.learn(seen, RULEIND.control_feat_fn, {"key_fn": RULEIND.control_key_fn}, {})
        n_correct = sum(1 for a in held if ruleind_plugin.apply(
            module_result.hypothesis, RULEIND.control_feat_fn(a), RULEIND.control_key_fn(a), "XOR0") == a["gold_class"])
        module_acc = round(n_correct / max(1, len(held)), 4)

        ctrl_rows.append({"seed": seed, "direct_ruleind_acc": direct_acc, "module_ruleind_acc": module_acc,
                           "delta": round(abs(direct_acc - module_acc), 4),
                           "simvote_acc": simvote_acc, "linear_acc": linear_acc,
                           "module_margin_over_simvote": round(module_acc - simvote_acc, 4)})
        print(f"[{ANCHOR_NAME}] PART B control seed={seed} direct_acc={direct_acc} module_acc={module_acc} "
              f"simvote_acc={simvote_acc} linear_acc={linear_acc}", flush=True)

    ctrl_module_acc_mean = round(sum(r["module_ruleind_acc"] for r in ctrl_rows) / len(ctrl_rows), 4)
    ctrl_max_delta = max(r["delta"] for r in ctrl_rows)
    ctrl_margin_mean = round(sum(r["module_margin_over_simvote"] for r in ctrl_rows) / len(ctrl_rows), 4)

    # ---- REAL ----
    real_seeds = RULEIND.REAL_SEEDS
    W_parser, parser_info = RULEIND.BASE.train_dep_parser("full")
    dev = RULEIND.BASE.read_conllu("en_ewt-ud-dev.conllu")
    test = RULEIND.BASE.read_conllu("en_ewt-ud-test.conllu")
    sents = dev + test
    sents = [s for s in sents if 1 <= len(s) <= 60]
    instances = RULEIND.BASE.attach_predictions(sents, W_parser)
    leak_clean = RULEIND.BASE._leak_probe(instances)
    print(f"[{ANCHOR_NAME}] PART B real: n_pp_instances={len(instances)} parser_uas={parser_info['uas_dev']} "
          f"leak_clean={leak_clean}", flush=True)

    real_rows = []
    real_episodes_for_part_c = None
    for seed in real_seeds:
        direct_row = RULEIND.run_real_seed(instances, seed, frac_seen=0.6)
        if "ruleind" not in direct_row:
            real_rows.append({"seed": seed, "skipped": direct_row.get("skipped")})
            continue

        seen, held, seen_v = RULEIND.BASE.verb_split(instances, seed, frac_seen=0.6)
        seen_fail = [a for a in seen if a["is_fail"]]
        held_fail = [a for a in held if a["is_fail"]]
        default_class = list(RULEIND.BASE.ROLES)[0]

        module_result = ruleind_plugin.learn(seen_fail, RULEIND.BASE.instance_feats,
                                              {"key_fn": RULEIND.BASE.instance_key, "exclude_prefixes": ("v:",)}, {})

        def module_predict_fn(a, _h=module_result.hypothesis, _dc=default_class):
            return ruleind_plugin.apply_with_margin(_h, RULEIND.BASE.instance_feats(a),
                                                      RULEIND.BASE.instance_key(a), _dc, a.get("pred_class"))

        module_eval = RULEIND.BASE.eval_heldout(module_predict_fn, held, 0.0)
        delta_gain = round(abs(module_eval["net_gain"] - direct_row["ruleind"]["net_gain"]), 4)
        delta_fix = round(abs((module_eval["heldout_fix_rate"] or 0) - (direct_row["ruleind"]["heldout_fix_rate"] or 0)), 4)
        real_rows.append({
            "seed": seed, "n_seen_fail": len(seen_fail), "n_held_fail": len(held_fail),
            "direct_net_gain": direct_row["ruleind"]["net_gain"], "module_net_gain": module_eval["net_gain"],
            "delta_net_gain": delta_gain,
            "direct_fix_rate": direct_row["ruleind"]["heldout_fix_rate"],
            "module_fix_rate": module_eval["heldout_fix_rate"], "delta_fix_rate": delta_fix,
            "simvote_net_gain": direct_row["simvote"]["net_gain"], "linear_net_gain": direct_row["linear"]["net_gain"],
            "module_margin_over_simvote": round(module_eval["net_gain"] - direct_row["simvote"]["net_gain"], 4),
        })
        print(f"[{ANCHOR_NAME}] PART B real seed={seed} direct_gain={direct_row['ruleind']['net_gain']} "
              f"module_gain={module_eval['net_gain']} delta={delta_gain}", flush=True)
        if seed == real_seeds[0]:
            real_episodes_for_part_c = {"instances": instances, "seen_fail": seen_fail}

    scored_real = [r for r in real_rows if "skipped" not in r]
    real_max_delta = max((r["delta_net_gain"] for r in scored_real), default=0.0)
    real_beat_simvote_margin_mean = (round(sum(r["module_margin_over_simvote"] for r in scored_real) / len(scored_real), 4)
                                      if scored_real else None)

    overall_max_delta = max(ctrl_max_delta, real_max_delta)
    reproduction_verdict = ("HARD_PASS_BEHAVIOR_PRESERVED" if overall_max_delta <= REPRO_HARD_PASS_MAX_DELTA
                             else ("HARD_FAIL_BEHAVIOR_CHANGED" if overall_max_delta > REPRO_HARD_FAIL_MIN_DELTA
                                   else "MIDDLE_BAND"))

    return {
        "ctrl_rows": ctrl_rows, "ctrl_module_acc_mean": ctrl_module_acc_mean, "ctrl_max_delta": ctrl_max_delta,
        "ctrl_module_margin_over_simvote_mean": ctrl_margin_mean,
        "banked_CONTROL_ruleind_acc_mean": banked["CONTROL_ruleind_acc_mean"],
        "real_rows": real_rows, "real_max_delta": real_max_delta,
        "real_beat_simvote_margin_mean": real_beat_simvote_margin_mean,
        "banked_beat_simvote_margin_mean": banked["beat_simvote_margin_mean"],
        "banked_PRIMARY_real_ruleind_net_gain_mean": banked["PRIMARY_real_ruleind_net_gain_mean"],
        "leak_clean": leak_clean, "parser_uas": parser_info["uas_dev"],
        "overall_max_delta": overall_max_delta, "reproduction_verdict": reproduction_verdict,
        "_instances": instances,
    }


# ================================================================================================
# PART C: model-selection auto-choice.
# ================================================================================================
def run_part_c(part_a, part_b):
    # ---- TASK_XOR_CONTROL ----
    xor_instances = RULEIND.make_control_instances(50, seed=0)
    xor_key_fn = lambda ep: next(f for f in ep["feats"] if f.startswith("a:"))  # noqa: E731
    xor_label_fn = lambda ep: ep["gold_class"]  # noqa: E731
    xor_spec = {
        "candidate_plugins": ["estimation", "ruleind"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": xor_key_fn, "label_fn": xor_label_fn,
                           "classes": ["XOR0", "XOR1"]},
            "ruleind": {"key_fn": RULEIND.control_key_fn},
        },
    }
    chosen_xor, chosen_res_xor, all_xor = registry.learn(xor_instances, RULEIND.control_feat_fn, xor_spec)

    # ---- TASK_PPATTACH_REAL ----
    instances = part_b["_instances"]
    seen, held, seen_v = RULEIND.BASE.verb_split(instances, RULEIND.REAL_SEEDS[0], frac_seen=0.6)
    seen_fail = [a for a in seen if a["is_fail"]]
    pp_key_fn = lambda a: next((f for f in RULEIND.BASE.instance_feats(a) if f.startswith("p:")), "p:NONE")  # noqa: E731
    pp_label_fn = lambda a: a["gold_class"]  # noqa: E731
    pp_spec = {
        "candidate_plugins": ["estimation", "ruleind"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl", "key_fn": pp_key_fn, "label_fn": pp_label_fn,
                           "classes": list(RULEIND.BASE.ROLES)},
            "ruleind": {"key_fn": RULEIND.BASE.instance_key, "exclude_prefixes": ("v:",)},
        },
    }
    chosen_pp, chosen_res_pp, all_pp = registry.learn(seen_fail, RULEIND.BASE.instance_feats, pp_spec)

    def _summ(all_results):
        return {name: {"compression_ratio": round(r.compression_ratio, 4) if r.compression_ratio != float("inf") else "inf",
                        "description_bits": round(r.description_bits, 2), "null_bits": round(r.null_bits, 2),
                        "n_free_params": r.n_free_params, "cost_rank": r.cost_rank, "is_episodic": r.is_episodic,
                        "metrics": r.metrics}
                for name, r in all_results.items()}

    print(f"[{ANCHOR_NAME}] PART C TASK_XOR_CONTROL: chosen={chosen_xor} details={_summ(all_xor)}", flush=True)
    print(f"[{ANCHOR_NAME}] PART C TASK_PPATTACH_REAL: chosen={chosen_pp} details={_summ(all_pp)}", flush=True)

    if chosen_xor != "ruleind":
        autoselect_verdict = "HARD_FAIL_AUTOSELECT_BROKEN_XOR_WRONG"
    elif chosen_pp == chosen_xor:
        autoselect_verdict = "HARD_FAIL_AUTOSELECT_BROKEN_NO_DISCRIMINATION"
    elif chosen_pp == "estimation":
        autoselect_verdict = "HARD_PASS_AUTOSELECT_DISCRIMINATES"
    else:
        autoselect_verdict = "MIDDLE_BAND"

    return {
        "chosen_xor_control": chosen_xor, "chosen_ppattach_real": chosen_pp,
        "xor_control_results": _summ(all_xor), "ppattach_real_results": _summ(all_pp),
        "autoselect_verdict": autoselect_verdict,
    }


# ================================================================================================
def run():
    t0 = time.perf_counter()
    out_dir = _out_dir()
    os.makedirs(out_dir, exist_ok=True)
    print(f"[{ANCHOR_NAME}] START centralized Learner module refactor proof", flush=True)

    part_a = run_part_a(out_dir)
    part_b = run_part_b(out_dir)
    part_c = run_part_c(part_a, part_b)

    behavior_preserved = (part_a["reproduction_verdict"] == "HARD_PASS_BEHAVIOR_PRESERVED"
                          and part_b["reproduction_verdict"] == "HARD_PASS_BEHAVIOR_PRESERVED")
    any_hard_fail_repro = (part_a["reproduction_verdict"] == "HARD_FAIL_BEHAVIOR_CHANGED"
                           or part_b["reproduction_verdict"] == "HARD_FAIL_BEHAVIOR_CHANGED")
    autoselect_pass = part_c["autoselect_verdict"] == "HARD_PASS_AUTOSELECT_DISCRIMINATES"
    autoselect_fail = part_c["autoselect_verdict"].startswith("HARD_FAIL")

    if any_hard_fail_repro or autoselect_fail:
        overall = "HARD_FAIL_REFACTOR"
    elif behavior_preserved and autoselect_pass:
        overall = "HARD_PASS_REFACTOR_PROVEN"
    else:
        overall = "MIDDLE_BAND_REFACTOR"

    elapsed = time.perf_counter() - t0
    msg = (f"{overall} | A(condenser) max_delta={part_a['max_delta']} verdict={part_a['reproduction_verdict']} "
           f"| B(ruleind) ctrl_max_delta={part_b['ctrl_max_delta']} real_max_delta={part_b['real_max_delta']} "
           f"verdict={part_b['reproduction_verdict']} ctrl_acc_mean={part_b['ctrl_module_acc_mean']} "
           f"(banked={part_b['banked_CONTROL_ruleind_acc_mean']}) "
           f"real_beat_simvote_margin_mean={part_b['real_beat_simvote_margin_mean']} "
           f"(banked={part_b['banked_beat_simvote_margin_mean']}) "
           f"| C(autoselect) xor->{part_c['chosen_xor_control']} ppattach->{part_c['chosen_ppattach_real']} "
           f"verdict={part_c['autoselect_verdict']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "verdict": overall, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "part_a_condenser_reproduction": {k: v for k, v in part_a.items() if not k.startswith("_")},
        "part_b_ruleind_reproduction": {k: v for k, v in part_b.items() if not k.startswith("_")},
        "part_c_autoselect": part_c,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "reproduction-delta + auto-select discrimination measurement, not a CRLB-bound cell",
        "deterministic_seeding": True,
        "module_paths": ["hdlab/learner/core.py", "hdlab/learner/registry.py",
                         "hdlab/learner/plugins/estimation_plugin.py", "hdlab/learner/plugins/ruleind_plugin.py"],
        "wrapped_source_cells": ["experiments/exp_online_knowledge_condenser_selectional_v1.py (29476)",
                                 "experiments/exp_parser_ruleinduction_cls_ppattach_v1.py (29485)"],
        "not_banked": True, "not_queued": True,
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}] DONE {round(elapsed, 1)}s -> {overall}", flush=True)
    print(msg, flush=True)
    return payload


if __name__ == "__main__":
    try:
        run()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_out_dir(), e)
        raise
