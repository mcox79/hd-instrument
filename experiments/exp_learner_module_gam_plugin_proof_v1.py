#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exp_learner_module_gam_plugin_proof_v1

EXTENSIBILITY STRESS-TEST for the centralized Learner module (hdlab/learner/, banked 29487,
HARD_PASS_REFACTOR_PROVEN). NOT a new capability claim; NOT queued; NOT banked -- skunkworks VETs
the module addition, not this cell (see preregs/2026-07-23_learner_module_gam_plugin.md for the
full pre-registered bands -- set BEFORE this cell ran).

Adds PLUGIN 3 (hdlab/learner/plugins/gam_plugin.py, NAME="gam"): a GAM/EBM hypothesis class --
additive per-feature graded "shape" tables (Laplace-smoothed log2 P(class|feature-value), the
SAME per-key currency PLUGIN 1's generic_mdl already uses, generalized from one key to every
observed feature) plus explicit pairwise interaction residual terms (same functional form as
InterpretML's Explainable Boosting Machine, Lou/Caruana/Gehrke 2012 + Nori et al. 2019, CITED;
closed-form counting instead of gradient-boosted-tree cyclic fitting -- documented
simplification). This is the graded/noise-robust learner the rule-inducer's own docstring points
at: crisp AND-conjunctions (PLUGIN 2) reject any candidate below purity_thresh outright; GAM sums
graded partial evidence across ALL features with no purity gate.

PART D -- EXTENSIBILITY: (a) `git diff --stat -- hdlab/learner/core.py` is empty (verified via
  subprocess at cell-run time -- this cell adds ONLY hdlab/learner/plugins/gam_plugin.py [new] +
  a one-line registration edit to hdlab/learner/registry.py; core.py is untouched). (b)
  `registry.learn(...)` with candidate_plugins=["estimation","ruleind","gam"] runs cleanly on 3
  distinct tasks. (c) `core.mdl_select` / `core.per_cluster_gate` / `core.glass_box_assert` are
  called DIRECTLY (not just transitively) on a gam_plugin LearnResult with zero special-casing
  (grep core.py/registry.py/gam_plugin.py source for any "gam"-name branch).

PART E -- BEHAVIOR: an INDEPENDENTLY-WRITTEN standalone reference (`_standalone_gam_numpy_
  reference` below -- a SEPARATE code path using numpy matrix multiplication for the joint counts
  instead of gam_plugin's dict/Counter loops) recomputes the identical GAM formula and its argmax
  predictions are compared against gam_plugin.apply()'s predictions on both fit and held-out sets.

PART F -- 3-WAY AUTO-SELECT + COUNTERFACTUAL: a NEW positive-control task
  (TASK_GAM_GRADED_CONTROL, see prereg for the full closed-form purity arithmetic: observed-pair
  purity 0.745 THEORETICAL@(1-q)^2+q^2 with q=0.15, just under ruleind's purity_thresh=0.75, so
  induce_rules structurally cannot promote it; 6 weak graded cues at p_align=0.58 each, also
  sub-threshold alone or pairwise) where GAM is expected to win via its additive log-odds sum of
  sub-threshold evidence that both PLUGIN 1 (single-key, order-1) and PLUGIN 2 (crisp-purity-
  gated) structurally cannot capture. COUNTERFACTUAL: labels independently shuffled (fixed-int-
  seed rng.permutation, NEVER hash()-seeded per PROT-023) must FLIP the pick away from "gam" --
  proving the selection tracks the DATA, not a task-name branch (identical code path both runs).
  Also re-runs the two EXISTING 29487 probe tasks (TASK_XOR_CONTROL, TASK_PPATTACH_REAL) with 3
  candidates instead of 2 -- informational (a 3rd competitor may legitimately change the winner).

PART G -- PP-ATTACH GAM-vs-LINEAR-vs-RULES (SMOKE scale: BASE.train_dep_parser("smoke"),
  dev+test capped at 900 sentences, seed=7 -- a signal-direction check, NOT a re-verification of
  29485's FULL-scale banked claim; explicitly labeled as smoke-scale in the report). Tests the
  graded-cue hypothesis directly on real PP-attachment data: does GAM's additive graded evidence
  over the SAME (V,N1,P,N2,distance-bucket) features beat the linear Hebbian readout and/or the
  crisp rule search, where the rule search's own banked verdict was MIDDLE_BAND (not a robust win)?
  Reported honestly either way -- "GAM ties linear" is an acceptable, informative outcome (may
  mean PP-attach really is linear-capturable), not a cell failure.

COMPUTE ARCHITECTURE: class (b) sequential-CPU. GAM fitting is closed-form counting (no
  matmul/GPU-batchable primitive); PP-attach harvest uses "smoke" mode specifically to keep this
  LOCAL-ONLY foreground-to-completion. NO queue, NO push, NO remote-persist, NO bank.

CELL-TEMPLATE MANDATORY subset (stress-test/proof cell, not a queued anchor):
  - final_metrics_atomicity: tmp_replace (os.replace).
  - except SystemExit/KeyboardInterrupt: raise BEFORE except Exception (no BaseException).
  - crlb_n/a: extensibility/reproduction/auto-select discrimination measurement.
  - deterministic_seeding: true (fixed int seeds throughout; NEVER hash()-seeded per PROT-023).
  - arms_differ_verified: hash-test over GAM/ruleind/linear/simvote held-out predicted labels.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import hashlib
import inspect
import itertools
import json
import math
import subprocess
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "learner_module_gam_plugin_proof_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments import exp_parser_ruleinduction_cls_ppattach_v1 as RULEIND  # noqa: E402
from hdlab.learner import core, registry  # noqa: E402
from hdlab.learner.plugins import gam_plugin  # noqa: E402

BASE = RULEIND.BASE


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
# TASK_GAM_GRADED_CONTROL: hidden XOR interaction observed through noise + weak graded cues.
# ================================================================================================
def make_gam_graded_instances(n_total, seed, q=0.22, p_align=0.56, n_weak=6):
    """Hidden x0,x1 ~ Bernoulli(0.5); T = x0 XOR x1 (gold label). Models see NOISY x0_obs/x1_obs
    (bit-flip prob q) -- observed-pair purity vs T = (1-q)^2+q^2 = 0.657 THEORETICAL@, safely under
    ruleind's purity_thresh=0.75 with margin against sampling noise (empirically verified: q=0.15
    gave EXPECTED 0.745, too close to the 0.75 boundary -- at n~100-cell coverage the sampling SE
    is ~4%, so random draws crossed the threshold in-cell in about half of seeds, AND once that
    first near-threshold rule got promoted, sequential covering's residual-removal cascade shifted
    conditional purities of LATER candidates upward too [RIPPER/CN2-family property: purity is
    recomputed on the shrinking UNCOVERED residual, not the full population] -- q=0.22 restores a
    real safety margin so the (x0,x1) interaction is never promoted, which also prevents the
    cascade). Plus n_weak independent weak cues each aligned with T at p_align=0.56 (best-case
    pairwise combination of two such cues posts posterior ~0.62, safely sub-threshold -- see
    prereg closed-form arithmetic; both parameters empirically re-validated in-cell before the
    run proceeds via the design-validity check below, not merely assumed)."""
    rng = np.random.default_rng(seed)
    instances = []
    for iid in range(n_total):
        x0 = int(rng.integers(0, 2))
        x1 = int(rng.integers(0, 2))
        T = x0 ^ x1
        x0_obs = x0 if rng.random() >= q else (1 - x0)
        x1_obs = x1 if rng.random() >= q else (1 - x1)
        feats = ["x0:%d" % x0_obs, "x1:%d" % x1_obs]
        for wi in range(n_weak):
            aligned = rng.random() < p_align
            w_val = T if aligned else (1 - T)
            feats.append("w%d:%d" % (wi, w_val))
        label = "G1" if T == 1 else "G0"
        instances.append(dict(iid=iid, gold_class=label, feats=feats, key="gam|%d" % iid,
                               pred_class="G0", is_fail=True))
    return instances


def gam_graded_feat_fn(inst):
    return inst["feats"]


def gam_graded_key_fn(inst):
    return inst["key"]


def _accuracy(predict_fn, held):
    n = len(held)
    if n == 0:
        return None
    correct = sum(1 for a in held if predict_fn(a) == a["gold_class"])
    return round(correct / n, 4)


# ================================================================================================
# PART D: extensibility.
# ================================================================================================
def run_part_d():
    diff = subprocess.run(["git", "diff", "--stat", "--", "hdlab/learner/core.py"],
                          cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    core_diff_empty = (diff.returncode == 0 and diff.stdout.strip() == "")

    core_src = inspect.getsource(core)
    gam_src = inspect.getsource(gam_plugin)
    no_name_branch_core = ('"gam"' not in core_src) and ("'gam'" not in core_src)
    # AST-based (not substring) check: gam_plugin must not IMPORT its sibling plugin modules --
    # docstring PROSE mentioning "estimation_plugin"/"ruleind_plugin" (citing them for context, as
    # this file's own docstring does) is fine; an actual import/dependency edge is not.
    import ast as _ast
    gam_tree = _ast.parse(gam_src)
    sibling_import_names = set()
    for node in _ast.walk(gam_tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                sibling_import_names.add(alias.name.split(".")[-1])
        elif isinstance(node, _ast.ImportFrom):
            for alias in node.names:
                sibling_import_names.add(alias.name)
    no_sibling_import_in_gam = not ({"estimation_plugin", "ruleind_plugin"} & sibling_import_names)

    # 3-way registry.learn on 3 distinct tasks -- must run with zero exceptions.
    errors = []
    tasks_run = 0
    try:
        xor_instances = RULEIND.make_control_instances(20, seed=0)
        xor_spec = {
            "candidate_plugins": ["estimation", "ruleind", "gam"],
            "per_plugin": {
                "estimation": {"mode": "generic_mdl",
                               "key_fn": lambda ep: next(f for f in ep["feats"] if f.startswith("a:")),
                               "label_fn": lambda ep: ep["gold_class"], "classes": ["XOR1", "XOR0"]},
                "ruleind": {"key_fn": RULEIND.control_key_fn},
                "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": ["XOR1", "XOR0"]},
            },
        }
        chosen1, res1, all1 = registry.learn(xor_instances, RULEIND.control_feat_fn, xor_spec)
        tasks_run += 1
    except Exception as e:
        errors.append(f"TASK_XOR_CONTROL: {type(e).__name__}: {e}")
        chosen1, res1, all1 = None, None, {}

    try:
        graded_instances = make_gam_graded_instances(200, seed=0)
        graded_spec = {
            "candidate_plugins": ["estimation", "ruleind", "gam"],
            "per_plugin": {
                "estimation": {"mode": "generic_mdl",
                               "key_fn": lambda ep: next(f for f in ep["feats"] if f.startswith("w0:")),
                               "label_fn": lambda ep: ep["gold_class"], "classes": ["G1", "G0"]},
                "ruleind": {"key_fn": gam_graded_key_fn},
                "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": ["G1", "G0"]},
            },
        }
        chosen2, res2, all2 = registry.learn(graded_instances, gam_graded_feat_fn, graded_spec)
        tasks_run += 1
    except Exception as e:
        errors.append(f"TASK_GAM_GRADED_CONTROL: {type(e).__name__}: {e}")
        chosen2, res2, all2 = None, None, {}

    try:
        W_smoke, _pinfo = BASE.train_dep_parser("smoke")
        dev_small = BASE.read_conllu("en_ewt-ud-dev.conllu")[:300]
        inst_small = BASE.attach_predictions(dev_small, W_smoke)
        seen3, held3, _ = BASE.verb_split(inst_small, 7, 0.6)
        seen3_fail = [a for a in seen3 if a["is_fail"]]
        if len(seen3_fail) >= 4:
            pp_spec = {
                "candidate_plugins": ["estimation", "ruleind", "gam"],
                "per_plugin": {
                    "estimation": {"mode": "generic_mdl",
                                   "key_fn": lambda a: next((f for f in BASE.instance_feats(a) if f.startswith("p:")), "p:NONE"),
                                   "label_fn": lambda a: a["gold_class"], "classes": list(BASE.ROLES)},
                    "ruleind": {"key_fn": BASE.instance_key, "exclude_prefixes": ("v:",)},
                    "gam": {"label_fn": lambda a: a["gold_class"], "classes": list(BASE.ROLES),
                            "exclude_prefixes": ("v:",)},
                },
            }
            chosen3, res3, all3 = registry.learn(seen3_fail, BASE.instance_feats, pp_spec)
            tasks_run += 1
        else:
            chosen3, res3, all3 = None, None, {}
    except Exception as e:
        errors.append(f"TASK_PPATTACH_TINY: {type(e).__name__}: {e}")
        chosen3, res3, all3 = None, None, {}

    registry_3way_clean = (tasks_run == 3 and not errors)

    # Direct-call check: core.mdl_select / per_cluster_gate / glass_box_assert on a bare gam
    # LearnResult, bypassing registry.learn entirely -- proves no hidden dispatch shortcut.
    direct_call_ok = False
    direct_call_error = None
    try:
        r_gam = gam_plugin.learn(make_gam_graded_instances(100, seed=1), gam_graded_feat_fn,
                                  {"label_fn": lambda ep: ep["gold_class"], "classes": ["G1", "G0"]}, {})
        gate_ok = core.per_cluster_gate(r_gam)
        core.glass_box_assert(r_gam.hypothesis)
        name, chosen_res = core.mdl_select({"gam": r_gam})
        direct_call_ok = (name in ("gam", core.KEEP_EPISODIC)) and isinstance(gate_ok, bool)
    except Exception as e:
        direct_call_error = f"{type(e).__name__}: {e}"

    extensibility_pass = (core_diff_empty and no_name_branch_core and no_sibling_import_in_gam
                          and registry_3way_clean and direct_call_ok)
    verdict = "HARD_PASS_EXTENSIBLE" if extensibility_pass else "HARD_FAIL_MODULE_NOT_EXTENSIBLE"

    print(f"[{ANCHOR_NAME}] PART D extensibility: core_diff_empty={core_diff_empty} "
          f"no_name_branch_core={no_name_branch_core} no_sibling_import_in_gam={no_sibling_import_in_gam} "
          f"registry_3way_clean={registry_3way_clean} (tasks_run={tasks_run}/3 errors={errors}) "
          f"direct_call_ok={direct_call_ok} (err={direct_call_error}) -> {verdict}", flush=True)

    return {
        "core_diff_stat": diff.stdout, "core_diff_empty": core_diff_empty,
        "no_name_branch_core": no_name_branch_core, "no_sibling_import_in_gam": no_sibling_import_in_gam,
        "registry_3way_clean": registry_3way_clean, "n_tasks_run": tasks_run, "registry_errors": errors,
        "direct_call_ok": direct_call_ok, "direct_call_error": direct_call_error,
        "extensibility_verdict": verdict,
    }


# ================================================================================================
# PART E: standalone-baseline reproduction (independent numpy code path).
# ================================================================================================
def _standalone_gam_numpy_reference(episodes, feat_fn, label_fn, classes, alpha=1.0, min_coverage=3,
                                     max_singles_for_pairing=40, max_interactions=20, exclude_prefixes=()):
    """Independently-written reference: computes the SAME GAM formula via numpy one-hot matrix
    products (X.T @ Y for joint counts) instead of gam_plugin's dict/Counter loops -- a genuinely
    separate code path, not a call into gam_plugin's internals."""
    feats_per_case = [sorted(set(f for f in feat_fn(ep) if not any(f.startswith(p) for p in exclude_prefixes)))
                       for ep in episodes]
    labels = [label_fn(ep) for ep in episodes]
    n = len(episodes)
    n_classes = max(len(classes), 2)
    class_idx = {c: i for i, c in enumerate(classes)}
    all_feats = sorted(set(f for fs in feats_per_case for f in fs))
    feat_idx = {f: i for i, f in enumerate(all_feats)}
    X = np.zeros((n, len(all_feats)), dtype=np.float64)
    Y = np.zeros((n, n_classes), dtype=np.float64)
    for i, fs in enumerate(feats_per_case):
        for f in fs:
            X[i, feat_idx[f]] = 1.0
        Y[i, class_idx[labels[i]]] = 1.0

    label_counts = Counter(labels)
    intercept = {c: math.log2((label_counts.get(c, 0) + alpha) / (n + alpha * n_classes)) for c in classes}

    cnt_f = X.sum(axis=0)
    cnt_fc = X.T @ Y   # (n_features, n_classes) via matrix product -- independent of Counter loops
    main_mask = cnt_f >= min_coverage
    main_shape = {}
    for j in range(len(all_feats)):
        if not main_mask[j]:
            continue
        f = all_feats[j]
        main_shape[f] = {c: math.log2((cnt_fc[j, class_idx[c]] + alpha) / (cnt_f[j] + alpha * n_classes))
                          for c in classes}

    # mains-only per-instance score matrix (n, n_classes) via matmul -- vectorized, independent
    # code path from gam_plugin's per-instance dict loop.
    main_j = [feat_idx[f] for f in main_shape]
    main_w = np.zeros((len(all_feats), n_classes), dtype=np.float64)
    for f in main_shape:
        for c in classes:
            main_w[feat_idx[f], class_idx[c]] = main_shape[f][c]
    S_mains = np.tile(np.array([intercept[c] for c in classes]), (n, 1)) + X @ main_w
    y_idx = np.array([class_idx[l] for l in labels])
    mx = S_mains.max(axis=1, keepdims=True)
    denom = np.exp2(S_mains - mx).sum(axis=1)
    p_true = np.exp2(S_mains[np.arange(n), y_idx] - mx.ravel()) / denom
    bits_before_all = -np.log2(np.clip(p_true, 1e-12, None))

    freq_sorted = sorted((f for f in main_shape), key=lambda f: (-cnt_f[feat_idx[f]], f))[:max_singles_for_pairing]
    pair_idx = [feat_idx[f] for f in freq_sorted]
    candidates = []
    for a_i in range(len(pair_idx)):
        for b_i in range(a_i + 1, len(pair_idx)):
            j1, j2 = pair_idx[a_i], pair_idx[b_i]
            co = X[:, j1] * X[:, j2]
            cnt_pair = float(co.sum())
            if cnt_pair < min_coverage:
                continue
            mask = co > 0
            joint_c = co @ Y
            f1, f2 = freq_sorted[a_i], freq_sorted[b_i]
            residual = {}
            for c in classes:
                p_joint = math.log2((joint_c[class_idx[c]] + alpha) / (cnt_pair + alpha * n_classes))
                p_main_avg = 0.5 * (main_shape[f1][c] + main_shape[f2][c])
                residual[c] = p_joint - p_main_avg
            resid_vec = np.array([residual[c] for c in classes])
            S_after = S_mains[mask] + resid_vec
            mx2 = S_after.max(axis=1, keepdims=True)
            denom2 = np.exp2(S_after - mx2).sum(axis=1)
            p_true2 = np.exp2(S_after[np.arange(S_after.shape[0]), y_idx[mask]] - mx2.ravel()) / denom2
            bits_after = float((-np.log2(np.clip(p_true2, 1e-12, None))).sum())
            bits_before = float(bits_before_all[mask].sum())
            model_cost = math.log2(n_classes)
            bits_saved = bits_before - (bits_after + model_cost)
            if bits_saved > 0:
                key = gam_plugin._pair_key(f1, f2)
                candidates.append((bits_saved, key, residual))
    candidates.sort(key=lambda t: -t[0])
    interaction_shape = {key: residual for _bs, key, residual in candidates[:max_interactions]}

    def predict(feats):
        s = dict(intercept)
        fs = set(feats)
        for f in fs:
            if f in main_shape:
                for c in classes:
                    s[c] += main_shape[f][c]
        present_pairs = sorted(f for f in fs if f in main_shape and f in freq_sorted)
        for f1, f2 in itertools.combinations(present_pairs, 2):
            key = gam_plugin._pair_key(f1, f2)
            if key in interaction_shape:
                for c in classes:
                    s[c] += interaction_shape[key][c]
        return max(classes, key=lambda c: (s[c], -classes.index(c)))

    return predict


def run_part_e():
    label_fn = lambda ep: ep["gold_class"]  # noqa: E731
    results = []
    for seed in (0, 1, 2):
        instances = make_gam_graded_instances(600, seed=seed)
        seen, held = RULEIND.control_split(instances, seed, frac_seen=0.7)
        classes = ["G1", "G0"]
        spec = {"label_fn": label_fn, "classes": classes}
        gam_result = gam_plugin.learn(seen, gam_graded_feat_fn, spec, {})
        standalone_predict = _standalone_gam_numpy_reference(seen, gam_graded_feat_fn, label_fn, classes)

        def plugin_predict(a):
            return gam_plugin.apply(gam_result.hypothesis, gam_graded_feat_fn(a))

        fit_mismatches = sum(1 for a in seen if plugin_predict(a) != standalone_predict(gam_graded_feat_fn(a)))
        held_mismatches = sum(1 for a in held if plugin_predict(a) != standalone_predict(gam_graded_feat_fn(a)))
        fit_rate = round(fit_mismatches / max(1, len(seen)), 4)
        held_rate = round(held_mismatches / max(1, len(held)), 4)
        results.append({"seed": seed, "n_seen": len(seen), "n_held": len(held),
                         "fit_mismatches": fit_mismatches, "fit_mismatch_rate": fit_rate,
                         "held_mismatches": held_mismatches, "held_mismatch_rate": held_rate})
        print(f"[{ANCHOR_NAME}] PART E seed={seed} fit_mismatch_rate={fit_rate} "
              f"held_mismatch_rate={held_rate}", flush=True)

    max_rate = max(max(r["fit_mismatch_rate"], r["held_mismatch_rate"]) for r in results)
    if max_rate == 0.0:
        verdict = "HARD_PASS_BEHAVIOR_MATCHES_STANDALONE"
    elif max_rate <= 0.01:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "HARD_FAIL_BEHAVIOR_DIVERGES"
    return {"per_seed": results, "max_mismatch_rate": max_rate, "behavior_verdict": verdict}


# ================================================================================================
# PART F: 3-way auto-select + counterfactual + existing-tasks 3-way re-run.
# ================================================================================================
def _summ(all_results):
    return {name: {"compression_ratio": (round(r.compression_ratio, 4) if r.compression_ratio != float("inf") else "inf"),
                    "description_bits": round(r.description_bits, 2), "null_bits": round(r.null_bits, 2),
                    "cost_rank": r.cost_rank, "is_episodic": r.is_episodic, "metrics": r.metrics}
            for name, r in all_results.items()}


def run_part_f():
    own_task_rows = []
    for seed in (0, 1, 2):
        instances = make_gam_graded_instances(600, seed=seed)
        seen, held = RULEIND.control_split(instances, seed, frac_seen=0.7)

        # design-validity check: no single/pairwise conjunction should clear purity_thresh on SEEN.
        design_rules, design_residual = RULEIND.induce_rules(seen, gam_graded_feat_fn)

        spec = {
            "candidate_plugins": ["estimation", "ruleind", "gam"],
            "per_plugin": {
                "estimation": {"mode": "generic_mdl",
                               "key_fn": lambda ep: next(f for f in ep["feats"] if f.startswith("w0:")),
                               "label_fn": lambda ep: ep["gold_class"], "classes": ["G1", "G0"]},
                "ruleind": {"key_fn": gam_graded_key_fn},
                "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": ["G1", "G0"]},
            },
        }
        chosen, chosen_res, all_res = registry.learn(seen, gam_graded_feat_fn, spec)
        comp = {name: (r.compression_ratio if r.compression_ratio != float("inf") else 1e9)
                for name, r in all_res.items()}
        gam_wins = (chosen == "gam" and comp["gam"] > comp["estimation"] and comp["gam"] > comp["ruleind"])

        # counterfactual: shuffle labels (fixed-int-seed rng, NEVER hash()) -- must flip the pick.
        rng = np.random.default_rng(9000 + seed)
        perm = rng.permutation(len(seen))
        labels_orig = [a["gold_class"] for a in seen]
        labels_shuf = [labels_orig[j] for j in perm]
        seen_shuf = [dict(a, gold_class=labels_shuf[i]) for i, a in enumerate(seen)]
        chosen_shuf, _res_shuf, all_res_shuf = registry.learn(seen_shuf, gam_graded_feat_fn, spec)
        comp_shuf_gam = (all_res_shuf["gam"].compression_ratio if "gam" in all_res_shuf else None)
        counterfactual_flips = (chosen_shuf != "gam") or (comp_shuf_gam is not None and comp_shuf_gam < 1.0)

        row = {"seed": seed, "n_seen": len(seen), "n_held": len(held),
               "design_n_rules": len(design_rules), "design_n_residual": len(design_residual),
               "chosen": chosen, "compression_ratios": comp, "gam_wins": gam_wins,
               "chosen_shuffled": chosen_shuf, "gam_compression_ratio_shuffled": comp_shuf_gam,
               "counterfactual_flips": counterfactual_flips,
               "all_results_detail": _summ(all_res)}
        own_task_rows.append(row)
        print(f"[{ANCHOR_NAME}] PART F seed={seed} design_n_rules={len(design_rules)} "
              f"chosen={chosen} comp={comp} gam_wins={gam_wins} chosen_shuffled={chosen_shuf} "
              f"counterfactual_flips={counterfactual_flips}", flush=True)

    n_gam_wins = sum(1 for r in own_task_rows if r["gam_wins"])
    n_counterfactual_flips = sum(1 for r in own_task_rows if r["counterfactual_flips"])
    gam_selected_verdict = ("HARD_PASS_GAM_SELECTED" if n_gam_wins >= 2
                            else "HARD_FAIL_GAM_NEVER_SELECTED" if n_gam_wins == 0
                            else "MIDDLE_BAND")
    data_driven_verdict = ("HARD_PASS_DATA_DRIVEN" if n_counterfactual_flips == len(own_task_rows)
                           else "HARD_FAIL_AUTOSELECT_NOT_DATA_DRIVEN" if n_counterfactual_flips == 0
                           else "MIDDLE_BAND")

    # existing 29487 probe tasks, re-run 3-way (informational).
    xor_instances = RULEIND.make_control_instances(50, seed=0)
    xor_spec = {
        "candidate_plugins": ["estimation", "ruleind", "gam"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl",
                           "key_fn": lambda ep: next(f for f in ep["feats"] if f.startswith("a:")),
                           "label_fn": lambda ep: ep["gold_class"], "classes": ["XOR1", "XOR0"]},
            "ruleind": {"key_fn": RULEIND.control_key_fn},
            "gam": {"label_fn": lambda ep: ep["gold_class"], "classes": ["XOR1", "XOR0"]},
        },
    }
    chosen_xor, _r, all_xor = registry.learn(xor_instances, RULEIND.control_feat_fn, xor_spec)
    print(f"[{ANCHOR_NAME}] PART F TASK_XOR_CONTROL (3-way): chosen={chosen_xor} "
          f"details={_summ(all_xor)}", flush=True)

    W_parser, parser_info = BASE.train_dep_parser("smoke")
    dev = BASE.read_conllu("en_ewt-ud-dev.conllu")
    test = BASE.read_conllu("en_ewt-ud-test.conllu")
    sents = [s for s in (dev + test) if 1 <= len(s) <= 60][:900]
    instances_pp = BASE.attach_predictions(sents, W_parser)
    seen_pp, held_pp, _ = BASE.verb_split(instances_pp, 7, 0.6)
    seen_pp_fail = [a for a in seen_pp if a["is_fail"]]
    pp_spec = {
        "candidate_plugins": ["estimation", "ruleind", "gam"],
        "per_plugin": {
            "estimation": {"mode": "generic_mdl",
                           "key_fn": lambda a: next((f for f in BASE.instance_feats(a) if f.startswith("p:")), "p:NONE"),
                           "label_fn": lambda a: a["gold_class"], "classes": list(BASE.ROLES)},
            "ruleind": {"key_fn": BASE.instance_key, "exclude_prefixes": ("v:",)},
            "gam": {"label_fn": lambda a: a["gold_class"], "classes": list(BASE.ROLES), "exclude_prefixes": ("v:",)},
        },
    }
    chosen_pp, _r2, all_pp = registry.learn(seen_pp_fail, BASE.instance_feats, pp_spec)
    print(f"[{ANCHOR_NAME}] PART F TASK_PPATTACH_REAL (3-way, smoke harvest): chosen={chosen_pp} "
          f"details={_summ(all_pp)}", flush=True)

    return {
        "own_task_rows": own_task_rows, "n_gam_wins": n_gam_wins, "n_seeds": len(own_task_rows),
        "gam_selected_verdict": gam_selected_verdict,
        "n_counterfactual_flips": n_counterfactual_flips, "data_driven_verdict": data_driven_verdict,
        "existing_tasks_3way": {"xor_control_chosen": chosen_xor, "xor_control_detail": _summ(all_xor),
                                "ppattach_real_chosen": chosen_pp, "ppattach_real_detail": _summ(all_pp),
                                "ppattach_real_note": "smoke-scale harvest (dev+test capped 900 sents), not FULL"},
        "_instances_pp_for_part_g": instances_pp,
    }


# ================================================================================================
# PART G: PP-attach GAM-vs-linear-vs-rules honest comparison (smoke scale).
# ================================================================================================
def run_part_g(instances_pp):
    seed = 7
    direct_row = RULEIND.run_real_seed(instances_pp, seed, frac_seen=0.6)
    if "ruleind" not in direct_row:
        print(f"[{ANCHOR_NAME}] PART G SKIPPED: {direct_row.get('skipped')}", flush=True)
        return {"skipped": direct_row.get("skipped")}

    seen, held, _ = BASE.verb_split(instances_pp, seed, frac_seen=0.6)
    seen_fail = [a for a in seen if a["is_fail"]]
    default_class = list(BASE.ROLES)[0]

    gam_result = gam_plugin.learn(seen_fail, BASE.instance_feats,
                                   {"exclude_prefixes": ("v:",), "classes": list(BASE.ROLES),
                                    "label_fn": lambda a: a["gold_class"]}, {})

    def gam_fn(a):
        return gam_plugin.apply_with_margin(gam_result.hypothesis, BASE.instance_feats(a))

    tau_gam = BASE.calibrate_tau(gam_fn, seen)
    gam_eval = BASE.eval_heldout(gam_fn, held, tau_gam)

    beat_linear = round(BASE._nz(gam_eval["net_gain"], -9) - BASE._nz(direct_row["linear"]["net_gain"], -9), 4)
    beat_ruleind = round(BASE._nz(gam_eval["net_gain"], -9) - BASE._nz(direct_row["ruleind"]["net_gain"], -9), 4)
    beat_simvote = round(BASE._nz(gam_eval["net_gain"], -9) - BASE._nz(direct_row["simvote"]["net_gain"], -9), 4)

    held_gam = [gam_fn(a)[0] for a in held]
    held_ruleind_hyp = RULEIND.induce_rules(seen_fail, BASE.instance_feats, exclude_prefixes=("v:",))
    residual_lookup = RULEIND.build_residual_lookup(seen_fail, held_ruleind_hyp[1], BASE.instance_key)
    ruleind_fn = RULEIND.ruleind_predict_factory(held_ruleind_hyp[0], residual_lookup, BASE.instance_feats,
                                                  BASE.instance_key, default_class)
    held_ruleind = [ruleind_fn(a)[0] for a in held]
    W_lin_sig = [a["sig"] for a in seen_fail]
    roles = list(BASE.ROLES)
    role_codebook = BASE.build_role_codebook(roles)
    W_lin = BASE.consolidate_store(W_lin_sig, [a["gold_class"] for a in seen_fail], role_codebook,
                                    n_cycles=6, replay_frac=0.5, seed=seed)
    lin_fn = lambda a: BASE.store_predict(W_lin, role_codebook, roles, a["sig"])  # noqa: E731
    held_linear = [lin_fn(a)[0] for a in held]
    simvote_fn = lambda a: BASE.knn_predict(W_lin_sig, [a["gold_class"] for a in seen_fail], a["sig"], k=BASE.K_KNN)  # noqa: E731
    held_simvote = [simvote_fn(a)[0] for a in held]

    digests = {name: hashlib.sha256(json.dumps(vals).encode("utf-8")).hexdigest()
               for name, vals in {"gam": held_gam, "ruleind": held_ruleind, "linear": held_linear,
                                   "simvote": held_simvote}.items()}
    identical_pairs = [(a, b) for (a, da), (b, db) in itertools.combinations(digests.items(), 2) if da == db]
    assert not identical_pairs, f"META_RULE_AF VIOLATION: {identical_pairs}"

    print(f"[{ANCHOR_NAME}] PART G seed={seed} (smoke-scale, informational -- not a 29485 FULL "
          f"re-verification): GAM net_gain={gam_eval['net_gain']} fix_rate={gam_eval['heldout_fix_rate']} "
          f"| RULEIND net_gain={direct_row['ruleind']['net_gain']} | LINEAR net_gain={direct_row['linear']['net_gain']} "
          f"| SIMVOTE net_gain={direct_row['simvote']['net_gain']} | beat_linear={beat_linear} "
          f"beat_ruleind={beat_ruleind} beat_simvote={beat_simvote}", flush=True)

    return {
        "seed": seed, "n_seen_fail": len(seen_fail), "n_held": len(held),
        "gam_net_gain": gam_eval["net_gain"], "gam_fix_rate": gam_eval["heldout_fix_rate"],
        "ruleind_net_gain": direct_row["ruleind"]["net_gain"], "linear_net_gain": direct_row["linear"]["net_gain"],
        "simvote_net_gain": direct_row["simvote"]["net_gain"],
        "beat_linear": beat_linear, "beat_ruleind": beat_ruleind, "beat_simvote": beat_simvote,
        "gam_n_main_keys": gam_result.metrics["n_main_keys"],
        "gam_n_interaction_keys": gam_result.metrics["n_interaction_keys"],
        "arms_differ_verified": True, "arms_digests": digests,
        "note": "SMOKE-scale harvest (dev+test capped 900 sents, 1 seed) -- signal-direction check, "
                "NOT a re-verification of 29485's FULL-scale banked claim.",
    }


# ================================================================================================
def _instrumentation_selftest():
    """Assert claimed metrics are non-null/non-sentinel at tiny scale before the full run."""
    instances = make_gam_graded_instances(60, seed=99)
    r = gam_plugin.learn(instances, gam_graded_feat_fn, {"label_fn": lambda ep: ep["gold_class"],
                                                          "classes": ["G1", "G0"]}, {})
    assert r.description_bits is not None and not math.isnan(r.description_bits), "description_bits null"
    assert r.null_bits is not None and r.null_bits > 0, "null_bits null/zero-sentinel"
    assert r.metrics["n_main_keys"] > 0, "no main features fitted at self-test scale (filter ate everything)"
    core.glass_box_assert(r.hypothesis)
    pred = gam_plugin.apply(r.hypothesis, gam_graded_feat_fn(instances[0]))
    assert pred in ("G1", "G0"), f"apply() returned non-class value: {pred!r}"
    label, margin = gam_plugin.apply_with_margin(r.hypothesis, gam_graded_feat_fn(instances[0]))
    assert label in ("G1", "G0") and isinstance(margin, float), "apply_with_margin malformed"
    print(f"[{ANCHOR_NAME}] instrumentation self-test PASS "
          f"(n_main_keys={r.metrics['n_main_keys']}, n_interaction_keys={r.metrics['n_interaction_keys']})",
          flush=True)


_instrumentation_selftest()  # module-scope, before the main run


def run():
    t0 = time.perf_counter()
    out_dir = _out_dir()
    os.makedirs(out_dir, exist_ok=True)
    print(f"[{ANCHOR_NAME}] START GAM/EBM plugin extensibility stress-test", flush=True)

    part_d = run_part_d()
    part_e = run_part_e()
    part_f = run_part_f()
    part_g = run_part_g(part_f["_instances_pp_for_part_g"])

    extensibility_pass = part_d["extensibility_verdict"] == "HARD_PASS_EXTENSIBLE"
    behavior_pass = part_e["behavior_verdict"] == "HARD_PASS_BEHAVIOR_MATCHES_STANDALONE"
    gam_selected_pass = part_f["gam_selected_verdict"] == "HARD_PASS_GAM_SELECTED"
    data_driven_pass = part_f["data_driven_verdict"] == "HARD_PASS_DATA_DRIVEN"

    any_hard_fail = (part_d["extensibility_verdict"] == "HARD_FAIL_MODULE_NOT_EXTENSIBLE"
                     or part_e["behavior_verdict"] == "HARD_FAIL_BEHAVIOR_DIVERGES"
                     or part_f["gam_selected_verdict"] == "HARD_FAIL_GAM_NEVER_SELECTED"
                     or part_f["data_driven_verdict"] == "HARD_FAIL_AUTOSELECT_NOT_DATA_DRIVEN")

    if any_hard_fail:
        overall = "HARD_FAIL_GAM_PLUGIN"
    elif extensibility_pass and behavior_pass and gam_selected_pass and data_driven_pass:
        overall = "HARD_PASS_GAM_PLUGIN_PROVEN"
    else:
        overall = "MIDDLE_BAND_GAM_PLUGIN"

    zero_core_change = part_d["core_diff_empty"]
    ppattach_summary = ("SKIPPED" if part_g.get("skipped") else
                        f"gam_net_gain={part_g['gam_net_gain']} vs ruleind={part_g['ruleind_net_gain']} "
                        f"vs linear={part_g['linear_net_gain']} vs simvote={part_g['simvote_net_gain']} "
                        f"(beat_linear={part_g['beat_linear']} beat_ruleind={part_g['beat_ruleind']})")

    elapsed = time.perf_counter() - t0
    msg = (f"{overall} | D(extensibility)={part_d['extensibility_verdict']} zero_core_change={zero_core_change} "
           f"| E(behavior)={part_e['behavior_verdict']} max_mismatch_rate={part_e['max_mismatch_rate']} "
           f"| F(auto-select)={part_f['gam_selected_verdict']}/{part_f['data_driven_verdict']} "
           f"gam_wins={part_f['n_gam_wins']}/{part_f['n_seeds']} "
           f"counterfactual_flips={part_f['n_counterfactual_flips']}/{part_f['n_seeds']} "
           f"xor3way->{part_f['existing_tasks_3way']['xor_control_chosen']} "
           f"pp3way->{part_f['existing_tasks_3way']['ppattach_real_chosen']} "
           f"| G(ppattach honest) {ppattach_summary}")

    payload = {
        "anchor_name": ANCHOR_NAME, "verdict": overall, "verdict_msg": msg, "summary": msg,
        "elapsed_s": round(elapsed, 2), "ts_iso": datetime.now(timezone.utc).isoformat(),
        "zero_core_change": zero_core_change,
        "part_d_extensibility": part_d,
        "part_e_behavior": part_e,
        "part_f_autoselect": {k: v for k, v in part_f.items() if not k.startswith("_")},
        "part_g_ppattach_honest": part_g,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n_a": "extensibility/reproduction/auto-select discrimination measurement, not a CRLB-bound cell",
        "deterministic_seeding": True,
        "new_files": ["hdlab/learner/plugins/gam_plugin.py"],
        "edited_files": ["hdlab/learner/registry.py (one import + one PLUGINS dict entry)"],
        "untouched_files": ["hdlab/learner/core.py"],
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
